#!/usr/bin/env python3
"""Windows-compatible trigger-eval runner for the brainstorming skill.

For each query, launches `claude -p` (via a powershell child so the claude.ps1
shim resolves) and detects whether the brainstorming skill was triggered
(a Skill tool_use referencing it, or a Read of its SKILL.md). Pass/fail per the
skill-creator convention: should_trigger passes if trigger_rate >= threshold;
should_not_trigger passes if trigger_rate < threshold.

Usage:
  python run_triggers.py <eval.json> <out.json> [runs_per_query] [workers]
"""
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

MODEL = "claude-opus-4-7"
TIMEOUT = 90
THRESHOLD = 0.5


def _decide_from_stream(stdout, result_box):
    """Read claude -p stream-json line by line; decide trigger ASAP.

    Mirrors the vendored harness: detect the Skill/Read tool firing from
    streaming events and stop immediately rather than waiting for the (long)
    brainstorming run to finish. Stores 'yes'/'no' in result_box[0].
    """
    pending = None          # 'Skill' or 'Read' tool block in progress
    acc = ""                # accumulated tool input json
    for line in stdout:     # blocking line iteration (no select needed)
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "stream_event":
            se = ev.get("event", {})
            st = se.get("type", "")
            if st == "content_block_start":
                cb = se.get("content_block", {})
                if cb.get("type") == "tool_use":
                    name = cb.get("name", "")
                    if name in ("Skill", "Read"):
                        pending, acc = name, ""
                    else:
                        result_box[0] = "no"   # model used a different tool first
                        return
            elif st == "content_block_delta" and pending:
                d = se.get("delta", {})
                if d.get("type") == "input_json_delta":
                    acc += d.get("partial_json", "")
                    if "brainstorming" in acc:
                        result_box[0] = "yes"
                        return
            elif st in ("content_block_stop", "message_stop"):
                if pending:
                    result_box[0] = "yes" if "brainstorming" in acc else "no"
                    return
                if st == "message_stop":
                    result_box[0] = "no"
                    return
        elif t == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") != "tool_use":
                    continue
                name = c.get("name", "")
                inp = c.get("input", {}) or {}
                if name == "Skill" and "brainstorming" in str(inp.get("skill", "")):
                    result_box[0] = "yes"
                    return
                fp = str(inp.get("file_path", ""))
                if name == "Read" and "brainstorming" in fp and "SKILL.md" in fp:
                    result_box[0] = "yes"
                    return
                result_box[0] = "no"
                return
        elif t == "result":
            if result_box[0] is None:
                result_box[0] = "no"
            return


def run_once(query: str) -> str:
    """Run one claude -p probe; return 'yes'/'no'/'timeout'/'error'."""
    env = dict(os.environ)
    env["BSQ"] = query
    ps_cmd = (
        "claude -p $env:BSQ --output-format stream-json --verbose "
        f"--include-partial-messages --model {MODEL}"
    )
    try:
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace", env=env,
        )
    except Exception:
        return "error"

    result_box = [None]
    reader = threading.Thread(target=_decide_from_stream, args=(proc.stdout, result_box))
    reader.daemon = True
    reader.start()
    reader.join(TIMEOUT)

    # Stop the (possibly still-running) claude process either way
    if proc.poll() is None:
        proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:
            pass

    if result_box[0] is None:
        return "timeout"
    return result_box[0]


def main():
    eval_path, out_path = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 6

    eval_set = json.loads(open(eval_path, encoding="utf-8").read())

    # Build (query, should_trigger, run_idx) jobs
    jobs = []
    for item in eval_set:
        for r in range(runs):
            jobs.append((item["query"], item["should_trigger"], r))

    triggers: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fut = {ex.submit(run_once, q): (q, st) for (q, st, r) in jobs}
        done = 0
        for f in as_completed(fut):
            q, st = fut[f]
            res = f.result()
            triggers.setdefault(q, []).append(res)
            done += 1
            print(f"[{done}/{len(jobs)}] {res:7} | {q[:55]}", file=sys.stderr, flush=True)

    results = []
    for item in eval_set:
        q = item["query"]
        outs = triggers.get(q, [])
        yes = sum(1 for o in outs if o == "yes")
        rate = yes / len(outs) if outs else 0.0
        should = item["should_trigger"]
        passed = (rate >= THRESHOLD) if should else (rate < THRESHOLD)
        results.append({
            "query": q,
            "should_trigger": should,
            "trigger_rate": rate,
            "triggers": yes,
            "runs": len(outs),
            "raw": outs,
            "pass": passed,
        })

    # Confusion stats
    tp = sum(r["triggers"] for r in results if r["should_trigger"])
    pos_runs = sum(r["runs"] for r in results if r["should_trigger"])
    fp = sum(r["triggers"] for r in results if not r["should_trigger"])
    neg_runs = sum(r["runs"] for r in results if not r["should_trigger"])
    fn = pos_runs - tp
    tn = neg_runs - fp
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    passed_q = sum(1 for r in results if r["pass"])

    out = {
        "model": MODEL,
        "runs_per_query": runs,
        "threshold": THRESHOLD,
        "queries_passed": passed_q,
        "queries_total": len(results),
        "precision": precision,
        "recall": recall,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "results": results,
    }
    open(out_path, "w", encoding="utf-8").write(json.dumps(out, indent=2))
    print(f"\nDONE: {passed_q}/{len(results)} queries passed | "
          f"precision={precision:.0%} recall={recall:.0%} | "
          f"FP={fp} FN={fn}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()

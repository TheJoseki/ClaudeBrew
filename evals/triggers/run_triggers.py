#!/usr/bin/env python3
"""Windows-compatible trigger-eval runner for the cbr:brainstorming skill.

For each query, launches `claude -p` (via a powershell child so the claude.ps1
shim resolves) and detects whether the brainstorming skill was triggered
(a Skill tool_use referencing it, or a Read of its SKILL.md). Detection is by the
substring "brainstorming", which matches both the standalone name and the plugin-
namespaced form `cbr:brainstorming` — so the same detector works whether the skill
is loaded via `--plugin-dir`/install or from a standalone `.claude/` checkout.
Pass/fail per the skill-creator convention: should_trigger passes if
trigger_rate >= threshold; should_not_trigger passes if trigger_rate < threshold.

Usage:
  python run_triggers.py <eval.json> <out.json> [runs_per_query] [workers]
"""
import json
import os
import subprocess
import sys
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Empty = use the CLI's current default model. Pinning a stale model measured the
# OLD model answering from memory (not the skill's triggerability) — e.g. opus-4-7
# answers "REST vs GraphQL" inline without consulting the `architecture` skill.
MODEL = os.environ.get("CBR_TRIGGER_MODEL", "")
TIMEOUT = 90
THRESHOLD = 0.5
# Which skill's triggering to detect (substring; matches the plain and `cbr:`-namespaced
# forms). Override to eval a different skill, e.g. CBR_TRIGGER_SKILL=design-system.
SKILL = os.environ.get("CBR_TRIGGER_SKILL", "brainstorming")
# When set, load the plugin into each headless probe so its skills are actually
# available to trigger (without this, `claude -p` runs with the plugin unloaded and
# every should-trigger query reads as a miss).
PLUGIN_DIR = os.environ.get("CBR_PLUGIN_DIR", "")


def _reader(stdout, box):
    """Accumulate the stream buffer; set box[0]='yes' AS SOON AS the target skill's
    SKILL.md read (or a Skill tool_use naming it) appears, so run_once can kill the
    probe immediately instead of waiting for the (possibly long) generation. 'no' at
    end of stream. Separators are normalized (JSON escapes Windows `\\`, nested
    tool_results double-escape it); requiring SKILL.md for the path avoids matching an
    unrelated file that merely contains the skill word (e.g. system-architecture.md).
    Block/event shapes vary across runs, so this matches the raw buffer, not a parse."""
    path_re = re.compile(r"skills/+" + re.escape(SKILL) + r"/+SKILL\.md")
    skill_re = re.compile(r'"skill":"[^"]*' + re.escape(SKILL))
    buf = ""
    for line in stdout:
        buf += line
        if path_re.search(buf.replace("\\", "/")) or skill_re.search(buf):
            box[0] = "yes"
            return
    box[0] = box[0] or "no"


def run_once(query: str) -> str:
    """Run one claude -p probe; return 'yes'/'no'/'timeout'/'error'."""
    env = dict(os.environ)
    env["BSQ"] = query
    plugin = f" --plugin-dir '{PLUGIN_DIR}'" if PLUGIN_DIR else ""
    # --max-turns 1: triggering is decided in the first assistant turn (the model
    # surfaces the skill's SKILL.md then); bounding it keeps probes fast and avoids
    # the model running the whole task (and its file side-effects).
    model = f" --model {MODEL}" if MODEL else ""
    ps_cmd = (
        "claude -p $env:BSQ --output-format stream-json --verbose "
        f"--include-partial-messages --max-turns 1{model}{plugin}"
    )
    try:
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace", env=env,
        )
    except Exception:
        return "error"

    box = [None]
    reader = threading.Thread(target=_reader, args=(proc.stdout, box))
    reader.daemon = True
    reader.start()
    reader.join(TIMEOUT)
    if proc.poll() is None:      # decided early ('yes') or hit TIMEOUT — stop the probe
        proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:
            pass
    return box[0] or "timeout"


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

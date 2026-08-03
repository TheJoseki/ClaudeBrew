#!/usr/bin/env python3
"""Durable tests for compact-context-saver.py (PreCompact checkpoint writer).

Run: python evals/test_compact_saver.py

Loaded IN-PROCESS via importlib (so `coverage` instruments it). main() is exercised
with patched stdin + CLAUDE_PROJECT_DIR over throwaway trees; assertions read the
written checkpoint. Exit non-zero if any case fails.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

_HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "cbr", "hooks",
)


def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HOOKS, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # __main__-guarded: does not run main()
    return mod


CS = _load("compact_context_saver", "compact-context-saver.py")

_FAILURES = []


def check(cond, msg):
    if not cond:
        _FAILURES.append(msg)


def write(root, relpath, content="", mtime=None):
    full = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    if mtime is not None:
        os.utime(full, (mtime, mtime))
    return full


def run_main(stdin_str, project_dir):
    """Invoke CS.main() with patched stdin + CLAUDE_PROJECT_DIR; return checkpoint text."""
    old_stdin, old_env = sys.stdin, os.environ.get("CLAUDE_PROJECT_DIR")
    sys.stdin = io.StringIO(stdin_str)
    os.environ["CLAUDE_PROJECT_DIR"] = project_dir
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                CS.main()
            except SystemExit:
                pass
    finally:
        sys.stdin = old_stdin
        if old_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = old_env
    path = os.path.join(project_dir, ".claude", "compact-checkpoint.md")
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_cs_minimal_empty_tree():
    with tempfile.TemporaryDirectory() as d:
        out = run_main("{}", d)
        check("Pre-Compact Checkpoint" in out, "checkpoint written")
        check("Plan file: none" in out, "no active plan -> none")
        check("Log file: none" in out, "no work-log -> none")
        check("(none detected)" in out, "no files/tasks detected")
        check("trigger: unknown" in out, "default trigger")


def test_cs_bad_stdin():
    with tempfile.TemporaryDirectory() as d:
        out = run_main("{not json", d)  # json.load fails -> data={}
        check("trigger: unknown" in out, "bad stdin -> defaults")


def test_cs_full_transcript():
    with tempfile.TemporaryDirectory() as d:
        tp = write(d, "transcript.jsonl",
                   '{"type":"tool_use","file_path":"src/a.py","description":"do a"}\n'
                   '{"type":"tool_use","file_path":"src/b.py","description":"do b"}\n')
        out = run_main(json.dumps({"trigger": "auto", "transcript_path": tp}), d)
        check("src/a.py" in out and "src/b.py" in out, "recent files parsed")
        check("do a" in out and "do b" in out, "recent tasks parsed")
        check("trigger: auto" in out, "trigger passed through")
        check("Tool calls in recent context window: 2" in out, "tool_count counted")


def test_cs_transcript_path_missing_file():
    with tempfile.TemporaryDirectory() as d:
        out = run_main('{"transcript_path":"C:/nope/does-not-exist.jsonl"}', d)
        check("(none detected)" in out, "missing transcript -> no files")


def test_cs_active_plan_with_phase():
    with tempfile.TemporaryDirectory() as d:
        write(d, "docs/streams/pay-20260801/plan/PLAN.md", "# Plan\n| 1 | Build | ⏳ IN_PROGRESS |\n")
        out = run_main("{}", d)
        check("Plan file: pay-20260801" in out, "active stream plan detected (reports stream folder)")
        check("⏳" in out and "IN_PROGRESS" in out, "current phase captured")


def test_cs_active_plan_no_phase_marker():
    with tempfile.TemporaryDirectory() as d:
        write(d, "docs/streams/pay-20260801/plan/PLAN.md", "# Plan\nno marker here\n")
        out = run_main("{}", d)
        check("Plan file: pay-20260801" in out, "stream plan detected")
        check("Current phase: N/A" in out, "no marker -> N/A")


def test_cs_newest_stream_plan():
    with tempfile.TemporaryDirectory() as d:
        write(d, "docs/streams/old-20260101/plan/PLAN.md", "old", mtime=1_000_000)
        write(d, "docs/streams/new-20260801/plan/PLAN.md", "new", mtime=2_000_000)
        out = run_main("{}", d)
        check("Plan file: new-20260801" in out, "newest stream's plan is reported active")


def test_cs_worklog_status():
    with tempfile.TemporaryDirectory() as d:
        write(d, "docs/streams/pay-20260801/work-logs/DEV-20260801.md", "# Log\nSTATUS: IN_PROGRESS\n")
        out = run_main("{}", d)
        check("Log file: DEV-20260801.md" in out, "work-log detected")
        check("STATUS: IN_PROGRESS" in out, "work-log status captured")


def test_cs_plan_read_error():
    # A directory where PLAN.md should be: glob matches it, open() raises -> except: pass.
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs", "streams", "bad-20260801", "plan", "PLAN.md"))
        out = run_main("{}", d)
        check("Plan file: bad-20260801" in out, "stream name set even if PLAN unreadable")
        check("Current phase: N/A" in out, "unreadable plan -> phase N/A via except")


def test_cs_worklog_read_error():
    # A directory where a work-log should be: selected as newest, open() raises -> except: pass.
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs", "streams", "x-20260801", "work-logs", "DEV-bad.md"))
        out = run_main("{}", d)
        check("Log file: DEV-bad.md" in out, "log name set even if unreadable")
        check("Status: N/A" in out, "unreadable log -> status N/A via except")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)}):")
        for f in _FAILURES:
            print("  -", f)
        sys.exit(1)
    print(f"OK — {len(tests)} compact-saver tests passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tests for settings_merge.py — the runnable proxy for /cbr:setup's worktree-gate
registration (a markdown skill can't be invoked from a subprocess test, but the
pure-Python merge it calls can). Run: python evals/test_settings_merge.py
"""
import json
import os
import subprocess
import sys
import tempfile

HELPER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "cbr", "hooks", "settings_merge.py",
)
HOOK = "/abs/path/to/enforce-worktree.py"


def commands(settings):
    return [h["command"] for e in settings["hooks"]["PreToolUse"] for h in e.get("hooks", [])]


def run(path):
    subprocess.run([sys.executable, HELPER, path, HOOK], check=True, capture_output=True, text=True)


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "settings.json")

        # 1. registers into a non-existent settings file, exactly once
        run(path)
        s = json.load(open(path))
        n = sum("enforce-worktree.py" in c for c in commands(s))
        ok = n == 1
        failures += not ok
        print(f"{'OK  ' if ok else 'FAIL'} register (count={n}, expect 1)")

        # 2. idempotent: a second run adds no duplicate
        run(path)
        s = json.load(open(path))
        n = sum("enforce-worktree.py" in c for c in commands(s))
        ok = n == 1
        failures += not ok
        print(f"{'OK  ' if ok else 'FAIL'} idempotent (count={n}, expect 1)")

        # 3. preserves unrelated settings + other PreToolUse entries
        json.dump({"model": "opus", "hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "x"}]}]}},
            open(path, "w"))
        run(path)
        s = json.load(open(path))
        cmds = commands(s)
        ok = (s.get("model") == "opus"
              and any(e.get("matcher") == "Bash" for e in s["hooks"]["PreToolUse"])
              and any("enforce-worktree.py" in c for c in cmds))
        failures += not ok
        print(f"{'OK  ' if ok else 'FAIL'} preserve unrelated settings")

    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

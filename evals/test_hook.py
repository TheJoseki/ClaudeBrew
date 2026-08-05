#!/usr/bin/env python3
"""Durable tests for enforce-worktree.py — run: python evals/test_hook.py

The hook's decision depends on the current branch, so these tests build a
throwaway git repo (on `main`, then on a feature branch) and feed the hook
synthetic PreToolUse payloads with cwd pointed at that repo. This makes the
expected results deterministic regardless of which branch you happen to be on
when you run the tests. Exit code is non-zero if any case fails.
"""
import json
import os
import subprocess
import sys
import tempfile

# test_hook.py lives in evals/; the hook ships inside the plugin. Resolve from
# the repo root (parent of evals/) into the plugin's hooks/ directory.
HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "claude", "hooks", "enforce-worktree.py",
)


def run_hook(file_path, cwd):
    payload = json.dumps({"tool_input": {"file_path": file_path}, "cwd": cwd})
    out = subprocess.run(
        [sys.executable, HOOK], input=payload, capture_output=True, text=True
    ).stdout.strip()
    return "DENY" if out else "ALLOW"


def git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as repo:
        git(["init", "-b", "main"], repo)
        git(["config", "user.email", "t@t"], repo)
        git(["config", "user.name", "t"], repo)
        git(["commit", "--allow-empty", "-m", "init"], repo)

        j = lambda *p: os.path.join(repo, *p)
        # On main: feature code denied, SDLC/config/docs allowed.
        cases_main = [
            (j("src", "app.ts"), "DENY"),
            (j("packages", "api", "server.py"), "DENY"),
            (j("docs", "streams", "pay-20260801", "brainstorm", "BRAINSTORM.md"), "ALLOW"),
            (j("docs", "streams", "pay-20260801", "assets", "stitch", "SCR-01.png"), "ALLOW"),
            (j(".claude", "settings.json"), "ALLOW"),
            (j(".claude", "hooks", "enforce-worktree.py"), "ALLOW"),
            (j("README.md"), "ALLOW"),
            (j(".gitignore"), "ALLOW"),
        ]
        for path, expect in cases_main:
            got = run_hook(path, repo)
            ok = got == expect
            failures += not ok
            print(f"{'OK  ' if ok else 'FAIL'} [main]    {got:5} expect={expect:5} {os.path.relpath(path, repo)}")

        # On a feature branch: everything is allowed (isolation already achieved).
        git(["checkout", "-b", "feature/x"], repo)
        for path, _ in cases_main:
            got = run_hook(path, repo)
            ok = got == "ALLOW"
            failures += not ok
            print(f"{'OK  ' if ok else 'FAIL'} [feature] {got:5} expect=ALLOW {os.path.relpath(path, repo)}")

    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

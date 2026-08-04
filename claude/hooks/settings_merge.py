#!/usr/bin/env python3
"""Idempotently register the worktree gate (enforce-worktree.py) as a PreToolUse
hook in a settings.json.

The worktree gate is OPT-IN: a plugin cannot ship harness settings, so /cbr:setup
merges the registration into the *user's* .claude/settings.json when they opt in.

Usage:  python settings_merge.py <settings.json path> <absolute enforce-worktree.py path>

The hook path MUST be absolute. A ${CLAUDE_PROJECT_DIR}-anchored or relative path
does not resolve inside a user's settings.json at load time — so the caller
resolves the real installed absolute path and passes it here. This is a pure function over
a settings dict (plus a thin CLI) so it is unit-testable without running the skill.
"""
import json
import os
import sys

MATCHER = "Edit|Write|NotebookEdit"


def _command(hook_path):
    return f'python "{hook_path}"'


def merge(settings, hook_path):
    """Add the worktree-gate PreToolUse registration if absent. Idempotent.

    Preserves any unrelated settings and other PreToolUse entries.
    """
    cmd = _command(hook_path)
    hooks = settings.setdefault("hooks", {})
    pre = hooks.setdefault("PreToolUse", [])
    for entry in pre:
        if entry.get("matcher") == MATCHER:
            existing = entry.setdefault("hooks", [])
            if not any(h.get("command") == cmd for h in existing):
                existing.append({"type": "command", "command": cmd})
            return settings
    pre.append({"matcher": MATCHER, "hooks": [{"type": "command", "command": cmd}]})
    return settings


def main():
    if len(sys.argv) != 3:
        print("usage: settings_merge.py <settings.json> <abs enforce-worktree.py>", file=sys.stderr)
        sys.exit(2)
    path, hook_path = sys.argv[1], sys.argv[2]
    settings = {}
    if os.path.isfile(path):
        try:
            settings = json.load(open(path, encoding="utf-8")) or {}
        except Exception:
            settings = {}
    merge(settings, hook_path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()

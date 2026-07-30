#!/usr/bin/env python3
"""PreToolUse hook — the deterministic gate behind the `worktree` skill.

Why this exists as a script and not as a line in SKILL.md: a markdown
instruction is a *probabilistic* constraint — the model reads it and usually
complies, but "usually" is not "always". This hook is run by the Claude Code
harness before every Edit/Write/NotebookEdit, so the constraint becomes
deterministic: feature code simply cannot be written on the base branch.

Contract (see https://code.claude.com/docs/en/hooks.md):
  - stdin  : JSON with tool_input.file_path (or notebook_path) and cwd
  - stdout : on a block, JSON {"hookSpecificOutput": {permissionDecision: deny}}
  - exit 0 : always (the decision rides in the JSON, not the exit code)

Design stance: fail OPEN. If git state can't be read (not a repo, git missing,
malformed input), the hook allows the edit. A safety gate that bricks unrelated
work is worse than one with a known, documented bypass — and the bypass here is
narrow (it only triggers when we genuinely can't tell where we are).
"""
import sys
import os
import json
import fnmatch
import subprocess

# Branches that count as "base" — editing feature code here is what we block.
BASE_BRANCHES = {"main", "master"}

# These paths are NOT feature code, so edits to them are always allowed — even
# on the base branch. This is the load-bearing list: without it the hook would
# block the brainstorming skill from writing its own artifact on main, which
# would make the whole pipeline self-defeating. It is *scope*, not an opt-out.
#   - docs/specs/* : SDLC handoff artifacts every stage reads/writes
#   - .claude/*    : skills, settings, hooks (harness config, never the product)
#   - *.md         : documentation, at any depth (fnmatch '*' spans '/')
#   - dotfiles that configure the repo/worktrees themselves
EXEMPT_GLOBS = [
    "docs/specs/*",
    ".claude/*",
    "*.md",
    ".gitignore",
    ".worktreeinclude",
]


def git(args, cwd):
    """Run a git command in cwd; return stripped stdout, or "" on any failure."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unreadable payload -> fail open

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    cwd = data.get("cwd") or os.getcwd()

    if not file_path:
        sys.exit(0)  # nothing to locate -> fail open

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if not branch or branch not in BASE_BRANCHES:
        # On a worktree/feature branch (or git unreadable) -> allow.
        sys.exit(0)

    repo_root = git(["rev-parse", "--show-toplevel"], cwd) or cwd
    try:
        rel = os.path.relpath(file_path, repo_root)
    except ValueError:
        # file on a different drive than the repo (Windows) -> outside the repo,
        # so it is not this repo's feature code -> fail open (allow), never deny.
        sys.exit(0)
    rel = rel.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]

    if any(fnmatch.fnmatch(rel, pat) for pat in EXEMPT_GLOBS):
        sys.exit(0)  # SDLC artifact / harness config / docs -> allow

    reason = (
        f"Hard-mandatory worktree policy: editing feature code on '{branch}' is "
        f"blocked ({rel}). Development of an approved approach must happen in an "
        f"isolated git worktree on a feature branch, not on the base branch. "
        f"Enter one first via the EnterWorktree tool (the `worktree` skill "
        f"orchestrates this), then retry this edit."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()

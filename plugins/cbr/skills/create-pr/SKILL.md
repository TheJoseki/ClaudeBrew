---
name: create-pr
description: Creates a Pull Request with a complete description for any project. TRIGGER: user asks to create PR, open pull request, push branch to review. NOT FOR: committing code, merging, or code review itself.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: core-sdlc
---

# PR Creator

$ARGUMENTS

## Live Project Context (auto-injected)

- Current branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(not a git repo)"`
- Changes vs base: !`git diff --stat $(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null || echo HEAD~1) 2>/dev/null | tail -5 || echo "(no diff available)"`
- Commits to merge: !`git log --oneline $(git merge-base HEAD main 2>/dev/null || echo HEAD~5)..HEAD 2>/dev/null || echo "(no log available)"`

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect project name, tech stack, and test commands before taking action.

## Required Reading

- `docs/CODING_RULES.md` — Git rules: branch naming, commit convention, PR checklist (if exists)

## Process

1. `git status` + `git diff --stat` to review all changes
2. Create PR description (summary, changes, test results)
3. `gh pr create`

## Checklist

- Backend tests pass (run backend test command from PROJECT.md)
- Frontend tests pass (run frontend test command from PROJECT.md)
- Type check passes (tsc, vue-tsc, mypy, or equivalent — per PROJECT.md)
- Role-based access verified
- Key business workflows tested
- i18n / localization complete (if applicable)
- No hardcoded secrets
- ORM migrations are safe (if applicable)
- Soft delete pattern followed (if applicable)

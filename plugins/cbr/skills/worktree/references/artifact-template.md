# Handoff artifact template — worktree stage

Write to `docs/specs/worktrees/WORKTREE-<topic>.md` (`<topic>` =
the same slug as the brainstorm). Write it **inside the worktree** (Phase 5), so
it lives on the feature branch alongside the work it describes. It is the contract
the `requirement` stage reads — that stage should be able to start from this file
plus the linked brainstorm alone.

This is a thin stage, so the artifact is short. It records *where the work now
lives* and *that isolation is enforced* — nothing more.

ALWAYS use this exact structure:

```markdown
# Worktree: <Topic>

- **Date:** YYYY-MM-DD
- **Stage:** 1.5 — worktree isolation
- **Status:** active
- **Author:** worktree skill

## 1. Source brainstorm
Path to the approved `…-brainstorm.md` this work derives from, and how it was
carried across (committed to base branch / copied via `.worktreeinclude`).

## 2. Isolation
- **Worktree path:** .claude/worktrees/<name>/
- **Feature branch:** <branch>
- **Base branch:** main | master
- **Base ref mode:** head | fresh
- **Entered via:** EnterWorktree (name) | EnterWorktree (existing path)

## 3. Enforcement status
- **Gate installed:** yes | no — OPT-IN `PreToolUse` hook (`enforce-worktree.py`)
  in a `.claude/settings.json`, registered by `/cbr:setup`. Default is **no**: the
  plugin does not ship it active.
- **Effect (if yes):** feature-code edits on the base branch are denied; edits
  inside this worktree are allowed.
- **If "no" (the default):** isolation is **advisory** — the move is done but no
  harness-level denial is in effect. State this explicitly and note that running
  `/cbr:setup` installs the gate to make it deterministic.

## 4. Scope carried forward
The approach being implemented (1–2 lines from the brainstorm's recommended
approach), and any open questions the brainstorm carried forward for `requirement`
to close.

## 5. Handoff notes
Next stage = `requirement`, run **inside this worktree**. The skill stops here;
the user decides when Stage 2 begins.
```

## Quality bar

Before handing off, the artifact must contain **zero** placeholders and must
reflect the *actual* state — the real branch name from `git`, the real worktree
path, and the true `Gate installed` value (never claim `yes` without confirming
the hook is registered). A handoff that misreports enforcement is worse than none,
because it tells the next stage isolation holds when it may not.

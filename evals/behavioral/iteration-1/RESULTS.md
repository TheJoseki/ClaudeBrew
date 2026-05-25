# worktree skill — behavioral eval, iteration 1

Date: 2026-05-25. Environment: Windows, Claude Code, model claude-opus-4-7.

## Why this eval is shaped differently from the standard skill-creator flow

The standard with-skill-vs-baseline subagent benchmark does not fit this skill in
this environment, for concrete reasons discovered via a read-only probe subagent:

- A subagent **inherits the real project's harness config** (active hook, the
  `worktree` skill is auto-available) and its session context is pinned to the
  real repo regardless of `cd`. So a clean "no-skill baseline" is not isolable
  in-place, and subagent edits/worktree calls target the real repo.
- The skill's "output" is **git side-effects** (a worktree + branch + committed
  spec + handoff artifact), not a portable file artifact — so the file-diff
  benchmark/viewer adds little signal here.

Instead: one **real end-to-end run by an independent subagent** against a
temporary approved brainstorm fixture, plus a **direct main-session validation**
of the load-bearing `EnterWorktree` switch. All mutations were cleaned up
(`git worktree remove`, `git reset --soft`, fixtures deleted) — repo verified
back to its pre-eval state.

## Run 1 — happy path (independent subagent, ~279s, ~90k tokens)

Prompt: "follow the worktree skill to set up isolation for the approved brainstorm
`docs/specs/2026-05-25-eval-demo-brainstorm.md` (topic `eval-demo`)."

| # | Phase | Result | Evidence |
|---|---|---|---|
| 0 | Preconditions/doctor | PASS | verified git repo, worktree support, hook registered, baseRef=head, not in a worktree |
| 1 | Confirm input | PASS | found Status: approved spec |
| 2 | Derive branch name | PASS | slug `eval-demo`, valid charset |
| 3 | Carry spec across (commit) | PASS | committed ONLY the spec (guardrail held); other changes left uncommitted |
| 4 | Enter worktree | PARTIAL | `EnterWorktree` **refused in subagent**; agent fell back to `git worktree add` and reported the session was not switched (honest) |
| 5 | Write handoff artifact | PASS | wrote `…-eval-demo-worktree.md` in the worktree |
| 6 | Confirm enforcement | PASS | empirically re-tested the gate (deny on main, allow in worktree / on docs) |
| 7 | Handoff/stop | PASS | did NOT invoke any downstream stage |

## Key finding (acted on)

`EnterWorktree` **refuses from a subagent / cwd-override session** ("would mutate
the parent session's process-wide working directory"); it works only from a
top-level session. The skill now documents this and the `git worktree add`
fallback (SKILL.md "When things go sideways"; worktree-mechanics.md §3).

## Direct validation — `EnterWorktree` in a main session (the real primary path)

`EnterWorktree(name="eval-switch-test")` in this top-level session → created
`.claude/worktrees/eval-switch-test` and **switched the session** (verified:
`pwd` and `git rev-parse --show-toplevel` both became the worktree; branch
`worktree-eval-switch-test`). `ExitWorktree(remove)` returned the session and
removed it. The load-bearing create+switch mechanism works as designed.

## Verdict

Orchestration logic is sound and the hard-gate is enforced. The skill triggers
and follows its workflow correctly; the one rough edge (subagent EnterWorktree)
is now documented with a working fallback. Remaining optional step:
description-trigger optimization (Windows: user-initiated `run_triggers.py`).

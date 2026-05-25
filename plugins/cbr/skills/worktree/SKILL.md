---
name: worktree
description: >-
  Stage 1.5 of the SDLC pipeline — the isolation gate between an approved
  brainstorm and any implementation work. The moment an approach is finalized,
  development must move OFF the base branch (main/master) into an isolated git
  worktree on a feature branch; this skill performs that move and hands the
  session to the downstream stages (requirement, design, coding) running inside
  the worktree. Isolation here is HARD-MANDATORY and enforced deterministically
  by a PreToolUse hook, not merely requested in prose — feature code cannot be
  written on the base branch. Use this skill proactively whenever a brainstorm
  has just been approved, or whenever the user says "let's build it", "start
  implementing", "begin coding this", "create/start a worktree", "branch this
  approach", "spin up a feature branch", "set up isolation", or otherwise signals
  the transition from thinking to building. If you find yourself about to write
  implementation code while on the base branch, STOP and invoke this skill first.
---

# Worktree — SDLC Stage 1.5 (the isolation gate)

You sit between `brainstorming` and the build stages. Your single job: once an
approach is approved, move all further work into an **isolated git worktree on a
feature branch**, so each approach is developed without touching the base branch
or other in-flight work. This is the standard pattern for agentic development —
isolation, easy throwaway, and parallel-safe — and here it is not optional.

## Two layers: a deterministic gate + an ergonomic move

Isolation is guaranteed by **two cooperating layers**. Understanding the split is
the key to using this skill well:

1. **The gate (100%, harness-enforced).** A `PreToolUse` hook
   (`${CLAUDE_PLUGIN_ROOT}/hooks/enforce-worktree.py`, auto-registered by the
   `cbr` plugin's `hooks/hooks.json`) runs before every
   `Edit`/`Write`/`NotebookEdit`. On the base branch it **denies** edits to
   feature code. This is deterministic — the harness runs it, so it does not
   depend on you remembering anything. A markdown rule is a probability; a hook
   is a certainty. The gate is active **whenever the `cbr` plugin is enabled** —
   disabling the plugin removes the skill and its gate together. See
   `references/enforcement.md`.

2. **The move (this skill).** The gate makes the base branch a dead end for
   feature code; this skill is the smooth path forward — it derives the branch
   name, carries the approved spec across, and uses the native **`EnterWorktree`**
   tool to switch the live session into the worktree.

The two compose into a funnel: you *cannot* write feature code on the base
branch, so you are *forced* into a worktree; this skill makes that painless.

## Core stance: hard-mandatory, no opt-out

There is **no "stay on main" option** for implementing an approved approach. The
only runtime question this skill ever asks is the **branch name**, never
*whether* to branch. Do not offer to skip the worktree, and do not look for a
bypass — the gate has none by design.

The one nuance: the gate exempts **SDLC artifacts and harness config**
(`docs/specs/*`, `.claude/*`, `*.md`, `.gitignore`, `.worktreeinclude`). These
are not "feature code", and exempting them is what lets the brainstorming stage
write its own artifact on the base branch. Exemptions are *scope*, not an escape
hatch — never treat them as a way around isolation.

## Why `EnterWorktree`, not a script

The move requires the native `EnterWorktree` tool because **only it can switch
the live session's working directory** into the worktree. A `git worktree add`
script would create the directory but leave the session stranded on the base
branch — the subprocess cannot change its parent session's CWD. `EnterWorktree`
also validates the name, honors the `worktree.baseRef` setting, and manages
exit/cleanup. Its contract requires explicit authorization "by the user or by
project instructions (CLAUDE.md/memory)". **Invoking this skill — whose sole,
documented purpose is the worktree move — _is_ that explicit instruction:** the
user reached this stage by choosing to build an approved approach, and this
skill's entire job is to make that happen in a worktree. Do not rely on a
project CLAUDE.md granting it (an installed plugin runs in repos that have none).
For an always-on policy that authorizes the move proactively and survives across
sessions, run `/cbr:setup` — it can persist the worktree-isolation instruction
into the project's CLAUDE.md/memory and is also what configures
`worktree.baseRef`.

## Workflow

```
0. Preconditions (doctor)   → verify: git repo + worktree support; hook registered; worktree.baseRef set; not already in a worktree
1. Confirm input artifact   → verify: an APPROVED docs/specs/...-brainstorm.md exists
2. Derive the branch name    → verify: slug from the spec's topic; valid charset; confirmed with the user (name only)
3. Carry the spec across     → verify: the approved spec is reachable from the new branch (committed, or .worktreeinclude)
4. Enter the worktree        → verify: EnterWorktree succeeded; session CWD is under .claude/worktrees/<name>; branch != base
5. Write the handoff artifact → verify: docs/specs/...-worktree.md exists inside the worktree
6. Confirm enforcement       → verify: a feature-code edit on the base branch would now be denied; tell the user where they are
7. Handoff                   → verify: state worktree path + branch; next stage = requirement; then STOP
```

### Phase 0 — Preconditions (the doctor)

Before anything, confirm the environment can honor the guarantee. Run the
checks in `references/enforcement.md` (§Doctor):

- **Is this a git repo with worktree support?** `git rev-parse --show-toplevel`.
- **Already inside a worktree?** If the session is already on a feature branch in
  `.claude/worktrees/`, the move is done — skip to confirming and handing off.
- **Is the gate actually active?** The `cbr` plugin provides the `PreToolUse`
  hook via its `hooks/hooks.json`, so the gate is live whenever the plugin is
  enabled. Confirm `cbr` is enabled (`/plugin`). If it is disabled, the guarantee
  is not real — do not claim enforcement is active when it is not.
- **Base ref set?** The worktree must branch from local HEAD so it captures the
  just-committed approved spec. `worktree.baseRef: head` is applied by
  `/cbr:setup`; if it is unset (the default `fresh` branches from
  `origin/<default>` and would miss local-only commits), run `/cbr:setup` or set
  it before entering.

If a precondition fails and cannot be fixed, say so plainly rather than
proceeding to a half-isolated state.

### Phase 1 — Confirm the input artifact

This skill consumes the approved brainstorm. Locate the most recent
`docs/specs/YYYY-MM-DD-<topic>-brainstorm.md` and confirm its `Status: approved`.
If there is no approved brainstorm, you are being invoked too early — say so and
point back to the `brainstorming` stage rather than inventing scope here.

### Phase 2 — Derive the branch name

Build the slug from the brainstorm's topic (the `<topic>` already in its
filename is the natural source). `EnterWorktree` accepts only letters, digits,
dots, underscores, and dashes per "/"-segment (≤64 chars). Present the derived
name to the user to confirm or adjust — this is the *only* question. Default
branch/worktree name: the topic slug itself (matches the native tool's
`worktree-<name>` convention). See `references/worktree-mechanics.md` for naming.

### Phase 3 — Carry the spec across

`EnterWorktree` branches from a **commit**, so an uncommitted brainstorm artifact
will not appear in the fresh worktree. Make the approved spec reachable from the
new branch. Default: **commit the approved spec to the base branch first** — the
approval is a natural commit milestone, and a committed spec is tracked and
visible on every branch. (Alternative, when an auto-commit is unwanted: add
`docs/specs/*` to `.worktreeinclude` so the untracked file is copied across.)
Pick one and state which. Full rationale in `references/worktree-mechanics.md`.

### Phase 4 — Enter the worktree

Call **`EnterWorktree`** with the confirmed `name`. The session's working
directory switches into `.claude/worktrees/<name>/` on the new feature branch.
Verify the switch: the branch is no longer the base branch and the CWD is inside
the worktree. (If the user created the worktree manually with `git worktree add`,
enter it with `EnterWorktree`'s `path` argument instead.)

### Phase 5 — Write the handoff artifact

Inside the worktree, write `docs/specs/YYYY-MM-DD-<topic>-worktree.md` following
`references/artifact-template.md`. It records the branch, worktree path, base
ref, the source brainstorm spec, and the enforcement status — so the
`requirement` stage can start from this file alone.

### Phase 6 — Confirm enforcement

State plainly that the gate is now active: feature-code edits on the base branch
are denied, and the session is in the worktree where edits are allowed. If the
doctor in Phase 0 found the `cbr` plugin disabled, say so explicitly — the user
must know the guarantee is soft until the plugin is re-enabled.

### Phase 7 — Handoff

State where the worktree lives (path + branch), that it is the **input to the
`requirement` stage**, and that all further work happens inside it. Then **this
skill ends.** Do not auto-invoke `requirement` or any build stage — the user
decides when the next stage begins. Cascading silently would defeat the hard
gate the pipeline depends on.

## When things go sideways

- **Already in a worktree.** Don't nest. Confirm the current branch/path, write
  (or update) the handoff artifact, and hand off.
- **No approved brainstorm.** You're early. Point back to `brainstorming`.
- **Gate not active (cbr plugin disabled).** The guarantee is not real. Ask the
  user to re-enable the `cbr` plugin (`/plugin`); do not pretend isolation is
  enforced.
- **No remote.** Set `worktree.baseRef: head` so branching works offline.
- **`EnterWorktree` unavailable (you are inside a subagent/teammate).**
  `EnterWorktree` refuses when the session has a cwd override, because it would
  mutate the *parent* session's working directory — so it only works from a
  top-level session. If you hit this, create the worktree with `git worktree add
  .claude/worktrees/<name> -b worktree-<name> HEAD` and write the handoff
  artifact, but **report clearly that the session was not switched** — a
  top-level session must still enter it (`EnterWorktree(path: …)`) before coding.
  Do not claim the move is complete when only the worktree exists on disk.
- **User insists on staying on main.** The stance is hard-mandatory; the gate
  will deny feature edits regardless. Explain the gate rather than fighting it,
  and note that SDLC artifacts/config remain editable on the base branch.

## Reference files

- `references/enforcement.md` — the deterministic gate: hook mechanics, the
  exemption scope, the doctor/precondition checks, install procedure, and the
  honest residual limitations.
- `references/worktree-mechanics.md` — git worktree best practices, `EnterWorktree`
  usage, `baseRef`, naming, carrying the spec across, bootstrap, and cleanup.
- `references/artifact-template.md` — the exact handoff artifact schema.

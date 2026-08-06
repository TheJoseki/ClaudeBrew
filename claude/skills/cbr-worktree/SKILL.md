---
name: cbr-worktree
description: >-
  Stage 1.5 of the SDLC pipeline — the isolation gate between an approved
  brainstorm and any implementation work. The moment an approach is finalized,
  development must move OFF the base branch (main/master) into an isolated git
  worktree on a feature branch; this skill performs that move and hands the
  session to the downstream stages (requirement, design, coding) running inside
  the worktree. The move is the skill's unconditional stance — it never offers a
  stay-on-main path for feature code. A PreToolUse gate can make that denial
  deterministic at the harness level, but the gate is OPT-IN: `claudebrew install --gate`
  registers it in your settings.json, and by default no harness gate is active.
  Use this skill proactively whenever a brainstorm
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

## Two layers: an always-on move + an opt-in deterministic gate

Isolation rests on **two layers**. Understanding the split is the key to using
this skill well — one always runs, the other is opt-in:

1. **The move (this skill) — always.** This skill derives the branch name,
   carries the approved spec across, and uses the native **`EnterWorktree`** tool
   to switch the live session into the worktree. It never offers a stay-on-main
   path for feature code. This layer always operates when the skill runs, but it
   is *probabilistic* — it holds because the model follows the skill.

2. **The gate (deterministic) — opt-in.** A `PreToolUse` hook
   (`enforce-worktree.py`) runs before every `Edit`/`Write`/`NotebookEdit`; on the
   base branch it **denies** edits to feature code. This is deterministic — the
   harness runs it, so it does not depend on the model remembering anything. But
   the `cbr` plugin **does not ship it active**: a plugin cannot register harness
   hooks, and an always-on gate would deny base-branch edits in *every* repo you
   install `cbr` into. It is instead **opt-in** — `claudebrew install --gate` registers it in
   your `.claude/settings.json`. **By default (setup not run — e.g. headless
   `claude -p` or CI) there is no harness gate**, and isolation rests on Layer 1
   alone. This is an accepted posture. See `references/enforcement.md`.

When the gate is installed the two compose into a funnel: you *cannot* write
feature code on the base branch, so you are *forced* into a worktree, and this
skill makes that painless. Without it, the skill still performs the move — it just
isn't backed by a harness-level denial.

## Core stance: hard-mandatory, no opt-out

There is **no "stay on main" option** for implementing an approved approach. The
only runtime question this skill ever asks is the **branch name**, never
*whether* to branch. Do not offer to skip the worktree, and do not look for a
bypass. Keep two things distinct: **the skill's behavior is unconditional** (it
always performs the move and never offers a stay-on-main path for feature code),
while **the harness-level denial is opt-in** (the `enforce-worktree.py` gate only
denies once `claudebrew install --gate` has registered it). Both are true at once — the stance
never bends; only the deterministic enforcement behind it is opt-in.

The one nuance: the gate exempts **SDLC artifacts and harness config**
(`docs/streams/*`, `.claude/*`, `*.md`, `.gitignore`, `.worktreeinclude`). These
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
sessions, run `claudebrew install --gate` — it can persist the worktree-isolation instruction
into the project's CLAUDE.md/memory and is also what configures
`worktree.baseRef`.

## Workflow

```
0. Preconditions (doctor)   → verify: git repo + worktree support; gate registration checked (opt-in — absent by default); worktree.baseRef set; not already in a worktree
1. Confirm input artifact   → verify: an APPROVED docs/streams/<slug>-*/brainstorm/BRAINSTORM.md exists
2. Derive the branch name    → verify: slug from the spec's topic; valid charset; confirmed with the user (name only)
3. Carry the spec across     → verify: the approved spec is reachable from the new branch (committed, or .worktreeinclude)
4. Enter the worktree        → verify: EnterWorktree succeeded; session CWD is under .claude/worktrees/<name>; branch != base
5. Write the handoff artifact → verify: docs/streams/<slug>-*/WORKTREE.md exists inside the worktree
6. Confirm enforcement       → verify: report the REAL gate state (registered → harness denies base-branch feature edits; not registered → advisory only, point to claudebrew install --gate); tell the user where they are
7. Handoff                   → verify: state worktree path + branch; next stage = requirement; then STOP
```

### Phase 0 — Preconditions (the doctor)

Before anything, confirm the environment can honor the guarantee. Run the
checks in `references/enforcement.md` (§Doctor):

- **Is this a git repo with worktree support?** `git rev-parse --show-toplevel`.
- **Already inside a worktree?** If the session is already on a feature branch in
  `.claude/worktrees/`, the move is done — skip to confirming and handing off.
- **Is the opt-in gate actually registered?** The gate is NOT shipped active —
  it only denies once `claudebrew install --gate` has registered `enforce-worktree.py` in a
  settings file. Check **all three** the harness merges — `~/.claude/settings.json`
  (user), `.claude/settings.json` (project), `.claude/settings.local.json`
  (project-local) — for a `PreToolUse` entry whose command contains
  `enforce-worktree`. Absent from all three → **no harness gate** (the default;
  fine for headless `claude -p`/CI). Registration alone is not enforcement:
  confirm the registered absolute path exists and `python` (or `py -3`) resolves,
  since a stale path or missing interpreter makes the harness treat the hook as
  non-blocking. Only claim enforcement when all three hold; otherwise say the gate
  is off and offer `claudebrew install --gate`. Either way, proceed with the move — it isolates
  regardless.
- **Base ref set?** The worktree must branch from local HEAD so it captures the
  just-committed approved spec. `worktree.baseRef: head` is applied by
  `claudebrew install --gate`; if it is unset (the default `fresh` branches from
  `origin/<default>` and would miss local-only commits), run `claudebrew install --gate` or set
  it before entering.

If a precondition fails and cannot be fixed, say so plainly rather than
proceeding to a half-isolated state.

### Phase 1 — Confirm the input artifact

This skill consumes the approved brainstorm. Locate the most recent
`docs/streams/<slug>-*/brainstorm/BRAINSTORM.md` and confirm its `Status: approved`.
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
`docs/streams/*` to `.worktreeinclude` so the untracked file is copied across.)
Pick one and state which. Full rationale in `references/worktree-mechanics.md`.

### Phase 4 — Enter the worktree

Call **`EnterWorktree`** with the confirmed `name`. The session's working
directory switches into `.claude/worktrees/<name>/` on the new feature branch.
Verify the switch: the branch is no longer the base branch and the CWD is inside
the worktree. (If the user created the worktree manually with `git worktree add`,
enter it with `EnterWorktree`'s `path` argument instead.)

### Phase 5 — Write the handoff artifact

Inside the worktree, write `docs/streams/<slug>-<YYYYMMDD>/WORKTREE.md` following
`references/artifact-template.md` (the stream folder already exists — brainstorming
scaffolded it; WORKTREE.md sits directly at the stream root). It records the branch,
worktree path, base
ref, the source brainstorm spec, and the enforcement status — so the
`requirement` stage can start from this file alone.

### Phase 6 — Confirm enforcement

Report the **real** gate state from the Phase 0 doctor, never a hoped-for one.
If the opt-in gate is registered (and its path + `python` check out): state that
feature-code edits on the base branch are denied and the session is in the
worktree where edits are allowed. If it is **not** registered (the default):
say plainly that the move is done but isolation is **advisory** — no harness-level
denial is in effect — and that running `claudebrew install --gate` installs the gate to make it
deterministic. Do not claim enforcement when the registration is absent.

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
- **Gate not registered (opt-in not run).** The harness-level denial is off (the
  default). Do the move anyway and report isolation as advisory; offer `claudebrew install --gate`
  to register `enforce-worktree.py` and make it deterministic. Do not pretend the
  harness enforces isolation when it does not.
- **No remote.** Set `worktree.baseRef: head` so branching works offline.
- **`EnterWorktree` unavailable (you are inside a subagent/teammate).**
  `EnterWorktree` refuses when the session has a cwd override, because it would
  mutate the *parent* session's working directory — so it only works from a
  top-level session. If you hit this, create the worktree with `git worktree add
  .claude/worktrees/<name> -b worktree-<name> HEAD` and write the handoff
  artifact, but **report clearly that the session was not switched** — a
  top-level session must still enter it (`EnterWorktree(path: …)`) before coding.
  Do not claim the move is complete when only the worktree exists on disk.
- **User insists on staying on main.** The stance is hard-mandatory: this skill
  will not help write feature code on the base branch. If the opt-in gate is
  installed, the harness denies those edits as well. Explain the stance rather
  than fighting it, and note that SDLC artifacts/config remain editable on the
  base branch.

## Reference files

- `references/enforcement.md` — the opt-in deterministic gate: hook mechanics, the
  exemption scope, the doctor/precondition checks, the opt-in registration
  procedure, and the honest residual limitations (including opt-in-by-default).
- `references/worktree-mechanics.md` — git worktree best practices, `EnterWorktree`
  usage, `baseRef`, naming, carrying the spec across, bootstrap, and cleanup.
- `references/artifact-template.md` — the exact handoff artifact schema.

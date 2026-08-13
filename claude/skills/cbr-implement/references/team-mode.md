# Team mode (`--team N`) — a real agent team for implementation

`--team` runs `cbr-implement` as a Claude Code **agent team**: N `cbr-developer` teammates, each its
own session and context window, implement disjoint slices of the feature **concurrently and with live
coordination** — they claim tasks, message the lead on conflicts, and are torn down when done. It is
the heavy end of parallel execution; for most multi-file work `--parallel` (fire-and-collect, no live
coordination) is cheaper and enough.

**`--team` vs `--parallel`** — know which you want:

| | `--parallel` | `--team` |
|---|---|---|
| Workers | **unnamed** `cbr-developer` — plain task workers | **named** `cbr-developer` — real team members |
| Coordination | none — spawn, each returns its slice, lead integrates | live — teammates `SendMessage` the lead, claim tasks via `TaskList`/`TaskUpdate`, escalate conflicts |
| Isolation | file-ownership only | file-ownership **+** optional `isolation:"worktree"` |
| Teardown | n/a (workers just finish) | explicit `shutdown_request` per teammate |
| Cost | lower | higher — confirm with the user before spawning |

## Precondition — do not silently degrade

`--team` requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set by `claudebrew install`; already in this
repo's dev `.claude/settings.json`). Check for it first. If it's absent, **STOP and tell the user** —
do **not** silently fall back to `--parallel` (that would quietly deliver a weaker, uncoordinated
execution model than the user asked for). Token cost scales with teammates, so always show your
reasoning and get the user's confirmation before spawning.

## The verified mechanism (this harness — capability-aware)

Confirmed empirically (Phase-7 spike, 2026-08-14), written to survive harness differences:

- **A *named* `Agent` spawn is a team member.** `Agent(subagent_type:"cbr-developer", name:"be-orders", …)`
  enrols the teammate in the session's implicit team and injects the full coordination toolset
  (`SendMessage` + `TaskCreate/Update/Get/List`) **beyond** `cbr-developer`'s 6-tool frontmatter
  allowlist. An **un**named spawn is a plain task worker with no coordination tools — so **always give
  each teammate a `name`.**
- **No `TeamCreate`/`TeamDelete` is needed** in this harness — naming enrols the teammate, and teardown
  is `shutdown_request` alone. **If your harness *does* expose `TeamCreate`/`TeamDelete`, you may use
  them** (create the team first, delete it after all members terminate); they are optional, not
  required. Do not assume either way — check what your tools offer.
- **Communication**: `SendMessage(to:"<name>", …)` — **lead↔teammate is spike-verified**; teammates
  reach the lead as `to:"main"`. (Direct teammate→teammate messaging is a documented agent-teams
  capability but was not spike-confirmed here — rely on lead-mediated relay unless you've verified it.)
  Plain text only — never hand-rolled JSON status; use `TaskUpdate` for status.
- **Teardown**: `SendMessage(to:"<name>", message:{type:"shutdown_request", reason:"…"})` per teammate;
  each replies `shutdown_response` and terminates. Only the lead runs teardown.

## Step 1 — split by file ownership (the conflict-prevention mechanism)

File ownership is what makes code-editing teammates safe. This is a **deliberate, scoped extension of
`cbr-brainstorming/references/teammate-mode.md`'s "teammates produce findings, not edits" rule** —
which was written for read-only *research* teammates. Implementation teammates **do** edit code; file
ownership replaces "don't edit the shared file" as the conflict-prevention rule (a different rule, not
that one relaxed by accident). Reuse the same ownership discipline as
`{{CBR_ROOT}}/docs/references/parallel-mode.md`: split only when slices are genuinely independent (no
shared file, no output-feeds-input chain); write the ownership map before spawning; every created/
modified file belongs to **exactly one** teammate; shared files (barrels, routers, migrations, locale
files) are **never delegated** — the lead integrates them after.

## Step 2 — spawn the named teammates (one message, concurrent)

Spawn all N in a single message so they run concurrently. Each spawn:

- `subagent_type: "cbr-developer"`, a role `name` (e.g. `be-orders`, `fe-checkout`), and — for real
  isolation — `isolation: "worktree"` (a temporary git worktree, auto-cleaned if unchanged).
- A **self-contained prompt** (teammates inherit none of the lead's history): the TECH spec section by
  path, its **File Ownership** list (the exact paths it may touch), acceptance criteria, and its
  **intermediate** work-log path `docs/streams/[feature]-[YYYYMMDD]/work-logs/DEV-[slice].md` (per-slice
  notes the lead consolidates in Step 3 into the single canonical `DEV-[YYYYMMDD].md` — not the final log).
- The hard File Ownership Rules restated verbatim (from `parallel-mode.md`): never modify an unowned
  file; on a needed unowned file or a detected conflict, **STOP and report to the lead immediately**;
  match existing patterns, don't improve adjacent code.

> **Worktree hooks caveat**: in a CBR-dogfooded repo a fresh worktree has the tracked
> `.claude/settings.json` (which registers hooks) but not the git-ignored `.claude/hooks/*.py` payload,
> which fail-closes every Bash/Edit/Write. Either provision the hooks in the teammate's worktree first
> (`node bin/claudebrew.mjs install --dev` inside it) or run the team with file-ownership alone (no
> `isolation:"worktree"`). Spawning is asynchronous — **wait, do not poll**; each teammate's report
> arrives as its own turn.

## Step 3 — coordinate, then merge (lead-owned)

- Teammates claim the lowest-ID unblocked task first (`TaskList` → `TaskUpdate` owner), mark
  `in_progress`/`completed`, and `SendMessage` the lead on a blocker or an ownership conflict — the lead
  resolves by restructuring tasks, never by letting two teammates edit one file.
- When all teammates report done, **the lead integrates**: merge each worktree/slice, wire the shared
  files no teammate owned, and run Self-Check (Step 4) across the merged result — each teammate verified
  only its own slice, so integration breakage surfaces only here. The teammates' per-slice `DEV-[slice].md`
  notes are consolidated by the lead into the **single** canonical `DEV-[YYYYMMDD].md` — one final work
  log, not N.

## Step 4 — tear down, then hand off

`shutdown_request` each teammate; once all have terminated, continue to `cbr-implement`'s normal Step 4
(Self-Check + Work Log) → Hand-off. **One team at a time, no nested teams** — a teammate cannot spawn
its own team, and the adversarial fix-loop team (below) may only start after this implementation team
is fully torn down.

## Adversarial fix-loop variant (`--team`, optional, non-default)

Only when `--team` is explicit and a bug resists the normal 2-round fix: spawn 2-3 named `cbr-developer`
teammates holding **competing root-cause hypotheses** (adversarial framing) and let the evidence decide.
**Sequential, never nested**: this may start **only after** any implementation team has been fully torn
down (`shutdown_request` completed for every member) — the "one team at a time, no nested teams" rule.
The default fix-loop (Phase 6's 2-round direct-fix + `systematic-debugging.md` escalation) is unchanged;
this variant is an opt-in, not the default path.

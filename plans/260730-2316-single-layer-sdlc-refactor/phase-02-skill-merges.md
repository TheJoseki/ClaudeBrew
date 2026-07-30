# Phase 2 — Skill Merges + Parallel Mode

**Depends on:** Phase 1 · **Goal:** consolidate knowledge clusters the user locked, and turn parallelism into a mode arg.

## Context
- SKILL.md budget < 500 lines → heavy content goes to `references/`; scripts/data stay as bundled assets.
- Merges break `evals/evals.json` → consolidate eval sets (handled where each merge lands; final sweep in Phase 3).

## Merge A — UI cluster → `design-system`
**Absorb** `ui-styling` (412) + `ui-ux-pro-max` (305) **into** `design-system` (315). Combined 1032 lines → impossible as one SKILL.md.
- **Shape:** keep dir `skills/design-system/`. Lean `SKILL.md` (<500) = router + Quick Reference. Move detail to:
  - `references/tokens.md` (from current design-system body)
  - `references/implementation.md` (from `ui-styling`: shadcn/Tailwind/dark-mode/responsive)
  - `references/ux-intelligence.md` (from `ui-ux-pro-max` inline DB/reasoning)
  - `scripts/` ← `ui-ux-pro-max/scripts/` (search.py, design_system.py); `data/` ← its CSVs. Fix script path constants.
- Update `SKILL.md` description to fold all three TRIGGER sets; keep double-quoted scalar.
- DELETE dirs `skills/ui-styling/`, `skills/ui-ux-pro-max/` after content moved.
- `design-screen` (executor) stays; update its `references/design-intelligence.md` pointer (8 refs to ui-ux-pro-max) → `design-system`.

## Merge B — Tech-design cluster → one skill
**Target name:** `architecture` (recommended) absorbs `api-patterns` + `database-design`. *(Confirm name at phase start.)*
- Lean `SKILL.md` = decision framework + when-to-use each sub-area; detail to `references/api-design.md`, `references/database-design.md` (from the two absorbed skills).
- Rewrite the three mutual `NOT FOR:` guards into internal section headers (they no longer cross skills).
- Keep the `design-function` (executor) hand-off; update its NOT FOR (4 refs to api-patterns) → `architecture`.
- DELETE `skills/api-patterns/`, `skills/database-design/` after content moved.

## Remove C — `create-pr`
- DELETE `skills/create-pr/`. Fold the git-branch/commit/PR step as a short "Deliver / open PR" section at the tail of `implement-feature` (or note it lives in the user's own git workflow). Remove `create-pr` from any connection tables.

## Parallel-as-mode D — execution skills (modeled on `ck:cook`)
`parallel-agents` was deleted (P1). **Resolved mechanism (plan Decision 2):** model on `C:\Works\Tool\ClaudeKit.CC\claudekit-engineer\claude\skills\cook` — `SKILL.md` (`argument-hint: [...] [--parallel]`) + `references/subagent-patterns.md` §Parallel Execution (`Task(subagent_type="fullstack-developer", prompt="Implement [phase-file] with file ownership: [files]")` × N).

Apply to execution skills `design-screen`, `design-function`, `implement-feature`, `unit-test`, `integration-test`:
1. **Add `Task`/`Agent` to `allowed-tools`** (this is the deliberate reversal — a skill spawning `general-purpose` subagents is NOT the deleted role-agent layer).
2. **Add `--parallel` to `argument-hint`** + a "## Parallel mode" block: default = single-stream; on `--parallel`, when scope splits cleanly (independent modules/screens/test targets), spawn N **`developer`** capability agents (from the P1 pool) each with an explicit **file-ownership boundary**, then synthesize. *(Pool `developer` carries the file-ownership persona + `model` tier; fall back to `general-purpose` only if the pool was skipped.)* No `.*-agent` hooks bind these.
3. Salvage the slice-by-file-ownership guidance from old `parallel-agents/SKILL.md` into **one** shared file `skills/implement-feature/references/parallel-mode.md`; lift `fullstack-developer.md`'s "File Ownership Rules" clause verbatim ("NEVER modify files not listed… if conflict detected, STOP and report"). Other skills reference it by path (DRY, no symlink).

**Divergence from cook (keep):** do NOT copy cook's auto-cascade (mandatory review/test subagents inside the skill). Per plan Decision 1, each execution skill **stops after its stage**; the user runs `review-code`/`unit-test` next. Adopt cook's spawn mechanism only.

## Fresh-eyes gate spawns E — gate skills (Fork 5 / B1)
Gate-owning skills must not self-grade. Add `Task`/`Agent` to `allowed-tools` and a "## Verdict" step to:
- `review-code` (G4) + `vulnerability-scanner` (G5a) → spawn `reviewer` (carry "assume AI-written, don't rubber-stamp" posture).
- `unit-test` (G6) + `integration-test` (G7) → spawn `tester`.

Flow per gate skill: spawn the fresh pool agent → agent writes the **verdict artifact** (JSON, schema from P3/C1) + findings → skill runs the validator via `Bash` → on FAIL/Critical, `AskUserQuestion` (per Decision 1, user gates; no auto-loop) → **stop**. The skill never writes its own PASS verdict inline (that would be self-grading).

## Files
- Modify: `design-system/SKILL.md` (+ new references/scripts/data), `architecture/SKILL.md` (+ references), `design-screen`, `design-function`, `implement-feature`, `unit-test`, `integration-test`.
- Delete: `ui-styling/`, `ui-ux-pro-max/`, `api-patterns/`, `database-design/`, `create-pr/`.

## Validation
- `claude plugin validate ./plugins/cbr` → 0 errors.
- `python skills/design-system/scripts/search.py` (smoke) resolves new data path.
- Each merged SKILL.md line count < 500.

## Risks
- `ui-ux-pro-max` scripts hardcode data paths → update after move or they break silently. Smoke-test.
- Description scalars MUST stay double-quoted (reconcile invariant) — merging TRIGGER text must not reintroduce a bare `: `.

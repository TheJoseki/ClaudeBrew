# The plan document — structure, task bar, and anti-patterns

The output contract is one file: `plan/PLAN.md` inside the work-stream. This reference is
how to shape it. Keep it short — a plan that needs scrolling is usually a plan that needs
simplifying.

## Task-breakdown properties (the quality bar)

Every task must be all five:

| Property | Definition |
|----------|------------|
| Small | Completable in one session |
| Focused | One deliverable per task |
| Verifiable | A concrete done-condition |
| Independent | Can be picked up without a verbal briefing |
| Ordered | Dependencies are explicit |

## Planning principles

1. **Keep it short** — fits on one screen where the work allows. If you must scroll, simplify.
2. **Be specific** — name the file, function, or endpoint. Never "implement feature".
3. **Mark dependencies** — if Task B needs Task A, say so.
4. **Separate phases from tasks** — phases group and gate; tasks are atomic.
5. **Update as you go** — stale status is worse than no status.

## Document structure

Lead with an overview that names the **source of truth** (the input-contract's output), then
phases, then done-conditions. A minimal shape:

```markdown
---
stream: <slug>-<YYYYMMDD>
title: "<Feature or change title>"
status: pending
---

# Implementation Plan: <feature>

## Overview
| Field | Value |
|-------|-------|
| Source of truth | requirements/SRS.md   (or brainstorm / research/RES-*.md / code) |
| Stream | docs/streams/<slug>-<YYYYMMDD>/ |
| Lane | greenfield  (or brownfield — stream-light) |

## Phases
### Phase 1 — <name>
**Status**: PENDING · **Output**: <artifact or code the phase produces>
| Task | File / target | Done-condition | Status |
|------|---------------|----------------|--------|
| ...  | src/...       | test passes / endpoint returns X | PENDING |

## Done conditions
- All phases DONE
- Tests 100% pass · Code review PASS
```

- **Greenfield plans** map phases onto the SDLC gates (G1 requirement → G2/G3 design → G4
  review → G6/G7 tests → G8 delivery); see `references/examples/PLAN-example.md` for the full
  gate-aligned form.
- **Brownfield (stream-light) plans** skip the design gates that don't apply — a maintenance
  change may go straight to implementation → review → test. The gates you skip read `pending`
  (benign), and the plan's phases are the real work list.

## Status values

`PENDING` | `IN_PROGRESS` | `BLOCKED` | `DONE` | `SKIPPED`

## Parallel-execution extension

When phases are independent, assign each to the stage skill that owns it so they can run
alongside each other. The plan records the ordering; it does not run anything — each stage is
still gated and started by the user.

| Phase | Task | Owner | Status |
|-------|------|-------|--------|
| 3a | Implementation | `implement-feature` (`--parallel` fans out to `cbr:developer` workers) | PENDING |
| 3b | Unit test cases | `unit-test` (Mode A) | PENDING |
| 3c | Integration test cases | `integration-test` (Mode A) | PENDING |

3b and 3c can be authored alongside 3a — they do not depend on each other.

## Anti-patterns

| Don't | Do |
|-------|-----|
| Verbose task descriptions | One line per task |
| Generic names ("implement feature") | Name the specific file / endpoint |
| No done-condition | A verifiable completion criterion |
| Plan not updated | Update status immediately |
| All tasks parallel | Sequence dependent tasks |
| Plan for hypothetical needs | Plan the current scope only |
| Plan with no named source | State which source of truth it was built from |

## Where it goes

Write to `docs/streams/<slug>-<YYYYMMDD>/plan/PLAN.md` — the feature's work-stream folder; the
filename drops the slug because the folder carries it. Then update `STREAM.md` (membership row
+ board) per the mandatory upkeep protocol in `rules/sdlc-conventions.md`.

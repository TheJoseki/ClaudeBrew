# SDLC Reference — ClaudeBrew

> On-demand detail behind the contract's SDLC map. Load this when you write or locate a stream artifact,
> open a stream, or need a gate's pass criteria. The contract carries the invariants; this file carries the
> tables and the full procedures. (Relocated from the former `sdlc-conventions.md`.)

## Stage Checkpoints

Stage-is-the-gate: a checkpoint is a stage's artifact plus a user-approval stop, not a numbered gate in a
fixed taxonomy. Six checkpoints are **code-tracked** — `hooks/lib/sdlc_state.py` computes their status and
feeds the progress display + `next_action`; every other stage stop is process-only (still hard-gate,
still no auto-cascade, just nothing in derived state tracks it individually — the surrounding
checkpoint's artifact covers it).

### Code-tracked

| Checkpoint | Stage | Criteria | Decided by | Verdict artifact |
|-----------|-------|----------|-------------|-------------------|
| REQUIREMENT | `analyze-requirement` | SRS complete, user stories + AC documented | User approval | — (artifact: `requirements/SRS.md`) |
| DESIGN | `design-function` | Basic + Detail design complete (module structure, DB, API endpoints, ORM schema, service methods, DTOs) | User approval | — (artifact: `design/TECH.md`) |
| REVIEW | `review-code` | 0 Critical findings, ≤2 Major (must fix) | `review-code` verdict (cbr-reviewer) + user | `gate: "REVIEW"` |
| SECURITY | `vulnerability-scanner` | 0 Critical, 0 Major findings; ≥1 verification entry (the audit command run). **Code-enforced staleness**: a verdict older than the stream's newest `work-logs/DEV-*.md` or `bug-reports/BUG-*.md` entry shows `STALE` and routes back to this stage — the replacement for a prose "re-scan after every fix" mandate | `vulnerability-scanner` verdict (cbr-reviewer) + user | `gate: "SECURITY"` |
| UNIT | `unit-test` | 100% pass, 100% TECH-spec functions covered, ≥1 passing verification entry | `unit-test` verdict (cbr-tester) + user | `gate: "UNIT"` |
| INTEGRATION | `integration-test` | 100% pass (API + E2E where applicable — E2E is N/A for backend-only) on a production-equivalent DB, ≥1 passing verification entry. API and E2E are sub-criteria of the same checkpoint — record the split inside the ITR, not in the `gate` field | `integration-test` verdict (cbr-tester) + user | `gate: "INTEGRATION"` |

**Never advance past an open Critical (or, for SECURITY, Major). Fix rounds are bounded by judgment —
escalate to the user if a fix round isn't converging, rather than looping indefinitely.**

**A verdict is evidence, not a decision.** A fresh pool agent writes it; the user decides whether the
checkpoint opens. No agent auto-passes one. Exactly four checkpoints are machine-validated —
`hooks/verdict-gate.py` + `schemas/verdict-artifact.schema.json` accept exactly `REVIEW`, `SECURITY`,
`UNIT`, `INTEGRATION`. Each verdict is written beside its checkpoint's report inside the stream
(`reviews/`, `security/`, `test-reports/`) and validated by
`hooks/verdict-gate.py --gate <REVIEW|SECURITY|UNIT|INTEGRATION> --artifact <path>` before the user
decides. The severities a verdict blocks on are defined in the verdict schema's `findings.severity`
description (SECURITY blocks on Critical-or-Major; every other checkpoint blocks on Critical only).

**Reading a pre-0.11.0 verdict:** a stream that hasn't been re-reviewed since the rename may still carry
old-named files (`VERDICT-G4.json` etc.) — `sdlc_state.py`'s `LEGACY_GATE_NAME` shim reads those for one
release and marks them `(legacy)` in the progress display. This is a display concern only: whether a
stream is open or closed depends solely on `STREAM.md`'s `status:` field (below), never on which
verdict-naming era produced a file.

### Process-only stops (no individually-tracked derived state)

Still a hard gate — the stage does no downstream work until the user approves — just not its own row in
`infer_gate_progress`.

| Stop | Stage | Criteria | Decided by |
|------|-------|----------|-----------|
| UI Design | `design-screen` | All screen states defined (default/load/empty/error) | User approval |
| Test Viewpoint | `design-function` (or the user directly) | `docs/TEST_VIEWPOINT.md` customized (no placeholders) + test layers defined | User approval |
| Design Review | `review-code` | Design-review checklist PASS (0 Critical, 0 Major), full SRS→BASIC→TECH traceability | Review verdict + user, human-readable only — no machine artifact |
| Pre-Delivery Security Re-scan | `vulnerability-scanner` | Re-scan after all bug fixes: 0 Critical, 0 Major clean | `vulnerability-scanner` re-scan + user — the explicit, user-triggered form of the SECURITY staleness check above |
| Delivery | user | Every checkpoint above green | User sign-off — then stamp `status: done` on `STREAM.md` to close the stream (see Work-Stream Grouping below; closing is a separate, authored step from any of the above) |

## Artifact Paths (canonical — stream-first)

A work-stream is a directory: every per-feature artifact lives under `docs/streams/<slug>-<YYYYMMDD>/` —
**folder = identity, sub-folder = type, filename drops the slug** (time-series artifacts keep date/round).
Paths below are relative to the stream root unless they start with `docs/`.

| Owner | Artifact | Path |
|-------|----------|------|
| `brainstorming` | Stream Manifest | `STREAM.md` |
| `brainstorming` | Brainstorm | `brainstorm/BRAINSTORM.md` |
| `explore` (owns) / `cbr-researcher` (writes) | Research | `research/RES-[topic]-R[n].md` (parallel: `research/RES-[topic]-R[n]-a[NN]-[angle].md`) |
| `worktree` | Worktree handoff | `WORKTREE.md` |
| `analyze-requirement` | SRS | `requirements/SRS.md` |
| `design-screen` | Screen Design | `requirements/SCREEN.md` |
| `design-function` | Basic Design | `design/BASIC.md` |
| `design-function` | Detail Design | `design/TECH.md` |
| `architecture` | ADR (stream-scoped) | `design/decisions/ADR-[topic]-[YYYYMMDD].md` |
| `implement-feature` | Work Log | `work-logs/DEV-[YYYYMMDD].md` |
| `review-code` | Design Review | `reviews/DESIGN-REVIEW-[YYYYMMDD].md` |
| `review-code` | Review Report | `reviews/REVIEW-[YYYYMMDD].md` |
| `vulnerability-scanner` | Security Report | `security/SEC-[YYYYMMDD].md` |
| cbr-reviewer (pool) | Gate Verdict — REVIEW | `reviews/VERDICT-REVIEW.json` (per-batch: `reviews/VERDICT-B[n]-REVIEW.json`) |
| cbr-reviewer (pool) | Gate Verdict — SECURITY | `security/VERDICT-SECURITY.json` |
| cbr-tester (pool) | Gate Verdict — UNIT | `test-reports/VERDICT-UNIT.json` |
| cbr-tester (pool) | Gate Verdict — INTEGRATION | `test-reports/VERDICT-INTEGRATION.json` |
| `unit-test` | Test Cases / Report | `test-cases/UTC.md` / `test-reports/UTR-R[n].md` |
| `integration-test` | Test Cases / Report | `test-cases/ITC.md` / `test-reports/ITR-R[n].md` |
| `fix-bug` | Bug Report | `bug-reports/BUG-[YYYYMMDD]-[nn].md` |
| `plan-writing` | Plan | `plan/PLAN.md` |
| `retro` | Retrospective | `retro/RETRO-[YYYYMMDD].md` |
| `handoff` | Session Handoff | `handoffs/HANDOFF-[YYYYMMDD].md` |
| user / relevant skill | DAR / CAR | `dars/DAR-[topic]-[YYYYMMDD].md` / `cars/CAR-[topic]-[YYYYMMDD].md` |
| `design-*` | Screen & design exports | `assets/<tool>/[SCR-XX]-[state].<ext>` (`stitch`\|`pencil`\|`figma`) |

**Project-level (at `docs/` root, NOT per-stream):** `docs/CODING-CHECKLIST.md`,
`docs/decisions/ADR-*.md`, `docs/risks/RISK-*.md`, and the seeded reference docs (`PROJECT.md`,
`CODING_RULES.md`, `CODING_CONVENTION.md`, `ARCHITECTURE.md`, `API_DESIGN.md`, `TEST_VIEWPOINT.md`,
`CODE-REVIEW-CHECKLIST.md`) — seeded from `{{CBR_ROOT}}/docs/_templates/`, never relocated into a stream.

**Auto-create rule:** never fail because a directory is missing — create it.

## Work-Stream Grouping & the opener law

Each feature's artifacts belong to one work-stream. Every per-feature artifact carries a
`stream: [slug]-[YYYYMMDD]` frontmatter field. `hooks/lib/sdlc_state.py` derives the active feature + gate
state from the stream folder; `STREAM.md` is its index, with two **authored** zones (membership table +
task board) and one **derived** zone (the gate snapshot). **Gate authority stays with the glob
(`sdlc_state.py`) — never hand-edit the gate zone; it is never a second source of truth.**

**Upkeep protocol (MANDATORY, every stage skill).** When a stage writes its output artifact it must:
(1) stamp `stream: [id]` in that artifact's frontmatter; (2) append/update the artifact's row in the
stream's `STREAM.md` membership table; (3) update the task-board status for its phase. Skills NEVER write
the derived Gate Status zone.

**Closing a stream (authored, not automatic).** `status: done` is the only thing that closes a stream —
no skill infers it from checkpoint/verdict state. Any stage skill MAY stamp it on `STREAM.md`
frontmatter at its own user-confirmed terminal stop; `retro` does so as a matter of course for a
`feature`-mode run, since reaching retro already presumes delivery is confirmed. A stream-light stream
that never reaches `retro` gets it from whichever stage the user calls "done" at instead — stamp it by
hand, or let that stage's own stop-gate do it.

**Opener law — open-if-none / join-if-exists, resolved by topic-slug.** A stream has three possible
openers (`brainstorming`, `explore`, `plan-writing`), all scaffolding `STREAM.md` from
`{{CBR_ROOT}}/docs/_templates/STREAM.md`. Before opening, an opener derives an `[a-z0-9-]` slug from its
topic and globs `docs/streams/*`, stripping each folder's trailing `-<YYYYMMDD>` to compare. Exactly one
match → **JOIN** (append artifacts + rows; never re-scaffold the manifest or overwrite an artifact — a
re-run writes a new round). No match → **OPEN** a new stream, even if unrelated streams are in flight.
More than one match → **ask** which, always offering "open a new stream". This is a prose lookup — **not**
`sdlc_state.py resolve_active_feature()`, which is topic-blind.

- **`brainstorming` (greenfield lane)** — spec-first front door; opens/joins, then the
  `analyze-requirement → design → …` chain fills the gates in order.
- **`explore` (brownfield scout / greenfield prior-art)** — discovery front door; scouts into
  `research/RES-*.md`, opens/joins, STOPS (research runs before REQUIREMENT).
- **`plan-writing` (brownfield, stream-light lane)** — maintenance work with no matching stream: opens one
  and writes `plan/PLAN.md` **without** an SRS/design or forcing REQUIREMENT/DESIGN. Its Step-1
  input-contract detects the source of truth (`requirements/SRS.md → brainstorm/BRAINSTORM.md →
  research/RES-*.md → code`; asks when several exist, refuses to plan on nothing).

`lane:` in `STREAM.md` frontmatter (`greenfield` default / `brownfield`) is descriptive metadata only —
not read by any hook. In a stream-light stream the checkpoints that never ran read `pending`, which is
benign — closing the stream never depends on them (see `status: done`, above).

## Artifact Lifecycle

Every stage artifact is created once, updated by named stages, consumed by named stages, and closed at a
checkpoint — nothing created-but-unused. `STREAM.md` is the orphan/gap surface. "Closed at" names the
checkpoint/stop that consumes it; the STREAM ITSELF only ever closes on an authored `status: done` (see
Work-Stream Grouping above) — no artifact's individual closure implies the stream is done.

| Artifact | Created by | Consumed by | Closed at |
|----------|-----------|-------------|-----------|
| STREAM.md | first opener (open-or-join) | `handoff`, `session-init` | `status: done` (authored, at Delivery) |
| BRAINSTORM | `brainstorming` | `analyze-requirement` | REQUIREMENT |
| RES | `explore` | `plan-writing` | superseded by an SRS/PLAN citation, else stream close |
| SRS | `analyze-requirement` | design, tests | REQUIREMENT |
| SCREEN | `design-screen` | `design-function`, `implement-feature` | UI Design stop |
| BASIC / TECH | `design-function` | `implement-feature`, `review-code`, tests | DESIGN |
| PLAN | `plan-writing` | all stages | Delivery |
| DEV log | `implement-feature` | `review-code` | REVIEW |
| REVIEW + VERDICT-REVIEW | `review-code` | user | REVIEW |
| SEC + VERDICT-SECURITY | `vulnerability-scanner` | user | SECURITY / Pre-Delivery Re-scan |
| UTR + VERDICT-UNIT | `unit-test` | user | UNIT |
| ITR + VERDICT-INTEGRATION | `integration-test` | user | INTEGRATION |
| BUG | `fix-bug` | `unit-test`, `integration-test` | on fix |
| RETRO | `retro` | next stream | after Delivery |

## Memory Tiers

| Tier | Scope | Files |
|------|-------|-------|
| 1 — Core | Always loaded | `.claude/rules/agent-contract.md`, `CLAUDE.md`, `PROJECT.md` |
| 2 — Project | Cross-session | stream artifacts under `docs/streams/**` (read on demand) |
| 3 — Agent | Per-agent | `.claude/agent-memory/<agent-name>/MEMORY.md` (pool agents with a `memory:` scope) |
| 4 — Session | Current run | work-log checkpoints (read on resume) |

## Defect Round Loop

Max **R5** retry rounds per phase (unit test, integration test, code review). Each round fixes reported
failures only — no scope creep, no refactoring. Run the full regression after every fix batch. If R5 is
exceeded, escalate to the user with specific failures — never silently pass.

# SDLC Reference — ClaudeBrew

> On-demand detail behind the contract's SDLC map. Load this when you write or locate a stream artifact,
> open a stream, or need a gate's pass criteria. The contract carries the invariants; this file carries the
> tables and the full procedures. (Relocated from the former `sdlc-conventions.md`.)

## Quality Gates

| Gate | Phase | Criteria | Decided By | Verdict artifact |
|------|-------|----------|------------|------------------|
| G1 | Requirement | SRS complete, user stories + AC documented | User approval | — |
| G2 | UI Design | All screen states defined (default/load/empty/error) | User approval | — |
| G3a | Basic Design | Module structure, DB table list, API endpoint list | User approval | — |
| G3b | Detail Design | ORM schema, service methods, DTOs complete | User approval | — |
| G3c | Test Viewpoint | `docs/TEST_VIEWPOINT.md` customized (no placeholders) + test layers defined | User approval | — |
| G3d | Design Review | Design-review checklist PASS (0 Critical, 0 Major), full SRS→BASIC→TECH traceability | Review verdict + user | — |
| G4 | Code Review | 0 Critical findings, ≤2 Major (must fix) | `review-code` verdict (cbr-reviewer) + user | `gate: "G4"` |
| G5a | Initial Security Scan | 0 Critical, 0 High findings — scan after implementation complete | `vulnerability-scanner` verdict (cbr-reviewer) + user | `gate: "G5a"` |
| G6 | Unit Tests | 100% pass, ≤R5 rounds, 100% TECH functions covered | `unit-test` verdict (cbr-tester) + user | `gate: "G6"` |
| G7a | API Integration | All API integration tests pass (100%, ≤R5) on production-equivalent DB | `integration-test` verdict (cbr-tester) + user | `gate: "G7"` |
| G7b | E2E Browser | All critical-journey E2E tests pass (100%, ≤R5) — **N/A for backend-only** | `integration-test` verdict (cbr-tester) + user | `gate: "G7"` |
| G5b | Pre-Delivery Security Re-scan | Re-scan after all bug fixes: 0 Critical, 0 High clean | `vulnerability-scanner` re-scan + user | — (reuses G5a shape) |
| G8 | Delivery | All gates above green (G5b required before G8) | User sign-off | — |

**Never advance past an open Critical. Max R5 retry rounds per phase.**

**A verdict is evidence, not a decision.** A fresh pool agent writes it; the user decides whether the gate
opens. No agent auto-passes a gate. Only four gates are machine-validated — `hooks/verdict-gate.py` +
`schemas/verdict-artifact.schema.json` accept exactly `G4, G5a, G6, G7`:

- **G7a and G7b both report under `gate: "G7"`** (API vs E2E sub-criteria; report the split in the ITR,
  not the `gate` field).
- **G3d** carries a human-readable review verdict only — no machine artifact.
- **G5b** re-runs the G5a scan and reuses its shape.

Each verdict is written beside its gate's report inside the stream (`reviews/`, `security/`,
`test-reports/`) and validated by `hooks/verdict-gate.py --gate <G> --artifact <path>` before the user
decides. The `Critical`/`Major` severity a verdict blocks on is defined in the verdict schema's
`findings.severity` description.

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
| cbr-reviewer (pool) | Gate Verdict — G4 | `reviews/VERDICT-G4.json` (per-batch: `reviews/VERDICT-B[n]-G4.json`) |
| cbr-reviewer (pool) | Gate Verdict — G5a | `security/VERDICT-G5a.json` |
| cbr-tester (pool) | Gate Verdict — G6 | `test-reports/VERDICT-G6.json` |
| cbr-tester (pool) | Gate Verdict — G7 | `test-reports/VERDICT-G7.json` |
| `unit-test` | Test Cases / Report | `test-cases/UTC.md` / `test-reports/UTR-R[n].md` |
| `integration-test` | Test Cases / Report | `test-cases/ITC.md` / `test-reports/ITR-R[n].md` |
| `fix-bug` | Bug Report | `bug-reports/BUG-[YYYYMMDD]-[nn].md` |
| `plan-writing` | Plan | `plan/PLAN.md` |
| `retro` | Retrospective | `retro/RETRO-[YYYYMMDD].md` |
| `handoff` | Session Handoff | `handoffs/HANDOFF-[YYYYMMDD].md` |
| user / relevant skill | DAR / CAR | `dars/DAR-[topic]-[YYYYMMDD].md` / `cars/CAR-[topic]-[YYYYMMDD].md` |
| `estimate` | Estimation | `estimate/EST-[YYYYMMDD].md` |
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
  `research/RES-*.md`, opens/joins, STOPS (research is pre-G1).
- **`plan-writing` (brownfield, stream-light lane)** — maintenance work with no matching stream: opens one
  and writes `plan/PLAN.md` **without** an SRS/design or forcing G1–G3. Its Step-1 input-contract detects
  the source of truth (`requirements/SRS.md → brainstorm/BRAINSTORM.md → research/RES-*.md → code`; asks
  when several exist, refuses to plan on nothing).

`lane:` in `STREAM.md` frontmatter (`greenfield` default / `brownfield`) is descriptive metadata only —
not read by any hook. In a stream-light stream the design gates that never ran read `pending`, which is
benign.

## Artifact Lifecycle

Every stage artifact is created once, updated by named stages, consumed by named stages, and closed at a
gate — nothing created-but-unused. `STREAM.md` is the orphan/gap surface.

| Artifact | Created by | Consumed by | Closed at |
|----------|-----------|-------------|-----------|
| STREAM.md | first opener (open-or-join) | `handoff`, `session-init` | G8 |
| BRAINSTORM | `brainstorming` | `analyze-requirement` | G1 |
| RES | `explore` | `plan-writing` | superseded by an SRS/PLAN citation, else stream close |
| SRS | `analyze-requirement` | design, tests | G1 |
| SCREEN | `design-screen` | `design-function`, `implement-feature` | G2 |
| BASIC / TECH | `design-function` | `implement-feature`, `review-code`, tests | G3a / G3b |
| PLAN | `plan-writing` | all stages | G8 |
| DEV log | `implement-feature` | `review-code` | G4 |
| REVIEW + VERDICT-G4 | `review-code` | user | G4 |
| SEC + VERDICT-G5a | `vulnerability-scanner` | user | G5a/G5b |
| UTR + VERDICT-G6 | `unit-test` | user | G6 |
| ITR + VERDICT-G7 | `integration-test` | user | G7 |
| BUG | `fix-bug` | `unit-test`, `integration-test` | on fix |
| RETRO | `retro` | next stream | post-G8 |

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

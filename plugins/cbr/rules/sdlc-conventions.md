---
description: SDLC quality gates, artifact paths, and skill conventions. Always loaded alongside CLAUDE.md.
---

# SDLC Conventions — ClaudeBrew

> Governs how skills behave, where artifacts go, and what quality gates must pass.

## Quality Gates (CMMI-style)

| Gate | Phase | Criteria | Decided By | Verdict artifact |
|------|-------|----------|------------|------------------|
| G1 | Requirement | SRS complete, user stories + AC documented | User approval | — |
| G2 | UI Design | All screen states defined (default/load/empty/error) | User approval | — |
| G3a | Basic Design (BD) | Module structure, DB table list, API endpoint list | User approval | — |
| G3b | Detail Design (DD) | ORM schema, service methods, DTOs complete | User approval | — |
| G3c | Test Viewpoint | `docs/TEST_VIEWPOINT.md` (copied from `docs/_templates/TEST_VIEWPOINT.md`, customized, no placeholders) + test layers defined | User approval | — |
| G3d | Design Review | 16-item checklist PASS (0 Critical, 0 Major), full SRS→BASIC→TECH traceability verified | Review verdict + user | — |
| G4 | Code Review | 0 Critical findings, ≤2 Major (must fix) | `review-code` verdict (cbr:reviewer) + user | `gate: "G4"` |
| G5a | Initial Security Scan | 0 Critical, 0 High OWASP findings — scan after implementation complete | `vulnerability-scanner` verdict (cbr:reviewer) + user | `gate: "G5a"` |
| G6 | Unit Tests | 100% pass rate, ≤R5 rounds, 100% TECH spec functions covered (Function Coverage Matrix) | `unit-test` verdict (cbr:tester) + user | `gate: "G6"` |
| G7a | API Integration Tests | All API integration tests pass (100%, ≤R5) on production-equivalent DB, 100% BASIC workflows + TECH API contracts covered (Workflow-API Matrix) | `integration-test` verdict (cbr:tester) + user | `gate: "G7"` |
| G7b | E2E Browser Tests | All critical user journey E2E tests pass (100%, ≤R5) — **N/A for backend-only projects** | `integration-test` verdict (cbr:tester) + user | `gate: "G7"` |
| G5b | Pre-Delivery Security Re-scan | Re-scan after all bug fixes: 0 Critical, 0 High confirmed clean | `vulnerability-scanner` re-scan + user | — (reuses the G5a shape) |
| G8 | Delivery | All gates above green (G5b required before G8) | User sign-off | — |

**Rule**: Never advance to the next phase with an open Critical issue. Max R5 retry loops per phase.

**A verdict is evidence, not a decision.** Where a gate has a verdict, a fresh pool agent
writes it and the *user* decides whether the gate opens. No agent auto-passes a gate, and
no skill advances past its own gate on the strength of a verdict it collected.

**Only four gates are machine-validated.** `hooks/verdict-gate.py` and
`schemas/verdict-artifact.schema.json` accept exactly four `gate` values — **G4, G5a, G6,
G7** — so only those four have a JSON verdict artifact:

- **G7a and G7b both report under `gate: "G7"`.** They are sub-criteria (API vs. E2E), not
  separate artifact values; writing `"G7a"` fails validation. Report the split inside the
  ITR, not in the `gate` field.
- **G3d** has no dedicated gate skill in the single-layer model, so it carries a
  human-readable review verdict only — no machine artifact.
- **G5b** is a re-run of the G5a scan and reuses that shape; it does not get its own
  artifact value.

The remaining gates are plain user approvals with no verdict at all.

Each verdict is written **beside its own gate's report, inside the stream** — `<stream>/reviews/` next to
the REVIEW, `<stream>/security/` next to the SEC report, `<stream>/test-reports/` next to the UTR/ITR — so a
gate's evidence and its verdict never drift apart. Every one is validated by
`hooks/verdict-gate.py --gate <G> --artifact <path>` before the user is asked to decide.

## Artifact Paths (Canonical — stream-first)

**A work-stream is a directory.** Every per-feature artifact lives under
`docs/streams/<slug>-<YYYYMMDD>/`: the **folder is the identity**, the **sub-folder is the type**, and the
**filename drops the slug** (a time-series artifact keeps only its date or round). Each artifact is written
by the skill that owns it — never deviate without explicit project override. Paths below are relative to the
stream root `docs/streams/<slug>-<YYYYMMDD>/` unless they start with `docs/`.

| Owner | Artifact | Path (relative to the stream folder) |
|-------|----------|--------------------------------------|
| `brainstorming` | Stream Manifest | `STREAM.md` (created at stream start; the stream's index + board) |
| `brainstorming` | Brainstorm | `brainstorm/BRAINSTORM.md` |
| `researcher` (pool) | Research Report | `research/RES-[topic].md` |
| `worktree` | Worktree handoff | `WORKTREE.md` |
| `analyze-requirement` | SRS | `requirements/SRS.md` |
| `design-screen` | Screen Design | `requirements/SCREEN.md` |
| `design-function` | Basic Design (BD) | `design/BASIC.md` |
| `design-function` | Detail Design (DD) | `design/TECH.md` |
| `architecture` | Decision record (ADR) | `design/decisions/ADR-[topic]-[YYYYMMDD].md` (stream-scoped) |
| `implement-feature` | Work Log | `work-logs/DEV-[YYYYMMDD].md` |
| `review-code` | Design Review Report | `reviews/DESIGN-REVIEW-[YYYYMMDD].md` |
| `review-code` | Review Report | `reviews/REVIEW-[YYYYMMDD].md` |
| `vulnerability-scanner` | Security Report | `security/SEC-[YYYYMMDD].md` |
| cbr:reviewer (pool) | Gate Verdict — G4 | `reviews/VERDICT-G4.json` (per-batch: `reviews/VERDICT-B[n]-G4.json`) |
| cbr:reviewer (pool) | Gate Verdict — G5a | `security/VERDICT-G5a.json` |
| cbr:tester (pool) | Gate Verdict — G6 | `test-reports/VERDICT-G6.json` |
| cbr:tester (pool) | Gate Verdict — G7 | `test-reports/VERDICT-G7.json` |
| `unit-test` (Mode A) | Test Cases | `test-cases/UTC.md` |
| `unit-test` (Mode B) | Test Report | `test-reports/UTR-R[n].md` |
| `integration-test` (Mode A) | Test Cases | `test-cases/ITC.md` |
| `integration-test` (Mode B) | Test Report | `test-reports/ITR-R[n].md` |
| `fix-bug` | Bug Report | `bug-reports/BUG-[YYYYMMDD]-[nn].md` |
| `plan-writing` | Plan | `plan/PLAN.md` |
| `design-screen` (Stitch) | Stitch Screen PNG/HTML | `assets/stitch/[SCR-XX]-[state].png` / `.html` |
| `design-function` | Screen Preview PNG | `assets/pencil/BASIC-[SCR-XX].png` |
| `retro` | Retrospective Report | `retro/RETRO-[YYYYMMDD].md` |
| `handoff` | Session Handoff | `handoffs/HANDOFF-[YYYYMMDD].md` |
| user / relevant skill | DAR Evaluation | `dars/DAR-[topic]-[YYYYMMDD].md` |
| user / relevant skill | Corrective Action Report | `cars/CAR-[topic]-[YYYYMMDD].md` |
| `estimate` | Estimation | `estimate/EST-[YYYYMMDD].md` (re-run per re-estimate → time-series) |
| `design-screen`/`design-function` | Screen & design exports | `assets/<tool>/[SCR-XX]-[state].<ext>` — `<tool>` ∈ `stitch` \| `pencil` \| `figma` |
| `analyze-requirement` | Business Process Flow | Inline Mermaid in `requirements/SRS.md` §6 |
| `design-function` | Service Flow / Class Diagram | Inline Mermaid in `design/TECH.md` §4.2 / §6 |

**Project-level (at `docs/` root, NOT per-stream):**

| Owner | Artifact | Path |
|-------|----------|------|
| `design-function` | Coding Checklist | `docs/CODING-CHECKLIST.md` (created once per project) |
| `architecture` | Project-wide ADR | `docs/decisions/ADR-[topic]-[YYYYMMDD].md` (a decision spanning streams) |
| user / relevant skill | Risk Register (EPIC) | `docs/risks/RISK-[epic-name].md` |
| Any skill | Reference Templates | `docs/_templates/[NAME].md` (on-demand loading) |
| Each pool agent (self) | Agent Memory | `.claude/agent-memory/<agent-name>/MEMORY.md` (native auto-managed) |

Project-level reference docs (`PROJECT.md`, `CODING_RULES.md`, `CODING_CONVENTION.md`, `ARCHITECTURE.md`,
`API_DESIGN.md`, `TEST_VIEWPOINT.md`, `CODE-REVIEW-CHECKLIST.md`) also live at `docs/` root, seeded from
`docs/_templates/`. **These and the project-level table above stay at `docs/` root — never relocate a
project-level doc into a stream folder** (G3c reads `docs/TEST_VIEWPOINT.md` there).

**Auto-create rule**: Never fail because a directory is missing — create it. A stream folder
`docs/streams/<slug>-<YYYYMMDD>/` contains, on demand: `brainstorm/`, `requirements/`, `design/`
(+ `design/decisions/`), `plan/`, `work-logs/`, `reviews/`, `security/`, `test-cases/`, `test-reports/`,
`bug-reports/`, `retro/`, `handoffs/`, `research/`, `dars/`, `cars/`, `estimate/`, and
`assets/{stitch,pencil,figma,diagrams}/`. The project-level dirs `docs/decisions/` and `docs/risks/` are
likewise auto-created.

## Work-Stream Grouping

Each feature's SDLC artifacts belong to one **work-stream**. `brainstorming` declares the stream once at
`docs/streams/[slug]-[YYYYMMDD]/STREAM.md` (the manifest) for the greenfield flow; a brownfield stream with
no brainstorm is opened **stream-light** by `plan-writing` (see *Stream openers & lanes* below). Every
per-feature artifact carries a `stream: [slug]-[YYYYMMDD]` frontmatter field — a persistent cross-artifact
identity carrier.

- **The stream folder IS the layout** — artifacts live under `docs/streams/[slug]-[YYYYMMDD]/` per the table
  above; there is no type-first layout. The folder name carries the slug; `hooks/lib/sdlc_state.py` derives
  the active feature + gate state from the stream folder, and `STREAM.md` is its index.
- `STREAM.md` has two **authored** zones (membership table + task board) and one **derived** zone (the
  G1–G8 gate snapshot). The derived zone is regenerated by `handoff`/`session-init` from artifact/verdict globs — **gate authority
  stays with the glob (`hooks/lib/sdlc_state.py`); never hand-edit the gate zone**, and it is never a
  second source of truth.
- **Project-level reference docs stay at `docs/` root** (one per project, NOT under a stream), seeded from
  `docs/_templates/`: `PROJECT.md`, `CODING_RULES.md`, `CODING_CONVENTION.md`, `ARCHITECTURE.md`,
  `API_DESIGN.md`, `TEST_VIEWPOINT.md`, `CODING-CHECKLIST.md`, `CODE-REVIEW-CHECKLIST.md`.

**Upkeep protocol (MANDATORY, every stage skill).** When a stage skill writes its output artifact it must:
(1) stamp `stream: [id]` in that artifact's frontmatter; (2) append/update the artifact's row in the
stream's `STREAM.md` membership table; (3) update the task-board status for its phase. `brainstorming`
(greenfield) or `plan-writing` (brownfield, stream-light) creates `STREAM.md` from
`docs/_templates/STREAM.md` at stream start. Skills NEVER write the derived Gate
Status zone — `handoff` / `session-init` regenerate it.

### Stream openers & lanes (greenfield vs stream-light)

A work-stream has two possible openers, both scaffolding `STREAM.md` from `docs/_templates/STREAM.md`:

- **`brainstorming` (greenfield lane).** The spec-first front door — opens the stream, then the
  `analyze-requirement → design → …` chain fills G1–G8 in order.
- **`plan-writing` (brownfield, stream-light lane).** When maintenance work starts on an existing
  codebase with **no** stream, `plan-writing` opens one directly and writes `plan/PLAN.md` — **without**
  writing an SRS/design or forcing G1–G3. Its Step-1 **input-contract** first detects the source of truth
  to plan from (priority `requirements/SRS.md → brainstorm/BRAINSTORM.md → research/RES-*.md → code`; it
  **asks the user** when several are present, and **refuses to plan on nothing**).

`lane:` in `STREAM.md` frontmatter records which — `greenfield` (default) or `brownfield`. It is
**descriptive metadata only**: gate authority stays with the `hooks/lib/sdlc_state.py` glob, never the
marker (`lane:` is not read by any hook — it does not affect `resolve_active_feature` or the archived
flag). In a stream-light stream the design gates that never ran read `pending`, which is **benign** — the
stream is simply early on the greenfield ladder, not in a gap. (The derived `Next:` hint may point at
`analyze-requirement` for the same reason; it is a suggestion, and a brownfield stream is free to skip
straight to `implement-feature`.)

## Artifact Lifecycle

Every **stage** artifact has a defined lifecycle: created once, updated by named stages, consumed by
named stages, closed at a gate — nothing created-but-unused or created-but-never-updated. Cross-cutting /
optional artifacts (WORKTREE, ADR, DESIGN-REVIEW, DAR, RISK, CAR, EST) follow the same
create→consume→close discipline via the Artifact-Paths table above. `STREAM.md` is the
orphan/gap surface — an artifact not linked from it is an orphan; a stage missing its expected artifact
is a gap.

| Artifact | Created by | Updated by | Consumed by | Closed at |
|----------|-----------|-----------|-------------|-----------|
| STREAM.md | `brainstorming` (greenfield) / `plan-writing` (brownfield stream-light) | every stage (row + board) | `handoff`, `session-init` | G8 |
| BRAINSTORM | `brainstorming` | — | `analyze-requirement` | G1 |
| SRS | `analyze-requirement` | `analyze-requirement` | `design-screen`, `design-function`, tests | G1 |
| SCREEN | `design-screen` | `design-screen` | `design-function`, `implement-feature` | G2 |
| BASIC | `design-function` | `design-function` | `implement-feature`, `integration-test` | G3a |
| TECH | `design-function` | `design-function` | `implement-feature`, `review-code`, `unit-test` | G3b |
| TEST_VIEWPOINT (project) | `design-function` | `design-function` | `unit-test`, `integration-test`, `validate-and-test` | G3c |
| CODING-CHECKLIST (project) | `design-function` | `review-code` | `implement-feature`, `review-code` | G4 |
| PLAN | `plan-writing` | any stage (status) | `handoff`, all stages | G8 |
| DEV log | `implement-feature` | `implement-feature` | `review-code` | G4 |
| REVIEW + VERDICT-G4 | `review-code` | `review-code` (R5 rounds) | user (gate decision) | G4 |
| SEC + VERDICT-G5a | `vulnerability-scanner` | `vulnerability-scanner` (G5b re-scan) | user (gate decision) | G5a/G5b |
| UTC (test cases) | `unit-test` (Mode A) | — | `unit-test` (Mode B) | G6 |
| UTR + VERDICT-G6 | `unit-test` | `fix-bug` loop | user (gate decision) | G6 |
| ITC (test cases) | `integration-test` (Mode A) | — | `integration-test` (Mode B) | G7 |
| ITR + VERDICT-G7 | `integration-test` | `fix-bug` loop | user (gate decision) | G7 |
| BUG | `fix-bug` | `fix-bug` | `unit-test`, `integration-test` | on fix |
| RETRO | `retro` | — | next stream | post-G8 |

Reference templates in `docs/_templates/` are created once (seeded to their project-level location) and
updated by the skill that owns them; they are not per-stream artifacts.

Gate verdicts (VERDICT-G4/G5a/G6/G7) are authored by the fresh pool agent (`cbr:reviewer`/`cbr:tester`)
the stage skill spawns — the skill owns the gate; the pool agent writes the verdict.

## Behavior Conventions

### Tech Stack Detection (All Skills — MANDATORY Step 0)

Priority order:
1. `CLAUDE.md` (auto-loaded) — if contains tech stack section
2. `PROJECT.md` in project root
3. Ask user if neither provides context — **never assume a framework**

### Memory Tier Convention

Skills and pool agents draw on 4 memory tiers (loaded in order):

| Tier | Scope | Files | Loaded By |
|------|-------|-------|-----------|
| 1 — Core | Always loaded | `.claude/rules/*.md`, `CLAUDE.md`, `PROJECT.md` | Claude Code (auto) |
| 2 — Project | Cross-session shared | The stream artifacts above — `docs/streams/**` | Read on demand by the skill that needs them |
| 3 — Agent | Per-agent persistent | `.claude/agent-memory/<agent-name>/MEMORY.md` | Claude Code native (auto-load 200 lines) for pool agents declaring a `memory:` scope |
| 4 — Session | Current execution only | Work-log checkpoints | Read on resume |

## Defect Round Loop Rules

- Maximum **R5** retry rounds per phase (unit test, integration test, code review)
- Each round: fix reported failures only — no scope creep or refactoring
- Full regression test run after every fix batch
- If R5 exceeded: escalate to user with specific failure details — never silently pass

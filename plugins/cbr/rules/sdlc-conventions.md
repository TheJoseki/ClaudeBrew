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

Each verdict is written **beside its own gate's report** — `docs/reviews/` next to the
REVIEW, `docs/security/` next to the SEC report, `docs/test-reports/` next to the UTR/ITR
— so a gate's evidence and its verdict never drift apart. Every one is validated by
`hooks/verdict-gate.py --gate <G> --artifact <path>` before the user is asked to decide.

## Artifact Paths (Canonical)

Each artifact is written by the skill that owns it. Never deviate without explicit project override.

| Owner | Artifact | Path Pattern |
|-------|----------|-------------|
| `brainstorming` | Brainstorm | `docs/specs/brainstorms/BRAINSTORM-[topic].md` |
| `worktree` | Worktree handoff | `docs/specs/worktrees/WORKTREE-[topic].md` |
| `analyze-requirement` | SRS | `docs/specs/requirements/SRS-[feature].md` |
| `design-screen` | Screen Design | `docs/specs/requirements/SCREEN-[feature].md` |
| `design-function` | Basic Design (BD書) | `docs/specs/basic-design/BASIC-[feature].md` |
| `design-function` | Detail Design (DD書) | `docs/specs/detail-design/TECH-[feature].md` |
| `architecture` | Decision record (ADR) | `docs/specs/decisions/ADR-[topic]-[YYYYMMDD].md` |
| `design-function` | Coding Checklist | `docs/CODING-CHECKLIST.md` (project-level, created once per project) |
| `implement-feature` | Work Log | `docs/work-logs/DEV-[feature]-[YYYYMMDD].md` |
| `review-code` | Design Review Report | `docs/reviews/DESIGN-REVIEW-[feature]-[YYYYMMDD].md` |
| `review-code` | Review Report | `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md` |
| `vulnerability-scanner` | Security Report | `docs/security/SEC-[feature]-[YYYYMMDD].md` |
| cbr:reviewer (pool) | Gate Verdict — G4 | `docs/reviews/VERDICT-[feature]-G4.json` (per-batch: `VERDICT-[feature]-B[n]-G4.json`) |
| cbr:reviewer (pool) | Gate Verdict — G5a | `docs/security/VERDICT-[feature]-G5a.json` |
| cbr:tester (pool) | Gate Verdict — G6 | `docs/test-reports/VERDICT-[feature]-G6.json` |
| cbr:tester (pool) | Gate Verdict — G7 | `docs/test-reports/VERDICT-[feature]-G7.json` |
| `unit-test` (Mode A) | Test Cases | `docs/test-cases/UTC-[feature].md` |
| `unit-test` (Mode B) | Test Report | `docs/test-reports/UTR-[feature]-R[n].md` |
| `integration-test` (Mode A) | Test Cases | `docs/test-cases/ITC-[feature].md` |
| `integration-test` (Mode B) | Test Report | `docs/test-reports/ITR-[feature]-R[n].md` |
| `fix-bug` | Bug Report | `docs/bug-reports/BUG-[YYYYMMDD]-[nn].md` |
| `plan-writing` | Plan | `docs/plans/PLAN-[feature]-[YYYYMMDD].md` |
| `analyze-requirement` | Business Process Flow | Inline Mermaid in `SRS-[feature].md` §6 |
| `design-screen` (Stitch) | Stitch Screen PNG | `docs/specs/stitch/[feature]-[SCR-XX]-[state].png` |
| `design-screen` (Stitch) | Stitch Reference Code | `docs/specs/stitch/[feature]-[SCR-XX]-[state].html` |
| `design-function` | Screen Preview PNG | `docs/specs/pencil/exports/BASIC-[feature]-[SCR-XX].png` |
| `design-function` | Service Flow Diagram | Inline Mermaid in `TECH-[feature].md` §4.2 |
| `design-function` | Class Diagram | Inline Mermaid in `TECH-[feature].md` §6 |
| `retro` | Retrospective Report | `docs/retros/RETRO-[type]-[feature/sprint]-[YYYYMMDD].md` |
| Each pool agent (self) | Agent Memory | `.claude/agent-memory/<agent-name>/MEMORY.md` (native auto-managed) |
| Any skill | Reference Templates | `docs/_templates/[NAME].md` (on-demand loading) |
| user / relevant skill | DAR Evaluation | `docs/dars/DAR-[feature]-[topic]-[YYYYMMDD].md` |
| user / relevant skill | Risk Register (EPIC) | `docs/risks/RISK-[epic-name].md` |
| user / relevant skill | Corrective Action Report | `docs/cars/CAR-[feature]-[topic]-[YYYYMMDD].md` |
| `estimate` | Estimation | `docs/estimates/EST-[feature]-[YYYYMMDD].md` |

**Auto-create rule**: If `docs/[subfolder]/` does not exist, create it. Never fail because a directory is missing. This includes `docs/specs/requirements/` (SRS, SCREEN), `docs/specs/basic-design/` (BASIC), `docs/specs/detail-design/` (TECH), `docs/specs/stitch/` (Stitch PNG/HTML exports), `docs/specs/pencil/exports/` (Pencil exports), `docs/reviews/` (review reports + the G4 verdict), `docs/security/` (security reports + the G5a verdict), `docs/test-reports/` (UTR/ITR + the G6/G7 verdicts), `docs/retros/` (retrospective reports), `docs/dars/` (DAR evaluations), `docs/risks/` (risk registers), `docs/cars/` (corrective action reports), `docs/estimates/` (estimation documents).

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
| 2 — Project | Cross-session shared | The artifacts above — `docs/specs/**`, `docs/plans/PLAN-*.md`, `docs/reviews/**` | Read on demand by the skill that needs them |
| 3 — Agent | Per-agent persistent | `.claude/agent-memory/<agent-name>/MEMORY.md` | Claude Code native (auto-load 200 lines) for pool agents declaring a `memory:` scope |
| 4 — Session | Current execution only | Work-log checkpoints | Read on resume |

## Defect Round Loop Rules

- Maximum **R5** retry rounds per phase (unit test, integration test, code review)
- Each round: fix reported failures only — no scope creep or refactoring
- Full regression test run after every fix batch
- If R5 exceeded: escalate to user with specific failure details — never silently pass

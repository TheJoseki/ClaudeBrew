---
description: SDLC quality gates, artifact paths, and agent conventions. Always loaded alongside CLAUDE.md.
---

# SDLC Conventions — ClaudeKit

> Governs how agents behave, where artifacts go, and what quality gates must pass.

## Quality Gates (CMMI-style)

| Gate | Phase | Criteria | Decided By |
|------|-------|----------|------------|
| G1 | Requirement | SRS complete, user stories + AC documented | User approval |
| G2 | UI Design | All screen states defined (default/load/empty/error) | User approval |
| G3a | Basic Design (BD) | Module structure, DB table list, API endpoint list | User approval |
| G3b | Detail Design (DD) | ORM schema, service methods, DTOs complete | User approval |
| G3c | Test Viewpoint | `docs/TEST_VIEWPOINT.md` (copied from `docs/_templates/TEST_VIEWPOINT.md`, customized, no placeholders) + test layers defined | User approval |
| G3d | Design Review | 16-item checklist PASS (0 Critical, 0 Major), full SRS→BASIC→TECH traceability verified | architect-agent (DESIGN_REVIEW mode) |
| G4 | Code Review | 0 Critical findings, ≤2 Major (must fix) | code-review-agent PASS |
| G5a | Initial Security Scan | 0 Critical, 0 High OWASP findings — scan after implementation complete | security-tester-agent PASS |
| G6 | Unit Tests | 100% pass rate, ≤R5 rounds, 100% TECH spec functions covered (Function Coverage Matrix) | unit-test-agent PASS |
| G7a | API Integration Tests | All API integration tests pass (100%, ≤R5) on production-equivalent DB, 100% BASIC workflows + TECH API contracts covered (Workflow-API Matrix) | integration-test-agent PASS |
| G7b | E2E Browser Tests | All critical user journey E2E tests pass (100%, ≤R5) — **N/A for backend-only projects** | integration-test-agent PASS |
| G5b | Pre-Delivery Security Re-scan | Re-scan after all bug fixes: 0 Critical, 0 High confirmed clean | security-tester-agent PASS |
| G8 | Delivery | All gates above green (G5b required before G8) | User sign-off |

**Rule**: Never advance to the next phase with an open Critical issue. Max R5 retry loops per phase.

## Artifact Paths (Canonical)

All agents write output to these paths. Never deviate without explicit project override.

| Agent | Artifact | Path Pattern |
|-------|----------|-------------|
| ba-agent | SRS | `docs/specs/requirements/SRS-[feature].md` |
| ui-designer-agent | Screen Design | `docs/specs/requirements/SCREEN-[feature].md` |
| architect-agent (BASIC_DESIGN) | Basic Design (BD書) | `docs/specs/basic-design/BASIC-[feature].md` |
| architect-agent (DETAIL_DESIGN) | Detail Design (DD書) | `docs/specs/detail-design/TECH-[feature].md` |
| architect-agent (DETAIL_DESIGN) | Coding Checklist | `docs/CODING-CHECKLIST.md` (project-level, created once per project) |
| developer-agent | Work Log | `docs/work-logs/DEV-[feature]-[YYYYMMDD].md` |
| architect-agent (DESIGN_REVIEW) | Design Review Report | `docs/reviews/DESIGN-REVIEW-[feature]-[YYYYMMDD].md` |
| code-review-agent | Review Report | `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md` |
| security-tester-agent | Security Report | `docs/security/SEC-[feature]-[YYYYMMDD].md` |
| unit-test-agent (Mode A) | Test Cases | `docs/test-cases/UTC-[feature].md` |
| unit-test-agent (Mode B) | Test Report | `docs/test-reports/UTR-[feature]-R[n].md` |
| integration-test-agent (Mode A) | Test Cases | `docs/test-cases/ITC-[feature].md` |
| integration-test-agent (Mode B) | Test Report | `docs/test-reports/ITR-[feature]-R[n].md` |
| bug-fix-agent | Bug Report | `docs/bug-reports/BUG-[YYYYMMDD]-[nn].md` |
| orchestrator-agent | Plan | `docs/plans/PLAN-[feature]-[YYYYMMDD].md` |
| ba-agent (PLANNING) | BA Council Input | `docs/plans/COUNCIL-[feature]-BA.md` |
| architect-agent (PLANNING) | Arch Council Input | `docs/plans/COUNCIL-[feature]-ARCH.md` |
| inter-agent mailbox | Flags | `docs/agent-comms/flags/FLAG-[agent]-[ts]-[feature].md` |
| inter-agent mailbox | Questions | `docs/agent-comms/questions/Q-[from]-[to]-[ts]-[feature].md` |
| inter-agent mailbox | Answers | `docs/agent-comms/answers/A-[from]-[to]-[ts]-[feature].md` |
| ba-agent | Business Process Flow | Inline Mermaid in `SRS-[feature].md` §6 |
| ui-designer-agent (Stitch) | Stitch Screen PNG | `docs/specs/stitch/[feature]-[SCR-XX]-[state].png` |
| ui-designer-agent (Stitch) | Stitch Reference Code | `docs/specs/stitch/[feature]-[SCR-XX]-[state].html` |
| architect-agent (BASIC_DESIGN) | Screen Preview PNG | `docs/specs/pencil/exports/BASIC-[feature]-[SCR-XX].png` |
| architect-agent (DETAIL_DESIGN) | Service Flow Diagram | Inline Mermaid in `TECH-[feature].md` §4.2 |
| architect-agent (DETAIL_DESIGN) | Class Diagram | Inline Mermaid in `TECH-[feature].md` §6 |
| orchestrator-agent (RETRO) | Retrospective Report | `docs/retros/RETRO-[type]-[feature/sprint]-[YYYYMMDD].md` |
| orchestrator-agent | Plan Registry | `docs/plans/PLAN-REGISTRY.md` (project-level, one file) |
| All council agents | Decision Ledger | `docs/plans/DECISION-LEDGER.md` (project-level, append-only) |
| Multiple agents | Backlog Registry | `docs/plans/BACKLOG-REGISTRY.md` (project-level, append-only) |
| All agents | Project Memory | `docs/memory/PROJECT-MEMORY.md` (project-level, append-only) |
| Each agent (self) | Agent Memory | `.claude/agent-memory/<agent-name>/MEMORY.md` (native auto-managed) |
| Extracted from agents | Reference Templates | `docs/_templates/[NAME].md` (on-demand loading) |
| architect-agent / any | DAR Evaluation | `docs/dars/DAR-[feature]-[topic]-[YYYYMMDD].md` |
| orchestrator-agent | Risk Register (EPIC) | `docs/risks/RISK-[epic-name].md` |
| orchestrator-agent / any | Corrective Action Report | `docs/cars/CAR-[feature]-[topic]-[YYYYMMDD].md` |
| orchestrator-agent | Estimation | `docs/estimates/EST-[feature]-[YYYYMMDD].md` |

**Auto-create rule**: If `docs/[subfolder]/` does not exist, create it. Never fail because a directory is missing. This includes `docs/specs/requirements/` (SRS, SCREEN), `docs/specs/basic-design/` (BASIC), `docs/specs/detail-design/` (TECH), `docs/specs/stitch/` (Stitch PNG/HTML exports), `docs/specs/pencil/exports/` (Pencil exports), `docs/memory/` (project memory), `docs/retros/` (retrospective reports), `docs/dars/` (DAR evaluations), `docs/risks/` (risk registers), `docs/cars/` (corrective action reports), `docs/estimates/` (estimation documents).

## Agent Behavior Conventions

### Tech Stack Detection (All Agents — MANDATORY Step 0)

Priority order:
1. `CLAUDE.md` (auto-loaded) — if contains tech stack section
2. `PROJECT.md` in project root
3. Ask user if neither provides context — **never assume a framework**

### Spawn Sizing (Orchestrator — Phase 4)

#### Initial Grouping Table (starting point)

| Size Signal | Small | Medium | Large |
|-------------|-------|--------|-------|
| Modules | ≤3 | 4–8 | 9+ |
| API Endpoints | ≤10 | 11–25 | 26+ |
| Screens | ≤3 | 4–8 | 9+ |

| Sizing | Dev Agents | UT Agents | IT Agents |
|--------|-----------|----------|----------|
| Small | 1 | 1 | 1 |
| Medium | 2 (BE/FE) | 2 (BE/FE) | 1 |
| Large | 3 (module split) | 3 (BE/FE/Store) | 2 (API/E2E) |

All Phase 4 agents MUST be spawned **concurrently in a single message**.

#### Context Budget Estimation (MANDATORY before Phase 4 spawn)

The initial grouping table above provides a **starting point**. Before spawning Phase 4 agents, orchestrator MUST verify that each batch fits within the context budget using this heuristic formula:

```
estimated_batch_tokens = 90K (baseline: rules + agent body + context injection + mandatory doc reads)
  + spec_tokens                (TECH spec size: Small ~5K, Medium ~10K, Large ~15K)
  + (files_to_create × 2K)    (new files — Write only)
  + (files_to_modify × 3K)    (existing files — requires Read before Edit, higher cost)
  + (dependency_fan_out × 2K) (per import chain from files to modify, max 2 levels deep)
  + 10K                        (safety buffer for tool output, errors, retries)
```

**Dependency fan-out**: For each file to MODIFY → Grep its imports → count distinct modules referenced. Limit analysis to 2 import levels deep. Sum across all modified files in the batch.

**Budget decision rule**:

| Estimated Tokens | Status | Action |
|------------------|--------|--------|
| ≤ 150K | **SAFE** | Spawn normally |
| 150K – 200K | **TIGHT** | Apply Input Pruning Protocol (see `phase-4-implementation.md`) |
| > 200K | **OVER** | Must split batch further before spawning |

#### Adaptive Batch Sizing Protocol

After G3b (TECH spec approved), before entering Phase 4:

1. **Initial grouping**: Use the sizing table above (Small=1, Medium=2, Large=3 batches)
2. **Dependency coupling**: Group modules sharing data entities into the same batch. Independent modules may go in separate batches. FE modules consuming BE APIs from the same feature → same batch (interface verification)
3. **Estimate context weight** per candidate batch using the formula above
4. **Apply ceiling**: If any batch > 200K → move the least-coupled module to a new batch
5. **Merge check**: If all batches < 120K → merge to reduce sequential overhead
6. **Hard limits**: Max 5 batches. If > 5 needed → recommend EPIC/WAVE decomposition to user

Record estimates in the PLAN file:

```markdown
## Context Budget Estimate
| Batch | Modules | Files (C/M) | Fan-out | Est. Tokens | Status |
|-------|---------|-------------|---------|-------------|--------|
| B1 | auth, user | 4C / 2M | 8 | ~145K | SAFE |
| B2 | approval-flow | 3C / 4M | 12 | ~185K | TIGHT |
| B3 | dashboard-fe | 5C / 1M | 3 | ~120K | SAFE |
```

### Planning Council Trigger (Orchestrator — Phase 0)

| Feature Complexity (Step 0.2) | Phase 0 Action |
|-------------------------------|----------------|
| **Simple** (≤2 files, no model change) | Solo triage — no council. **CAO registry reads + context injection + registry updates + memory updates are MANDATORY for ALL complexity levels including Simple.** Only the Planning Council (ba + architect debate) is skipped. |
| **Medium / Large / Complex / Critical** | Sequential Planning Council: BA first → Architect reads BA output → optional Critic for Complex/Critical |

Planning Council flow (Sequential Chain):

```
orchestrator-agent (runs each step sequentially)
    │
    ├── P1: Agent(ba-agent) → writes COUNCIL-{feature}-BA.md
    │       (requirements, domain risks, sizing estimate)
    │
    ├── P2: Agent(architect-agent) → reads COUNCIL-BA.md FIRST
    │       → writes COUNCIL-{feature}-ARCH.md (aligned with BA)
    │
    ├── P3: [Complex/Critical only] Agent(architect-agent, critic mode)
    │       → reads BOTH COUNCIL artifacts → writes COUNCIL-{feature}-REVIEW.md
    │
    ├── Read all COUNCIL artifacts
    └── Synthesize into PLAN (with alignment verification)
```

> **Resume safety**: Check if COUNCIL artifacts exist → resume from next missing step.
> Artifacts are idempotent — re-running a step overwrites the previous output.

Orchestrator reads all COUNCIL artifacts and synthesizes into the final PLAN file.

### Session Resume Pattern

If a session was interrupted, orchestrator resumes by:
1. Reading `docs/plans/PLAN-[feature]-[date].md`
2. Finding first phase with status `⏳` (pending)
3. Continuing from that phase — no re-work of completed phases

```
@orchestrator-agent Resume feature [feature-name]
Plan file: docs/plans/PLAN-[feature]-[date].md
Continue from phase with status ⏳ PENDING
```

### Plan Types & Hierarchy (Orchestrator)

Every PLAN file MUST include these frontmatter fields:

```yaml
---
feature: [feature-name]
status: ACTIVE              # ACTIVE | SUSPENDED | COMPLETED
plan_type: FEATURE          # EPIC | WAVE | FEATURE | HOTFIX | INTERRUPT
parent: —                   # parent plan feature-name, or — if top-level
suspended_at: —             # timestamp when suspended (if applicable)
suspend_reason: —           # reason for suspension (if applicable)
---
```

| Type | When to Use | Parent Required |
|------|-------------|-----------------|
| EPIC | Multi-wave master plan spanning weeks | No |
| WAVE | Deliverable batch within an EPIC | Yes (EPIC) |
| FEATURE | Standalone feature not part of an EPIC | No |
| HOTFIX | Urgent fix that interrupts active work | Yes (interrupted plan) |
| INTERRUPT | Unplanned work (demo prep, assessment) | Yes (interrupted plan) |

### Interrupt Protocol (Orchestrator)

When an unplanned task interrupts an active plan:

1. **CHECKPOINT**: Write `## Checkpoint` section to the active PLAN file (phase, progress %, pending decisions, loaded context files)
2. **SUSPEND**: Update PLAN-REGISTRY.md — active plan status → ⏸️ SUSPENDED
3. **CREATE**: Create new PLAN with `plan_type: HOTFIX/INTERRUPT`, `parent: [suspended-plan]`
4. **EXECUTE**: Run interrupt plan with context injection (reads parent checkpoint + relevant decisions)
5. **IMPACT**: If interrupt changes anything in parent scope, write `## Impact Notes` to parent PLAN
6. **RESUME**: On completion, read parent checkpoint + impact notes → update affected specs → resume from checkpoint

### Spec Sync Protocol (Orchestrator + Developer)

When developer discovers code differs from TECH spec during implementation:

1. Developer creates CONTESTED decision in DECISION-LEDGER.md
2. Developer creates DESIGN_DEBT item in BACKLOG-REGISTRY.md
3. Developer writes FLAG to `docs/agent-comms/flags/` (priority: MEDIUM+)
4. Developer adds `## Spec Deviations` section to work-log
5. Orchestrator triages: update spec to match code, or fix code to match spec
6. Orchestrator marks the losing decision as SUPERSEDED, closes BACKLOG item

### Memory Tier Convention

Agents operate with 4 memory tiers (loaded in order):

| Tier | Scope | Files | Loaded By |
|------|-------|-------|-----------|
| 1 — Core | Always loaded | `.claude/rules/*.md`, `CLAUDE.md`, `PROJECT.md` | Claude Code (auto) |
| 2 — Project | Cross-session shared | `docs/plans/PLAN-REGISTRY.md`, `DECISION-LEDGER.md`, `BACKLOG-REGISTRY.md`, `docs/memory/PROJECT-MEMORY.md` | SubagentStart hook (auto) |
| 3 — Agent | Role-specific persistent | `.claude/agent-memory/<agent-name>/MEMORY.md` | Claude Code native (auto-load 200 lines) |
| 4 — Session | Current execution only | Work-log checkpoints, PLAN checkpoint section | Agent reads on resume |

### Progressive Disclosure Convention

Agent definition files (`.claude/agents/*.md`) follow a 3-level structure:

| Level | Content | Size Limit | When Loaded |
|-------|---------|-----------|-------------|
| 1 — Frontmatter | Role, capabilities, tools, model, memory, skills | ≤20 lines | Always |
| 2 — Body | Core execution protocol, I/O format, quality gates, `## Required Reading` | ≤200 lines | At spawn |
| 3 — Required Reading | Templates, examples, edge cases (loaded via Read tool) | Unlimited | On-demand by agent |

Agents MUST NOT read Level 3 references upfront — only when reaching the relevant execution step. The `## Required Reading` section in agent body lists files with timing instructions for when to load each one.

## Team Lifecycle Convention

- Max 1 active Agent Team at a time — sequential lifecycle
- Team lifetime scoped to phase/batch — TeamDelete after batch/phase completes
- TeamCreate only from orchestrate skill (main session) — agents never self-organize
- Session resume: check if artifacts exist → skip team creation if outputs already produced
- Templates: see `skills/orchestrate/references/team-templates.md` for 5 predefined templates
- Fallback: TeamCreate fails → auto-degrade to file-based comms (`docs/agent-comms/`)

## Defect Round Loop Rules

- Maximum **R5** retry rounds per phase (unit test, integration test, code review)
- Each round: fix reported failures only — no scope creep or refactoring
- Full regression test run after every fix batch
- If R5 exceeded: escalate to user with specific failure details — never silently pass

# Plan: [Feature Name]

**Date**: [YYYY-MM-DD] | **Type**: [NEW_FEATURE / ENHANCEMENT / BUG_FIX / UI_CHANGE / REFACTOR]
**Complexity**: [Small / Medium / Large] | **Sizing**: Small (1 batch) · Medium (2 batches) · Large (3 batches)
**Status**: IN_PROGRESS

---

## Summary

[1-2 sentence description of what this feature does and why it is needed.]

## Scope

**Included**: [what is in scope for this feature]
**Excluded**: [what is explicitly out of scope — prevents scope creep]

---

## Deliverable Inventory

> Fill after Phase 1 (SRS) approved.
> List by project type — choose the format that matches the project (check PROJECT.md):
>
> - **Web / Mobile app**: UI screens (Name, Route, Role)
> - **API-only / Microservice**: endpoints or resources (Resource, Method + Path, Role)
> - **ETL / Pipeline / Batch**: batch jobs (Job Name, Trigger, Output)
> - **Event-driven / Worker**: workers or queues (Worker, Queue, Purpose)

| ID | Deliverable | Detail (route / path / trigger / queue) | Role / Consumer | Status |
|----|-------------|-----------------------------------------|-----------------|--------|
| D-01 | [Screen / Endpoint / Job / Worker] | [/path or trigger or queue name] | [User / Admin / System] | PENDING |
| D-02 | | | | PENDING |

---

## Module & API Inventory

> Fill after Phase 3 (TECH) approved.
> List every backend module / service that will be created or modified.

| ID | Module | Key APIs / Entry Points | Dev Batch | Status |
|----|--------|------------------------|-----------|--------|
| M-01 | [Module name] | GET /x, POST /x | Batch-1 | PENDING |
| M-02 | [Module name] | PUT /x, DELETE /x | Batch-1 | PENDING |

---

## Dev Batches

> Derived from Module & Deliverable Inventories after Phase 3.
> Sizing rule: Small = 1 batch · Medium = 2 batches · Large = 3 batches

| Batch | Scope Description | Modules / Deliverables | Estimated Tasks |
|-------|-------------------|------------------------|-----------------|
| Batch-1 | Backend: [modules] | M-01, M-02 | [n] |
| Batch-2 | Frontend / Jobs: [deliverables] | D-01, D-02 | [n] |

---

## Work Breakdown Structure (WBS)

> Master task list. Update Status as each task completes.
> Batch column: `-` = not part of a dev batch (design/test phases); `background` = runs parallel to Phase 4.

| ID | Phase | Task | Agent | Input | Output | Batch | Status |
|----|-------|------|-------|-------|--------|-------|--------|
| T-01 | 1. Requirement | Analyze requirements | ba-agent | PLAN file | SRS-[f].md | - | PENDING |
| T-02 | 2. UI Design | Design deliverables (screens / API spec / job spec) | ui-designer-agent | SRS | SCREEN-[f].md | - | PENDING |
| T-03 | 3. Tech Design | DB schema + API endpoints + service layer | architect-agent | SRS, SCREEN | TECH-[f].md | - | PENDING |
| T-04 | 4. Implement | Batch-1: [scope summary] | developer-agent | TECH, SCREEN | code + DEV-[f]-B1.md | Batch-1 | PENDING |
| T-05 | 4. Review | Review Batch-1 | code-review-agent | DEV-[f]-B1.md | REVIEW-[f]-B1.md | Batch-1 | PENDING |
| T-06 | 4. Implement | Batch-2: [scope summary] | developer-agent | TECH, SCREEN | code + DEV-[f]-B2.md | Batch-2 | PENDING |
| T-07 | 4. Review | Review Batch-2 | code-review-agent | DEV-[f]-B2.md | REVIEW-[f]-B2.md | Batch-2 | PENDING |
| T-08 | 4b. UT Cases | Create Unit Test Cases (parallel) | unit-test-agent | TECH | UTC-[f].md | background | PENDING |
| T-09 | 4c. IT Cases | Create Integration Test Cases (parallel) | integration-test-agent | TECH, SRS | ITC-[f].md | background | PENDING |
| T-10 | 5. Security | OWASP scan on all implemented code | security-tester-agent | all code | SEC-[f].md | - | PENDING |
| T-11 | 6. Unit Test | Execute UTC — Round R1 | unit-test-agent | UTC-[f].md | UTR-[f]-R1.md | - | PENDING |
| T-12 | 7. Integration | Execute ITC — Round R1 | integration-test-agent | ITC-[f].md | ITR-[f]-R1.md | - | PENDING |

> **Note for Small features**: Only T-04 + T-05 (1 batch). Remove T-06, T-07. Keep T-08–T-12.
> **Note for Large features**: Add T-13 (Implement Batch-3) + T-14 (Review Batch-3) following the same pattern.

---

## Quality Gates Log

> Updated by orchestrator as each gate passes.

| Gate | Phase | Condition | Result | Date |
|------|-------|-----------|--------|------|
| G1 — SRS | Phase 1 | User approval | ⏳ PENDING | - |
| G2 — Screen / Deliverable Design | Phase 2 | User approval | ⏳ PENDING | - |
| G3 — Tech Design | Phase 3 | User approval | ⏳ PENDING | - |
| G4 — Code Review B1 | Phase 4 | REVIEW verdict = PASS | ⏳ PENDING | - |
| G4b — Code Review B2 | Phase 4 | REVIEW verdict = PASS (Medium/Large only) | ⏳ PENDING | - |
| G5 — Security Scan | Phase 5 | 0 Critical/High OWASP findings | ⏳ PENDING | - |
| G6 — Unit Tests | Phase 6 | 100% pass, ≤ R5 rounds | ⏳ PENDING | - |
| G7 — Integration Tests | Phase 7 | 100% pass, ≤ R5 rounds | ⏳ PENDING | - |
| G8 — Delivery | Phase 8 | All gates green, user sign-off | ⏳ PENDING | - |

---

## Sizing Reference

| Signal | Small | Medium | Large |
|--------|-------|--------|-------|
| Deliverables (screens / endpoints / jobs) | ≤ 3 | 4–8 | 9+ |
| Modules | ≤ 3 | 4–8 | 9+ |
| API Endpoints | ≤ 10 | 11–25 | 26+ |
| Dev Batches | 1 | 2 | 3 |

---

*This template is used by `orchestrator-agent` at Step 0.3. Fill in placeholders and remove unused batch rows based on final sizing.*

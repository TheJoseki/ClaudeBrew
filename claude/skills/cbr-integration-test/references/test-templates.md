# Integration Test Document Templates

> Reference for integration-test. Loaded on-demand when creating ITC/ITR documents.

## ITC Document Template (Mode A Output)

File: `docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md`

```markdown
# Integration Test Cases: [Feature Name]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Author**: integration-test
**Input TECH**: docs/streams/[feature]-[YYYYMMDD]/design/TECH.md
**Input SRS**: docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md
**HTTP Test Library**: [detected from PROJECT.md]
**E2E Framework**: [Playwright / Cypress / Supertest — detected]
**Complexity**: Small / Medium / Large
**Target ITC Count**: ≥[30/80/150]

## Test Scope
| Workflow | Actors (Roles) | Endpoints / Screens Tested |
|----------|---------------|---------------------------|

## Test Cases

### TC-IT-[feature]-001: [Test Case Name]
| Field | Value |
|-------|-------|
| **ID** | TC-IT-[feature]-001 |
| **Workflow** | [workflow name] |
| **Type** | API / Browser E2E |
| **Priority** | High / Medium / Low |
| **Actors** | [roles involved] |
| **Precondition** | [seed data required] |
| **Steps** | [numbered steps] |
| **Expected** | [expected result per step] |
| **Category** | Happy path / Rejection / RBAC / Edge |

## Workflow Test Matrix
| Workflow | Scenarios | TC IDs | AC IDs Covered |
|----------|-----------|--------|---------------|

## Scenario Coverage Check
| Workflow | Happy | Reject | Cancel | Concurrent | Edge |
|----------|-------|--------|--------|------------|------|

## Business Flow Chains (from BASIC §6.5 + TECH §4.3)

An integration chain must be a real **business flow** — a sequence of steps that
crosses an actor/role switch, a module boundary, or a state change — not three CRUD
calls on one entity dressed up as a chain (create → list → view is CRUD isolation, not
integration). Use realistic, production-shaped seed data, and cover each chain's
unhappy paths (the Negative Test Matrix below), not only the happy path.

### CHAIN-[feature]-001: [Flow Name — Happy Path]
| Field | Value |
|-------|-------|
| **Flow ID** | BF-xxx (from BASIC §6.5) |
| **Type** | CRUD / Approval / Auth / Multi-actor / State Machine / Async |
| **Actors** | [Role A, Role B] |
| **Business Steps** | [count of state-changing steps] |

| Step | Actor | Business Action | API Call (from TECH §4.3) | Expected | State Verification |
|------|-------|-----------------|--------------------------|----------|-------------------|
| 1 | Admin | Create account with role | POST /api/users | 201 | GET /api/users → contains new user |
| 2 | New User | Login with credentials | POST /api/auth/login | 200+token | Token has role=assigned_role |
| 3 | New User | Access role feature | GET /api/dashboard | 200 | Only permitted data returned |
| 4 | New User | Perform business action | POST /api/[entity] | 201 | GET /api/[entity]/:id returns entity |
| 5 | Admin | Verify action result | GET /api/[entity]/:id | 200 | Entity state correct, audit fields set |

**Cross-Entity Verification**: User.lastLoginAt updated, [entity] linked to user, audit trail created.

### CHAIN-[feature]-001-E1: [Flow Name — Error Variant]
[Same format, diverges at specific step per BASIC §6.5 Error/Rejection Paths table]

## Negative Test Matrix
| Endpoint | 401 No Token | 403 Wrong Role | 400 Per Rule | 404 Not Found | 409 Conflict |
|----------|-------------|----------------|--------------|---------------|-------------|

## Coverage Gaps
[List any BASIC §6.5 flows not fully covered, or Negative Matrix cells not filled — empty if all covered]

## Test Data Setup
[Describe seed data: users per role, teams/departments, prerequisite records, file uploads]

## Script Locations (Mode B will create)
| Test Type | Script Path |
|-----------|------------|
| API integration | `tests/integration/[feature].test.[ext]` |
| Browser E2E | `tests/e2e/[feature].spec.[ext]` |
```

---

## ITR Document Template (Mode B Output)

File: `docs/streams/[feature]-[YYYYMMDD]/test-reports/ITR-R[n].md`

```markdown
# Integration Test Report: [Feature Name] — Round R[n]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Round**: R[n]
**Author**: integration-test
**ITC Document**: docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md
**Scripts**: tests/e2e/[feature].spec.ts, tests/integration/[feature].test.ts

## Summary
| Metric | Value |
|--------|-------|
| Total ITCs | X |
| Passed | X |
| Failed | X |
| Pass Rate | X% |
| API tests | X passed / X total |
| Browser E2E | X passed / X total |

## Result: PASS / FAIL

## Workflow Results
| Workflow | Happy | Reject | RBAC | Edge | Status |
|----------|-------|--------|------|------|--------|

## Failed Test Cases
| TC ID | Workflow | Error | Steps to Reproduce | Severity |
|-------|----------|-------|-------------------|---------|

## Bug Reports (for fix-bug)
| Bug ID | TC ID | Description | Steps to Reproduce | Expected | Actual | Severity |
|--------|-------|-------------|-------------------|---------|--------|---------|

## Screenshots / Videos (Playwright)
[List of failure screenshots: `test-results/[name]-failed.png`]

## Actual Test Output
[Paste actual terminal output from test run]

## Next Action
- FAIL → fix-bug fixes bugs above → re-run R[n+1]
- R5 PASS → report to the user with the verdict artifact: Integration Tests 100% PASS (INTEGRATION is the user's call)
```




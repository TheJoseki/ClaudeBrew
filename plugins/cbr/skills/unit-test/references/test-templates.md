# Unit Test Document Templates

> Reference for unit-test-agent. Loaded on-demand when creating UTC/UTR documents.

## UTC Document Template (Mode A Output)

File: `docs/test-cases/UTC-[feature-name].md`

```markdown
# Unit Test Cases: [Feature Name]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Author**: unit-test-agent
**Input TECH**: docs/specs/detail-design/TECH-[feature].md
**Techniques**: EP, BVA, Decision Table, Error Guessing (ISTQB CTFL 4.0)
**Test Runner**: [detected from PROJECT.md]
**Complexity**: Small / Medium / Large
**Target UTC Count**: ≥[80/200/400]

## Test Scope
| Layer | Component | Test File Path |
|-------|-----------|---------------|
| BE Controller | [ControllerName] | [path/to/controller.spec.ts] |
| BE Service | [ServiceName] | [path/to/service.spec.ts] |
| FE Component | [ComponentName] | [path/to/Component.spec.ts] |
| FE Store | [StoreName] | [path/to/store.spec.ts] |

## Test Cases

### TC-UT-[feature]-001: [Test Case Name]
| Field | Value |
|-------|-------|
| **ID** | TC-UT-[feature]-001 |
| **Component** | [Controller / Service / Component / Store] |
| **Technique** | EP / BVA / Decision Table / Error Guessing |
| **Priority** | High / Medium / Low |
| **Precondition** | [setup required] |
| **Input** | [input data] |
| **Expected** | [expected result] |
| **Category** | Happy path / Negative / Edge case |

[Repeat for ALL TCs — must meet quantity target]

## Coverage Matrix
| AC ID (from SRS) | TC IDs | Coverage |
|-----------------|--------|----------|

## Technique Distribution Check
| Technique | Count | % |
|-----------|-------|---|
| EP | X | X% |
| BVA | X | X% |
| Decision Table | X | X% |
| Error Guessing | X | X% |
| **Total** | X | 100% |

## Test Data
[Describe mock data needed, factory functions, seed data]
```

---

## UTR Document Template (Mode B Output)

File: `docs/test-reports/UTR-[feature]-R[n].md`

```markdown
# Unit Test Report: [Feature Name] — Round R[n]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Round**: R[n]
**Author**: unit-test-agent
**UTC Document**: docs/test-cases/UTC-[feature].md

## Summary
| Metric | Value |
|--------|-------|
| Total TCs | X |
| Passed | X |
| Failed | X |
| Skipped | X |
| Pass Rate | X% |
| BE Coverage | X% |
| FE Coverage | X% |

## Result: PASS / FAIL
(PASS requires: 100% pass rate at R5 + BE ≥85% + FE ≥75%)

## Passed Test Cases
[list or "All X TCs passed"]

## Failed Test Cases
| TC ID | Component | Error Message | Severity |
|-------|-----------|--------------|---------|

## Bug Reports (for bug-fix-agent)
| Bug ID | TC ID | Description | Steps to Reproduce | Expected | Actual | Severity |
|--------|-------|-------------|-------------------|---------|--------|---------|

## Coverage Report
[Paste actual coverage output from test runner]

## Next Action
- FAIL → bug-fix-agent fixes bugs listed above → re-run R[n+1]
- R5 PASS (100% + coverage gates) → Notify orchestrator-agent: Unit Tests GATE PASSED
```

---

## Test Patterns (adapt to detected framework)

### Backend Controller Test

```
describe('[Feature]Controller', () => {
  // Set up test module using the backend testing framework
  // Mock the service dependency
  // Test each endpoint:
  //   - Happy path returns expected shape with correct HTTP status
  //   - Returns 401 when no authentication token
  //   - Returns 403 when wrong role
  //   - Returns 400 for invalid input (test each validation rule)
  //   - Returns 404 for unknown ID
  //   - Delegates to service with correct arguments
})
```

### Backend Service Test

```
describe('[Feature]Service', () => {
  // Set up with mocked ORM/repository
  // Test business logic:
  //   - Applies soft delete filter in ALL queries
  //   - Applies correct pagination (skip/take or offset/limit)
  //   - Populates audit columns (createdBy, updatedAt) on create/update
  //   - Enforces role-based data scope
  //   - Throws correct HTTP exception with correct message
  //   - Business rules: state machine transitions, validations
})
```

### Frontend Component Test

```
describe('[Feature]Component', () => {
  // Mount with required providers (store, i18n, router)
  // Test:
  //   - Renders table data from store correctly
  //   - All i18n keys resolve (no missing translation warnings)
  //   - Loading skeleton visible while fetching
  //   - Empty state visible when no data
  //   - Error state visible on API error
  //   - User interactions trigger correct store actions
  //   - Pagination controls work correctly
  //   - Dialog open/close/submit flows
})
```




# ITR Document Template

Use this template when creating `docs/test-reports/ITR-[feature]-R[n].md`.

```markdown
# Integration Test Report: [Feature] — Round R[n]
Date: [YYYY-MM-DD] | ITC: docs/test-cases/ITC-[feature].md

## Summary
| Total | Passed | Failed | Pass Rate |
|-------|--------|--------|-----------|

## RESULT: PASS / FAIL

## Workflow Results
| Workflow | Status | Notes |
|----------|--------|-------|

## Failed TCs
| TC ID | Error | Severity |
|-------|-------|---------|

## Bug Reports (→ fix-bug)
| Bug ID | TC ID | Description | Steps | Expected | Actual | Severity |
|--------|-------|-------------|-------|---------|--------|---------|

## Next
- FAIL: fix-bug fixes → re-run R[n+1]
- R5 PASS: report to the user with the verdict artifact
```

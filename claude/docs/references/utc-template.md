# Unit Test Document Templates

## UTC Document Template

Use this template when creating `docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md`.

```markdown
# Unit Test Cases: [Feature]
Date: [YYYY-MM-DD] | Techniques: EP, BVA, DT, EG
Backend test framework: [detected from PROJECT.md]
Frontend test framework: [detected from PROJECT.md]

## Test Scope
| Layer | Component | Test File |
|-------|-----------|-----------|
| BE Controller/Route | [name] | [path].spec.[ext] |
| BE Service/Handler | [name] | [path].spec.[ext] |
| FE Component | [name] | [path].spec.[ext] |
| FE Store/State | [name] | [path].spec.[ext] |

## Test Cases
### TC-UT-[feature]-001: [Name]
- Component: | Technique: EP/BVA/EG | Priority: High
- Input: | Expected: | Category: Happy path/Negative/Edge
```

## UTR Document Template

Use this template when creating `docs/streams/[feature]-[YYYYMMDD]/test-reports/UTR-R[n].md`.

```markdown
# Unit Test Report: [Feature] — Round R[n]
Date: [YYYY-MM-DD] | UTC: docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md

## Summary
| Total | Passed | Failed | Pass Rate | BE Coverage | FE Coverage |
|-------|--------|--------|-----------|------------|------------|
| X | X | X | X% | X% | X% |

## RESULT: PASS / FAIL

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

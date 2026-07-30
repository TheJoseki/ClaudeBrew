# Code Review Output Document Template

Use this template when creating `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md`.

```markdown
# Code Review: [Feature Name]
**Feature ID**: [feature] | **Date**: [YYYY-MM-DD] | **Reviewer**: review-code
**Tech Stack**: [detected from PROJECT.md]

---
## VERDICT: PASS / FAIL
[1-3 sentence summary]

---
## Findings

### Critical (blocks PASS)
| # | File | Line | Issue | Fix |
|---|------|------|-------|-----|

### Major (fix before merge)
| # | File | Line | Issue | Fix |
|---|------|------|-------|-----|

### Minor
| # | File | Line | Issue |
|---|------|------|-------|

---
## Security Checklist
- [ ] Auth guards present ✅/❌
- [ ] Role-based access correct ✅/❌
- [ ] Input validation (DTO/schema) ✅/❌
- [ ] No raw SQL / injection risk ✅/❌
- [ ] No hardcoded secrets ✅/❌
- [ ] Soft delete filter ✅/❌

## Action
- PASS → Phase 6: Unit Test Execution
- FAIL → implement-feature fix Critical/Major → re-review
```

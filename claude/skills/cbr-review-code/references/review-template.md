# Code Review Output Template

> Reference for review-code. Loaded on-demand when creating review report.

## Review Report Template

File: `docs/streams/[feature]-[YYYYMMDD]/reviews/REVIEW-BN.md`

> Reference checklist: `.claude/skills/review-code/references/leader-review-checklist.md`

```markdown
# Code Review: [Feature Name] — Batch N
**Feature ID**: [feature-name]
**Batch**: Batch-N | **Scope**: [modules/deliverables in this batch]
**Date**: [YYYY-MM-DD]
**Reviewer**: review-code
**DEV Work Log**: docs/streams/[feature]-[YYYYMMDD]/work-logs/DEV-BN.md
**TECH Spec**: docs/streams/[feature]-[YYYYMMDD]/design/TECH.md

---
## VERDICT: PASS / CONDITIONAL PASS / FAIL

[1-3 sentence summary of verdict reason]

---
## Score Summary

| Dimension | Weight | Score (1–5) | Weighted |
|-----------|--------|-------------|---------|
| Correctness | 30% | [x] | [x×0.30] |
| Security | 25% | [x] | [x×0.25] |
| Performance | 20% | [x] | [x×0.20] |
| Code Quality | 15% | [x] | [x×0.15] |
| Test Coverage | 10% | [x] | [x×0.10] |
| **Total** | 100% | — | **[sum]** |

Verdict threshold: ≥3.5 + 0 Critical = PASS · Any Critical = FAIL · <3.5 or 3+ Major = FAIL

---
## Findings

### Critical (must fix — blocks PASS)
| # | File | Line | Issue | Required Fix |
|---|------|------|-------|-------------|

### Major (should fix before merge)
| # | File | Line | Issue | Suggested Fix |
|---|------|------|-------|--------------|

### Minor (nice to have)
| # | File | Line | Issue | Suggestion |
|---|------|------|-------|-----------|

---
## Spec Adherence
| TECH Spec Section | Specified | Implemented | Match |
|---|---|---|---|
| [endpoint/service/model] | [spec says] | [code does] | YES / DEVIATION |

Deviations without a matching FLAG-developer-* file → Critical finding.

---
## Security Checklist
- [ ] Authentication guards on all protected endpoints
- [ ] Authorization decorators correct
- [ ] Input validation via DTOs/schemas
- [ ] DB access follows project convention; raw SQL uses parameterized statements only
- [ ] No hardcoded secrets
- [ ] File type/size validation (if applicable)
- [ ] Scope/isolation enforced for scoped roles

## Performance Notes
[ORM N+1 risks, missing pagination, frontend re-render issues]

## Action Required
- PASS: Proceed to next batch or Phase 5 Security Scan
- CONDITIONAL PASS: implement-feature must fix Major findings before next batch
- FAIL: implement-feature must fix Critical/Major → re-submit (max R2 per batch)
```




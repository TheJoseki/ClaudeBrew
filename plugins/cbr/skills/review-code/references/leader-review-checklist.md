# Code Review Checklist — Tech Lead Review

> Reference for `review-code`. Check all dimensions before issuing verdict.
> Input: `docs/streams/[feature]-[YYYYMMDD]/work-logs/DEV-BN.md` (scope list of files for this batch only).

---

## 1. Security (CRITICAL — any finding = automatic FAIL)

- [ ] Auth guard on every protected endpoint — no unguarded routes
- [ ] No secrets or credentials hardcoded in source files
- [ ] Input sanitized before use in DB / shell / file system
- [ ] DB access follows project convention (check `docs/CODING_RULES.md`):
  - ORM-only projects: no raw SQL present
  - Projects allowing raw SQL: every query uses parameterized statements, no string interpolation
- [ ] No sensitive data exposed in error messages or API responses
- [ ] CORS policy is explicit — no wildcard (`*`) on production routes

## 2. Correctness

- [ ] Implementation matches the TECH spec for this batch (compare DEV work log vs TECH spec sections)
- [ ] All WBS scope items for this batch are present in the work log
- [ ] Edge cases handled: empty collections, null/undefined, boundary values
- [ ] Error responses follow the API design patterns in `docs/API_DESIGN.md`
- [ ] Soft delete filters applied consistently (if project uses soft delete)

## 3. Performance

- [ ] No N+1 query patterns — relations loaded with eager joins / select_related where needed
- [ ] Indexes exist for columns used in WHERE / JOIN / ORDER BY (check migration files)
- [ ] No synchronous blocking operations in async context
- [ ] No unbounded queries — list endpoints have pagination or limit

## 4. Code Quality

- [ ] SRP respected — controllers/views delegate all business logic to services
- [ ] DRY — no logic duplicated between files in this batch
- [ ] Naming is descriptive and consistent with existing codebase conventions
- [ ] Functions ≤ 50 lines; extract helpers if longer
- [ ] No TODO / FIXME / debug statements in submitted code

## 5. Testing

- [ ] New business logic has unit tests
- [ ] At least one negative test per new endpoint (401, 403, 400 validation)
- [ ] Test names clearly describe the scenario: `test_[action]_[scenario]_[expected]`

---

## Verdict Rules

| Condition | Verdict |
|-----------|---------|
| Any Security finding (Section 1) | **FAIL** — Critical, must fix before next batch |
| 3+ Major findings (Section 2–5) | **FAIL** — fix and re-review (max R2 per batch) |
| 1–2 Major findings | **PASS with required fixes** — developer fixes then no re-review needed |
| Only Minor findings | **PASS** — note findings for awareness |
| No findings | **PASS** |

---

## Review Report Format

Write findings in `docs/streams/[feature]-[YYYYMMDD]/reviews/REVIEW-BN.md`:

```markdown
# Code Review — [Feature] Batch N
**Date**: [YYYY-MM-DD] | **Reviewer**: review-code | **Verdict**: PASS / FAIL

## Checklist Summary
| Section | Status | Finding Count |
|---------|--------|---------------|
| Security | ✅ PASS / ❌ FAIL | [n] |
| Correctness | ✅ PASS / ⚠️ ISSUES | [n] |
| Performance | ✅ PASS / ⚠️ ISSUES | [n] |
| Code Quality | ✅ PASS / ⚠️ ISSUES | [n] |
| Testing | ✅ PASS / ⚠️ ISSUES | [n] |

## Critical Findings (must fix)
- [file:line] — [description]

## Major Findings (should fix)
- [file:line] — [description]

## Minor Findings (optional)
- [file:line] — [description]

## Verdict
**[PASS / FAIL]** — [one-sentence rationale]
```

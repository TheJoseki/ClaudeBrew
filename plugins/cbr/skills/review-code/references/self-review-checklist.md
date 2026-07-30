# Developer Self-Review Checklist

> Complete BEFORE creating the work log for your batch.
> Every item must be checked. Mark `[x]` or note N/A with reason.

---

## Functionality

- [ ] All WBS scope items for this batch are implemented (cross-check Batch row in PLAN file)
- [ ] No scope items skipped without explicit note in work log
- [ ] Feature works end-to-end for the happy path
- [ ] Edge cases handled: empty input, null values, boundary values

## Code Quality

- [ ] No TODO / FIXME / console.log / print debug statements left in code
- [ ] Functions follow SRP — each function does exactly one thing
- [ ] No code duplication (DRY) — shared logic extracted to service/util
- [ ] All inputs validated at API boundary (DTO / Serializer / Schema)
- [ ] Naming is descriptive — no single-letter vars outside loops, no abbreviations

## Framework Standards

- [ ] TypeScript strict — no `any` types (TypeScript projects only)
- [ ] Auth guards / middleware applied on all protected endpoints
- [ ] DTOs defined and validated for all request/response shapes
- [ ] DB access follows project convention — check `docs/CODING_RULES.md`:
  - ORM-only projects: no raw SQL
  - Projects allowing raw SQL: ALL queries use parameterized statements, never string interpolation
- [ ] Soft delete filters applied on all list/read queries (if project uses soft delete)
- [ ] No secrets or credentials hardcoded — use environment variables

## Testing

- [ ] Unit tests written for all new business logic (services, utils)
- [ ] At least one negative test per endpoint (401 / 403 / 400 validation)
- [ ] Tests pass: run test command from `PROJECT.md` Build Commands
- [ ] Type check passes: run type-check command from `PROJECT.md`

## Documentation

- [ ] Work log (`docs/work-logs/DEV-[feature]-BN.md`) lists every file created/modified in this batch
- [ ] Work log notes any deviations from the TECH spec and the reason why
- [ ] Work log includes self-review result: "Self-review: PASS" or lists items still pending

---

## How to Report Self-Review in Work Log

Add this block at the end of the work log before submitting for review:

```
## Self-Review Result

| Category | Status | Notes |
|----------|--------|-------|
| Functionality | ✅ PASS / ⚠️ PARTIAL | [notes if partial] |
| Code Quality | ✅ PASS / ⚠️ PARTIAL | [notes] |
| Framework Standards | ✅ PASS / ⚠️ N/A | [notes] |
| Testing | ✅ PASS / ⚠️ PARTIAL | [notes] |
| Documentation | ✅ PASS | - |

**Overall**: READY FOR REVIEW / NEEDS MORE WORK
```

> If any category is PARTIAL or NEEDS MORE WORK, fix it before proceeding to code-review-agent.

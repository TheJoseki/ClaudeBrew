# Developer Work Log Template

> Reference for implement-feature. Loaded on-demand when creating work log after implementation.

## Work Log Output Template

File: `docs/work-logs/DEV-[feature]-BN.md` (replace BN with actual batch: B1, B2, B3)

```markdown
# Work Log: [Feature Name] — Batch N
**Feature ID**: [feature-name]
**Batch**: Batch-N | **Scope**: [modules/deliverables in this batch]
**Date**: [YYYY-MM-DD]
**Developer**: implement-feature
**Input TECH spec**: docs/specs/detail-design/TECH-[feature].md
**Status**: COMPLETED

## Files Created
| File | Type | Description |
|------|------|-------------|
| [backend module file] | BE | Module definition |
| [backend controller file] | BE | REST endpoints |
| [backend service file] | BE | Business logic |
| ... | ... | ... |

## Files Modified
| File | Change Summary |
|------|---------------|

## Schema Migration
- Migration name: `[migration-name]`
- Tables affected: [list]

## Self-Check Results
- [ ] Backend TypeScript/type check: PASS
- [ ] Backend Tests: PASS
- [ ] Frontend TypeScript/type check: PASS
- [ ] Frontend Tests: PASS
- [ ] ESLint/Linter: PASS

## Context Checkpoint (MANDATORY for ALL batch sizes — SAFE and TIGHT)

> Write a checkpoint after each implementation sub-step (data layer done, service layer done, etc.).
> This prevents context overflow and enables graceful partial completion via STATUS: PARTIAL.
> SAFE batches (≤150K): checkpoint after sub-step 1 of 2. TIGHT batches (150–200K): checkpoint after each of 3 sub-steps.
> See `sdlc-conventions.md` § Context Budget Estimation for thresholds and formula (90K baseline).

### Sub-step 1 Complete
- Files created: [list]
- Files modified: [list]
- Key decisions made: [list]
- Remaining scope: [list]
- Self-check status: PASS / pending

### Sub-step 2 Complete
- Files created: [list]
- Files modified: [list]
- Key decisions made: [list]
- Remaining scope: [list]
- Self-check status: PASS / pending

### Sub-step 3 Complete
- Files created: [list]
- Files modified: [list]
- Key decisions made: [list]
- Remaining scope: [list — should be empty at this point]
- Self-check status: PASS / pending

## Implementation Notes
[Any deviations from TECH spec, decisions made, known limitations]

## Known Gaps / TODO for QA
[Anything QA (unit-test, integration-test) should pay attention to]

## Self-Review Result
> Complete the checklist at `docs/CODING-CHECKLIST.md` (or `.claude/skills/review-code/references/self-review-checklist.md` if not available)
> then summarize results here before submitting for code review.

| Category | Status | Notes |
|----------|--------|-------|
| Functionality | ✅ PASS / ⚠️ PARTIAL | |
| Code Quality | ✅ PASS / ⚠️ PARTIAL | |
| Framework Standards | ✅ PASS / ⚠️ N/A | |
| Testing | ✅ PASS / ⚠️ PARTIAL | |
| Documentation | ✅ PASS | |

**Overall**: READY FOR REVIEW
```




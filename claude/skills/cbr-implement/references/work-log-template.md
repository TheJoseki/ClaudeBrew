# Developer Work Log Template

> Reference for `cbr-implement`'s Implement internal phase. Loaded on-demand when creating the
> work log after implementation.

## Work Log Output Template

File: `docs/streams/[feature]-[YYYYMMDD]/work-logs/DEV-[YYYYMMDD].md` (the canonical, date-based
name — see `{{CBR_ROOT}}/docs/references/sdlc-reference.md`'s Artifact Paths table; this is not a
per-batch file).

```markdown
# Work Log: [Feature Name]
**Feature ID**: [feature-name]
**Scope**: [modules/deliverables covered]
**Date**: [YYYY-MM-DD]
**Developer**: cbr-implement
**Input TECH spec**: docs/streams/[feature]-[YYYYMMDD]/design/TECH.md
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
> On long multi-file work, checkpoint progress here and return PARTIAL with remaining scope rather than pushing past coherence (see `rules/agent-contract.md`).

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
[Anything cbr-verify's testing phases should pay attention to]

## Self-Review Result
> Complete the checklist at `docs/CODING-CHECKLIST.md` per `checklist-driven-development.md` §3,
> then summarize results here before handing off to `cbr-verify`.

| Category | Status | Notes |
|----------|--------|-------|
| Functionality | ✅ PASS / ⚠️ PARTIAL | |
| Code Quality | ✅ PASS / ⚠️ PARTIAL | |
| Framework Standards | ✅ PASS / ⚠️ N/A | |
| Testing | ✅ PASS / ⚠️ PARTIAL | |
| Documentation | ✅ PASS | |

**Overall**: READY FOR REVIEW
```




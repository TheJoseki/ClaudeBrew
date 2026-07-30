# Handoff: user-authentication

> **Worked example** — demonstrates the expected output format from `/handoff`.
> Scenario: Mid-sprint handoff at Phase 6 (Unit Tests). Developer handing off to another team member.

**Date**: 2026-03-20
**Created by**: developer-agent (session ending)
**Recipient**: next session / incoming developer
**Feature**: User Authentication — register, login, JWT, password reset, auth guards

---

## State Summary (5 bullets max)

- [DONE] G1 SRS approved — `docs/specs/requirements/SRS-user-auth.md`
- [DONE] G3b TECH spec approved — `docs/specs/detail-design/TECH-user-auth.md` (JWT + bcrypt + refresh token rotation)
- [DONE] G4 Code Review PASSED — 0 Critical, 1 Major fixed (AuthService not injecting UserRepository correctly)
- [PENDING] G6 Unit Tests — 14/16 tests pass; 2 failures in `auth.service.spec.ts` (see Open Issues)
- [PENDING] G7a API Integration Tests — not started, blocked on G6

---

## Current Phase

**Active phase**: Phase 6 — Unit Tests
**Last completed gate**: G4 Code Review ✅ (2026-03-19)
**Next required action**: Fix 2 failing unit tests in `src/auth/auth.service.spec.ts`, then re-run:
```bash
cd backend && npx jest --testPathPattern=auth --coverage --verbose
```
Expected: 16/16 pass, coverage ≥ 85%

---

## Artifacts Status

| Artifact | Path | Status |
|----------|------|--------|
| PLAN | docs/plans/PLAN-user-auth-20260318.md | ✅ exists |
| SRS | docs/specs/requirements/SRS-user-auth.md | ✅ exists |
| TECH spec | docs/specs/detail-design/TECH-user-auth.md | ✅ exists |
| Work Log | docs/work-logs/DEV-user-auth-20260320.md | ✅ exists |
| Code Review | docs/reviews/REVIEW-user-auth-20260319.md | ✅ PASSED |
| UTC | docs/test-cases/UTC-user-auth.md | ✅ 16 test cases |
| UTR | docs/test-reports/UTR-user-auth-R1.md | ⚠️ 2 FAIL |
| ITC | docs/test-cases/ITC-user-auth.md | ✅ exists (not run yet) |
| Bug reports | — | None open |

---

## Open Issues

| # | Type | Description | Severity | File/Location |
|---|------|-------------|----------|--------------|
| 1 | Test failure | `should hash password on register` — bcrypt mock not resolving | Major | `src/auth/auth.service.spec.ts:47` |
| 2 | Test failure | `should return 401 on invalid credentials` — returns 500 instead | Major | `src/auth/auth.service.spec.ts:89` |

**Issue 1 detail**: The test mocks `bcrypt.hash` but doesn't return a Promise — needs `jest.fn().mockResolvedValue('hashed')` instead of `jest.fn().mockReturnValue('hashed')`.

**Issue 2 detail**: `UserRepository.findByEmail` throws when user not found instead of returning `null`. Need to update mock: `mockFn.mockResolvedValue(null)` and update the service to handle `null` gracefully.

---

## Key Decisions Made

| Decision | Rationale | Reference |
|----------|-----------|-----------|
| Refresh token rotation (invalidate old token on each use) | Prevents token theft via replay attack | TECH spec §3.2 |
| bcrypt rounds = 12 (not default 10) | Security requirement from CODING_RULES.md §7 | docs/CODING_RULES.md |
| Refresh tokens stored in DB (not cookie-only) | Allows server-side revocation for logout | SRS FR-AUTH-04 |
| Separate AuthModule from UserModule | Dependency direction: Auth depends on User, not reverse | TECH spec §2.1 |

---

## Resume Instructions

```
@orchestrator-agent Resume feature user-authentication
Plan file: docs/plans/PLAN-user-auth-20260318.md
Continue from Phase 6 (Unit Tests) — status ⏳ PENDING

Context: See docs/handoffs/HANDOFF-user-auth-20260320.md
Open issues: 2 failing unit tests — see Open Issues table.
Fix src/auth/auth.service.spec.ts issues #1 and #2 first,
then re-run: cd backend && npx jest --testPathPattern=auth --coverage
```

---

## Warnings

- The `refresh_tokens` DB table was added in migration `20260318_add_refresh_tokens.sql` — ensure this migration ran in the test DB before running integration tests
- Do NOT run integration tests until unit tests fully pass (UTR must be R1 100% before ITC)
- The `AuthGuard` is currently applied only to `UserController` — check TECH spec for full list of controllers that need it before G7

# Estimate: User Authentication

> **Worked example** — demonstrates the expected output format from `/estimate`.
> Feature: "User Authentication — register, login, JWT, password reset, auth guards"

**Date**: 2026-03-20
**Team**: 2 developers (1 BE, 1 FE)
**Methodology**: Agile — 2-week sprints
**Estimation basis**: WBS story points (1 pt ≈ 0.5 developer-days)

---

## Summary

| Metric | Value |
|--------|-------|
| Total story points | 28 |
| Raw effort (MD) | 14 man-days |
| Buffer applied | 20% (medium feature: 21–60 pts) |
| Adjusted effort (MD) | 16.8 man-days |
| Adjusted effort (MM) | 0.84 man-months |
| Recommended team | 2 developers (1 BE, 1 FE) |
| Calendar duration | ~8.4 working days ≈ 2 weeks (with team above) |

---

## WBS Breakdown

| # | Phase | Module | Task | Points | Notes |
|---|-------|--------|------|--------|-------|
| 1 | Backend | Schema | User model + migration (id, email, password_hash, role, created_at) | 2 | Standard ORM schema |
| 2 | Backend | Auth | Register endpoint (POST /auth/register) — DTO, validation, bcrypt hash | 3 | Email uniqueness check |
| 3 | Backend | Auth | Login endpoint (POST /auth/login) — credential verify, JWT issue | 3 | Access + refresh tokens |
| 4 | Backend | Auth | JWT strategy + auth guard implementation | 3 | Reusable guard for all routes |
| 5 | Backend | Auth | Refresh token endpoint (POST /auth/refresh) | 2 | Token rotation pattern |
| 6 | Backend | Auth | Password reset — request email (POST /auth/forgot-password) | 3 | Email service integration |
| 7 | Backend | Auth | Password reset — confirm + update (POST /auth/reset-password) | 2 | Token expiry validation |
| 8 | Frontend | Auth | Login page (form, validation, error states) | 3 | Accessible form |
| 9 | Frontend | Auth | Register page (form, validation, email confirm notice) | 2 | |
| 10 | Frontend | Auth | Auth store (state: user, token, isLoading, error) | 2 | Pinia / Vuex / Redux |
| 11 | Frontend | Auth | Protected route guard + redirect to login | 2 | Router-level guard |
| 12 | Tests | Unit | BE unit tests — AuthService (register, login, refresh, reset) | 3 | Mock DB, ≥85% coverage |
| 13 | Tests | Integration | API integration tests (POST /register, /login, /refresh, /forgot, /reset) | 5 | Real DB, negative cases |
| 14 | DevOps | Config | JWT_SECRET, JWT_EXPIRES_IN env vars + CI env setup | 1 | |

**Total: 36 points** — wait, recalculate: 2+3+3+3+2+3+2+3+2+2+2+3+5+1 = **36** — reclassified as large buffer (30%).

> **Note**: After re-counting, total is 36 points (not 28 as initially estimated). This is a common estimating recalibration when tasks are fully broken down. Revised summary below.

---

## Revised Summary (after full WBS)

| Metric | Value |
|--------|-------|
| Total story points | 36 |
| Raw effort (MD) | 18 man-days |
| Buffer applied | 20% (medium feature: 21–60 pts) |
| Adjusted effort (MD) | 21.6 man-days |
| Adjusted effort (MM) | 1.08 man-months |
| Recommended team | 2 developers (1 BE, 1 FE) |
| Calendar duration | ~10.8 working days ≈ 2.5 weeks |

---

## Phase Ratio

| Phase | Points | MD | % |
|-------|--------|----|---|
| Requirements (G1) | — | 2.2 | 10% |
| Design (G2, G3a, G3b) | — | 3.2 | 15% |
| Implementation (G4+) | 25 | 9.7 | 45% |
| Testing (G6, G7) | 8 | 4.3 | 20% |
| Bug fix + delivery (G8) | — | 2.2 | 10% |
| **Total** | **36** | **21.6** | **100%** |

---

## Assumptions

- Project already has Node.js/NestJS backend + Vue.js frontend configured
- Email service (SMTP or SendGrid) available — not estimating email provider setup
- JWT library already in package.json (jsonwebtoken / @nestjs/jwt)
- Database migrations handled by existing ORM tooling
- UI component library available — login form uses existing components, not built from scratch
- 1 pt ≈ 0.5 developer-days at sustainable pace (not crunch)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Email service integration complexity | Medium | Medium | Spike email service in Day 1 — unblock early |
| Refresh token rotation security edge cases | Low | High | Use reference implementation (e.g., nestjs/passport docs) |
| FE auth store + router guard interaction bugs | Medium | Medium | Write integration test covering full login → protected route flow |
| JWT secret rotation in production not planned | Low | High | Document rotation procedure in deployment guide |

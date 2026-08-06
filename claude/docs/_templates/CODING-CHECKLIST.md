# Coding Checklist — [PROJECT_NAME]

> Project-specific checklist created by `design-function` (Step D1).
> Used by `implement-feature` (self-review before work-log) and `review-code` + a fresh `cbr-reviewer` verdict (audit).
> Fill every `[… — e.g. …]` placeholder with actual values from PROJECT.md.

---

## 1. Security

- [ ] Auth guards on all protected endpoints — framework: [auth framework — e.g. JWT middleware]
- [ ] Role-based access control matches permission matrix from SRS
- [ ] Input validation via DTOs/schemas on all API endpoints
- [ ] No hardcoded secrets, API keys, or credentials in code
- [ ] CSRF protection on mutating endpoints (if web app)
- [ ] File upload validation: type whitelist, size limit, filename sanitization
- [ ] SQL injection prevention: ORM only, no raw queries without parameterization
- [ ] XSS prevention: output encoding in templates/responses

## 2. Data Layer

- [ ] ORM schema matches TECH spec entity definitions
- [ ] All migrations are reversible (up + down)
- [ ] Soft delete filter applied to ALL query operations (if project uses soft delete)
- [ ] Foreign key constraints match entity relationships
- [ ] Index definitions for frequently queried columns
- [ ] Seed data for development/testing (if applicable)
- [ ] Database: [database + ORM — e.g. Postgres + Prisma]

## 3. API Layer

- [ ] All endpoints from TECH spec are implemented
- [ ] Request/response DTOs match TECH spec definitions
- [ ] HTTP status codes: 200/201 success, 400 validation, 401 unauth, 403 forbidden, 404 not found
- [ ] Pagination on list endpoints (page, limit, total count)
- [ ] Error response format is consistent across all endpoints
- [ ] API versioning follows project convention: [versioning — e.g. URL prefix /api/v1]

## 4. Frontend

- [ ] Components follow single responsibility principle
- [ ] State management for shared/async state, local state for UI-only
- [ ] Loading/error/empty states handled for all async operations
- [ ] Form validation matches backend DTO constraints
- [ ] i18n: no hardcoded user-facing strings (if project uses i18n)
- [ ] Responsive breakpoints tested (if applicable)
- [ ] Framework: [frontend framework — e.g. React]

## 5. Code Quality

- [ ] No TODO / FIXME / debug statements in committed code
- [ ] Functions ≤50 lines, single responsibility
- [ ] Naming: descriptive, no abbreviations, consistent with project convention
- [ ] No duplicate logic — shared code extracted to utils/services
- [ ] TypeScript strict mode: no `any` types (if TypeScript project)
- [ ] Import order follows project convention

## 6. Testing

- [ ] Unit tests written for all new service/business logic
- [ ] Negative test cases: auth failure, validation failure, not found
- [ ] Test isolation: no shared mutable state between tests
- [ ] Test naming: `test_[action]_[scenario]_[expected]`
- [ ] Coverage meets project minimum: BE ≥[NN — e.g. 80]%, FE ≥[NN — e.g. 80]%
- [ ] Test runner: [test framework — e.g. Vitest]

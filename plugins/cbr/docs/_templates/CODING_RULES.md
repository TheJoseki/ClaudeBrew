# Coding Rules — [PROJECT_NAME]

> **Version**: 1.0
> **Standards**: PMBOK 7th Ed · CMMI V3.0 · OWASP 2025 · ISO/IEC 25010:2023 · Clean Code · SOLID
> **Applies to**: All agents (human & AI) working on this codebase
> Copy from `docs/_templates/CODING_RULES.md` to `docs/CODING_RULES.md` and fill in per project.

---

## 1. Golden Rules (Customize per project)

| # | Rule | Severity |
|---|------|----------|
| GR-01 | **Read docs/ before coding** — `ARCHITECTURE.md`, `API_DESIGN.md` are source of truth | CRITICAL |
| GR-02 | **TypeScript strict** — No `any`, no `@ts-ignore`, no `@ts-expect-error`, explicit return types (if TS project) | CRITICAL |
| GR-03 | **No hardcoded strings** — All user-facing text must use i18n system (if applicable) | CRITICAL |
| GR-04 | **Soft delete only** — `[DeleteFlag]` column: active value / deleted value. NEVER hard delete | CRITICAL |
| GR-05 | **Auth + Guards** — Every protected endpoint must have authentication guard + role check | CRITICAL |
| GR-06 | **ORM only** — No raw SQL, no raw queries unless PM-approved (document why) | CRITICAL |
| GR-07 | **Input validation** — All client input must go through framework validation (DTOs / Pydantic / Params) | CRITICAL |
| GR-08 | **Audit trail** — Set `CreateBy`, `CreateDate` on create; `UpdateBy`, `UpdateDate` on update | HIGH |
| GR-09 | **[PROJECT_SPECIFIC_RULE_1]** — [Description] | HIGH |
| GR-10 | **[PROJECT_SPECIFIC_RULE_2]** — [Description] | HIGH |

---

## 2. Security Rules (OWASP 2025)

### 2.1 Authentication & Authorization

| Rule | Description | Implementation |
|------|-------------|----------------|
| SEC-01 | Access token TTL = [VALUE] | Framework JWT config |
| SEC-02 | Refresh token TTL = [VALUE] | Stored in localStorage / HttpOnly cookie |
| SEC-03 | Auto-refresh on 401 | HTTP interceptor, queue pending requests |
| SEC-04 | Password policy: [DEFINE_POLICY] | Regex / validation rule |
| SEC-05 | Role-based access: Admin-only routes = [LIST_ROUTES] | FE route guards + BE `@Roles()` or equivalent |
| SEC-06 | [PROJECT_SCOPE_RULE] — e.g. department scope for manager queries | BE service filter |
| SEC-07 | Logout must invalidate refresh token | BE blacklist or delete token record |

### 2.2 Input Validation

| Rule | Description |
|------|-------------|
| SEC-08 | All DTOs / serializers must have field validators (`@IsString`, `@IsNotEmpty`, `@MaxLength`, etc.) |
| SEC-09 | File upload: extension whitelist — [LIST_ALLOWED_TYPES] |
| SEC-10 | File size limit: [MAX_SIZE] maximum per file |
| SEC-11 | Never inject user input directly into queries — ORM parameterized queries only |
| SEC-12 | Sanitize HTML output — prevent XSS |

### 2.3 Infrastructure

| Rule | Description |
|------|-------------|
| SEC-13 | CORS whitelist — allowed origins only |
| SEC-14 | HTTPS enforced in production |
| SEC-15 | Secrets in [SECRET_MANAGER] — never hardcode |
| SEC-16 | Never commit `.env`, credentials, tokens to git |

---

## 3. Backend Rules

### 3.1 Module Pattern (Adapt to framework)

**NestJS**:
```
modules/<module>/
├── <module>.module.ts          # @Module: imports, controllers, providers, exports
├── <module>.controller.ts      # @Controller: routes, guards, swagger decorators
├── <module>.service.ts         # @Injectable: business logic, ORM queries
├── dto/
│   ├── create-<module>.dto.ts  # Create DTO + class-validator
│   ├── update-<module>.dto.ts  # PartialType(CreateDto)
│   └── query-<module>.dto.ts   # Query/filter/pagination DTO
└── <module>.spec.ts            # Unit tests (Jest)
```

**Django**:
```
<app>/
├── models.py           # ORM models
├── serializers.py      # DRF serializers (validation)
├── views.py            # ViewSets / APIViews
├── urls.py             # URL routing
├── permissions.py      # Custom permission classes
└── tests.py            # Unit tests
```

### 3.2 Controller Rules

| Rule | Description |
|------|-------------|
| BE-01 | Controller = thin layer, delegate all logic to service |
| BE-02 | Every controller must have API documentation decorators (`@ApiTags`, `@ApiBearerAuth` or equivalent) |
| BE-03 | Every endpoint must have summary/description annotation |
| BE-04 | Protected endpoints: authentication guard + role guard |
| BE-05 | Inject user context from request / JWT payload |
| BE-06 | Return consistent response format: `{ data, total, page, pageSize }` for lists |

### 3.3 Service Rules

| Rule | Description |
|------|-------------|
| BE-07 | Service = business logic layer, all ORM queries here |
| BE-08 | Every `findMany`/`findAll` must filter `[DeleteFlag]: [ACTIVE_VALUE]` |
| BE-09 | Create: set `[DeleteFlag]: [ACTIVE_VALUE]`, `CreateBy`, `CreateDate` |
| BE-10 | Update: set `UpdateBy`, `UpdateDate` |
| BE-11 | Delete: soft delete `[DeleteFlag]: [DELETED_VALUE]`, set `UpdateBy`, `UpdateDate` |
| BE-12 | Use eager loading / `include` for related data — avoid N+1 |
| BE-13 | Multi-table operations: use database transactions |
| BE-14 | Error handling: throw framework HTTP exception with proper status code |
| BE-15 | Pagination default: `page=1`, `pageSize=[DEFAULT_PAGE_SIZE]` |

### 3.4 DTO / Serializer Rules

| Rule | Description |
|------|-------------|
| BE-16 | Every input field must have validation decorator |
| BE-17 | String fields: `@IsString()` + `@MaxLength(n)` |
| BE-18 | Required fields: `@IsNotEmpty()` |
| BE-19 | Optional fields: `@IsOptional()` + optional API property annotation |
| BE-20 | Update DTO: extends / inherits from Create DTO as partial |
| BE-21 | Query DTO: pagination fields + filter fields |

### 3.5 ORM Schema Rules

| Rule | Description |
|------|-------------|
| BE-22 | PK strategy: [INT_AUTO_INCREMENT or UUID] |
| BE-23 | Soft delete column: `[DeleteFlag] [VARCHAR(1) or Boolean]` default `[ACTIVE_VALUE]` |
| BE-24 | Audit columns: `CreateBy`, `CreateDate`, `UpdateBy`, `UpdateDate` on every table |
| BE-25 | FK relations: defined with proper `onDelete` behavior |
| BE-26 | Self-referential: `ParentId` FK to same table (for tree structures) |
| BE-27 | String lengths: match design spec |

### 3.5 Implementation Order (Backend)

Adapt to detected framework:
- **NestJS**: ORM Schema → Migration → DTOs → Services → Controllers → Module
- **Django**: Models → Serializers → Views → URLs → Admin
- **Rails**: Model → Controller → Views → Routes → Tests
- **Express**: Types → Models → Services → Routes → Middleware

---

## 4. Frontend Rules

### 4.1 Component Rules

| Rule | Description |
|------|-------------|
| FE-01 | `<script setup lang="ts">` — NO Options API (Vue 3 projects) |
| FE-02 | TypeScript strict — no `any`, explicit types for props/emits/refs |
| FE-03 | UI framework components only — do not mix with raw HTML form elements |
| FE-04 | All displayed text: `$t('key')` or `t('key')` — NO hardcoded strings |
| FE-05 | Composition API imports: `ref`, `computed`, `onMounted`, `watch` |
| FE-06 | `storeToRefs()` when destructuring Pinia store state/getters |
| FE-07 | Responsive: desktop-first (≥1264px), support tablet (≥600px) |

### 4.2 Pinia Store Rules

| Rule | Description |
|------|-------------|
| FE-08 | Typed state interface: `interface FeatureState { ... }` |
| FE-09 | Actions: async, call API service, update state, handle errors |
| FE-10 | Getters: computed properties, no side effects |
| FE-11 | Never call API directly in component — delegate via store actions |

### 4.3 API Service Rules

| Rule | Description |
|------|-------------|
| FE-12 | One service file per module: `src/services/<module>.service.ts` |
| FE-13 | Use HTTP client instance with JWT interceptor (auto-refresh) |
| FE-14 | Base URL: `[API_BASE_URL]` (configured via env) |
| FE-15 | Return typed responses: `Promise<ApiResponse<T>>` |

### 4.4 Router Rules

| Rule | Description |
|------|-------------|
| FE-16 | Auth guard: redirect to `/login` if not authenticated |
| FE-17 | Role guard: redirect to `/403` if not permitted |
| FE-18 | Lazy loading: `() => import('@/views/...')` for all routes |
| FE-19 | Route meta: `{ requiresAuth: boolean, roles: string[] }` |

### 4.5 i18n Rules

| Rule | Description |
|------|-------------|
| FE-20 | Flat namespace per module: `common.*`, `auth.*`, `[module].*` |
| FE-21 | Every key must exist in both `[LANG_1].json` and `[LANG_2].json` |
| FE-22 | Default locale: `[DEFAULT_LOCALE]` |
| FE-23 | Dynamic params: `$t('message', { name: user.name })` |

### 4.6 Type Rules

| Rule | Description |
|------|-------------|
| FE-24 | Interfaces for all data models: `src/types/<module>.ts` |
| FE-25 | Enums for status codes: `[EntityStatus]`, `[RoleCode]` |
| FE-26 | API response wrapper: `PaginatedResponse<T>`, `ApiResponse<T>` |
| FE-27 | Props interface: `interface Props { ... }` + `defineProps<Props>()` |

### 4.7 Implementation Order (Frontend)

Adapt to detected framework:
- **Vue.js 3**: Types → API Services → Pinia Stores → Components → Views → Router → i18n
- **React**: Types → API Services → State/Context → Components → Pages → Router
- **Next.js**: Types → API routes → Server components → Client components → Layouts

---

## 5. Performance Rules

| Rule | Description |
|------|-------------|
| PERF-01 | ORM eager loading / `include` instead of multiple queries (avoid N+1) |
| PERF-02 | Pagination on all list endpoints (default `[DEFAULT_PAGE_SIZE]`/page) |
| PERF-03 | Proper `where` filters pushed to DB — do not filter in-memory |
| PERF-04 | Database indexes on frequently queried columns |
| PERF-05 | Frontend lazy loading routes: `() => import(...)` |
| PERF-06 | `computed` instead of `method` for derived state |
| PERF-07 | `v-once` for static content, `v-memo` for expensive renders (Vue 3) |
| PERF-08 | API response target: `< [TARGET_MS]ms`, page load: `< [TARGET_S]s` |
| PERF-09 | Image optimization: lazy loading, proper sizing |
| PERF-10 | No blocking operations in request handlers |

---

## 6. Code Quality Rules

### 6.1 Clean Code

| Rule | Description |
|------|-------------|
| QUAL-01 | Function length ≤ 50 lines — split if longer |
| QUAL-02 | Single Responsibility Principle — 1 function = 1 task |
| QUAL-03 | DRY — no duplicate code, extract to shared utilities/composables |
| QUAL-04 | KISS — prefer simple, readable solutions |
| QUAL-05 | YAGNI — do not implement features that are not yet needed |
| QUAL-06 | Meaningful names: variables, functions, classes must be self-documenting |
| QUAL-07 | Comments: explain WHY, not WHAT (code explains itself) |
| QUAL-08 | No `console.log` in production code — use proper logger |
| QUAL-09 | No unused imports/variables — ESLint enforced |
| QUAL-10 | No magic numbers — extract to named constants |

### 6.2 Error Handling

| Rule | Description |
|------|-------------|
| QUAL-11 | BE: `try/catch` + HTTP exception with proper status codes |
| QUAL-12 | FE: `try/catch` in store actions + user-friendly error messages |
| QUAL-13 | API errors: consistent format `{ statusCode, message, error }` |
| QUAL-14 | Toast/Snackbar for user feedback (success, error, warning) |
| QUAL-15 | Loading states: progress indicator or skeleton loaders |
| QUAL-16 | Empty states: meaningful message + action button |
| QUAL-17 | 404 page: friendly "not found" with navigation |

---

## 7. Git Rules

### 7.1 Branch Strategy

| Pattern | Usage | Example |
|---------|-------|---------|
| `feature/<module>-<description>` | New feature | `feature/auth-login` |
| `fix/<description>` | Bug fix | `fix/login-redirect-loop` |
| `refactor/<description>` | Code improvement | `refactor/extract-composables` |
| `test/<description>` | Test additions | `test/approval-unit-tests` |
| `docs/<description>` | Documentation | `docs/coding-rules` |

### 7.2 Commit Convention (Conventional Commits)

```
<type>(<scope>): <description>

feat(auth): add JWT refresh token rotation
fix(auth): resolve infinite redirect loop on 401
refactor(documents): extract folder tree composable
test(approval): add unit tests for status transitions
docs(coding): update coding rules
chore(deps): upgrade dependencies
```

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Test additions or fixes |
| `docs` | Documentation only |
| `chore` | Build, deps, configs |
| `style` | Formatting, whitespace (no logic change) |
| `perf` | Performance improvement |

### 7.3 PR Rules

| Rule | Description |
|------|-------------|
| GIT-01 | PR description: summary + changes + test results |
| GIT-02 | All tests pass before merge |
| GIT-03 | TypeScript check pass (`tsc --noEmit`, `vue-tsc --noEmit`) |
| GIT-04 | Code review PASS (no Critical findings) |
| GIT-05 | i18n coverage: all keys in both languages (if applicable) |
| GIT-06 | No secrets, credentials, or `.env` files |

---

## 8. Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| **Files (BE)** | kebab-case | `approval.controller.ts`, `create-approval.dto.ts` |
| **Files (FE)** | PascalCase (components), kebab-case (others) | `ApprovalList.vue`, `approval.service.ts` |
| **Classes** | PascalCase | `ApprovalService`, `CreateApprovalDto` |
| **Interfaces** | PascalCase | `Approval`, `UserPayload`, `PaginatedResponse` |
| **Variables** | camelCase | `approvalStatus`, `currentUser` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `DEFAULT_PAGE_SIZE` |
| **Enums** | PascalCase (name), PascalCase (values) | `EntityStatus.Draft`, `EntityStatus.Approved` |
| **DB Tables** | [CONVENTION — e.g. PascalCase] | `Users`, `Approvals` |
| **DB Columns** | [CONVENTION — e.g. PascalCase] | `CreateBy`, `DeleteFlag` |
| **API Routes** | kebab-case | `/api/v1/my-requests`, `/api/v1/folder-tree` |
| **i18n Keys** | camelCase with dots | `common.save`, `module.statusDraft` |
| **CSS Classes** | kebab-case (BEM optional) | `approval-card`, `status-badge--approved` |
| **Git Branches** | kebab-case | `feature/auth-login` |

---

## 9. Domain-Specific Rules (Customize per project)

> Replace this section with project-specific business rules.

- **DOM-01**: [BUSINESS_RULE_1 — e.g. "Approval requests can only be submitted by Employee role"]
- **DOM-02**: [BUSINESS_RULE_2 — e.g. "File attachments max [SIZE], allowed types: [LIST]"]
- **DOM-03**: [WORKFLOW_RULE — e.g. "Status transitions: Draft → Submitted → Approved/Rejected"]
- **DOM-04**: [SCOPE_RULE — e.g. "Manager/Reviewer can only see records from their own department"]
- **DOM-05**: [DATA_RULE — e.g. "Edit operation resets workflow status to Draft"]

---

## 10. Enforcement

| Method | Tool | Scope |
|--------|------|-------|
| TypeScript strict | `tsconfig.json` + `vue-tsc` | BE + FE (TS projects) |
| Lint | ESLint / Ruff / Rubocop | All code |
| Input validation | class-validator / Pydantic / ActiveRecord | BE input |
| Form validation | UI framework rules | FE input |
| Unit tests | Jest (BE) + Vitest (FE) | All modules |
| Integration tests | Supertest (BE) + Vitest (FE) | Workflows |
| Code review | code-review-agent | Pre-merge |
| Type check CI | `npx tsc --noEmit` + `npx vue-tsc --noEmit` | CI pipeline |
| Test coverage | ≥ 80% | CI pipeline |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    [PROJECT_NAME] Coding Rules                   │
├─────────────────────────────────────────────────────────────────┤
│ [CUSTOMIZE THESE ITEMS]                                         │
│                                                                 │
│ Always:                                                         │
│ + TypeScript strict (no any, no @ts-ignore)                     │
│ + Composition API <script setup lang="ts"> (Vue 3)              │
│ + $t('key') for all UI text (i18n)                              │
│ + [DeleteFlag] soft delete                                      │
│ + Auth Guards + @Roles() on all protected endpoints             │
│ + Validation DTOs for all input                                 │
│ + ORM only (no raw SQL)                                         │
│ + Audit: CreateBy/Date, UpdateBy/Date                           │
│ + Function <= 50 lines, SRP, DRY                                │
│ + Conventional commits: feat/fix/refactor/test/docs             │
│ + Tests pass + TypeScript check before merge                    │
│                                                                 │
│ Never:                                                          │
│ - No hardcoded strings                                          │
│ - No console.log in production                                  │
│ - No raw SQL                                                    │
│ - No hard delete                                                │
│ - No Options API (Vue 3)                                        │
│ - No secrets in code / git                                      │
│ - No unused imports/variables                                   │
└─────────────────────────────────────────────────────────────────┘
```

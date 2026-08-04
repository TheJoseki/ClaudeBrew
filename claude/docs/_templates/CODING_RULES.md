# Coding Rules — [PROJECT_NAME]

> **Version**: 1.0
> **Standards**: PMBOK 7th Ed · CMMI V3.0 · OWASP 2025 · ISO/IEC 25010:2023 · Clean Code · SOLID
> **Applies to**: All agents (human & AI) working on this codebase
> Created/updated by `design-function`; enforced by `review-code` + fresh `cbr:reviewer` verdict + user.
> Framework specifics are PROJECT.md-driven — fill each `[… — e.g. …]` slot from your stack.
> Copy from `docs/_templates/CODING_RULES.md` to `docs/CODING_RULES.md` and fill in per project.

## 1. Golden Rules (Customize per project)
| # | Rule | Severity |
|---|------|----------|
| GR-01 | **Read docs/ before coding** — `ARCHITECTURE.md`, `API_DESIGN.md` are source of truth | CRITICAL |
| GR-02 | **Typed strict** — no untyped escapes or type suppressions; explicit signatures [— e.g. TS `strict`, no `any`, no `@ts-ignore`] (if typed language) | CRITICAL |
| GR-03 | **No hardcoded strings** — all user-facing text goes through the i18n system (if applicable) | CRITICAL |
| GR-04 | **Soft delete only** — `[DeleteFlag]` column: active value / deleted value. NEVER hard delete | CRITICAL |
| GR-05 | **Auth + guards** — every protected endpoint has an authentication guard + role check | CRITICAL |
| GR-06 | **ORM only** — no raw SQL/queries unless approved (document why) | CRITICAL |
| GR-07 | **Input validation** — all client input passes framework validation [— e.g. DTOs, schemas, serializers] | CRITICAL |
| GR-08 | **Audit trail** — set `CreateBy`, `CreateDate` on create; `UpdateBy`, `UpdateDate` on update | HIGH |
| GR-09 | **[PROJECT_RULE_1 — e.g. "money handled as integer minor units"]** | HIGH |
| GR-10 | **[PROJECT_RULE_2 — e.g. "all timestamps stored in UTC"]** | HIGH |

## 2. Security Rules (OWASP 2025)

### 2.1 Authentication & Authorization
| Rule | Description | Implementation |
|------|-------------|----------------|
| SEC-01 | Access token TTL = [VALUE — e.g. 15m] | Framework JWT config |
| SEC-02 | Refresh token TTL = [VALUE — e.g. 7d] | HttpOnly cookie or secure store |
| SEC-03 | Auto-refresh on 401 | HTTP interceptor, queue pending requests |
| SEC-04 | Password policy: [POLICY — e.g. ≥12 chars, mixed case + digit] | Validation rule |
| SEC-05 | Role-based access: admin-only routes = [ROUTES — e.g. `/admin/*`] | Route guards + server-side role check |
| SEC-06 | [SCOPE_RULE — e.g. "managers see only their own department"] | Service-layer filter |
| SEC-07 | Logout invalidates the refresh token | Server-side blacklist or token-record delete |

### 2.2 Input Validation
| Rule | Description |
|------|-------------|
| SEC-08 | Every input field has a validator [— e.g. type, non-empty, max-length] |
| SEC-09 | File upload: extension whitelist — [TYPES — e.g. pdf, png, jpg] |
| SEC-10 | File size limit: [MAX_SIZE — e.g. 10 MB] maximum per file |
| SEC-11 | Never inject user input into queries — ORM / parameterized only |
| SEC-12 | Sanitize / encode output — prevent XSS |

### 2.3 Infrastructure
| Rule | Description |
|------|-------------|
| SEC-13 | CORS whitelist — allowed origins only |
| SEC-14 | HTTPS enforced in production |
| SEC-15 | Secrets in [SECRET_MANAGER — e.g. Vault, AWS Secrets Manager] — never hardcode |
| SEC-16 | Never commit `.env`, credentials, or tokens to git |

## 3. Backend Rules

### 3.1 Module Pattern

Organize each backend module as thin layers — routing/controller, business/service, data/ORM, input validation, tests — following the framework's idiomatic layout [— e.g. NestJS module/controller/service/dto; Django models/serializers/views/urls; Rails model/controller/routes].

### 3.2 Controller / Route Rules
| Rule | Description |
|------|-------------|
| BE-01 | Controller = thin layer; delegate all logic to the service |
| BE-02 | Every controller has API-doc annotations [— e.g. OpenAPI/Swagger tags + auth marker] |
| BE-03 | Every endpoint has a summary/description annotation |
| BE-04 | Protected endpoints: authentication guard + role guard |
| BE-05 | Inject user context from the request / auth payload |
| BE-06 | Consistent list response: `{ data, total, page, pageSize }` |

### 3.3 Service Rules
| Rule | Description |
|------|-------------|
| BE-07 | Service = business-logic layer; all ORM queries live here |
| BE-08 | Every list/find query filters `[DeleteFlag]: [ACTIVE_VALUE]` |
| BE-09 | Create: set `[DeleteFlag]: [ACTIVE_VALUE]`, `CreateBy`, `CreateDate` |
| BE-10 | Update: set `UpdateBy`, `UpdateDate` |
| BE-11 | Delete: soft delete `[DeleteFlag]: [DELETED_VALUE]`, set `UpdateBy`, `UpdateDate` |
| BE-12 | Eager-load related data — avoid N+1 |
| BE-13 | Multi-table operations use database transactions |
| BE-14 | Error handling: throw the framework's HTTP exception with the correct status code |
| BE-15 | Pagination default: `page=1`, `pageSize=[DEFAULT_PAGE_SIZE — e.g. 20]` |

### 3.4 DTO / Serializer Rules
| Rule | Description |
|------|-------------|
| BE-16 | Every input field has a validation rule |
| BE-17 | String fields are typed and length-bounded |
| BE-18 | Required fields explicitly marked non-optional |
| BE-19 | Optional fields explicitly marked optional + documented |
| BE-20 | Update DTO inherits from the Create DTO as a partial |
| BE-21 | Query DTO: pagination fields + filter fields |

### 3.5 ORM Schema Rules
| Rule | Description |
|------|-------------|
| BE-22 | PK strategy: [PK — e.g. int auto-increment or UUID] |
| BE-23 | Soft-delete column `[DeleteFlag]` [TYPE — e.g. varchar(1) or boolean] default `[ACTIVE_VALUE]` |
| BE-24 | Audit columns `CreateBy`, `CreateDate`, `UpdateBy`, `UpdateDate` on every table |
| BE-25 | FK relations defined with proper `onDelete` behavior |
| BE-26 | Self-referential `ParentId` FK for tree structures |
| BE-27 | String lengths match the design spec |

### 3.6 Implementation Order (Backend)

Follow the framework's idiomatic build order [— e.g. schema → migration → DTOs → services → controllers → module].

## 4. Frontend Rules

### 4.1 Component Rules
| Rule | Description |
|------|-------------|
| FE-01 | Single responsibility; use the framework's modern component style, not legacy patterns [— e.g. composition API, function components] |
| FE-02 | Typed strict — explicit types for props/inputs/state (if typed language) |
| FE-03 | Use UI-framework components — do not mix with raw HTML form elements |
| FE-04 | All displayed text via the i18n system [— e.g. `t('key')`] — no hardcoded strings |
| FE-05 | Use framework state/lifecycle primitives idiomatically [— e.g. reactive refs, effect/lifecycle hooks] |
| FE-06 | Preserve reactivity when consuming shared store state [— e.g. ref-preserving destructure] |
| FE-07 | Responsive: desktop-first [— e.g. ≥1264px], support tablet [— e.g. ≥600px] |

### 4.2 State Management Rules
| Rule | Description |
|------|-------------|
| FE-08 | Typed state shape [— e.g. `interface FeatureState { … }`] |
| FE-09 | Actions: async, call the API service, update state, handle errors |
| FE-10 | Getters / derived state: pure, no side effects |
| FE-11 | Never call the API directly in a component — delegate via the state layer |

### 4.3 API Service Rules
| Rule | Description |
|------|-------------|
| FE-12 | One service file per module [— e.g. `services/<module>.service.*`] |
| FE-13 | Use a shared HTTP client with an auth interceptor (auto-refresh) |
| FE-14 | Base URL: `[API_BASE_URL]` (from env) |
| FE-15 | Return typed responses [— e.g. `ApiResponse<T>`] |

### 4.4 Router Rules
| Rule | Description |
|------|-------------|
| FE-16 | Auth guard: redirect to `/login` if not authenticated |
| FE-17 | Role guard: redirect to `/403` if not permitted |
| FE-18 | Lazy-load routes [— e.g. dynamic `import()` per route] |
| FE-19 | Route meta: `{ requiresAuth, roles }` |

### 4.5 i18n Rules
| Rule | Description |
|------|-------------|
| FE-20 | Flat namespace per module: `common.*`, `auth.*`, `[module].*` |
| FE-21 | Every key exists in both `[LANG_1].json` and `[LANG_2].json` |
| FE-22 | Default locale: `[DEFAULT_LOCALE — e.g. en]` |
| FE-23 | Dynamic params via interpolation [— e.g. `t('hello', { name })`] |

### 4.6 Type Rules
| Rule | Description |
|------|-------------|
| FE-24 | Interfaces for all data models [— e.g. `types/<module>.*`] |
| FE-25 | Enums for status / role codes [— e.g. `EntityStatus`, `RoleCode`] |
| FE-26 | API response wrappers [— e.g. `PaginatedResponse<T>`, `ApiResponse<T>`] |
| FE-27 | Typed component props/inputs [— e.g. a typed props declaration] |

### 4.7 Implementation Order (Frontend)

Follow the framework's idiomatic build order [— e.g. types → API services → state stores → components → views → router → i18n].

## 5. Performance Rules
| Rule | Description |
|------|-------------|
| PERF-01 | Eager-load related data instead of multiple queries (avoid N+1) |
| PERF-02 | Pagination on all list endpoints (default `[DEFAULT_PAGE_SIZE — e.g. 20]`/page) |
| PERF-03 | Push `where` filters to the DB — do not filter in memory |
| PERF-04 | Database indexes on frequently queried columns |
| PERF-05 | Lazy-load frontend routes |
| PERF-06 | Prefer memoized/derived state over recomputing in render [— e.g. computed properties] |
| PERF-07 | Memoize static/expensive renders using framework primitives [— e.g. render-memo directives/hooks] |
| PERF-08 | API response target `< [TARGET_MS — e.g. 300]ms`, page load `< [TARGET_S — e.g. 2]s` |
| PERF-09 | Image optimization: lazy loading, proper sizing |
| PERF-10 | No blocking operations in request handlers |

## 6. Code Quality Rules

### 6.1 Clean Code
| Rule | Description |
|------|-------------|
| QUAL-01 | Function length ≤ 50 lines — split if longer |
| QUAL-02 | Single Responsibility — 1 function = 1 task |
| QUAL-03 | DRY — no duplicate code; extract to shared utilities |
| QUAL-04 | KISS — prefer simple, readable solutions |
| QUAL-05 | YAGNI — do not build features not yet needed |
| QUAL-06 | Meaningful, self-documenting names |
| QUAL-07 | Comments explain WHY, not WHAT |
| QUAL-08 | No debug logging in production code — use a proper logger |
| QUAL-09 | No unused imports/variables — linter-enforced |
| QUAL-10 | No magic numbers — extract named constants |

### 6.2 Error Handling
| Rule | Description |
|------|-------------|
| QUAL-11 | Backend: catch + HTTP exception with correct status codes |
| QUAL-12 | Frontend: catch in state actions + user-friendly messages |
| QUAL-13 | Consistent API error format `{ statusCode, message, error }` |
| QUAL-14 | Toast/snackbar for user feedback (success, error, warning) |
| QUAL-15 | Loading states: progress indicator or skeleton loaders |
| QUAL-16 | Empty states: meaningful message + action |
| QUAL-17 | 404 page: friendly "not found" with navigation |

## 7. Git Rules

### 7.1 Branch Strategy
| Pattern | Usage |
|---------|-------|
| `feature/<module>-<description>` | New feature |
| `fix/<description>` | Bug fix |
| `refactor/<description>` | Code improvement |
| `test/<description>` | Test additions |
| `docs/<description>` | Documentation |

### 7.2 Commit Convention (Conventional Commits)

Format: `<type>(<scope>): <description>` — e.g. `feat(auth): add refresh-token rotation`.
Types: `feat` | `fix` | `refactor` | `test` | `docs` | `chore` | `style` | `perf`.

### 7.3 PR Rules
| Rule | Description |
|------|-------------|
| GIT-01 | PR description: summary + changes + test results |
| GIT-02 | All tests pass before merge |
| GIT-03 | Type check passes [— e.g. `tsc --noEmit`] |
| GIT-04 | Code review PASS (no Critical findings) |
| GIT-05 | i18n coverage: all keys in every locale (if applicable) |
| GIT-06 | No secrets, credentials, or `.env` files |

## 8. Naming Conventions
| Entity | Convention | Example |
|--------|-----------|---------|
| Files (backend) | kebab-case | `approval.controller.[ext]` |
| Files (frontend components) | PascalCase | `ApprovalList.[ext]` |
| Files (frontend other) | kebab-case | `approval.service.[ext]` |
| Classes | PascalCase | `ApprovalService` |
| Interfaces | PascalCase | `PaginatedResponse` |
| Variables | camelCase | `currentUser` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |
| Enums | PascalCase name + values | `EntityStatus.Draft` |
| DB Tables | [CONVENTION — e.g. PascalCase] | `Users` |
| DB Columns | [CONVENTION — e.g. PascalCase] | `CreateBy` |
| API Routes | kebab-case | `/api/v1/my-requests` |
| i18n Keys | camelCase with dots | `common.save` |
| CSS Classes | kebab-case (BEM optional) | `status-badge--approved` |
| Git Branches | kebab-case | `feature/auth-login` |

## 9. Domain-Specific Rules (Customize per project)

> Replace this section with project-specific business rules.

- **DOM-01**: [BUSINESS_RULE — e.g. "requests can only be submitted by the Employee role"]
- **DOM-02**: [ATTACHMENT_RULE — e.g. "attachments max 10 MB, types: pdf/png/jpg"]
- **DOM-03**: [WORKFLOW_RULE — e.g. "status: Draft → Submitted → Approved/Rejected"]
- **DOM-04**: [SCOPE_RULE — e.g. "reviewers see only their own department"]
- **DOM-05**: [DATA_RULE — e.g. "edit resets workflow status to Draft"]

## 10. Enforcement
| Method | Tool | Scope |
|--------|------|-------|
| Strict typing | [TYPE_CHECKER — e.g. `tsc --noEmit`] | Typed code |
| Lint | [LINTER — e.g. ESLint, Ruff, Rubocop] | All code |
| Input validation | [VALIDATION_LIB — e.g. schema/DTO validators] | Backend input |
| Form validation | UI framework rules | Frontend input |
| Unit tests | [BE_TEST_RUNNER] + [FE_TEST_RUNNER] | All modules |
| Integration tests | [INTEGRATION_RUNNER] | Workflows |
| Code review | `review-code` + fresh `cbr:reviewer` verdict | Pre-merge |
| Type check CI | [TYPE_CHECKER — e.g. `tsc --noEmit`] | CI pipeline |
| Test coverage | ≥ [COVERAGE — e.g. 80]% | CI pipeline |

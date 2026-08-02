# Architecture — [PROJECT_NAME]

> Created/updated by `architecture` / `design-function`; verdict by fresh `cbr:reviewer` + user.
> Copy from `docs/_templates/ARCHITECTURE.md` to `docs/ARCHITECTURE.md` and fill in per project.
> **Single source of truth for the cross-cutting API contract** (auth flow, error shape, pagination, status codes, RBAC) — see the *API Contract* section below. The per-endpoint catalog lives in `docs/API_DESIGN.md`; do not restate these patterns there.

---

## System Overview

Fill one row per layer/component. Add or remove rows to match the real topology. Use `/` (not `|`) to separate choices inside a cell.

| Layer | Component | Responsibility | Talks to |
|-------|-----------|----------------|----------|
| Client | [CLIENT — e.g. React SPA / Next.js SSR / mobile app / server-rendered pages] | [RESPONSIBILITY] | [DOWNSTREAM — e.g. REST API] |
| Edge | [EDGE — e.g. CDN / reverse proxy / API gateway / none] | [RESPONSIBILITY] | [DOWNSTREAM] |
| API | [BACKEND — e.g. NestJS / Django / Rails / FastAPI] | [RESPONSIBILITY] | [DATA_STORES] |
| Data | [DATABASE — e.g. PostgreSQL / MySQL / MongoDB] | [RESPONSIBILITY] | — |
| Storage | [STORAGE — e.g. S3 / GCS / local FS / none] | [RESPONSIBILITY] | — |
| Async | [ASYNC — e.g. queue / cron / workflow engine / none] | [RESPONSIBILITY] | — |

```mermaid
%% Optional — delete this block if the table above is sufficient.
%% flowchart LR: draw the real topology (client -> edge -> api -> data / storage / async).
```
> Optional — delete the `mermaid` block above if a table is sufficient.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | [FRONTEND — e.g. React / Vue / Next.js / none (API-only)] | [PURPOSE — e.g. client UI] |
| UI | [UI_LIBRARY — e.g. shadcn/ui / Vuetify / MUI] | Component library |
| State | [STATE — e.g. Redux / Pinia / TanStack Query / none] | Client state management |
| Router | [ROUTER — e.g. React Router / Vue Router / file-based] | Client routing + auth guards |
| i18n | [I18N — e.g. i18next / vue-i18n / none] | [LANG_DEFAULT] + [LANG_SECONDARY] |
| HTTP | [HTTP_CLIENT — e.g. fetch / axios / ky] | [PURPOSE — e.g. API calls with auth-token interceptor] |
| Backend | [BACKEND — e.g. NestJS / Django / Rails / FastAPI] | [PURPOSE — e.g. REST API] |
| ORM | [ORM — e.g. Prisma / TypeORM / SQLAlchemy / ActiveRecord] | Data access |
| Auth | [AUTH_SCHEME — e.g. JWT Bearer / session cookie / OAuth2 + PKCE] | [PURPOSE — e.g. access + refresh credentials] |
| Database | [DATABASE — e.g. PostgreSQL / MySQL / MongoDB] on [HOSTING — e.g. RDS / self-managed] | [REGION_OR_NOTE] |
| Storage | [STORAGE — e.g. S3 / GCS / local FS / none] | [STORAGE_PURPOSE] |
| Async | [ASYNC — e.g. BullMQ / Celery / cron / none] | [ASYNC_PURPOSE] |
| Deploy | [DEPLOY — e.g. ECS Fargate / Vercel / Railway / Docker Compose] | [DEPLOY_DESCRIPTION] |

---

## API Contract

Cross-cutting request/response conventions every endpoint obeys. The per-endpoint catalog lives in `docs/API_DESIGN.md`.

### Base URL & Versioning
- **Prefix**: [API_PREFIX — e.g. /api/v1/ / /api/ / none]
- **Versioning**: [VERSIONING — e.g. URL path /v1/ / header / none]

### Authentication Flow
- **Scheme**: [AUTH_SCHEME — e.g. JWT Bearer / session cookie / OAuth2 + PKCE]
- **Credential transport**: [TRANSPORT — e.g. Authorization header / HttpOnly cookie]
- **Access lifetime**: [ACCESS_TTL — e.g. 15m] · **Refresh/renewal**: [REFRESH_TTL — e.g. 7d / none]
- **On expiry**: [RENEWAL_FLOW — e.g. call the refresh endpoint, retry once; on failure send the user to login]
- **Client storage**: [TOKEN_STORAGE — e.g. HttpOnly cookie / localStorage / in-memory]

```mermaid
%% Optional — delete this block if the description above is sufficient.
%% sequenceDiagram: client -> API (login) -> credentials; client -> API (call + credential); API -> client (401) -> renew.
```
> Optional — delete the `mermaid` block above if the description is sufficient.

### Credential Policy (if applicable)
- Length: [MIN_LENGTH — e.g. 8]–[MAX_LENGTH — e.g. 64]
- Must include: [PASSWORD_REQUIREMENTS — e.g. upper, lower, digit, symbol]
- Format: [PASSWORD_REGEX — e.g. ^(?=.*[A-Z])(?=.*\d).{8,}$]

### Standard Error Response
Shape returned for every 4xx/5xx. Pick one envelope and keep it consistent across all endpoints.

```json
{
  "statusCode": 400,
  "message": "[HUMAN_READABLE — e.g. Validation failed]",
  "error": "[ERROR_LABEL — e.g. Bad Request]",
  "errors": { "[FIELD]": ["[FIELD_ERROR]"] }
}
```
> The shape above is illustrative — replace it with the project's chosen envelope (e.g. `{ code, message }`, RFC 9457 problem+json) and record the choice in `PROJECT.md` → Error format.

### Pagination Convention
- **Style**: [PAGINATION — e.g. offset (page/pageSize) / cursor / none]
- **Response envelope**:

```json
{
  "count": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5,
  "results": []
}
```
> Adjust field names to the chosen style (cursor-based uses `nextCursor` instead of `page`/`totalPages`).

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 204 | No content (e.g. delete) |
| 400 | Validation error |
| 401 | Unauthenticated (missing/expired credential) |
| 403 | Forbidden (role not permitted) |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable (if used instead of 400) |
| 500 | Server error |

---

## Role-Based Access Control

### Roles

| ID | Code | Name | Description |
|----|------|------|-------------|
| 1 | [ROLE_CODE_1] | [ROLE_NAME_1] | [ROLE_DESCRIPTION_1] |
| 2 | [ROLE_CODE_2] | [ROLE_NAME_2] | [ROLE_DESCRIPTION_2] |
| N | [ROLE_CODE_N] | [ROLE_NAME_N] | [ROLE_DESCRIPTION_N] |

### Permission Matrix

| Feature | [ROLE_1] | [ROLE_2] | [ROLE_N] |
|---------|----------|----------|----------|
| Dashboard | [Y/N] | [Y/N] | [Y/N] |
| [FEATURE_1] | [Y/N] | [Y/N] | [Y/N] |
| [FEATURE_2] | [Y/N] | [Y/N] | [Y/N] |
| Admin: [ADMIN_FEATURE] | [Y/N] | [Y/N] | [Y/N] |

### Route / Endpoint Guards

Map protected paths to the roles allowed. Enforced by [ENFORCEMENT — e.g. client route guard + server middleware/decorator].

| Path / Route | Auth | Allowed roles |
|--------------|------|---------------|
| [ROUTE — e.g. /admin/[resource]] | Yes | [admin_role] |
| [ROUTE — e.g. /[restricted]] | Yes | [role_1], [role_2] |
| * (all authenticated) | Yes | all |

---

## Data Model

Fill one row per entity; describe relationships in the last column.

| Entity | Key fields | Relationships |
|--------|-----------|---------------|
| [ENTITY_1] | [PK], [FIELDS] | [e.g. has many [ENTITY_2]] |
| [ENTITY_2] | [PK], [FK], [FIELDS] | [e.g. belongs to [ENTITY_1]] |
| [ENTITY_N] | [PK], [FIELDS] | [RELATIONSHIP] |

```mermaid
%% Optional — delete this block if the table above is sufficient.
%% erDiagram: draw entities and relationships (ENTITY_1 has-many ENTITY_2, etc.).
```
> Optional — delete the `mermaid` block above if a table is sufficient.

### Key Design Patterns
1. **PK strategy**: [PK_STRATEGY — e.g. INT autoincrement / UUID v4 / ULID]
2. **Delete strategy**: [DELETE — e.g. soft delete via a flag column (DeleteFlag / deletedAt) / hard delete]
3. **Audit columns**: [AUDIT — e.g. CreatedBy, CreatedAt, UpdatedBy, UpdatedAt / none]
4. **Role join**: [ROLE_JOIN — e.g. many-to-many via join table / single role column / n/a]
5. **Tree / hierarchy**: [TREE — e.g. ParentId self-FK / closure table / n/a]
6. **Versioning**: [VERSIONING — e.g. version column / none]

---

## Storage Integration (if applicable)

> Delete this section if the project has no external file/object storage.

- **Provider**: [STORAGE — e.g. S3 / GCS / SharePoint / local FS]
- **Layout**: [STRUCTURE — e.g. bucket/{tenant}/{entity}/{file}]
- **Allowed types**: [FILE_TYPES — e.g. PDF, DOCX, XLSX, JPG, PNG]
- **Max size**: [MAX_FILE_SIZE — e.g. 50MB per file]

### DB ↔ Storage mapping

| DB table | Storage concept | Key fields |
|----------|-----------------|------------|
| [TABLE_1] | [STORAGE_CONCEPT_1] | [KEY_FIELDS] |
| [TABLE_2] | [STORAGE_CONCEPT_2] | [KEY_FIELDS] |

- **Upload flow**: [UPLOAD_FLOW — e.g. client -> POST upload endpoint (multipart) -> validate size/type -> store -> create record -> return entity]

---

## Workflow / State Machine (if applicable)

> Delete this section if there is no multi-step approval or status workflow.

| Step | Actor | Actions |
|------|-------|---------|
| 1 | [ACTOR_1] | [ACTIONS] |
| 2 | [ACTOR_2] | [ACTIONS] |
| N | [ACTOR_N] | [ACTIONS] |

```mermaid
%% Optional — delete this block if the table above is sufficient.
%% stateDiagram-v2: INITIAL -> STATE_2 (action); STATE_2 -> APPROVED / REJECTED.
```
> Optional — delete the `mermaid` block above if a table is sufficient.

---

## Frontend Architecture (if applicable)

> Delete this section for API-only projects. Directory layout: see `docs/CODING_CONVENTION.md`.

### State stores

| Store | State | Key actions |
|-------|-------|-------------|
| [AUTH_STORE — e.g. useAuthStore] | user, credentials, isAuthenticated | login, logout, renew |
| [FEATURE_STORE_1] | items, pagination | fetchList, create, update, remove |
| [UI_STORE — e.g. useUiStore] | locale, theme, layout | setLocale, toggle... |

### Routes

| Path | View | Auth | Roles |
|------|------|------|-------|
| /login | [LoginView] | No | — |
| / | [DashboardView] | Yes | all |
| /[module] | [ModuleListView] | Yes | all |
| /[module]/:id | [ModuleDetailView] | Yes | all |
| /admin/[module] | [AdminModuleView] | Yes | [admin_role] |

---

## Internationalization (if applicable)

> Delete this section for single-language projects.

- **Default**: [LANG_DEFAULT — e.g. en] · **Secondary**: [LANG_SECONDARY — e.g. vi]
- **Rule**: every user-facing string goes through the i18n layer — no hardcoded copy.
- **Structure**: [I18N_STRUCTURE — e.g. flat namespace per module, key `module.action`]

---

## Security

| Concern | Implementation |
|---------|----------------|
| Auth | [AUTH_SCHEME — e.g. JWT Bearer / session cookie] with [RENEWAL — e.g. refresh flow] |
| Role enforcement | [ENFORCEMENT — e.g. client guards + server middleware/decorator] |
| Scope isolation | [SCOPE_FILTER — e.g. tenant/owner query filter] |
| File validation | [FILE_VALIDATION — e.g. type whitelist + size limit] (if applicable) |
| Input validation | [VALIDATION — e.g. DTO/schema validation; ORM, no raw SQL] |
| CORS | [CORS — e.g. whitelist allowed origins] |
| Transport | [TRANSPORT_SEC — e.g. HTTPS enforced in production] |
| Secrets | [SECRET_MANAGER — e.g. env vars / Vault / SSM] |
| Activity logging | [ACTIVITY_LOG — e.g. CRUD actions logged to an audit table] (if applicable) |
| Delete safety | [DELETE — e.g. soft-delete flag prevents accidental loss] (if applicable) |

---

## Deployment

Fill one row per deployed component.

| Component | Service / Runtime | Notes |
|-----------|-------------------|-------|
| Frontend | [FE_TARGET — e.g. static host + CDN / SSR runtime / n/a] | [BUILD_ARTIFACT] |
| API | [API_TARGET — e.g. container runtime / serverless / VM] | [BUILD_ARTIFACT] |
| Database | [DB_TARGET — e.g. managed DB / self-hosted] | [HA_OPTION] |
| Storage | [STORAGE_TARGET — e.g. object storage / n/a] | [PROVIDER] |
| Async | [ASYNC_TARGET — e.g. queue/cron worker / n/a] | (if applicable) |

```mermaid
%% Optional — delete this block if the table above is sufficient.
%% flowchart LR: static/CDN -> api runtime -> db; storage and async workers alongside.
```
> Optional — delete the `mermaid` block above if a table is sufficient.

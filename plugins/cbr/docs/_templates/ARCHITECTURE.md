# Architecture — [PROJECT_NAME]

> **Version**: 1.0
> **Source**: PROJECT.md + design docs
> Copy from `docs/_templates/ARCHITECTURE.md` to `docs/ARCHITECTURE.md` and fill in per project.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     [CDN_PROVIDER] CDN                           │
│                   ([FRONTEND_FRAMEWORK] static assets)           │
└──────────────────────┬───────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│            [FRONTEND_FRAMEWORK] SPA (Browser)                    │
│  [UI_FRAMEWORK] · [STATE_MANAGER] · [ROUTER] · [I18N] · [HTTP]   │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐        │
│  │  Views  │  │  Stores  │  │ Services │  │ Composables│        │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘        │
│       └─────────────┴──────────────┴──────────────┘               │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTPS (JWT Bearer)
┌──────────────────────▼───────────────────────────────────────────┐
│                  [BACKEND_FRAMEWORK] REST API                     │
│  [AUTH_LIBRARY] · Controllers · DTOs · Services · Guards         │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐       │
│  │ Auth Module  │  │ [MODULE_1]     │  │ [MODULE_2]      │       │
│  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘       │
│         │                  │                     │                 │
│  ┌──────▼───────┐  ┌──────▼────────┐  ┌────────▼────────┐       │
│  │ [MODULE_3]   │  │ [MODULE_4]    │  │ [MODULE_5]      │       │
│  └──────────────┘  └───────────────┘  └─────────────────┘       │
└──────┬───────────────────┬───────────────────┬───────────────────┘
       │                   │                   │
┌──────▼──────┐   ┌───────▼──────┐   ┌────────▼─────────┐
│ [DATABASE]  │   │ [STORAGE]    │   │ [WORKFLOW] (if)  │
│ on [HOSTING]│   │ [PROVIDER]   │   │                  │
└─────────────┘   └──────────────┘   └──────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | [FRONTEND_FRAMEWORK] + TypeScript + [BUILD_TOOL] | SPA framework |
| UI | [UI_FRAMEWORK] | Component library |
| State | [STATE_MANAGER] | Centralized state management |
| Router | [ROUTER] | Client-side routing + auth guards |
| i18n | [I18N_LIBRARY] | [LANG_1] (default) + [LANG_2] |
| HTTP | [HTTP_CLIENT] | API calls with JWT interceptor |
| Backend | [BACKEND_FRAMEWORK] + TypeScript + [ORM] | REST API |
| Auth | [AUTH_LIBRARY] | Access ([ACCESS_TTL]) + Refresh ([REFRESH_TTL]) tokens |
| Database | [DATABASE] on [HOSTING] | [REGION_OR_NOTE] |
| Storage | [STORAGE_PROVIDER] | [STORAGE_PURPOSE] |
| Workflow | [WORKFLOW_AUTOMATION] (if applicable) | [WORKFLOW_PURPOSE] |
| Deploy | [DEPLOYMENT_PLATFORM] | [DEPLOY_DESCRIPTION] |

---

## Authentication Architecture

### JWT Flow

```
┌────────┐         ┌──────────┐         ┌──────────┐
│  SPA   │──login──▶│ REST API │──verify──▶│ Database │
│        │◀─tokens─┤          │◀─user────┤          │
└───┬────┘         └──────────┘         └──────────┘
    │
    │ Every API call:
    │ Authorization: Bearer <access_token>
    │
    │ On 401:
    │ ──refresh──▶ POST /api/v1/auth/refresh/
    │ ◀─new access─┤
    │
    │ On refresh fail:
    │ ──redirect──▶ /login
```

### Token Configuration
- **Access token**: [ACCESS_TTL] TTL
- **Refresh token**: [REFRESH_TTL] TTL
- **Storage**: `localStorage` (access + refresh) [or HttpOnly cookie]
- **HTTP interceptor**: Auto-refresh on 401, queue pending requests

### Password Policy
- Length: [MIN_LENGTH]-[MAX_LENGTH] characters
- Must include: [PASSWORD_REQUIREMENTS]
- Format: `[PASSWORD_REGEX]`

---

## Role-Based Access Control

### Roles

| ID | Code | Name | Description |
|----|------|------|-------------|
| 1 | [ROLE_CODE_1] | [ROLE_NAME_1] | [ROLE_DESCRIPTION_1] |
| 2 | [ROLE_CODE_2] | [ROLE_NAME_2] | [ROLE_DESCRIPTION_2] |
| 3 | [ROLE_CODE_3] | [ROLE_NAME_3] | [ROLE_DESCRIPTION_3] |
| N | [ROLE_CODE_N] | [ROLE_NAME_N] | [ROLE_DESCRIPTION_N] |

### Permission Matrix

| Feature | [ROLE_1] | [ROLE_2] | [ROLE_3] | [ROLE_N] |
|---------|----------|----------|----------|----------|
| Dashboard | [Y/N] | [Y/N] | [Y/N] | [Y/N] |
| [FEATURE_1] | [Y/N] | [Y/N] | [Y/N] | [Y/N] |
| [FEATURE_2] | [Y/N] | [Y/N] | [Y/N] | [Y/N] |
| Admin: [ADMIN_FEATURE] | [Y/N] | [Y/N] | [Y/N] | [Y/N] |

### Frontend Route Guards

```typescript
const roleGuards = {
  '/admin/[resource]': ['[admin_role]'],
  '/[restricted_route]': ['[role_1]', '[role_2]'],
  '*': ['[role_1]', '[role_2]', '[role_3]', '[role_n]']  // all authenticated
}
```

---

## [STORAGE_PROVIDER] Integration (if applicable)

### [STORAGE] Structure

[CUSTOMIZE: describe your storage structure]

```
[STORAGE_ROOT]
├── [CONTAINER/BUCKET/SITE]
│   ├── [FOLDER_STRUCTURE]
│   │   ├── [SUBFOLDER]
│   │   │   └── [FILE]
│   │   └── [FILE]
│   └── [ANOTHER_FOLDER]
```

### DB <-> [STORAGE] Mapping

| DB Table | [STORAGE] Concept | Key Fields |
|----------|-------------------|------------|
| [TABLE_1] | [STORAGE_CONCEPT_1] | [KEY_FIELDS] |
| [TABLE_2] | [STORAGE_CONCEPT_2] | [KEY_FIELDS] |

### File Upload Flow

```
User -> [Select File] -> [FRONTEND_FRAMEWORK] SPA
  -> POST /api/v1/[resource]/upload (multipart)
    -> [BACKEND_FRAMEWORK] validates (size <= [MAX_SIZE], allowed extension)
    -> Upload to [STORAGE_PROVIDER]
    -> Create [Entity] record in [DATABASE]
    -> [IF_APPLICABLE: Create workflow/approval record]
    -> Return [entity] + [additional_data] response
```

### Allowed File Types
[CUSTOMIZE: list allowed extensions — e.g. PDF, DOCX, XLSX, JPG, PNG]

### File Size Limit
[MAX_FILE_SIZE] maximum per file

---

## [WORKFLOW_AUTOMATION] Integration (if applicable)

### Workflow Status Flow

[CUSTOMIZE: define your workflow states]

```
[INITIAL_STATE]
    │ [ACTION]
    ▼
[STATE_2]
  ┌──┴──┐
[A]   [B]
  │     │
  ▼     ▼
[STATE_3] [STATE_4]
```

### Workflow Steps

| Step | Actor | Actions |
|------|-------|---------|
| 1 | [ACTOR_1] | [ACTIONS_AVAILABLE] |
| 2 | [ACTOR_2] | [ACTIONS_AVAILABLE] |
| N | [ACTOR_N] | [ACTIONS_AVAILABLE] |

---

## Database Schema

### [N] Tables

[CUSTOMIZE: fill in your DB schema diagram]

```
┌────────────┐     ┌──────────────────┐     ┌──────────┐
│ [ENTITY_1] │──┬──│   [ENTITY_2]     │     │[ENTITY_3]│
└────────────┘  │  └──────────────────┘     └──────────┘
                │
┌────────────┐  │  ┌──────────────────┐
│ [ENTITY_4] │──┼──│   [ENTITY_5]     │
└────────────┘  │  └────────┬─────────┘
                │  ┌────────▼─────────┐
                │  │   [ENTITY_6]     │──┐ (self-ref if tree)
                │  └────────┬─────────┘  │
                │           │            │
                │  ┌────────▼─────────┐  │
                ├──│   [ENTITY_7]     │◀─┘
                │  └──────────────────┘
```

### Key Design Patterns

1. **[PK_STRATEGY]** PKs — [INT Auto-increment or UUID]
2. **Soft Delete**: `DeleteFlag [VARCHAR(1) or Boolean]` — active value / deleted value
3. **Audit Columns**: `CreateBy`, `CreateDate`, `UpdateBy`, `UpdateDate` on every table
4. **[ROLE_JOIN]**: Many-to-many via join table (if applicable)
5. **[TREE_STRUCTURE]**: `ParentId` FK to same table (if applicable)
6. **[VERSION_TRACKING]**: `[VersionField]` tracks [STORAGE] version (if applicable)

---

## Frontend Architecture

### Directory Structure

[See `docs/CODING_CONVENTION.md` section 1.2 for full directory structure]

### State Management ([STATE_MANAGER])

[CUSTOMIZE: fill in stores for your project]

| Store | State | Key Actions |
|-------|-------|-------------|
| `useAuthStore` | user, tokens, isAuthenticated | login, logout, refreshToken |
| `use[Feature1]Store` | items, pagination | fetchList, create, update, remove |
| `use[Feature2]Store` | [state] | [actions] |
| `useUiStore` | sidebarCollapsed, locale, theme | toggleSidebar, setLocale |

### Routing

[CUSTOMIZE: fill in your project routes]

| Path | View | Auth | Roles |
|------|------|------|-------|
| `/login` | LoginView | No | — |
| `/` | DashboardView | Yes | all |
| `/[module]` | [Module]ListView | Yes | all |
| `/[module]/:id` | [Module]DetailView | Yes | all |
| `/admin/[module]` | Admin[Module]View | Yes | [admin_role] |

---

## Internationalization (i18n)

- **Default**: [LANG_1] (`[LOCALE_CODE]`)
- **Secondary**: [LANG_2] (`[LOCALE_CODE]`)
- **Rule**: Every user-facing string uses `$t('key')` — NO hardcoded text
- **Structure**: Flat namespace per module

```json
{
  "common": { "save": "[TRANSLATE]", "cancel": "[TRANSLATE]" },
  "auth": { "login": "[TRANSLATE]", "forgotPassword": "[TRANSLATE]" },
  "[module1]": { "[action]": "[TRANSLATE]" },
  "[module2]": { "[action]": "[TRANSLATE]" }
}
```

---

## Security

| Concern | Implementation |
|---------|---------------|
| Auth | JWT with auto-refresh interceptor |
| Role enforcement | FE route guards + BE Guards + @Roles() |
| [SCOPE_ISOLATION] | [SCOPE_QUERY_FILTER] |
| File validation | Extension whitelist + [MAX_SIZE] size limit |
| Input sanitization | [VALIDATION_LIBRARY] DTO validation, ORM (no raw SQL) |
| CORS | Whitelist allowed origins |
| HTTPS | Enforced in production |
| Secrets | [SECRET_MANAGER] |
| Activity logging | All CRUD actions logged to [ACTIVITY_LOG_TABLE] |
| Soft delete | [DeleteFlag] pattern prevents accidental data loss |

---

## Deployment

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ [CDN_SERVICE]│    │ [LB_SERVICE] │    │ [DB_SERVICE] │
│ (SPA assets) │    │              │    │ ([HA_OPTION]) │
└──────┬───────┘    └──────┬───────┘    └──────────────┘
       │                   │
       │            ┌──────▼───────┐
       │            │ [API_RUNTIME]│
       │            │ ([BACKEND])  │
       │            └──────────────┘
       │
┌──────▼───────┐
│[STATIC_HOST] │
│ (SPA assets) │
└──────────────┘
```

- [FRONTEND_FRAMEWORK] SPA built -> [STATIC_HOST] -> [CDN_SERVICE]
- [BACKEND_FRAMEWORK] API -> [BUILD_ARTIFACT] -> [API_RUNTIME]
- [DATABASE] -> [DB_HOST]
- [STORAGE_PROVIDER] -> [STORAGE_SDK]
- [WORKFLOW_AUTOMATION] -> [TRIGGER_MECHANISM] (if applicable)

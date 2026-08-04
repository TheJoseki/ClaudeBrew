# API Design — [PROJECT_NAME]

> Created/updated by `architecture` / `design-function`; verdict by fresh `cbr:reviewer` + user.
> Copy this template to `docs/API_DESIGN.md` and fill in per project.
> **Per-endpoint catalog only.** Cross-cutting patterns (auth, errors, pagination, status codes, RBAC) live in `docs/ARCHITECTURE.md` — do not duplicate here.
> **Backend**: [BACKEND — e.g. NestJS / Django / Rails / FastAPI] · **Auth**: [AUTH_SCHEME — e.g. JWT / session cookie / OAuth2] · **Base URL**: [API_PREFIX — e.g. /api/v1/ / /api/ / none]

---

## Endpoint Catalog

One row per endpoint. `Auth` = required role(s) or `public`. The DTO columns name the request/response shapes — define the ones that need documenting in *Endpoint Detail* below (or point to code). For auth, error, pagination, and status-code conventions, see `docs/ARCHITECTURE.md`.

| Method | Path | Auth | Req DTO | Res DTO | Notes |
|--------|------|------|---------|---------|-------|
| GET | /[module] | [public / role] | — | [EntityListDto] | [e.g. paginated list + search — envelope in ARCHITECTURE.md] |
| POST | /[module] | [role] | [CreateEntityDto] | [EntityDto] | [e.g. 201 on success] |

---

## Endpoint Detail (expand as needed)

Add one block per endpoint that needs a documented contract. Keep it to DTOs and validations — **error and pagination shapes live in `docs/ARCHITECTURE.md`**, do not restate them here.

### [METHOD — e.g. POST] /[path — e.g. /module]
- **Auth**: [public / role]
- **Request DTO** ([DtoName — e.g. CreateEntityDto]):

```json
{ "[FIELD_1]": "[TYPE_OR_EXAMPLE]", "[FIELD_2]": "[TYPE_OR_EXAMPLE]" }
```

- **Response DTO** ([DtoName — e.g. EntityDto]):

```json
{ "[FIELD_1]": "[TYPE_OR_EXAMPLE]" }
```

- **Validations**: [VALIDATIONS — e.g. FIELD_1 required, FIELD_2 max 200 chars, FIELD_3 unique]

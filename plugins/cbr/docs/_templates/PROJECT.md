# PROJECT.md — [PROJECT_NAME]

> Copy file này vào root project và điền vào các placeholder. Agents sẽ đọc file này để detect tech stack.

## Project Context

- **Name**: [PROJECT_NAME]
- **Domain**: [SHORT_DESCRIPTION — e.g. "E-commerce platform for SMBs", "HR management system"]
- **Language**: [Vietnamese | English | Both]

## Tech Stack

- **Backend**: [e.g. NestJS 10.x | Django 5.x | Rails 7.x | Express.js | FastAPI]
- **Frontend**: [e.g. Vue.js 3 + Vuetify 3 | React 18 + shadcn/ui | Next.js 14 | None (API only)]
- **Database**: [e.g. PostgreSQL 16 | MySQL 8 | MongoDB 7 | SQLite]
- **ORM**: [e.g. Prisma 5.x | Drizzle | SQLAlchemy 2.x | ActiveRecord | TypeORM]
- **Auth**: [e.g. JWT access(15min)/refresh(7d) | Session-based | OAuth2 + PKCE | Passport.js]
- **Storage**: [e.g. AWS S3 | Google Cloud Storage | SharePoint | Local filesystem]
- **Deploy**: [e.g. AWS ECS Fargate | Vercel | Railway | Docker Compose | Heroku]
- **Cache**: [e.g. Redis | Memcached | None]
- **Queue**: [e.g. BullMQ | Celery | None]

## Architecture Decisions

- **API prefix**: [e.g. /api/v1/ | /api/ | none]
- **Pagination**: [e.g. 20 items/page, offset-based | cursor-based | infinite scroll]
- **Soft delete**: [Yes — column: [COLUMN_NAME e.g. DeleteFlag VARCHAR(1)] | No — hard delete]
- **Audit columns**: [Yes — [COLUMN_NAMES e.g. CreatedBy, CreatedAt, UpdatedBy, UpdatedAt] | No]
- **PK strategy**: [INT autoincrement | UUID v4 | ULID | Snowflake ID]
- **i18n**: [VI default + EN | EN only | None]
- **Error format**: [e.g. { statusCode, message, error } | { code, message } | RFC 9457]

## Domain Model

[ENTITY_1] → [ENTITY_2] → [ENTITY_3] → ... → [ENTITY_N]

> Example: User → Organization → Project → Task → Comment

## Roles & Permissions

| Role | Permissions |
| --- | --- |
| [ROLE_1] | [e.g. Full CRUD + user management] |
| [ROLE_2] | [e.g. Read + approve/reject in own department] |
| [ROLE_3] | [e.g. Create + submit own items] |

## Key Conventions

- [CONVENTION_1 — e.g. "Soft delete: never hard delete, use DeleteFlag='1'"]
- [CONVENTION_2 — e.g. "All timestamps in UTC, display in Asia/Ho_Chi_Minh"]
- [CONVENTION_3 — e.g. "File upload max 50MB, allowed: PDF, DOCX, XLSX, JPG, PNG"]

## Build Commands

```bash
# Backend test (all):      [e.g. cd backend && npx jest --verbose]
# Backend test (single):   [e.g. cd backend && npx jest --testPathPattern=<module>]
# Frontend test (all):     [e.g. cd frontend && npx vitest run]
# Frontend test (single):  [e.g. cd frontend && npx vitest run <file>]
# Type check:              [e.g. npx tsc --noEmit]
# Dev start (backend):     [e.g. cd backend && npm run start:dev]
# Dev start (frontend):    [e.g. cd frontend && npm run dev]
# Build:                   [e.g. npm run build]
```

## Test Configuration

- **TEST_DB_ENGINE**: [e.g. PostgreSQL 16 | MySQL 8 | MongoDB 7 | SQLite (unit tests only — not for integration)]
- **TEST_DB_URL_ENV**: [env var name — e.g. TEST_DATABASE_URL | DATABASE_TEST_URL]
- **E2E_FRAMEWORK**: [e.g. Playwright | Cypress | None (backend-only project)]
- **E2E_BASE_URL**: [e.g. http://localhost:3000]

> **Why this matters**: `TEST_DB_ENGINE` tells agents which database engine integration tests must use.
> Integration tests running against a lightweight substitute instead of this engine = silent false pass.
> `E2E_FRAMEWORK: None` disables G7b (E2E gate) for backend-only projects.

## Approval/Workflow States (if applicable)

> Delete this section if not applicable

| State | Code | Description |
| --- | --- | --- |
| [STATE_1] | [1] | [e.g. Draft — not yet submitted] |
| [STATE_2] | [2] | [e.g. Submitted — pending review] |
| [STATE_N] | [N] | [...] |

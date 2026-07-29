---
name: design-function
description: System Architect designs ORM schema, API endpoints, and technical spec for any project. Tech stack detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to design API endpoints, ORM schema, or technical architecture for a feature. NOT FOR: writing actual code (use implement-feature).
allowed-tools: Read, Grep, Glob, Write, Edit
argument-hint: "[feature name]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Technical Design

Feature to design:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Do NOT hardcode framework assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect tech stack first |
| Step 1: Design | Always — core design work |
| Step 2: TECH File | Always — mandatory output artifact |
| Checklist | Before marking done |

## Step 1: Read Input (MANDATORY)

- `docs/CODING_RULES.md` — BE rules, naming, domain rules (if exists)
- `docs/CODING_CONVENTION.md` — Module templates, ORM conventions (if exists)
- `docs/ARCHITECTURE.md` — System architecture, patterns (if exists)
- `docs/API_DESIGN.md` — Existing endpoints for reference (if exists)
- Input SRS: `docs/specs/requirements/SRS-[feature].md`
- Input SCREEN: `docs/specs/requirements/SCREEN-[feature].md` (if exists)

## Step 2: Design

1. ORM schema changes (models, relations, indexes) — format per PROJECT.md ORM
2. Backend module structure (files to create)
3. Controller/router endpoints (method, route, guards/middleware, DTOs/validators)
4. Service/handler methods (signature, logic, ORM ops)
5. DTOs / input validators (per PROJECT.md validation library)
6. Error handling scenarios
7. External integrations (storage, messaging, etc.) if needed
8. Performance considerations (N+1, indexes, pagination)

**ORM Schema format** — use convention from PROJECT.md:
- Prisma example: `model [EntityName] { Id Int @id @default(autoincrement()) ... }`
- SQLAlchemy example: `class [EntityName](Base): __tablename__ = "[table]" ...`
- TypeORM example: `@Entity() class [EntityName] { @PrimaryGeneratedColumn() id: number ... }`
- Other ORMs: follow PROJECT.md conventions

**API prefix** — use prefix from PROJECT.md (e.g. `/api/v1/`, `/api/`, etc.)

## Step 3: Create TECH File (MANDATORY — DO NOT SKIP)

File: `docs/specs/detail-design/TECH-[feature-name].md`

> **Template**: See [`references/template.md`](references/template.md) for the full output document template.

## Checklist before Done
- [ ] ORM schema: soft delete, audit cols, PK, FK on delete (per project conventions)
- [ ] Controllers/routes: auth guards + role guards + Swagger/OpenAPI docs
- [ ] DTOs/validators: validation decorators on all fields
- [ ] Services: soft delete filter, audit columns set
- [ ] Pagination for all list endpoints
- [ ] N+1 addressed with eager loading / includes
- [ ] File `docs/specs/detail-design/TECH-[feature].md` CREATED ✅

## Verification

**Skill triggers correctly when:**
- User says: "Design the API endpoints for the product module"
- User says: "Create the ORM schema for the order feature"
- User says: "Write the technical design for user management"

**Skill does NOT trigger for:**
- "Implement the product module" (use implement-feature)
- "Analyze requirements for orders" (use analyze-requirement)
- "Design the UI screens for user management" (use design-screen)

**Expected outputs:**
- Artifact: `docs/specs/detail-design/TECH-[feature].md`
- Quality gate: All endpoints have auth guards, DTOs, and pagination; N+1 addressed

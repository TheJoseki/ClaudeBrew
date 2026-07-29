---
name: implement-feature
description: Full-stack Developer implements a feature for any project. Tech stack detected from PROJECT.md/CLAUDE.md. TRIGGER: technical design already exists (TECH spec), user wants to implement code. NOT FOR: features without existing specs (use full-sdlc), or bug fixes (use fix-bug).
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Skill
argument-hint: "[feature name (optional — reads TECH spec)]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Implement Feature

Feature to implement:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Do NOT hardcode framework assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect tech stack first |
| Step 1: Read Inputs | Always — mandatory before coding |
| Step 2: Backend | When project has backend |
| Step 3: Frontend | When project has frontend |
| Step 4: Self-Check | Always — must pass before work log |
| Step 5: Work Log | Always — mandatory output artifact |

## Precondition Check (MANDATORY — stop if not met)

Required artifacts for this skill:

- [ ] `docs/specs/detail-design/TECH-[feature].md` — Grep/Glob to verify file exists

If TECH spec **NOT FOUND**:
> STOP. Report: "Cannot implement — TECH spec not found at `docs/specs/detail-design/TECH-[feature].md`.
> Run `/design-function` first to create the technical specification."
> Do NOT approximate or infer missing TECH spec content.

---

## Step 1: Read Input Artifacts (MANDATORY)

1. Read TECH spec: `docs/specs/detail-design/TECH-[feature].md` — source of truth
2. Read SCREEN spec: `docs/specs/requirements/SCREEN-[feature].md` (if FE work needed)
3. Read coding standards:
   - `docs/CODING_RULES.md` — golden rules, security, BE/FE rules, naming
   - `docs/CODING_CONVENTION.md` — code templates, import order, patterns

## Step 2: Backend Implementation

**Implementation order (detect from PROJECT.md):**
- NestJS: ORM Schema → Migration → DTOs → Services → Controllers → Module
- Django: Models → Forms/Serializers → Views → URLs → App config
- Rails: Model → Controller → Views → Routes
- Express/Fastify: Schema → Validators → Services → Routes → App registration
- Other: follow PROJECT.md conventions

Key requirements (adapt field names to project conventions):
- Soft delete filter in all queries
- Audit columns on create (created_by/created_at) and update (updated_by/updated_at)
- Auth guards + role guards on all protected endpoints
- Input validation via DTO/schema/serializer for all inputs
- API docs (Swagger/OpenAPI or equivalent) on all endpoints

## Step 3: Frontend Implementation

**Implementation order (detect from PROJECT.md):**
- Vue.js: Types → API Service → Store → Components → Views → Router → i18n
- React: Types → API Service → State (Redux/Zustand/etc.) → Components → Pages → Router
- Next.js: Types → API routes → State → Components → Pages → i18n
- Other: follow PROJECT.md conventions

Key requirements (adapt to project's UI library):
- TypeScript strict — no `any` type
- All user-facing text via i18n — no hardcoded strings
- [UI_LIBRARY] components only (e.g. Vuetify, shadcn/ui, Ant Design, MUI — per PROJECT.md)
- State management per PROJECT.md (Pinia, Redux, Zustand, etc.)

## Step 4: Self-Check (MUST PASS before creating work log)

Run commands from PROJECT.md Build Commands section. Typical examples:

```bash
# Type check
cd backend && npx tsc --noEmit          # NestJS/TypeScript
cd frontend && npx vue-tsc --noEmit     # Vue.js + TypeScript

# Tests
cd backend && npx jest --passWithNoTests
cd frontend && npx vitest run --passWithNoTests

# Lint
cd backend && npx eslint src/ --ext .ts
cd frontend && npx eslint src/ --ext .ts,.vue
```

If errors exist → FIX before continuing.

## Step 5: Create Work Log (MANDATORY — DO NOT SKIP)

> **Next steps after work log**: `/lint-and-validate` → `/review-code` (mandatory quality gate before PR)

Create `docs/work-logs/DEV-[feature]-[YYYYMMDD].md`:

```markdown
# Work Log: [Feature Name]
**Feature ID**: [feature] | **Date**: [YYYY-MM-DD] | **Status**: COMPLETED
**Tech Stack**: [detected from PROJECT.md]

## Files Created
| File | Type | Description |
|------|------|-------------|

## Files Modified
| File | Change Summary |
|------|---------------|

## Schema Migration
- Name/ID: [migration-name or N/A]
- Tables/Collections affected: [list]

## Self-Check Results
- [ ] Backend TS/type check: PASS
- [ ] Backend Tests: PASS
- [ ] Frontend TS/type check: PASS
- [ ] Frontend Tests: PASS
- [ ] Lint: PASS

## Implementation Notes
[Deviations from TECH spec, decisions made]

## Known Gaps / QA Notes
[What unit-test-agent / integration-test-agent should focus on]
```

## Checklist before Done
- [ ] TypeScript strict — no `any`, no `@ts-ignore`
- [ ] Backend: auth guards + role guards on all protected endpoints
- [ ] Backend: input validation (DTO/schema/serializer) for all inputs
- [ ] Backend: API docs (Swagger or equivalent) on all endpoints
- [ ] ORM: soft delete filter in all queries
- [ ] ORM: audit columns set on create and update
- [ ] Frontend: Composition API / hooks pattern per PROJECT.md — no legacy Options API
- [ ] Frontend: All strings via i18n — both locale files updated
- [ ] Self-check: all commands PASS
- [ ] Work log: `docs/work-logs/DEV-[feature]-[date].md` CREATED ✅

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Before this | `design-function` | TECH spec does not exist yet — design first |
| Before this | `design-screen` | SCREEN spec does not exist yet (if frontend work needed) |
| After this | `lint-and-validate` | Always — run type check + lint immediately after implementation |
| After this | `review-code` | Always — mandatory quality gate before creating a PR |
| Parallel | `unit-test` | Mode A — write UTC document at same time as implementation (Phase 4b) |
| Parallel | `integration-test` | Mode A — write ITC document at same time as implementation (Phase 4c) |
| On bug found | `fix-bug` | Self-check (Step 4) reveals a bug during implementation |
| Called from | `full-sdlc` | Phase 4a — invoked automatically by orchestrator |

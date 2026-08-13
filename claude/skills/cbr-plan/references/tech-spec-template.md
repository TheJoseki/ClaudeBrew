# DETAIL_DESIGN Output Template

> Reference for `cbr-plan`'s Tech-Design internal phase. Loaded on-demand when producing the Detail Design (DD / TECH spec) — ORM schema, service methods, DTOs.

## Architecture Patterns

### Backend Module Structure
Follow framework's standard module/layer structure from PROJECT.md. Example:
```
backend/src/modules/<module>/
├── <module>.module.ts
├── <module>.controller.ts
├── <module>.service.ts
├── dto/ (create, update, query DTOs)
├── entities/ (ORM entity)
└── <module>.spec.ts
```

### ORM Conventions
From PROJECT.md: INT auto-increment PKs, soft delete column, audit columns, FK cascade strategy.

### API Conventions
Prefix from PROJECT.md (default `/api/v1/`). Auth guards on all protected routes.
List: `{ data, total, page, pageSize }`. Single: `{ data }`. Pagination default 20/page.

---

## TECH Spec Template

File: `docs/streams/[feature]-[YYYYMMDD]/design/TECH.md`

```markdown
# Technical Design: [Feature Name]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Author**: cbr-plan
**Input SRS**: docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md
**Input Basic Design**: docs/streams/[feature]-[YYYYMMDD]/design/BASIC.md
**Status**: DRAFT

## 1. Data Schema Changes

### 1.1 ER Diagram (Detailed)
[Mermaid erDiagram with full column types, constraints]

### 1.2 ORM Schema Definition
[Full ORM schema using project's ORM syntax]

## 2. Backend Module Structure
[Files to create/modify with full paths]

## 3. Controller Endpoints
| Method | Route | Guard/Role | Request DTO | Response | Description |
|--------|-------|-----------|-------------|----------|-------------|

## 4. Service Methods

### 4.1 Method Signatures
| Method | Signature | Logic Summary | Data Operations |
|--------|-----------|---------------|-----------------|

### 4.2 Service Interaction Flow
[draw.io preferred, Mermaid fallback — sequence diagram]

### 4.3 Business Flow → Implementation Mapping

> Maps each BASIC Business Flow (§6.5) to API call sequence + state transitions. Direct input for `cbr-implement`'s Integration Mode A — each row = 1 test step.

| Flow ID | Source | Reference |
|---------|--------|-----------|
| BF-001 | BASIC.md §6.5 | [Flow Name] |

| Step | BASIC Business Action | API Call(s) | Service Method | DB State Change | Verification Query |
|------|----------------------|-------------|----------------|-----------------|-------------------|
| 1 | Create new account | POST /api/users | userService.create() | INSERT users + INSERT user_roles | GET /api/users?sort=createdAt |
| 2 | Verify in list | GET /api/users | userService.findAll() | — | Response contains new user |
| 3 | Login as created user | POST /api/auth/login | authService.login() | UPDATE users.lastLoginAt | Token payload has correct role |
| 4 | Access dashboard | GET /api/dashboard | dashboardService.getByRole() | — | Only role-permitted data returned |
| 5 | Perform business action | POST /api/[entity] | [entity]Service.create() | INSERT [entity] | GET /api/[entity]/:id returns created |
| 6 | Admin verify result | GET /api/[entity]/:id | [entity]Service.findById() | — | Entity has correct state + audit fields |

**Key**: "Verification Query" column = API call that ITC uses to assert state after each step. This is the key difference from CRUD tests — each step has verification, not just the final step.

## 5. DTOs / Input Schemas
[Full validation schema per DTO]

## 6. Class Diagram
[draw.io preferred, Mermaid fallback — UML class diagram]

## 7. Guards & Decorators
[List guards and custom decorators needed]

## 8. External Integration (if applicable)
## 9. Error Handling
| Scenario | HTTP Status | Error Code | Message |
|----------|------------|------------|---------|

## 10. Performance Considerations
## 11. Frontend Impact
## 12. Migration Notes
```

---

## Constraint Compliance Check

| Check | Rule |
|-------|------|
| Business rules present? | Reference only — definitions in SRS |
| UI layout present? | REMOVE — belongs in SCREEN spec |
| Raw SQL? | Replace with ORM or justify |
| Items not in BASIC? | STOP — retroactive gap, report to the user |

## Quality Rubric (DESIGN checkpoint — ALL ≥ 3)

| Dimension | 3 — Acceptable |
|-----------|----------------|
| Service methods | Params/returns typed |
| ORM schema | Columns/types + constraints |
| API endpoints | Request/response bodies |
| DTO/Serializer | Validation rules per field |
| Test implications | Each method has test note |

## Self-Review Checklist — DETAIL_DESIGN

- [ ] Soft delete, audit columns, PK/FK per PROJECT.md
- [ ] Auth guards + API docs on all endpoints
- [ ] DTOs with complete validation
- [ ] Soft delete filter in all list queries
- [ ] Pagination on all list endpoints
- [ ] Joins/includes for relations (no N+1)
- [ ] Indexes defined
- [ ] Error codes documented
- [ ] Consistent with BASIC spec
- [ ] Diagrams: draw.io preferred, Mermaid fallback
- [ ] CODING-CHECKLIST created (Step D1)
- [ ] TEST_VIEWPOINT updated (Step D2)

---

## Step D1: CODING-CHECKLIST Template

File: `docs/CODING-CHECKLIST.md` — create if missing, update if exists.
[See full template in `cbr-plan/SKILL.md` § Step D1]

## Step D2: TEST_VIEWPOINT Section 0

Update `docs/TEST_VIEWPOINT.md` Section 0 (Test Layer Infrastructure) with actual values from PROJECT.md.
Replace all `[PLACEHOLDER]` with real values. Status: ⏳ PENDING APPROVAL.

## Step D3: E2E Scaffold

If frontend + E2E framework declared → note scaffold files in TECH spec.
If no E2E framework → note "the INTEGRATION E2E sub-criterion is N/A".




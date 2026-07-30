# BASIC_DESIGN Output Template

> Reference for `design-function`. Loaded on-demand when producing the Basic Design (BD書) — module structure, DB table list, API endpoint list.

## Template

File: `docs/specs/basic-design/BASIC-[feature-name].md`

```markdown
# Basic Design: [Feature Name]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Author**: design-function
**Input SRS**: docs/specs/requirements/SRS-[feature].md
**Status**: DRAFT

## 1. System Architecture (システムアーキテクチャ)
[Where this feature fits. Mermaid diagram or draw.io preferred.]

## 2. Module / Subsystem Breakdown
| Module | Files to Create/Modify | Purpose |
|--------|------------------------|---------|

## 3. Database Design

### 3.1 ER Diagram
[Mermaid erDiagram or draw.io]

### 3.2 Table List
| Table Name | Purpose | Key Columns | Relations |
|------------|---------|-------------|-----------|

### 3.3 Index Strategy
| Table | Index On | Reason |
|-------|----------|--------|

### 3.4 Migration Overview
[Schema changes, data migrations needed]

## 4. API Endpoint List
| # | Method | URL | Auth/Role | Description |
|---|--------|-----|-----------|-------------|

## 5. Cross-Module Interaction Flow
[Mermaid sequenceDiagram or draw.io — only if non-trivial cross-module interactions]

## 6. Screen-to-API Mapping
| Screen | User Action | API Called | Notes |
|--------|-------------|------------|-------|

## 6.5 Business Flow Scenarios (ビジネスフローシナリオ)

> Input for ITC generation. Each SRS user journey → 1+ business flow scenario. Described at **business step** level (user actions that change system state), NOT API call level.

### Flow Template:
| Flow ID | Flow Name | SRS Trace | Actors | Type |
|---------|-----------|-----------|--------|------|
| BF-001 | [e.g., Account Creation → First Login → Dashboard Access] | US-01, US-03 | Admin, New User | Multi-actor |

#### BF-001: [Flow Name]
| Step | Actor | Screen | Business Action | State Change | Next Screen |
|------|-------|--------|-----------------|--------------|-------------|
| 1 | Admin | User Management | Create new account with role assignment | User record created (status: ACTIVE), role assigned | User List |
| 2 | Admin | User List | Verify account appears in list | — (verification) | — |
| 3 | New User | Login | Login with created credentials | Session created, lastLoginAt updated | Dashboard |
| 4 | New User | Dashboard | Access role-specific features | — (verification: only permitted menus visible) | — |
| 5 | New User | [Business Screen] | Perform main business action per role | Business entity created/modified | Result Screen |
| 6 | Admin | [Admin Screen] | Verify business action result | — (cross-entity verification) | — |

**Error/Rejection Paths** (per flow):
| Variant | Diverges at Step | Trigger | Expected Outcome |
|---------|-----------------|---------|-----------------|
| BF-001-E1 | Step 3 | Wrong password | Login fails, account locked after N attempts |
| BF-001-E2 | Step 4 | Insufficient permissions | 403, redirect to unauthorized page |

**Flow Types**: CRUD / Approval / Auth / Multi-actor / State Machine / Async

## 7. External Integration Overview
[External services, webhooks, file storage — high level]

## 8. Error Handling Strategy
| Category | HTTP Status Range | Handling Approach |
|----------|------------------|-------------------|

## 9. Non-Functional Considerations
[Performance, security, scalability — high level]

## 10. UI Screen Previews (画面プレビュー)
> From docs/specs/requirements/SCREEN-[feature].md. Default state only.
> Use Pencil MCP `get_screenshot(frameId)` → save to docs/specs/pencil/exports/

| Screen | Name | Preview | Frame ID |
|--------|------|---------|----------|
```

## Self-Review Checklist — BASIC_DESIGN

- [ ] System Architecture diagram reflects actual layers
- [ ] Module breakdown covers all SRS deliverables
- [ ] ER diagram with correct relations
- [ ] All API endpoints from SRS covered
- [ ] Screen-to-API mapping complete
- [ ] No implementation details (no DTOs, no ORM decorators)
- [ ] Section 10 populated if frontend exists
- [ ] File `docs/specs/basic-design/BASIC-[feature].md` CREATED AND WRITTEN

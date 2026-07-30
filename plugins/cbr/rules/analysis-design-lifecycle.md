---
description: Quality criteria for analysis/design deliverables and cross-phase traceability. Always loaded — governs SRS, BASIC, TECH artifact standards.
---

# Analysis & Design Lifecycle Standards

> Quality criteria that ALL analysis/design artifacts MUST meet. Agent execution steps live in agent definitions — this file defines the STANDARDS their output is judged against.

## 1. SRS Quality Criteria (G1 Gate Standard)

An SRS passes G1 only when ALL of these hold:

| Criterion | Minimum Standard |
|-----------|-----------------|
| Background | States WHY (business need), not just WHAT |
| Actors | Every actor has access level + at least 1 user story |
| User Stories | MoSCoW priority + Given/When/Then for every story |
| Acceptance Criteria | Each AC is independently testable — a tester can write a TC from it |
| Business Rules | No contradictions; edge cases documented for each rule |
| Process Flow | At least 1 Mermaid diagram with happy + exception paths |
| Data Requirements | Every field has type, required flag, and validation constraint |
| Scope Boundaries | Explicit IN scope and OUT of scope lists |

**Anti-patterns**: API endpoint paths, ORM fields, UI implementation details — these belong in downstream specs.

## 2. Basic Design Quality Criteria (G3a Gate Standard)

| Criterion | Minimum Standard |
|-----------|-----------------|
| Module Breakdown | Every SRS user story maps to at least one module |
| DB Design | ER diagram + table list with key columns and relations |
| API Endpoint List | Method, URL, auth/role, description for every endpoint |
| Screen-to-API Mapping | Every screen action maps to an API call |
| Business Flow Scenarios | Every SRS user journey has ≥1 business flow (§6.5). Each flow has ≥3 business steps with state changes. Error/rejection paths defined per flow |
| No Implementation Details | Zero DTOs, decorators, ORM syntax, service signatures |
| Consistency with SRS | No new features not in SRS; no SRS features missing |

## 3. Detail Design Quality Criteria (G3b Gate Standard)

| Criterion | Minimum Standard |
|-----------|-----------------|
| ORM Schema | Full column types, constraints, indexes, relations — code-ready |
| Service Methods | Typed params + returns, logic summary, data operations |
| DTOs | Every field with validation rules (type, min/max, required, pattern) |
| Controller Endpoints | Request DTO, response shape, HTTP status codes, guard/role |
| Error Handling | Every error scenario has HTTP status + error code + message |
| Diagrams | Service flow (sequence) + class diagram — Mermaid |
| Business Flow Mapping | Every BASIC business flow (§6.5) mapped to API calls + service methods + DB state changes + verification queries (§4.3) |
| BASIC Consistency | Every endpoint in BASIC is detailed; no new endpoints without BASIC amendment |

## 4. Database Design Standards (All Design Phases)

### Naming Conventions
- Tables: `snake_case` plural (e.g., `user_profiles`) — or follow PROJECT.md if overridden
- Columns: `snake_case` — no abbreviations except `id`, `url`, `dto`
- Foreign keys: `<referenced_table_singular>_id` (e.g., `user_id`)
- Indexes: `idx_<table>_<columns>` (e.g., `idx_users_email`)

### Mandatory Columns (if project convention requires)

| Column | Type | Purpose |
|--------|------|---------|
| `id` | PK (auto-increment or UUID per PROJECT.md) | Primary identifier |
| `created_at` | TIMESTAMP | Audit — row creation time |
| `updated_at` | TIMESTAMP | Audit — last modification |
| `deleted_at` | TIMESTAMP NULL | Soft delete (if project uses it) |
| `created_by` | FK to users (if project requires) | Audit — creator |

### Normalization & Integrity
- Start at 3NF minimum. Denormalize only with measured evidence (document in DECISION-LEDGER)
- Foreign keys MUST have database-level constraints (not just application-level)
- FK columns MUST be indexed
- No CSV-in-column, no EAV pattern, no magic strings for status — use enum or lookup table
- Money/currency: `DECIMAL(p,s)` — never `FLOAT`

### Migration Rules
- Every migration MUST be reversible (up + down)
- Schema changes before data migrations
- Zero-downtime: additive changes first (add column → deploy → backfill → enforce constraint)

## 5. Cross-Phase Traceability Requirements

Every downstream artifact MUST trace back to its source:

```
SRS (US-n, AC-n, BR-n)
  → BASIC (Module → endpoints → tables → business flows §6.5)
    → TECH (Service methods → DTOs → ORM entities → flow impl mapping §4.3)
      → Code (files implement TECH items)
        → Tests (UTCs trace to TECH functions / ITCs trace to BASIC business flows via TECH §4.3)
```

### Traceability Rules
- **SRS → BASIC**: Every user story referenced in at least one module's purpose
- **BASIC → TECH**: Every API endpoint in BASIC has full detail in TECH
- **TECH → Code**: Every service method in TECH has an implementation file
- **TECH → UTC**: Every function in TECH has ≥1 unit test case (Function Coverage Matrix)
- **BASIC → ITC**: Every business flow in BASIC §6.5 has ≥1 integration test chain (ITC traces to BF-xxx)
- **BASIC flow → TECH mapping**: Every BF-xxx in BASIC has implementation mapping in TECH §4.3
- **Gap = STOP**: If a downstream agent finds an upstream gap, it writes a FLAG — never guesses

## 6. Design Decision Evaluation

When multiple valid approaches exist for any design decision, use the DAR protocol defined in `dar-evaluation-protocol.md`. Quick DAR for medium-impact choices; Full DAR for architecture-impacting or irreversible decisions.

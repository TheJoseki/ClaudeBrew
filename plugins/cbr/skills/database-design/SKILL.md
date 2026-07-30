---
name: database-design
description: "Database design principles and decision framework, asking the user for preferences before making technology choices. TRIGGER: choosing a database type, designing schemas/indexes, optimizing queries, planning migrations, or reviewing data models. NOT FOR: the per-feature endpoint/ORM tech-spec artifact (use design-function), API style or contract design (use api-patterns), or system structure (use architecture)."
allowed-tools: Read, Grep
metadata:
  version: "3.1"
  category: design
---

# Database Design

$ARGUMENTS

---

## Core Principles

1. **Ask before choosing** — database type and ORM are project decisions. Confirm with the user.
2. **Design for reads** — most applications read far more than they write.
3. **Normalize first, denormalize with evidence** — denormalize only when measured.
4. **Data integrity at database level** — constraints, FKs, and NOT NULL belong in the schema.
5. **Soft delete by convention** — if the project uses it, every deletable entity needs the flag.

---

## Context Questions (Ask or Check PROJECT.md)

1. Database type: Relational or Document?
2. ORM: Which one does the project use?
3. Naming convention: `snake_case` or `camelCase`?
4. Soft delete: Column name/type?
5. Audit columns: `created_by`, `updated_at` required?
6. Scale expectation: Thousands, millions, or more?

---

## Schema Design Guidelines

| Data Type | Use for | Avoid |
| --------- | ------- | ----- |
| `VARCHAR(n)` | Bounded text | Unbounded text |
| `TEXT` | Long-form content | Short codes |
| `BOOLEAN` | True/false flags | `VARCHAR('Y'/'N')` |
| `TIMESTAMP` | Audit columns, events | `VARCHAR` for dates |
| `DECIMAL(p,s)` | Money, percentages | `FLOAT` for money |
| `UUID` / `BIGINT` | Primary keys | Composite PKs unless join table |

---

## Indexing

**Always index:** PK (auto), FK columns, frequent WHERE/ORDER BY columns.

**Index deliberately:** Composite (most selective column first), partial, unique.

**Don't over-index:** Low-cardinality columns alone, "just in case" indexes.

---

## Anti-Patterns

| Anti-Pattern | Fix |
| ------------ | --- |
| EAV pattern | Proper columns or JSONB with schema |
| CSV in a column | Normalize into child table |
| Magic strings for status | Enum type or lookup table |
| Missing audit columns | Add created/updated timestamps |
| No soft delete filter | Apply filter in all ORM queries |
| FK without index | Add index on FK column |

---

## Optional: Decision Log

If significant schema decisions were made this session, write a record to:
`docs/specs/decisions/ADR-database-design-[YYYYMMDD].md`

```markdown
## Database Design Decisions — [YYYYMMDD]

**Scope**: [table/schema/migration analyzed]
**Decisions made**: [DB type, ORM, indexing strategy, normalization choices, etc.]
**Alternatives rejected**: [what was considered and why it was not chosen]
**Deferred**: [design decisions NOT made + reason]
**Re-check**: [trigger — e.g., "when adding reporting queries", "if row count exceeds 1M"]
```

This record enables architect-agent to stay consistent with prior data design choices.

---

## Checklist

- [ ] Database type and ORM confirmed
- [ ] All tables have clear primary key
- [ ] Audit columns present (if convention requires)
- [ ] Soft delete column present (if convention requires)
- [ ] FK columns indexed
- [ ] No magic strings for status/type fields
- [ ] Pagination strategy decided for list queries

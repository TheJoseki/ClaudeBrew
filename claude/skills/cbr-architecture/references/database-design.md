# Database Design

Data-layer decisions: database type, schema shape, indexing, and the migration
path. Read the sections the current request touches — not the whole file.

**Related sub-areas:** system structure and the ADR format live in `SKILL.md`;
the contract exposing this data lives in `api-design.md`.

---

## Principles

1. **Ask before choosing** — database type and ORM are project decisions. Confirm
   with the user.
2. **Design for reads** — most applications read far more than they write.
3. **Normalize first, denormalize with evidence** — denormalize only when
   measured.
4. **Data integrity at database level** — constraints, FKs, and NOT NULL belong
   in the schema.
5. **Soft delete by convention** — if the project uses it, every deletable entity
   needs the flag.

---

## Context questions

Ask, or check `PROJECT.md`, before designing anything:

1. Database type: Relational or Document?
2. ORM: Which one does the project use?
3. Naming convention: `snake_case` or `camelCase`?
4. Soft delete: Column name/type?
5. Audit columns: `created_by`, `updated_at` required?
6. Scale expectation: Thousands, millions, or more?

---

## Schema design

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

> A cursor- or keyset-paginated endpoint needs a sortable, indexed key — decide
> the index and the pagination model together. See `api-design.md`
> § Response format and pagination.

---

## Anti-patterns

| Anti-Pattern | Fix |
| ------------ | --- |
| EAV pattern | Proper columns or JSONB with schema |
| CSV in a column | Normalize into child table |
| Magic strings for status | Enum type or lookup table |
| Missing audit columns | Add created/updated timestamps |
| No soft delete filter | Apply filter in all ORM queries |
| FK without index | Add index on FK column |

---

## Checklist

- [ ] Database type and ORM confirmed
- [ ] All tables have clear primary key
- [ ] Audit columns present (if convention requires)
- [ ] Soft delete column present (if convention requires)
- [ ] FK columns indexed
- [ ] No magic strings for status/type fields
- [ ] Pagination strategy decided for list queries
- [ ] ADR written for non-obvious schema choices (format in `SKILL.md`)

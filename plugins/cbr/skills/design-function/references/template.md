# TECH File Output Document Template

Use this template when creating `docs/streams/[feature]-[YYYYMMDD]/design/TECH.md`.

```markdown
# Technical Design: [Feature Name]
**Feature ID**: [feature] | **Date**: [YYYY-MM-DD] | **Author**: design-function
**Input SRS**: docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md
**Tech Stack**: [detected from PROJECT.md]

## 1. ORM Schema Changes
[Schema in format matching PROJECT.md ORM — see Step 2 note above]
Include soft delete field, audit columns, and PK per project conventions.

## 2. Module Structure (files to create)
## 3. Controller Endpoints
| Method | Route | Guard/Role | DTO/Validator | Response |
|--------|-------|-----------|--------------|----------|

## 4. Service Methods
| Method | Signature | Logic | ORM Ops |
|--------|-----------|-------|---------|

## 5. DTOs / Input Validators (with validation decorators)
## 6. Error Handling
| Scenario | HTTP | Message |
|----------|------|---------|

## 7. Performance
- N+1 prevention: [list eager loads / includes]
- Indexes: [list]

## 8. Frontend Impact
| Component/Store | Change |
|----------------|--------|
```

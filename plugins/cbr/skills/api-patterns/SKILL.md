---
name: api-patterns
description: API design principles and decision-making framework. Covers REST vs GraphQL vs tRPC selection, response formats, versioning, pagination, authentication, rate limiting, and security testing. Use when designing APIs, choosing API style, or reviewing API endpoints.
allowed-tools: Read, Write, Edit, Grep, Glob
metadata:
  version: "3.1"
  category: design
---

# API Patterns

$ARGUMENTS

---

## Selective Reading Rule

Read ONLY the files relevant to the current task. Check the content map below.

---

## Content Map

| File | Description | When to Read |
| ---- | ----------- | ------------ |
| [api-style.md](api-style.md) | REST vs GraphQL vs tRPC decision tree | Choosing API type |
| [rest.md](rest.md) | Resource naming, HTTP methods, status codes | Designing REST API |
| [response.md](response.md) | Envelope pattern, error format, pagination | Response structure |
| [graphql.md](graphql.md) | Schema design, when to use, security | Considering GraphQL |
| [trpc.md](trpc.md) | TypeScript monorepo, type safety | TS fullstack projects |
| [versioning.md](versioning.md) | URI/Header/Query versioning | API evolution |
| [auth.md](auth.md) | JWT, OAuth, Passkey, API Keys | Auth pattern selection |
| [rate-limiting.md](rate-limiting.md) | Token bucket, sliding window | API protection |
| [documentation.md](documentation.md) | OpenAPI/Swagger best practices | API documentation |
| [security-testing.md](security-testing.md) | OWASP API Top 10, auth/authz testing | Security review |

---

## Related Skills

| Skill | Use For |
| ----- | ------- |
| `database-design` | Database schema backing the API |
| `architecture` | System-level design decisions |
| `vulnerability-scanner` | Security audit of API endpoints |

---

## Decision Checklist

Before designing an API, answer:

1. Who are the consumers? (browser, mobile, server, third-party)
2. REST, GraphQL, or tRPC? (read `api-style.md`)
3. What authentication model? (read `auth.md`)
4. Versioning strategy needed? (read `versioning.md`)
5. What is the expected request volume?
6. What pagination model? (offset, cursor, keyset)
7. How will errors be structured?
8. Is rate limiting needed?

---

## Optional: Decision Log

If significant design decisions were made this session, write a record to:
`docs/decisions/api-patterns-[YYYYMMDD].md`

```markdown
## API Design Decisions — [YYYYMMDD]

**Scope**: [endpoint group / API module analyzed]
**Decisions made**: [API style chosen, auth pattern, versioning approach, etc.]
**Alternatives rejected**: [what was considered and why it was not chosen]
**Deferred**: [decisions NOT made + reason]
**Re-check**: [trigger for revisiting — e.g., "when adding external partner API"]
```

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Use verbs in URLs (`/getUsers`) | Use nouns (`/users`) |
| Return 200 for errors | Use proper HTTP status codes |
| Ignore pagination | Always paginate list endpoints |
| Mix naming conventions | Consistent casing throughout |
| Expose internal IDs unnecessarily | Use public-facing identifiers |
| Skip input validation | Validate at API boundary |

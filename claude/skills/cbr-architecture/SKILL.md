---
name: cbr-architecture
description: "Design-decision framework covering system structure, API contracts, and data models. Tech stack detected from PROJECT.md/CLAUDE.md. TRIGGER: choosing module boundaries or system structure; picking an API style (REST/GraphQL/tRPC) or reviewing endpoint conventions — versioning, pagination, response format, auth, rate limiting, API security; choosing a database type, designing schemas/indexes, planning migrations, or optimizing queries; weighing a hard-to-reverse structural trade-off or writing an ADR. NOT FOR: producing a feature's endpoint/ORM tech-spec artifact (use design-function)."
allowed-tools: Read, Write, Edit, Grep, Glob
metadata:
  version: "3.1"
  category: design
---

# Architecture

$ARGUMENTS

---

## Core Principles

1. **Simplest thing that satisfies the requirement.** Complexity must be justified
   by a concrete, present need — not a hypothetical future one.
2. **Ask before choosing.** Database type, ORM, and API style are project-level
   decisions with long half-lives. Confirm with the user or `PROJECT.md`; never
   silently pick a default.
3. **Decide once, record why.** Anything hard to reverse gets an ADR, so the next
   session inherits the reasoning instead of re-deriving it.

---

## The three sub-areas

This skill covers structural decisions at three layers. Identify which one the
request touches, then read only that detail file.

| Sub-area | Covers | Detail |
| -------- | ------ | ------ |
| **System structure** | Module boundaries, cross-cutting concerns, service split, async workflows, dependency cost | This file (below) |
| **API contracts** | Style selection (REST/GraphQL/tRPC), resource naming, status codes, response envelope, pagination, versioning, auth, rate limiting, docs, security testing | [`references/api-design.md`](references/api-design.md) |
| **Data models** | Database type, schema and column types, indexing, normalization, migrations, query shape | [`references/database-design.md`](references/database-design.md) |

Read selectively — pull in a detail file only when the request lands in that
sub-area. A request often spans two (e.g. "paginated orders endpoint" is API
contract + indexing); read both, and keep the decisions consistent.

**Entry points into the detail files:**

| Question | Go to |
| -------- | ----- |
| REST, GraphQL, or tRPC? | [api-design.md § Choosing an API style](references/api-design.md#choosing-an-api-style) |
| How should responses, errors, and pages be shaped? | [api-design.md § Response format and pagination](references/api-design.md#response-format-and-pagination) |
| How do we version / authenticate / rate-limit this API? | [api-design.md § Versioning](references/api-design.md#versioning), [§ Authentication](references/api-design.md#authentication), [§ Rate limiting](references/api-design.md#rate-limiting) |
| Is this endpoint set safe? | [api-design.md § API security testing](references/api-design.md#api-security-testing) |
| Relational or document? Which ORM? | [database-design.md § Context questions](references/database-design.md#context-questions) |
| What column types, keys, and indexes? | [database-design.md § Schema design](references/database-design.md#schema-design), [§ Indexing](references/database-design.md#indexing) |

---

## Reference Files (Read Before Deciding)

| File | Purpose |
| ---- | ------- |
| `docs/ARCHITECTURE.md` | System patterns, auth flow, module structure |
| `docs/API_DESIGN.md` | REST API conventions, endpoint patterns |
| `docs/CODING_RULES.md` | Non-negotiable rules this architecture must satisfy |
| `PROJECT.md` | Tech stack constraints, existing framework choices |

---

## Decision Framework

### Step 1: Understand the constraints

1. What is the scale? (single user, team, enterprise)
2. What are the consistency requirements?
3. What are the team's existing skills?
4. What does the tech stack already provide?

### Step 2: Apply the decision tree

```
New structural requirement
  Does existing architecture handle it?  → Extend, don't introduce new pattern
  Is this a cross-cutting concern?       → Middleware / decorator / interceptor
  Is this shared state across services?  → Evaluate event-driven or shared store
  Is this a new bounded domain?          → New module with its own service layer
  Does this require a new dependency?    → Evaluate cost vs. benefit explicitly
  Does this expose a new contract?       → references/api-design.md
  Does this add or reshape stored data?  → references/database-design.md
```

### Step 3: Document the decision (ADR)

Write hard-to-reverse decisions to an ADR whose location follows the decision's
scope:

- **Belongs to one feature's work-stream** →
  `docs/streams/[feature]-[YYYYMMDD]/design/decisions/ADR-[topic]-[YYYYMMDD].md`
- **Spans multiple streams (project-wide)** →
  `docs/decisions/ADR-[topic]-[YYYYMMDD].md`

`[topic]` is a short kebab-case slug for the subject decided (e.g.
`ADR-background-jobs-20260731.md`), not the name of this skill.

```markdown
## ADR: [Short Title]
**Date**: YYYY-MM-DD | **Status**: Proposed / Accepted / Deprecated

### Scope
[System / module / API surface / schema analyzed]

### Context
[What problem requires this decision?]

### Decision
[What was chosen?]

### Alternatives Considered
| Option | Pros | Cons |

### Consequences
[What becomes easier? What becomes harder?]

### Deferred
[Decisions NOT made + reason]

### Re-check
[Trigger for revisiting — e.g., "when adding a second service",
"if row count exceeds 1M", "when adding an external partner API"]
```

The ADR is the handoff: a later stage (or a later session) reads this file rather
than re-deriving the trade-off. Skip it for choices that are cheap to reverse —
say so and move on.

---

## Patterns by Concern

| Concern | Prefer | Avoid |
| ------- | ------ | ----- |
| Module structure | Feature-first | Layer-first for large apps |
| Cross-cutting | Middleware / guards | Duplicating logic per handler |
| Async workflows | Queue + worker | Inline blocking calls |
| Data access | ORM with filters | Raw SQL without filters |
| API contracts | Versioned endpoints | Breaking changes in-place |
| Config | Environment variables | Hardcoded values |

---

## Validation Checklist

- [ ] Matches tech stack in PROJECT.md
- [ ] Simplest solution being used
- [ ] Respects existing module boundaries
- [ ] Auth/authorization at the correct layer
- [ ] Test strategy exists for this component
- [ ] API contract decisions checked against `references/api-design.md`
- [ ] Data model decisions checked against `references/database-design.md`
- [ ] ADR written for non-obvious choices

---

## Related Skills

| Skill | When to use alongside |
| ----- | --------------------- |
| `design-function` | Translating these decisions into a feature's endpoint/ORM tech spec |
| `vulnerability-scanner` | Security audit of the implemented endpoints |
| `review-code` | Verifying implementation matches intent |

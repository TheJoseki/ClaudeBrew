---
name: architecture
description: "Architecture decision framework for any software project. Trigger when designing system structure, choosing patterns, evaluating trade-offs, or writing ADRs. Tech stack detected from PROJECT.md/CLAUDE.md."
allowed-tools: Read, Grep
metadata:
  version: "3.1"
  category: design
---

# Architecture

$ARGUMENTS

---

## Core Principle

Prefer the simplest architecture that satisfies current requirements. Complexity must be justified by a concrete, present need — not a hypothetical future one.

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
```

### Step 3: Document the decision (ADR format)

```markdown
## ADR: [Short Title]
**Date**: YYYY-MM-DD | **Status**: Proposed / Accepted / Deprecated

### Context
[What problem requires this decision?]

### Decision
[What was chosen?]

### Alternatives Considered
| Option | Pros | Cons |

### Consequences
[What becomes easier? What becomes harder?]
```

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
- [ ] ADR written for non-obvious choices

---

## Optional: Decision Log

If significant architecture decisions were made this session, write an ADR to:
`docs/specs/decisions/ADR-architecture-[YYYYMMDD].md`

```markdown
## Architecture Decision — [YYYYMMDD]

**Scope**: [system / module / layer analyzed]
**Decision made**: [what architecture choice was made]
**Rationale**: [why this over alternatives]
**Trade-offs accepted**: [what becomes harder with this choice]
**Deferred**: [decisions NOT made + reason]
**Re-check**: [trigger — e.g., "when adding second service", "when team grows past 5"]
```

This record enables future orchestrators to understand prior decisions without re-deriving them.

---

## Related Skills

| Skill | When to use alongside |
| ----- | --------------------- |
| `design-function` | Translating architecture into API + service design |
| `database-design` | Data layer decisions |
| `api-patterns` | API style and endpoint design |
| `review-code` | Verifying implementation matches intent |

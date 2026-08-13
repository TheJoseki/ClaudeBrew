# Code Review Checklist — Two-Pass Methodology

> Run by `cbr-verify` and the fresh `cbr-reviewer` gate agent (two-pass methodology).

## Pass 1: CRITICAL (must fix before merge)

### SQL & Data Safety
- [ ] All queries use ORM or parameterized statements (no string interpolation)
- [ ] No TOCTOU race conditions (check-then-act without proper locking)
- [ ] No N+1 query patterns inside loops
- [ ] Bulk operations use transactions where atomicity is needed

### Race Conditions & Concurrency
- [ ] Shared mutable state protected by lock/mutex/atomic operations
- [ ] No XSS vectors (user input rendered without sanitization)
- [ ] Async operations have proper error handling (no swallowed promises)

### Auth & Trust Boundary
- [ ] Auth guard on every new protected endpoint/route
- [ ] LLM or external API output validated/sanitized before database writes
- [ ] No secrets, API keys, or tokens in code, logs, or error messages
- [ ] CSRF protection on mutating endpoints

### Enum & Value Completeness
- [ ] New enum/union values handled in ALL consumers (trace through entire codebase)
- [ ] Switch/match statements have exhaustive cases or explicit default handling

## Pass 2: INFORMATIONAL (fix or acknowledge)

- [ ] No dead code or commented-out blocks
- [ ] No magic numbers or string literals — use named constants
- [ ] Test coverage exists for new code paths (unit + integration)
- [ ] No type coercion at module boundaries (explicit parsing/validation)
- [ ] Error handling uses specific catch, not generic catch-all
- [ ] Function/method length reasonable (≤50 lines preferred)
- [ ] Naming is self-documenting (no abbreviations, no single-letter vars except loops)

## Fix-First Heuristic

After completing the review, classify each finding:

| Classification | Action | Examples |
|---------------|--------|---------|
| **AUTO-FIX** | Agent fixes directly using Edit tool, then reports | Unused imports, formatting, missing semicolons, obvious null checks |
| **ASK** | Batch ALL items into 1 AskUserQuestion | Design decisions, security trade-offs, architectural changes, ambiguous intent |

**Report format for AUTO-FIX**: `[AUTO-FIXED] file:line — Problem → Fix applied`

**Order**: Complete all AUTO-FIX items first (show summary), then present ASK batch (single question using 4-part format).

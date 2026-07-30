---
name: testing-patterns
description: "Testing patterns and strategies for any project, covering the testing pyramid, AAA, mocking, test data, and anti-patterns. TRIGGER: choosing test types, structuring test suites, or reviewing test quality and strategy. NOT FOR: writing the unit tests for a specific module (use unit-test), integration tests (use integration-test), or executing a suite (use run-tests)."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: quality
---

# Testing Patterns

$ARGUMENTS

---

## Testing Pyramid

```
      [ E2E ]         Few, slow — critical user journeys
    [Integration]     Some — module boundaries and contracts
  [  Unit Tests  ]    Many, fast — isolated business logic
```

If you have more E2E tests than unit tests, the pyramid is inverted.

---

## Test Type Selection

| Type | Covers | When |
| ---- | ------ | ---- |
| Unit | Single function/class | Business logic, validators, state transitions |
| Integration | Two+ real components | ORM queries, API handler + service |
| E2E | Full request flow | Critical paths, auth flow, payment |
| Contract | API shape | When downstream consumers depend on your API |

Default: unit for logic, integration for data access, one E2E per critical path.

---

## Mocking Principles

1. **Mock at the boundary** — external services, databases, third-party APIs
2. **Prefer fakes over mocks** — in-memory implementations are more reliable
3. **Don't mock what you don't own** — wrap third-party libs in a thin adapter
4. **Verify behavior, not calls** — assert on output, not on internal method calls

---

## Test Organization

**Naming:** `[unit] [scenario] [expected outcome]`

```
getUserById: when user not found: throws NotFoundException
calculateTax: when rate is zero: returns original amount
```

**Grouping:** `describe` → `describe('when...')` → `it('...')`

---

## Test Data Strategies

| Strategy | Use when |
| -------- | -------- |
| Inline literals | Test needs specific values |
| Builder/factory | Many tests need object variations |
| Fixtures | Complex nested objects, API responses |
| Seeded database | Integration tests with real ORM |

Each test must set up its own state. No shared mutable state.

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Test implementation details | Test inputs/outputs |
| Share mutable state between tests | Reset in `beforeEach` |
| Assert too many things | One logical assertion |
| Only happy path | Add error/invalid input tests |
| Over-mock | Integration-test real wiring |
| Skip flaky tests permanently | Fix or delete |

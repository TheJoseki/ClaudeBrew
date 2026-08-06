---
name: cbr-testing-strategy
description: "Testing strategy and patterns for any project — the testing pyramid, test-type selection, mocking boundaries, test organization and naming, test-data strategies, anti-patterns, and the test-first RED-GREEN-REFACTOR cycle with the Three Laws of TDD and the AAA pattern. TRIGGER: deciding what mix of unit, integration, and E2E tests to write, structuring or reviewing a test suite's quality, choosing what to test first, or running a tests-first TDD loop for new functionality. NOT FOR: writing the actual test cases for a specific module (use unit-test), integration tests (use integration-test), or executing an existing suite (use validate-and-test)."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: quality
---

# Testing Strategy

$ARGUMENTS

You decide **what** to test and **when** to write it. The concrete test cases are
authored by `unit-test` / `integration-test`, and the suite is executed by
`validate-and-test` — this skill supplies the strategy those stages follow.

## Content Map

| Section | When to read |
| --- | --- |
| Part 1: Test Strategy | Choosing test types, mocking, organization, test data |
| Part 2: TDD | Writing tests before the code exists |
| Anti-Patterns | Reviewing an existing suite, or before calling tests done |

---

## Part 1: Test Strategy

### Testing pyramid

```
      [ E2E ]         Few, slow — critical user journeys
    [Integration]     Some — module boundaries and contracts
  [  Unit Tests  ]    Many, fast — isolated business logic
```

If you have more E2E tests than unit tests, the pyramid is inverted.

### Test type selection

| Type | Covers | When |
| ---- | ------ | ---- |
| Unit | Single function/class | Business logic, validators, state transitions |
| Integration | Two+ real components | ORM queries, API handler + service |
| E2E | Full request flow | Critical paths, auth flow, payment |
| Contract | API shape | When downstream consumers depend on your API |

Default: unit for logic, integration for data access, one E2E per critical path.

### Mocking principles

1. **Mock at the boundary** — external services, databases, third-party APIs
2. **Prefer fakes over mocks** — in-memory implementations are more reliable
3. **Don't mock what you don't own** — wrap third-party libs in a thin adapter
4. **Verify behavior, not calls** — assert on output, not on internal method calls

### Test organization

**Naming:** `[unit] [scenario] [expected outcome]`

```
getUserById: when user not found: throws NotFoundException
calculateTax: when rate is zero: returns original amount
```

**Grouping:** `describe` → `describe('when...')` → `it('...')`

### Test data strategies

| Strategy | Use when |
| -------- | -------- |
| Inline literals | Test needs specific values |
| Builder/factory | Many tests need object variations |
| Fixtures | Complex nested objects, API responses |
| Seeded database | Integration tests with real ORM |

Each test must set up its own state. No shared mutable state.

---

## Part 2: TDD (test-first)

### Three Laws of TDD

1. Write no production code unless it makes a failing test pass.
2. Write only enough of a test to make it fail.
3. Write only enough production code to make the currently failing test pass.

### RED-GREEN-REFACTOR cycle

```
RED      → Write a test that fails for the right reason
GREEN    → Write minimum code to make it pass
REFACTOR → Clean up code and tests while keeping green
Repeat
```

### AAA pattern (Arrange-Act-Assert)

```
// Arrange — set up inputs, dependencies, state
// Act     — execute the single behavior under test
// Assert  — verify one outcome
```

Rules:

- One Act per test
- One logical assertion per test
- Repeated Arrange belongs in `beforeEach` or a builder

### When TDD pays off

| Scenario | TDD value |
| -------- | --------- |
| New business logic | High |
| Bug fix (reproduce first) | High |
| API endpoint (contract-first) | High |
| Exploring unfamiliar API | Low (spike first, then TDD) |
| Pure configuration/wiring | Low |

### Test prioritization

1. Core business logic (calculations, rules, state machines)
2. API contract (request/response, status codes, errors)
3. Integration boundaries (ORM queries, external services)
4. Edge cases (null, empty, boundary values)

### TDD across the pipeline stages

| Stage | Responsibility |
| ----- | -------------- |
| `unit-test` (Mode A) | Writes the UTC document (RED specification) |
| `implement-feature` | Implements production code (GREEN) |
| `unit-test` (Mode B) | Executes tests via `cbr-tester`, reports failures |
| `fix-bug` | Fixes failures |

### Optional: decision log

If TDD was applied to a significant new module or a problematic area this
session, record it in the active feature's stream at
`docs/streams/[feature]-*/design/decisions/ADR-tdd-<slug>-[YYYYMMDD].md`:

```markdown
## TDD Session — [YYYYMMDD]

**Scope**: [module/service/function where TDD was applied]
**RED tests written**: [count and brief description]
**GREEN implementations**: [what was implemented to pass tests]
**REFACTOR changes**: [clean-up applied after GREEN]
**Deferred**: [tests or refactors NOT done + reason]
**Re-check**: [when to revisit — e.g. before adding new business rules to OrderService]
```

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Write tests after the code | Write the test first |
| Write tests that always pass | Confirm RED for the right reason before writing code |
| Test implementation details | Test inputs and outputs |
| One massive test asserting many things | One behavior, one logical assertion per test |
| Only cover the happy path | Add error and invalid-input cases |
| Mock everything | Mock at the boundary only; integration-test the real wiring |
| Share mutable state between tests | Each test sets up its own state; reset in `beforeEach` |
| Skip the REFACTOR step | Always clean up after GREEN |
| Skip flaky tests permanently | Fix or delete them |

## Verification

**Skill triggers correctly when:**

- User says: "What mix of unit, integration, and E2E tests should this service have?"
- User says: "Our tests are brittle and slow — review the strategy"
- User says: "Let's build this test-first with TDD"

**Skill does NOT trigger for:**

- "Write the unit tests for applyDiscount" (use `unit-test`)
- "Write integration tests for the order API" (use `integration-test`)
- "Run the test suite" (use `validate-and-test`)

**Expected outputs:**

- A recommended test mix and structure, with the reasoning behind it
- For TDD work: a RED-GREEN-REFACTOR loop, optionally an ADR decision log

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Feeds | `unit-test` | Strategy and TDD cycle the UTC document follows |
| Feeds | `integration-test` | Which boundaries warrant an integration test |
| Then | `validate-and-test` | Execute the suite once the tests exist |
| On FAIL | `fix-bug` | A failing test has a clear root cause |
| Related | `review-code` | Reviewing test quality alongside code quality |

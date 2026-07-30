---
name: tdd-workflow
description: "Test-Driven Development workflow with RED-GREEN-REFACTOR cycle. Trigger when writing new functionality with tests first, practicing TDD, or establishing test-first development. Includes Three Laws, AAA pattern, and multi-agent TDD."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: quality
---

# TDD Workflow

$ARGUMENTS

---

## Three Laws of TDD

1. Write no production code unless it makes a failing test pass.
2. Write only enough of a test to make it fail.
3. Write only enough production code to make the currently failing test pass.

---

## RED-GREEN-REFACTOR Cycle

```
RED      → Write a test that fails for the right reason
GREEN    → Write minimum code to make it pass
REFACTOR → Clean up code and tests while keeping green
Repeat
```

---

## AAA Pattern (Arrange-Act-Assert)

```
// Arrange — set up inputs, dependencies, state
// Act     — execute the single behavior under test
// Assert  — verify one outcome
```

Rules:
- One Act per test
- One logical assertion per test
- Repeated Arrange belongs in `beforeEach` or a builder

---

## When to Use TDD

| Scenario | TDD Value |
| -------- | --------- |
| New business logic | High |
| Bug fix (reproduce first) | High |
| API endpoint (contract-first) | High |
| Exploring unfamiliar API | Low (spike first, then TDD) |
| Pure configuration/wiring | Low |

---

## Test Prioritization

1. Core business logic (calculations, rules, state machines)
2. API contract (request/response, status codes, errors)
3. Integration boundaries (ORM queries, external services)
4. Edge cases (null, empty, boundary values)

---

## Multi-Agent TDD Pattern

| Agent | Responsibility |
| ----- | -------------- |
| `unit-test-agent` (Mode A) | Writes UTC document (RED specification) |
| `developer-agent` | Implements production code (GREEN) |
| `unit-test-agent` (Mode B) | Executes tests, reports failures |
| `bug-fix-agent` | Fixes failures |

---

## Optional: Decision Log

If TDD was applied to a significant new module or a problematic area this session, write a record to:
`docs/decisions/tdd-workflow-[YYYYMMDD].md`

```markdown
## TDD Session — [YYYYMMDD]

**Scope**: [module/service/function where TDD was applied]
**RED tests written**: [count and brief description]
**GREEN implementations**: [what was implemented to pass tests]
**REFACTOR changes**: [clean-up applied after GREEN]
**Deferred**: [tests or refactors NOT done + reason]
**Re-check**: [when to revisit — e.g., "before adding new business rules to OrderService"]
```

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Write tests after code | Write test first |
| Test implementation details | Test inputs and outputs |
| One massive test | One behavior per test |
| Mock everything | Mock at the boundary only |
| Skip REFACTOR step | Always clean up after GREEN |
| Write tests that always pass | Confirm RED before writing code |

---
name: run-tests
description: "Runs test suite for any project. Backend and frontend test commands detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to run the test suite, check test results, verify all tests pass. NOT FOR: writing test cases (use unit-test/integration-test)."
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[feature or module name (optional)]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Run Tests

$ARGUMENTS

## Live Project Context (auto-injected)

- Working dir: !`pwd`
- Package files detected: !`ls package.json pyproject.toml Gemfile Cargo.toml go.mod 2>/dev/null | tr '\n' ' ' || echo "(none found)"`
- Existing test config: !`ls jest.config* vitest.config* pytest.ini setup.cfg .rspec 2>/dev/null | tr '\n' ' ' || echo "(none found)"`

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack and test commands before running anything.
Do NOT hardcode test framework commands — use commands from PROJECT.md Build Commands section.

## Commands

Use commands from PROJECT.md Build Commands section. Typical examples by framework:

```bash
# Backend — full suite with coverage
cd backend && [backend test command] --coverage --verbose
# e.g. NestJS/Jest: npx jest --coverage --verbose
# e.g. Django/Pytest: pytest --cov --verbose
# e.g. Rails/RSpec: bundle exec rspec --format documentation

# Backend — specific module
cd backend && [backend test command] --testPathPattern="[module]" --verbose

# Backend — E2E / integration
cd backend && [backend E2E test command] --verbose

# Frontend — full suite with coverage
cd frontend && [frontend test command] --coverage --reporter=verbose
# e.g. Vitest: npx vitest run --coverage --reporter=verbose
# e.g. Jest: npx jest --coverage --verbose

# Frontend — specific file
cd frontend && [frontend test command] [path-to-file]

# Type check (run before tests)
cd backend && [backend type check command]
cd frontend && [frontend type check command]
```

## After Running: Create Quick Report

If called by another skill or a pool agent, output results in this format:

```markdown
## Test Run Result — [YYYY-MM-DD HH:MM]
**Scope**: [Backend / Frontend / Both]
**Suite**: [Unit / E2E / All]
**Framework**: [detected from PROJECT.md]

| Metric | Backend | Frontend |
|--------|---------|----------|
| Total | X | X |
| Passed | X | X |
| Failed | X | X |
| Coverage | X% | X% |

**Status**: PASS / FAIL

### Failed Tests (if any)
| Test Name | Error | File |
|-----------|-------|------|
```

## Quality Gates
- Unit coverage: ≥80% (from `docs/TEST_VIEWPOINT.md`)
- R5 pass rate: 100% (gate for delivery)
- Type check: 0 errors (gate before testing)

> **Auto-routing on FAIL**:
> - Clear error with obvious root cause → `/fix-bug` with failed test name + error
> - Intermittent / flaky / no clear cause / fix already attempted → `/systematic-debugging`

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| On FAIL (clear cause) | `fix-bug` | Error message is clear, root cause obvious |
| On FAIL (unclear/flaky) | `systematic-debugging` | Intermittent failures, no clear root cause, or previous fix didn't hold |
| After PASS | `implement-feature` | All tests green — the PR step lives in that skill |
| Called from | `unit-test` / `integration-test` | Mode B — execute the UTC/ITC document just created |
| Called from | `implement-feature` | Self-check step — quick verify during development |

---
name: validate-and-test
description: "Runs a project's quality commands after code changes — linting, type checking, light static analysis, then the backend and frontend test suites — and reports the result against the quality gates. Commands come from PROJECT.md/CLAUDE.md or are auto-detected from project config; never hardcoded. TRIGGER: user asks to run lint, type-check, validate code quality, run the test suite, check test results, or verify everything passes before calling the work done. NOT FOR: writing test cases (use unit-test or integration-test), choosing what to test (use testing-strategy), or deep security auditing (use vulnerability-scanner)."
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[feature or module name (optional)]"
metadata:
  version: "3.1"
  category: quality
---

# Validate and Test

$ARGUMENTS

You execute a project's existing quality commands and report what they say. You
do not author tests and you do not decide test strategy — you run the checks and
turn their output into a verdict.

## Live Project Context (auto-injected)

- Working dir: !`pwd`
- Package files detected: !`ls package.json pyproject.toml Gemfile Cargo.toml go.mod 2>/dev/null | tr '\n' ' ' || echo "(none found)"`
- Existing test config: !`ls jest.config* vitest.config* pytest.ini setup.cfg .rspec 2>/dev/null | tr '\n' ' ' || echo "(none found)"`

## Content Map

| Section | When to read |
| --- | --- |
| Step 0 | Always — detect commands before running anything |
| Part 1: Validate | Lint, type check, static analysis after code changes |
| Part 2: Test | Executing the test suite and reporting results |
| Quality Gates | Always — the bar a run has to clear |

Both parts can run alone. The full order is **validate first, then test** — a
type error makes a test run meaningless, so type check is a gate *before* tests.

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect the tech stack and its
Build Commands **before running anything**. Do NOT hardcode lint or test
framework commands.

If PROJECT.md has no Build Commands section, detect from project config:

- `package.json` scripts (`lint`, `check`, `typecheck`, `test`)
- `pyproject.toml` tool sections
- `.eslintrc.*`, `tsconfig.json`, `ruff.toml`, `Cargo.toml`, `go.mod`

Or run the bundled detector, which prints the correct lint + type-check commands
for the current directory:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/validate-and-test/scripts/detect_stack.sh"
```

Machine-readable form, to run the commands it found:

```bash
eval "$(bash "${CLAUDE_PLUGIN_ROOT}/skills/validate-and-test/scripts/detect_stack.sh" --export)"
$TYPE_CMD && $LINT_CMD
```

Handles TypeScript / JavaScript / Python / Ruby / Go / Rust, and detects
npm/yarn/pnpm automatically.

---

## Part 1: Validate (lint, types, static analysis)

**Mandatory rule:** no code is reported as "done" without passing lint and type
checks.

### Procedures by ecosystem

**Node.js / TypeScript**

1. **Lint/fix**: `npm run lint`, or `npx eslint "path" --fix`
2. **Types**: `npx tsc --noEmit`
3. **Dependency audit**: `npm audit --audit-level=high`

**Python**

1. **Lint**: `ruff check "path" --fix`
2. **Types**: `mypy "path"`
3. **Static security scan**: `bandit -r "path" -ll`

**Other ecosystems** — take the commands from PROJECT.md or the detector above.

The dependency audit here is deliberately light. Deep code-level vulnerability
analysis (OWASP Top 10, injection paths, secrets, attack surface) is
`vulnerability-scanner`, not this skill.

### Quality loop

```
1. Write/edit code
2. Run lint + type check
3. Analyze the report
4. Fix the issues, repeat
5. Mark done only when all checks pass
```

### Error handling

| Situation | Action |
| --------- | ------ |
| Lint fails | Fix style/syntax issues immediately |
| Type check fails | Correct the type mismatches before proceeding |
| No linter configured | Check for config files, suggest creating one |
| Audit warnings | Report to the user with severity |

---

## Part 2: Test (execute the suite)

Use the commands from PROJECT.md's Build Commands section. The shapes below are
illustrative — detect, do not assume.

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
```

Run the type check (Part 1) before the suite — it is a gate, not a suggestion.

### After running: quick report

When called by another skill or a pool agent, output results in this format:

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

---

## Quality Gates

- Lint: clean
- Type check: 0 errors (gate before testing)
- Unit coverage: ≥80% (from `docs/TEST_VIEWPOINT.md`)
- R5 pass rate: 100% (gate for delivery)

> **Auto-routing on FAIL**: route to `/fix-bug` with the failed test name and
> error. When the failure is intermittent, has no clear cause, or a fix has
> already been attempted, say so — `fix-bug` (its systematic-debugging
> methodology) covers those cases.

## Verification

**Skill triggers correctly when:**

- User says: "Run lint and type checks before I call this done"
- User says: "Run the full test suite and tell me if everything passes"
- User says: "Run just the payment module tests"

**Skill does NOT trigger for:**

- "Write test cases for the payment module" (use `unit-test` / `integration-test`)
- "What mix of unit and E2E tests should we have?" (use `testing-strategy`)
- "Do an OWASP audit of the codebase" (use `vulnerability-scanner`)

**Expected outputs:**

- Lint + type-check results, looped until clean
- The Test Run Result table, with a PASS/FAIL status against the quality gates

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Called from | `implement-feature` | Always — type check + lint immediately after implementation |
| Called from | `unit-test` / `integration-test` | Mode B — execute the UTC/ITC document just created |
| On FAIL | `fix-bug` | Any failing test — it escalates internally when the cause is unclear or intermittent |
| After PASS | `review-code` | Mandatory quality gate before PR |
| Related | `vulnerability-scanner` | Deep security audit — beyond this skill's light dependency audit |

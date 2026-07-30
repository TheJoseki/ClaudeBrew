---
name: unit-test
description: "QA Unit Test agent writes and runs unit tests following ISTQB CTFL 4.0. Test framework detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to write or run unit tests for specific modules, controllers, services, or components. NOT FOR: integration/E2E tests (use integration-test)."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
metadata:
  version: "3.1"
  category: core-sdlc
---

# QA Unit Test — ISTQB CTFL 4.0

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Detect backend test framework (Jest, Pytest, RSpec, etc.) and frontend test framework (Vitest, Jest, RTL, etc.).
Do NOT hardcode framework assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect test framework first |
| Mode A: Create UTC | When called in Phase 4b (parallel with developer) |
| Mode B: Execute | When called in Phase 6 (after code review PASS) |

## Determine Operating Mode

**Mode A (CREATE)**: Called in parallel with developer-agent (Phase 4b)
- Input: TECH spec + code (just implemented or being implemented)
- Output: `docs/test-cases/UTC-[feature].md`

**Mode B (EXECUTE R[n])**: Called after Code Review PASS (Phase 6)
- Input: `docs/test-cases/UTC-[feature].md` + code
- Output: `docs/test-reports/UTR-[feature]-R[n].md`
- **Precondition**: Grep for `docs/test-cases/UTC-[feature].md` before proceeding.
  If NOT FOUND → STOP: "UTC not found. Run `/unit-test` Mode A first to create the test cases."

## Required Reading
- `docs/TEST_VIEWPOINT.md` — ISTQB techniques, TC catalog, quality gates
- `docs/CODING_RULES.md` — Rules to verify (soft delete, guards, i18n, no any)
- `docs/specs/detail-design/TECH-[feature].md` — Technical spec
- `docs/work-logs/DEV-[feature]-*.md` — Dev log (if exists)

---

## Mode A: Create UTC Document

File: `docs/test-cases/UTC-[feature].md`

> **Template**: See [`references/utc-template.md`](references/utc-template.md) for the full UTC and UTR document templates.

**MUST cover**:
- Auth 401 (no token) and RBAC 403 (wrong role)
- CRUD happy paths (create, read, update, delete)
- Key business workflow transitions (valid + invalid states)
- Input validation 400 errors (missing required, invalid format, max length)
- Soft delete: deleted records excluded from queries
- Component render, store/state actions, i18n keys

**Adapt test syntax to detected test framework** — examples below are illustrative:
- [BACKEND_TEST_FRAMEWORK] (detect from PROJECT.md — e.g. Jest + NestJS testing, Pytest, RSpec)
- [FRONTEND_TEST_FRAMEWORK] (detect from PROJECT.md — e.g. Vitest + Vue Test Utils, Jest + RTL, Cypress Component)

---

## Mode B: Execute Round R[n]

### Commands

Run commands from PROJECT.md Build Commands section. Typical examples:

```bash
# Backend — full suite with coverage
cd backend && [backend test command] --coverage --verbose

# Backend — specific module
cd backend && [backend test command] --testPathPattern="[module]" --verbose

# Frontend — full suite with coverage
cd frontend && [frontend test command] --coverage --reporter=verbose
```

Adapt syntax to the detected test framework from PROJECT.md.

### UTR Document (MUST CREATE after each round)

File: `docs/test-reports/UTR-[feature]-R[n].md`

> **Template**: See [`references/utc-template.md`](references/utc-template.md) for the full UTR document template.

### Round Gates
| R1 | R2 | R3 | R4 | R5 |
|----|----|----|----|----|
| Baseline | ≥70% | ≥90% | ≥95% | 100% GATE |

## Verification

**Skill triggers correctly when:**
- User says: "Write unit tests for the order service"
- User says: "Create unit test cases for the authentication controller"
- User says: "Run unit tests for the payment module"

**Skill does NOT trigger for:**
- "Write integration tests for the order API workflow" (use integration-test)
- "Review the order service code" (use review-code)
- "Run all tests" (use run-tests)

**Expected outputs:**
- Artifact (Mode A): `docs/test-cases/UTC-[feature].md`
- Artifact (Mode B): `docs/test-reports/UTR-[feature]-R[n].md`
- Quality gate: ≥80% coverage; R5 = 100% pass rate

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Parallel with | `implement-feature` | Mode A — write UTC alongside implementation (Phase 4b) |
| Parallel with | `integration-test` | Mode A — both test types created in same phase concurrently |
| After Mode A | `run-tests` | Mode B — execute the UTC document just created |
| On FAIL (Mode B) | `fix-bug` | Fix failing tests found during execution round |
| Called from | `full-sdlc` | Phase 4b (Mode A) and Phase 6 (Mode B) |
| Related | `tdd-workflow` | For strict TDD — write tests *before* implementation |

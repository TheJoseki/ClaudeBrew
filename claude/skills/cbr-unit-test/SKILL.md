---
name: cbr-unit-test
description: "QA Unit Test agent writes and runs unit tests. Test framework detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to write or run unit tests for specific modules, controllers, services, or components. NOT FOR: integration/E2E tests (use integration-test)."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Agent, AskUserQuestion
argument-hint: "[feature name] [--parallel]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# QA Unit Test

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Detect backend test framework (Jest, Pytest, RSpec, etc.) and frontend test framework (Vitest, Jest, RTL, etc.).
Do NOT hardcode framework assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect test framework first |
| Mode A: Create UTC | When writing test cases (supports `--parallel`) |
| Mode B: Execute | When running the suite as the UNIT gate |
| Parallel mode | Mode A only, when invoked with `--parallel` |

## Determine Operating Mode

**Mode A (CREATE)** — author the test cases
- Input: TECH spec + code (just implemented or being implemented)
- Output: `docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md`
- This is execution work; it may run `--parallel`.

**Mode B (EXECUTE R[n])** — the **UNIT quality gate**
- Input: `docs/streams/[feature]-*/test-cases/UTC.md` + code
- Output: `docs/streams/[feature]-[YYYYMMDD]/test-reports/UTR-R[n].md` + the UNIT verdict artifact
- Run by a freshly spawned `cbr-tester`, never graded here — see Mode B below.
- **Precondition**: Grep for `docs/streams/[feature]-*/test-cases/UTC.md` before proceeding.
  If NOT FOUND → STOP: "UTC not found. Run `/unit-test` Mode A first to create the test cases."

## Required Reading
- `docs/TEST_VIEWPOINT.md` — test viewpoint, TC catalog, quality gates
- `docs/CODING_RULES.md` — Rules to verify (soft delete, guards, i18n, no any)
- `docs/streams/[feature]-*/design/TECH.md` — Technical spec
- `docs/streams/[feature]-*/work-logs/DEV-*.md` — Dev log (if exists)

---

## Mode A: Create UTC Document

File: `docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md`

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

### Parallel mode (`--parallel`) — Mode A only

**Default is single-stream.** With `--parallel`, when the feature has several
independent test targets (separate services, controllers, components), spawn N
`cbr-developer` subagents in one message — one target per worker, each owning
only its own test files — then merge their cases into the single UTC document
here.

Workers are always `cbr-developer`. **Never spawn `cbr-tester` as a parallel
worker** — it is reserved for the Mode B gate, where its value is that it did
not author what it runs.

> **Procedure**: `{{CBR_ROOT}}/docs/references/parallel-mode.md`

Mode A ends at the UTC document. It does **not** roll on into Mode B — the user
decides when the gate runs.

---

## Mode B: Execute Round R[n] — the UNIT gate (fresh eyes)

**Do not run the suite and grade it yourself.** A freshly spawned `cbr-tester`
executes the tests and writes the verdict; this skill owns the criteria and the
user gate, not the judgment.

### The criteria this skill owns (hand these to the tester)

Test commands come from PROJECT.md's Build Commands section — never assume a
framework. Typical shapes:

```bash
# Backend — full suite with coverage
cd backend && [backend test command] --coverage --verbose

# Backend — specific module
cd backend && [backend test command] --testPathPattern="[module]" --verbose

# Frontend — full suite with coverage
cd frontend && [frontend test command] --coverage --reporter=verbose
```

Round gates — each round (`R[n]`, max R5) fixes only the failures the previous round
reported, then re-runs the full suite. The gate is met when the targeted suite is
**100% green**; if it is not green by R5, escalate to the user rather than pass.

UNIT also requires the coverage target in `docs/TEST_VIEWPOINT.md` to be met and 100%
of TECH-spec functions covered (Function Coverage Matrix).

### Step 1 — Spawn one `cbr-tester`

**Resolve the stream folder once** — the newest `docs/streams/[feature]-*/` (create it
if absent) — and use that one resolved path for both the report/verdict writes below and
the `verdict-gate.py --artifact` argument in Step 2, so the two never drift.

Single `Agent` call, Mode EXECUTE, with a prompt carrying:

- **Scope**: `docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md` + the code under test.
- **Commands**: the PROJECT.md test commands above (tell it to detect, not assume).
- **Round**: which R[n] this is (fix only this round's reported failures).
- **Outputs**, both mandatory:
  - Test report → `docs/streams/[feature]-[YYYYMMDD]/test-reports/UTR-R[n].md`
    (template: [`references/utc-template.md`](references/utc-template.md))
  - Verdict artifact → `docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-UNIT.json`, conforming
    to `{{CBR_ROOT}}/schemas/verdict-artifact.schema.json`, with
    `gate: "UNIT"` and `producedBy: "cbr-tester"`.
- **Evidence requirement**: `verification` MUST hold the actual command(s) run
  and their result — UNIT blocks without at least one `result: "pass"` entry.
  Summarize output; never paste raw dumps or secrets into the artifact.
- `decision: PASS` only when the targeted suite is fully green at this round's bar.

### Step 2 — Validate

```bash
python "{{CBR_ROOT}}/hooks/verdict-gate.py" --gate UNIT --artifact docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-UNIT.json
```

Exit `0` = PASS. Exit `2` = BLOCK (FAIL decision, unresolved Critical, **no
passing verification entry**, leaked secret, or malformed artifact). Fails
**closed** — an unrun suite cannot pass.

### Step 3 — Gate the user in, then stop

- **Exit 0** → report PASS with the command(s) run, pass rate and coverage, then
  **stop**.
- **Exit 2, or `decision: FAIL`** → `AskUserQuestion` presenting the blocking
  reason and each failing test, with options along the lines of: *fix now via
  `/fix-bug`* · *re-run this round after manual fixes* · *accept and proceed
  anyway* · *stop here*.

**Stop either way.** No automatic fix-loop, no self-triggered next round, no
advancing to `integration-test` — the user re-invokes `/fix-bug` and then this
skill for R[n+1].

## Verification

**Skill triggers correctly when:**
- User says: "Write unit tests for the order service"
- User says: "Create unit test cases for the authentication controller"
- User says: "Run unit tests for the payment module"

**Skill does NOT trigger for:**
- "Write integration tests for the order API workflow" (use integration-test)
- "Review the order service code" (use review-code)
- "Run all tests" (use validate-and-test)

**Expected outputs:**
- Artifact (Mode A): `docs/streams/[feature]-[YYYYMMDD]/test-cases/UTC.md`
- Artifacts (Mode B, written by the spawned `cbr-tester`):
  `docs/streams/[feature]-[YYYYMMDD]/test-reports/UTR-R[n].md` and
  `docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-UNIT.json`
- Quality gate: UNIT — coverage target in `docs/TEST_VIEWPOINT.md` met, 100% pass by R5,
  `verdict-gate.py --gate UNIT` run with its exit code reported

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Parallel with | `implement-feature` | Mode A — write UTC alongside implementation (Phase 4b) |
| Parallel with | `integration-test` | Mode A — both test types created in same phase concurrently |
| On FAIL (Mode B) | `fix-bug` | Fix failing tests found during execution round |
| Related | `testing-strategy` | For strict TDD — write tests *before* implementation |

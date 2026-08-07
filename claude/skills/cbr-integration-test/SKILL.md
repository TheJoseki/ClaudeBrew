---
name: cbr-integration-test
description: "Integration Test agent tests E2E workflows, key business workflows, and role-based access for any project. Test framework detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to write or run integration/E2E tests, test API workflows, test browser flows. NOT FOR: unit tests (use unit-test), or code review."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Agent, AskUserQuestion
argument-hint: "[feature name] [--parallel]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Integration Test

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Detect E2E/integration test framework and HTTP test library from PROJECT.md.
Do NOT hardcode framework assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect test framework first |
| Mode A: Create ITC | When writing test cases (supports `--parallel`) |
| Mode B: Execute | When running the suite as the G7 gate |
| Parallel mode | Mode A only, when invoked with `--parallel` |

## Determine Operating Mode

**Mode A (CREATE)** — author the test cases
- Input: TECH spec + SRS
- Output: `docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md`
- This is execution work; it may run `--parallel`.

**Mode B (EXECUTE R[n])** — the **G7 quality gate**
- Input: `docs/streams/[feature]-*/test-cases/ITC.md`
- Output: `docs/streams/[feature]-[YYYYMMDD]/test-reports/ITR-R[n].md` + the G7 verdict artifact
- Run by a freshly spawned `cbr-tester`, never graded here — see Mode B below.
- **Precondition**: Grep for `docs/streams/[feature]-*/test-cases/ITC.md` before proceeding.
  If NOT FOUND → STOP: "ITC not found. Run `/integration-test` Mode A first to create the test cases."

## Required Reading
- `docs/TEST_VIEWPOINT.md` — Integration TC catalog, quality gates
- `docs/API_DESIGN.md` — Endpoint chains, request/response (if exists)
- `docs/ARCHITECTURE.md` — Key business workflows, role-based access (if exists)
- `docs/streams/[feature]-*/design/TECH.md`, `docs/streams/[feature]-*/requirements/SRS.md`

---

## Mode A: Create ITC Document

File: `docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md`

> **Template**: See [`references/itc-template.md`](references/itc-template.md) for the full ITC document template.
> **Script templates**: See [`references/script-templates.md`](references/script-templates.md) for Playwright and HTTP integration test script templates.

**MUST cover**:
- Auth flow: login → token → protected route → refresh → logout
- [Key business workflow from PROJECT.md] happy path (all actors in sequence)
- Rejection/reversal paths for key workflows
- RBAC: each role sees only permitted data
- Admin-only routes: non-admin → 403
- Soft delete: deleted records do not appear in listings

### Parallel mode (`--parallel`) — Mode A only

**Default is single-stream.** With `--parallel`, when the feature has several
independent workflows or endpoint chains, spawn N `cbr-developer` subagents in
one message — one workflow per worker, each owning only its own test/script
files — then merge their cases into the single ITC document here. Shared
fixtures, seed data and auth setup stay in this context: they are the files
every worker would otherwise collide on.

Workers are always `cbr-developer`. **Never spawn `cbr-tester` as a parallel
worker** — it is reserved for the Mode B gate, where its value is that it did
not author what it runs.

> **Procedure**: `{{CBR_ROOT}}/skills/cbr-implement-feature/references/parallel-mode.md`

Mode A ends at the ITC document. It does **not** roll on into Mode B — the user
decides when the gate runs.

---

## Mode B: Execute Round R[n] — the G7 gate (fresh eyes)

**Do not run the suite and grade it yourself.** A freshly spawned `cbr-tester`
executes the tests and writes the verdict; this skill owns the criteria and the
user gate, not the judgment.

### The criteria this skill owns (hand these to the tester)

Test commands come from PROJECT.md's Build Commands section — never assume a
framework. Typical shapes:

```bash
# Backend integration / E2E tests
cd backend && [backend E2E test command] --verbose

# Frontend E2E tests (if applicable)
cd frontend && [E2E test command] --reporter=list
```

- [HTTP integration test library] (e.g. Supertest, httpx, RestAssured — per PROJECT.md)
- [E2E test framework] (e.g. Playwright, Cypress, Selenium — per PROJECT.md)

Round gates — each round (`R[n]`, max R5) fixes only the failures the previous round
reported, then re-runs the full suite. The gate is met when the targeted suite is
**100% green**; if it is not green by R5, escalate to the user rather than pass.

G7 covers both the API integration suite and, where the project has a UI, the
critical-journey E2E suite. Run against a production-equivalent database, and
require 100% of BASIC workflows plus the TECH API contracts to be covered
(Workflow-API Matrix). E2E browser coverage is **N/A for backend-only projects**
— say so explicitly rather than passing it silently.

### Step 1 — Spawn one `cbr-tester`

**Resolve the stream folder once** — the newest `docs/streams/[feature]-*/` (create it
if absent) — and use that one resolved path for both the report/verdict writes below and
the `verdict-gate.py --artifact` argument in Step 2, so the two never drift.

Single `Agent` call, Mode EXECUTE, with a prompt carrying:

- **Scope**: `docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md` + the workflows under test.
- **Commands**: the PROJECT.md test commands above (tell it to detect, not assume).
- **Round**: which R[n] this is, and the pass-rate bar for that round.
- **Outputs**, both mandatory:
  - Test report → `docs/streams/[feature]-[YYYYMMDD]/test-reports/ITR-R[n].md`
    (template: [`references/itr-template.md`](references/itr-template.md))
  - Verdict artifact → `docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-G7.json`, conforming
    to `{{CBR_ROOT}}/schemas/verdict-artifact.schema.json`, with
    `producedBy: "cbr-tester"` and **`gate: "G7"` exactly** — the API/E2E split
    is reported inside the ITR, never as a `G7a`/`G7b` gate value, which the
    validator rejects.
- **Evidence requirement**: `verification` MUST hold the actual command(s) run
  and their result — G7 blocks without at least one `result: "pass"` entry.
  Summarize output; never paste raw dumps or secrets into the artifact.
- `decision: PASS` only when the targeted suite is fully green at this round's bar.

### Step 2 — Validate

```bash
python "{{CBR_ROOT}}/hooks/verdict-gate.py" --gate G7 --artifact docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-G7.json
```

Exit `0` = PASS. Exit `2` = BLOCK (FAIL decision, unresolved Critical, **no
passing verification entry**, leaked secret, or malformed artifact). Fails
**closed** — an unrun suite cannot pass.

### Step 3 — Gate the user in, then stop

- **Exit 0** → report PASS with the command(s) run, pass rate, and which suites
  ran vs were N/A, then **stop**.
- **Exit 2, or `decision: FAIL`** → `AskUserQuestion` presenting the blocking
  reason and each failing workflow, with options along the lines of: *fix now
  via `/fix-bug`* · *re-run this round after manual fixes* · *accept and proceed
  anyway* · *stop here*.

**Stop either way.** No automatic fix-loop and no self-triggered next round —
the user re-invokes `/fix-bug` and then this skill for R[n+1].

## Verification

**Skill triggers correctly when:**
- User says: "Write integration tests for the order API workflow"
- User says: "Create E2E tests for the checkout browser flow"
- User says: "Run integration tests for the payment feature"

**Skill does NOT trigger for:**
- "Write unit tests for the order service" (use unit-test)
- "Review the integration test code quality" (use review-code)
- "Run all tests including unit tests" (use validate-and-test)

**Expected outputs:**
- Artifact (Mode A): `docs/streams/[feature]-[YYYYMMDD]/test-cases/ITC.md`
- Artifacts (Mode B, written by the spawned `cbr-tester`):
  `docs/streams/[feature]-[YYYYMMDD]/test-reports/ITR-R[n].md` and
  `docs/streams/[feature]-[YYYYMMDD]/test-reports/VERDICT-G7.json`
- Quality gate: G7 — all key business workflows covered, R5 = 100% pass rate,
  `verdict-gate.py --gate G7` run with its exit code reported

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Parallel with | `implement-feature` | Mode A — write ITC alongside implementation (Phase 4c) |
| Parallel with | `unit-test` | Mode A — both created concurrently; unit tests execute first |
| After Mode A | `validate-and-test` | Mode B — execute the ITC document just created |
| On FAIL (Mode B) | `fix-bug` | Fix integration test failures |
| Related | `architecture` | For REST API test patterns and endpoint chain design |

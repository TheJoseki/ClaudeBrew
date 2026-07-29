---
name: integration-test
description: Integration Test agent tests E2E workflows, key business workflows, and role-based access for any project. Test framework detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to write or run integration/E2E tests, test API workflows, test browser flows. NOT FOR: unit tests (use unit-test), or code review.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
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
| Mode A: Create ITC | When called in Phase 4c (parallel with developer) |
| Mode B: Execute | When called in Phase 7 (after unit tests PASS) |

## Determine Operating Mode

**Mode A (CREATE)**: Parallel with developer-agent (Phase 4c)
- Input: TECH spec + SRS
- Output: `docs/test-cases/ITC-[feature].md`

**Mode B (EXECUTE R[n])**: After Code Review PASS (Phase 7)
- Input: `docs/test-cases/ITC-[feature].md`
- Output: `docs/test-reports/ITR-[feature]-R[n].md`
- **Precondition**: Grep for `docs/test-cases/ITC-[feature].md` before proceeding.
  If NOT FOUND → STOP: "ITC not found. Run `/integration-test` Mode A first to create the test cases."

## Required Reading
- `docs/TEST_VIEWPOINT.md` — Integration TC catalog, quality gates
- `docs/API_DESIGN.md` — Endpoint chains, request/response (if exists)
- `docs/ARCHITECTURE.md` — Key business workflows, role-based access (if exists)
- `docs/specs/detail-design/TECH-[feature].md`, `docs/specs/requirements/SRS-[feature].md`

---

## Mode A: Create ITC Document

File: `docs/test-cases/ITC-[feature].md`

> **Template**: See [`references/itc-template.md`](references/itc-template.md) for the full ITC document template.
> **Script templates**: See [`references/script-templates.md`](references/script-templates.md) for Playwright and HTTP integration test script templates.

**MUST cover**:
- Auth flow: login → token → protected route → refresh → logout
- [Key business workflow from PROJECT.md] happy path (all actors in sequence)
- Rejection/reversal paths for key workflows
- RBAC: each role sees only permitted data
- Admin-only routes: non-admin → 403
- Soft delete: deleted records do not appear in listings

---

## Mode B: Execute Round R[n]

### Commands

Run commands from PROJECT.md Build Commands section. Typical examples:

```bash
# Backend integration / E2E tests
cd backend && [backend E2E test command] --verbose

# Frontend E2E tests (if applicable)
cd frontend && [E2E test command] --reporter=list
```

Adapt syntax to the detected test framework from PROJECT.md:
- [HTTP integration test library] (e.g. Supertest, httpx, RestAssured — per PROJECT.md)
- [E2E test framework] (e.g. Playwright, Cypress, Selenium — per PROJECT.md)

### ITR Document (MUST CREATE after each round)

File: `docs/test-reports/ITR-[feature]-R[n].md`

> **Template**: See [`references/itr-template.md`](references/itr-template.md) for the full ITR document template.

### Round Gates
| R1 | R2 | R3 | R4 | R5 |
|----|----|----|----|----|
| Baseline | ≥70% | ≥90% | ≥95% | 100% GATE |

## Verification

**Skill triggers correctly when:**
- User says: "Write integration tests for the order API workflow"
- User says: "Create E2E tests for the checkout browser flow"
- User says: "Run integration tests for the payment feature"

**Skill does NOT trigger for:**
- "Write unit tests for the order service" (use unit-test)
- "Review the integration test code quality" (use review-code)
- "Run all tests including unit tests" (use run-tests)

**Expected outputs:**
- Artifact (Mode A): `docs/test-cases/ITC-[feature].md`
- Artifact (Mode B): `docs/test-reports/ITR-[feature]-R[n].md`
- Quality gate: All key business workflows covered; R5 = 100% pass rate

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Parallel with | `implement-feature` | Mode A — write ITC alongside implementation (Phase 4c) |
| Parallel with | `unit-test` | Mode A — both created concurrently; unit tests execute first |
| After Mode A | `run-tests` | Mode B — execute the ITC document just created |
| On FAIL (Mode B) | `fix-bug` | Fix integration test failures |
| Called from | `full-sdlc` | Phase 4c (Mode A) and Phase 7 (Mode B) |
| Related | `api-patterns` | For REST API test patterns and endpoint chain design |

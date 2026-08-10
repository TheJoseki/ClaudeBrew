# Test Viewpoint — [PROJECT_NAME — e.g. Acme Store]

> Created/updated by `design-function` (Step D2 fills Section 0 from PROJECT.md); consumed by `unit-test`, `integration-test`, and `validate-and-test`; gate verdict by a fresh `cbr-tester` + user.
> A short, project-specific judgment prompt: **what to test, where the risk is, and how the test gates map** — not a technique-cataloguing exercise.
> Copy this template to `docs/TEST_VIEWPOINT.md`, then replace every `[… — e.g. …]` slot with real project values. Gate G3c requires zero remaining placeholder brackets.

---

## Section 0 — Test Layer Infrastructure

> Machine-read contract. Keep the table shape and the two labelled lines below intact and greppable — `design-function` writes here (Step D2) and `validate-and-test` reads the coverage line back.

Coverage target: BE ≥[NN — e.g. 80]% | FE ≥[NN — e.g. 80]%
Coverage tool: [tool — e.g. coverage.py / c8 / v8]
Status: [PENDING APPROVAL | APPROVED — e.g. PENDING APPROVAL]

| Layer | Framework | Test DB / Fixtures | Run command |
|-------|-----------|--------------------|-------------|
| Unit | [framework — e.g. pytest / Jest / Vitest] | [fixtures — e.g. in-memory + mocks] | [run command — e.g. npm run test:unit] |
| Integration | [framework — e.g. Supertest / pytest + httpx] | [test DB — e.g. ephemeral Postgres container] | [run command — e.g. npm run test:integration] |
| E2E | [framework — e.g. Playwright; or "N/A — backend-only"] | [seed data — e.g. seeded temp DB + fixtures] | [run command — e.g. npm run test:e2e] |

---

## Section 1 — Gate Mapping

Which test activity satisfies which quality gate. Pass criteria and deciding authority are the authority in `{{CBR_ROOT}}/docs/references/sdlc-reference.md` — this table is the test-side view.

| Gate | Test activity | Pass criteria | Decided by |
|------|---------------|---------------|------------|
| G3c | This viewpoint approved | Section 0 filled, all layers defined, zero placeholder brackets | User approval |
| G6 | Unit tests | 100% pass, ≤R5 rounds, 100% TECH-spec functions covered | `unit-test` verdict (fresh `cbr-tester`) + user |
| G7a | API integration tests | 100% pass, ≤R5 rounds, all BASIC workflows + TECH API contracts covered | `integration-test` verdict (fresh `cbr-tester`) + user |
| G7b | E2E browser tests | 100% pass, ≤R5 rounds, all critical journeys covered — N/A for backend-only | `integration-test` verdict (fresh `cbr-tester`) + user |

> Verdict-artifact note: G7a and G7b are sub-criteria and both report under `gate: "G7"` in the verdict JSON — writing `"G7a"`/`"G7b"` fails schema validation. Record the API-vs-E2E split inside the integration test report (ITR), not in the `gate` field.

---

## Section 2 — What to test (risk-first)

Judgment, not a matrix. Name where this project actually breaks, then spend the test effort there.

- **Highest-risk areas** — the modules where a defect is most costly (e.g. auth/RBAC, payments, data integrity, anything touching money or permissions). List them and say *why* each is risky.
- **Layers per area** — for each risk area, which layers carry the weight (unit for pure logic, integration for cross-module workflows, E2E for critical user journeys). A CRUD screen and a payment flow do not deserve the same depth.
- **Negative paths that must fail correctly** — the unhappy paths the system must reject, not just the happy path: unauthenticated (401), wrong role (403), invalid input per validation rule (400), missing resource (404), uniqueness conflict (409). Cover the ones each endpoint actually has.
- **Realistic data** — test with data shaped like production (real IDs, boundary sizes, unicode, empty/null), not just tidy fixtures.

Fill in per project:

| Risk area | Why it's risky | Layers to test | Key negative paths |
|-----------|----------------|----------------|--------------------|
| [area — e.g. auth/RBAC] | [why — e.g. broken access control is the top OWASP risk] | [layers — e.g. unit + integration] | [e.g. 401 no token, 403 wrong role] |
| [area — e.g. …] | [why] | [layers] | [negative paths] |

---

## Section 3 — Test Case Catalog

Seed with representative cases per layer; expand during `unit-test` / `integration-test` Mode A. Every row's `Gate` must be one of G6 / G7a / G7b.

| TC-ID | Layer | Scenario | Expected | Gate |
|-------|-------|----------|----------|------|
| [TC-001 — e.g. TC-001] | Unit | [scenario — e.g. valid credentials return a session token] | [expected — e.g. 200 + token payload] | G6 |
| [TC-002 — e.g. TC-002] | Integration | [scenario — e.g. list endpoint at max page size] | [expected — e.g. 200 + N items, no overflow] | G7a |

---

## Section 4 — G3c Pass Checklist

Check every item before requesting G3c approval. These are gate checks, not fill-in slots.

- [ ] Section 0 filled with real frameworks, fixtures, and run commands (no placeholder brackets)
- [ ] Coverage target and coverage tool set from PROJECT.md
- [ ] Gate mapping reviewed; G7b marked N/A if the project is backend-only
- [ ] Section 2 names the real risk areas, their layers, and their negative paths (no generic filler)
- [ ] Test Case Catalog seeded with at least one case per applicable layer
- [ ] Zero remaining `[… — e.g. …]` placeholder brackets in this document

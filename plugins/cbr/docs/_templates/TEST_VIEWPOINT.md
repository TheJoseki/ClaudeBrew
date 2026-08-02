# Test Viewpoint — [PROJECT_NAME — e.g. Acme Store]

> Created/updated by `design-function` (Step D2 fills Section 0 from PROJECT.md); consumed by `unit-test`, `integration-test`, and `validate-and-test`; gate verdict by a fresh `cbr:tester` + user.
> Methodology: ISTQB CTFL · ISO/IEC 25010.
> Copy `docs/_templates/TEST_VIEWPOINT.md` → `docs/TEST_VIEWPOINT.md`, then replace every `[… — e.g. …]` slot with real project values. Gate G3c requires zero remaining placeholder brackets.

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

Which test activity satisfies which quality gate. Pass criteria and deciding authority are the authority in `rules/sdlc-conventions.md` — this table is the test-side view.

| Gate | Test activity | Pass criteria | Decided by |
|------|---------------|---------------|------------|
| G3c | This viewpoint approved | Section 0 filled, all layers defined, zero placeholder brackets | User approval |
| G6 | Unit tests | 100% pass, ≤R5 rounds, 100% TECH-spec functions covered | `unit-test` verdict (fresh `cbr:tester`) + user |
| G7a | API integration tests | 100% pass, ≤R5 rounds, all BASIC workflows + TECH API contracts covered | `integration-test` verdict (fresh `cbr:tester`) + user |
| G7b | E2E browser tests | 100% pass, ≤R5 rounds, all critical journeys covered — N/A for backend-only | `integration-test` verdict (fresh `cbr:tester`) + user |

> Verdict-artifact note: G7a and G7b are sub-criteria and both report under `gate: "G7"` in the verdict JSON — writing `"G7a"`/`"G7b"` fails schema validation. Record the API-vs-E2E split inside the integration test report (ITR), not in the `gate` field.

---

## Section 2 — ISTQB Technique Application

One line per technique naming where it is applied in this project.

| Technique | Where applied |
|-----------|---------------|
| Equivalence partitioning | [where applied — e.g. login input classes: valid / invalid / empty] |
| Boundary value analysis | [where applied — e.g. pagination page size at 0, 1, max, max+1] |
| Decision table | [where applied — e.g. role × resource permission matrix] |
| State transition | [where applied — e.g. order status DRAFT → PAID → SHIPPED transitions] |

---

## Section 3 — Test Case Catalog

Seed with representative cases per layer; expand during `unit-test` / `integration-test` Mode A. Every row's `Gate` must be one of G6 / G7a / G7b.

| TC-ID | Layer | Technique | Scenario | Expected | Gate |
|-------|-------|-----------|----------|----------|------|
| [TC-001 — e.g. TC-001] | Unit | Equivalence partitioning | [scenario — e.g. valid credentials return a session token] | [expected — e.g. 200 + token payload] | G6 |
| [TC-002 — e.g. TC-002] | Integration | Boundary value | [scenario — e.g. list endpoint at max page size] | [expected — e.g. 200 + N items, no overflow] | G7a |

---

## Section 4 — G3c Pass Checklist

Check every item before requesting G3c approval. These are gate checks, not fill-in slots.

- [ ] Section 0 filled with real frameworks, fixtures, and run commands (no placeholder brackets)
- [ ] Coverage target and coverage tool set from PROJECT.md
- [ ] Gate mapping reviewed; G7b marked N/A if the project is backend-only
- [ ] Each ISTQB technique either has a real application or is marked N/A with a reason
- [ ] Test Case Catalog seeded with at least one case per applicable layer
- [ ] Zero remaining `[… — e.g. …]` placeholder brackets in this document

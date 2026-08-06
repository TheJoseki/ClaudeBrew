---
description: Test quality standards — business flow-driven ITC, scenario generation, negative matrix, risk scoring. Always loaded to ensure deep IT coverage.
---

# Test Quality Standards

> Defines WHAT makes a quality test case. Agent execution steps live in agent definitions — this file defines the STANDARDS their output is judged against.

## 1. Business Flow-Driven ITC (MANDATORY)

### Definitions

- **Business step** = user action that changes system state OR crosses actor/module boundary
- **CRUD unit** = single endpoint test (create OR read OR update OR delete in isolation)
- **Business flow chain** = sequence of ≥3 business steps spanning ≥2 actors or modules

**Rule**: ITCs MUST be business flow chains, NOT CRUD units.
Primary input: BASIC spec §6.5 (Business Flow Scenarios) + TECH spec §4.3 (Implementation Mapping).

### Anti-Pattern (REJECT)

Create entity → List entities → View entity = 3 API calls but **NOT** integration testing.
Why: same actor, same module, no state change between steps. This is CRUD isolation dressed as chaining.

### Valid Chain (ACCEPT)

Admin creates account (step 1, state: user created) → New user logs in (step 2, actor switch, state: session) → New user accesses role feature (step 3, module cross) → Admin verifies result (step 4, actor switch back, cross-entity verify).

### What Counts as 1 Business Step

| Criterion | Example |
|-----------|---------|
| Actor/role switch | Login as different user, perform action |
| Module boundary cross | From module A → action in module B |
| State-changing action | Create/update/delete that modifies DB |
| Approval/workflow transition | Status change requiring different actor |

**Does NOT count**: GET-only verification (used to assert, not a business step), list/pagination, redirect without action.

### Minimum Chain Depth per Flow Type

| Flow Type | Min Business Steps | Required Characteristic |
|-----------|--------------------|------------------------|
| Single-actor CRUD | 3 steps + cross-entity verify | State verified after each mutation |
| Multi-actor | 4+ steps | ≥2 actor switches |
| Approval/workflow | All transitions | Every status + actor handoff |
| Auth lifecycle | Full cycle | Register→Login→Use→Refresh→Logout→Denied |
| State Machine | All states | Every valid + invalid transition |

## 2. Scenario Generation Algorithm

**Input**: Business Flows from BASIC §6.5 + Implementation Mapping from TECH §4.3.

Per business flow:
```
MIN scenarios = 1(happy) + E(error paths from §6.5) + R(roles) + C(1 if multi-actor) + 1(teardown verify)
Floor = max(formula_result, 5)
```

- `E` = count of Error/Rejection Path rows in BASIC §6.5 for this flow
- `R` = count of distinct roles involved in the flow
- `C` = 1 if flow involves ≥2 actors (concurrent scenario), else 0

`integration-test` reads BASIC §6.5 Error/Rejection Paths table → each variant = 1 error scenario.

### Flow Type → Required Scenario Patterns

| Type | Required Patterns |
|------|------------------|
| CRUD | Happy CRUD cycle + soft delete verify + cascade verify |
| Approval | Submit → Approve + Submit → Reject + Resubmit after reject |
| Auth | Register→Login→Access→Refresh→Logout→Access(denied) |
| Multi-actor | Actor A creates → Actor B processes → Actor A verifies |
| State Machine | All valid transitions + all invalid transitions (expect 4xx) |
| Async | Trigger → Poll status → Completion → Verify side effects |

## 3. Negative Test Matrix (UTC + ITC — MANDATORY)

Every API endpoint MUST appear in a Negative Test Matrix:

| Column | Rule |
|--------|------|
| 401 | No token / expired token |
| 403 | Per role that should NOT have access |
| 400 | One TC **per validation rule** in DTO (not just "invalid input") |
| 404 | For every endpoint with path parameter |
| 409 | For every endpoint with uniqueness constraint |

**Missing cell = gap** → MUST fill before finalizing UTC/ITC artifact.

## 4. Risk-Based Test Prioritization

### Module Risk Classification

| Risk Level | Multiplier | Examples |
|------------|-----------|---------|
| Security | ×3 | Auth, RBAC, token management, encryption |
| Business-critical | ×2 | Payment, approval workflows, data integrity |
| Standard | ×1 | CRUD, listing, search, reporting |

### Adjusted Targets

- **UTC quantity**: Adjusted = Base target × weighted_avg(risk multipliers across modules)
- **ITC scenarios**: Security flows get 3× more error scenarios than standard flows

### Coverage Gates (Risk-Adjusted)

| Module Risk | Statement Coverage | Branch Coverage |
|-------------|-------------------|-----------------|
| Security (×3) | ≥95% | ≥90% |
| Business-critical (×2) | ≥90% | ≥85% |
| Standard (×1) | ≥85% | ≥80% |

## 5. Coverage Verification Checklist (BEFORE submitting UTC/ITC)

### UTC Checklist
- [ ] Function Coverage Matrix complete — every TECH spec function has ≥1 TC
- [ ] Negative Test Matrix — zero empty required cells
- [ ] Soft delete verified on ALL query methods
- [ ] Risk-adjusted quantity met

### ITC Checklist
- [ ] Every BASIC §6.5 business flow has ≥1 happy chain + all error variants
- [ ] Every scenario has ≥3 business steps (actor switches, module crosses, state changes)
- [ ] Cross-entity verification present after each state-changing step
- [ ] Error paths from §6.5 all covered as separate scenarios
- [ ] Negative Test Matrix — zero empty required cells

**Gap Reporting MANDATORY**: If ANY item fails → list gaps in artifact `## Coverage Gaps` section.

## 6. Soft Delete & State Verification

Every query method in TECH spec → test MUST verify soft-deleted records excluded:
- `findAll`/`list` → absent from results | `findById` → 404 | `search`/`filter` → absent | `count` → not counted

After each state-changing step: verify entity state, audit columns (updatedAt/By), related entity impact, side effects.
Cascade: soft delete parent → verify child behavior (cascade soft delete OR orphan handling per TECH spec).

## 7. Test Data Strategy

- **NO placeholders**: `"test1"`, `"user1@test.com"` → YES: realistic domain data matching field constraints
- **Multi-role setup MANDATORY**: 1 user per role in BASIC §6.5, distinct data, separate tokens/sessions
- **Preconditions explicit**: each flow step set up independently, teardown restores clean state

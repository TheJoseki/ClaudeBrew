---
description: Proactive risk management and corrective action (CAR) for materialized issues. Adds forward-looking risk identification to the reactive handling of blockers at each gate.
---

# Risk & Issue Management — ClaudeBrew

> Proactive risk identification + structured corrective action when issues materialize. Urgent blockers go straight to the user; this rule handles systematic risk tracking and root-cause resolution.

## 1. Risk Assessment Timing

| Trigger | Who | Action |
|---------|-----|--------|
| Project start (Step 0) | `plan-writing` | Initial risk register in PLAN file |
| Each stage gate | the stage skill | Review + update risk register before asking for approval |
| Scope change or new requirement | `analyze-requirement` | Add new risks |
| New technology introduced | `design-function` / `architecture` | Add technical risks |
| 3-Strike escalation triggered | any stage | Add issue + CAR |
| Gate FAIL (≥2 times same gate) | user, at the gate | Assess if systemic → CAR |
| Security scan findings | `vulnerability-scanner` | Add security risks |

## 2. Risk Register Format

Embedded as `## Risk Register` section in PLAN file (FEATURE-level).
For EPIC plans: separate file at `docs/risks/RISK-[epic-name].md`.

```markdown
## Risk Register
| ID | Category | Risk | P | I | Score | Response | Owner | Status |
|----|----------|------|---|---|-------|----------|-------|--------|
| R-01 | Technical | [description] | 3 | 4 | 12 | Mitigate: [action] | [agent] | OPEN |
```

### Scoring
- **Probability (P)**: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain
- **Impact (I)**: 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Critical
- **Score**: P × I (range: 1–25)

### Response Thresholds

| Score | Level | Required Action |
|-------|-------|----------------|
| 1–4 | LOW | Accept — monitor only |
| 5–9 | MEDIUM | Mitigate — define specific action in plan |
| 10–15 | HIGH | Mitigate + raise to the user immediately |
| 16–25 | CRITICAL | Avoid or Transfer — escalate to user immediately |

### Risk Categories

| Category | Examples |
|----------|---------|
| Technical | Unfamiliar tech, complex integration, performance bottleneck |
| Schedule | Dependency delay, underestimated effort, scope creep |
| Resource | Context budget overflow, agent capability gap |
| External | Third-party API change, library deprecation |
| Quality | Insufficient test coverage, design debt accumulation |
| Security | New attack surface, credential management, data exposure |

### Response Strategies
- **Mitigate**: Reduce probability or impact (e.g., spike first, add tests)
- **Accept**: Acknowledge, monitor, no action unless triggered
- **Transfer**: Move ownership (e.g., to user, to external team)
- **Avoid**: Change plan to eliminate the risk entirely

### Status Values
`OPEN` → `MITIGATING` → `OCCURRED` (create CAR) → `CLOSED` | `ACCEPTED`

## 3. CAR (Corrective Action Report)

**Trigger**: Risk materializes OR gate fails ≥2 times OR 3-Strike escalation.

**Artifact path**: `docs/cars/CAR-[feature]-[topic]-[YYYYMMDD].md`

### CAR Template

```markdown
# CAR: [Issue Title]

**Feature**: [name] | **Date**: YYYY-MM-DD | **Severity**: CRITICAL/HIGH/MEDIUM
**Related Risk**: R-XX (or "Unidentified risk")
**Related Gate**: G[N] (if gate failure)

## Issue Description
[What happened — observable symptoms, not guesses]

## Root Cause Analysis (5-Why)
1. Why? [surface cause]
2. Why? [deeper cause]
3. Why? [systemic cause]
(Continue until root cause is actionable — typically 3-5 levels)

## Corrective Action (fix THIS issue)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| [specific fix] | [agent] | [date] | PENDING |

## Preventive Action (prevent RECURRENCE)
| Action | Owner | Target | Status |
|--------|-------|--------|--------|
| [process/rule change] | [agent] | [when] | PENDING |

## Verification
- [ ] Corrective action completed
- [ ] Affected gate re-passed
- [ ] Preventive action documented in the CAR, the risk register, or a rule update
```

## 4. Integration Rules

- HIGH/CRITICAL risks (score ≥10) → raise to the user immediately, do not wait for the gate
- Risk materializes → update status to OCCURRED and create a CAR
- CAR preventive actions → recorded in the CAR and surfaced to the user at the next gate
- At each stage gate: review risk register, update scores, close resolved risks
- Risk register review is MANDATORY at Step 0 for all plans (not just Medium+ complexity)

## 5. Stage Responsibility

| Stage | Risk Responsibility |
|-------|-------------------|
| `plan-writing` | Maintain risk register in PLAN, review it at each gate, create CARs for gate failures |
| `design-function` / `architecture` | Identify technical risks during BASIC/DETAIL design |
| `implement-feature` | Report risks that emerge during implementation (→ register update + raise at the gate) |
| `unit-test` / `integration-test` | Report quality risks when coverage gaps found |
| `vulnerability-scanner` | Report security risks from scan findings |

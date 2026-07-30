---
description: DAR (Decision Analysis and Resolution) protocol — structured evaluation for decisions with uncertainty. Produces ADR records. Always loaded alongside sdlc-conventions.md.
---

# DAR Evaluation Protocol — ClaudeBrew

> Structured process for evaluating alternatives BEFORE making a decision. An ADR records WHAT was decided; DAR defines HOW to evaluate the alternatives.

## 1. Trigger Conditions

| Condition | DAR Level |
|-----------|-----------|
| >2 valid approaches with non-trivial trade-offs | Quick DAR |
| New technology or library choice | Quick DAR |
| Architecture-impacting change (new module, DB schema, API pattern) | Full DAR |
| Irreversible or high-cost-to-reverse decision | Full DAR |
| Security-sensitive design choice | Full DAR |
| Cross-team or cross-feature impact | Full DAR |
| Disagreement between agents (COUNCIL contradiction) | Full DAR |

**Skip DAR when**: Only 1 viable option, decision is trivially reversible, or project convention already covers it.

## 2. Quick DAR (inline, ≤15 min)

For medium-impact decisions. Inline in the producing artifact (COUNCIL, TECH spec, work-log).

```markdown
### DAR: [Decision Title]
**Options**: A) [option] | B) [option] | C) [option]
**Criteria**: [2-3 most relevant from §4]
**Winner**: [option] — [1-sentence rationale]
**Why not others**: A) [reason rejected] | C) [reason rejected]
```

After completing → record the outcome inline in the stage artifact, tagged `Source: DAR-QUICK`.

## 3. Full DAR (separate artifact)

For critical/irreversible decisions. Artifact path: `docs/dars/DAR-[feature]-[topic]-[YYYYMMDD].md`

### Full DAR Template

```markdown
# DAR: [Decision Title]

**Feature**: [feature-name] | **Date**: YYYY-MM-DD | **Author**: [agent-name]
**Status**: EVALUATING → DECIDED

## Context
[Why this decision is needed — 2-3 sentences max]

## Options
| ID | Option | Description |
|----|--------|-------------|
| A | [name] | [1-2 sentence description] |
| B | [name] | [1-2 sentence description] |
| C | [name] | [1-2 sentence description] |

## Evaluation Matrix
| Criteria | Weight | A | B | C |
|----------|--------|---|---|---|
| [criterion-1] | 0.XX | 1-5 | 1-5 | 1-5 |
| [criterion-2] | 0.XX | 1-5 | 1-5 | 1-5 |
| **Weighted Total** | **1.0** | **X.XX** | **X.XX** | **X.XX** |

## Decision
**Selected**: [Option X] (score: X.XX)
**Rationale**: [2-3 sentences — why this wins on the criteria that matter most]

## Rejected Alternatives
- **[Option Y]**: [Why not — specific weakness]
- **[Option Z]**: [Why not — specific weakness]

## Risks of Selected Option
| Risk | Mitigation |
|------|-----------|
| [risk-1] | [mitigation] |
```

After completing → write the ADR, tagged `Source: DAR-[feature]-[topic]`.

## 4. Standard Evaluation Criteria

Pick 3-5 relevant criteria per DAR. Weights MUST sum to 1.0.

| Criteria | What to Assess | Typical Weight |
|----------|---------------|----------------|
| Feasibility | Can we build this with current stack/skills? | 0.15–0.25 |
| Maintainability | Long-term code complexity, coupling | 0.10–0.20 |
| Performance | Latency, throughput, scalability impact | 0.10–0.20 |
| Security | Attack surface, data exposure, auth impact | 0.10–0.20 |
| Team Expertise | Familiarity with approach, learning curve | 0.05–0.15 |
| Timeline Impact | Calendar delay, blocking other work | 0.10–0.20 |
| Cost | Infrastructure, licensing, operational cost | 0.05–0.15 |

**Scoring**: 1=Poor, 2=Below Average, 3=Adequate, 4=Good, 5=Excellent.

## 5. Integration Rules

- Full DAR → always writes an ADR at `docs/specs/decisions/ADR-[topic]-[YYYYMMDD].md`
- Quick DAR → recorded inline in the stage artifact that raised it (SRS, TECH, work log)
- If a DAR revisits a previous decision → mark the old ADR SUPERSEDED and reference its ID from the new one
- Before implementation starts, verify every NEEDS RESOLUTION decision has a DAR
- **"Why not" is mandatory** — every rejected option MUST have a recorded rationale

## 6. Stage Responsibility

| Stage | DAR Responsibility |
|-------|-------------------|
| `design-function` | Full DAR for architecture decisions in the BASIC/DETAIL design |
| `architecture` | Full DAR for cross-cutting/system-level decisions; writes the ADR |
| `analyze-requirement` | Quick DAR for requirement ambiguity resolution |
| `implement-feature` | Quick DAR for implementation approach choices during coding |

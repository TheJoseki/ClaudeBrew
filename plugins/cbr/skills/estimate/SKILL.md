---
name: estimate
description: "WBS estimation for any software feature. Breaks down scope into tasks, assigns complexity points, converts to MD/MM, and produces a structured estimate document. TRIGGER: user asks to estimate a feature, create a WBS, plan effort, or size work. NOT FOR: creating implementation plans (use plan-writing), or estimating ongoing sprint velocity."
allowed-tools: Read, Grep, Glob, Write, Edit
argument-hint: "[feature description]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Estimate — WBS Feature Estimation

Feature to estimate:

$ARGUMENTS

## Live Project Context (auto-injected)

- PROJECT.md exists: !`test -f PROJECT.md && echo "YES — read for team size and methodology" || echo "NOT FOUND — will ask user"`
- Existing estimates: !`ls docs/estimates/EST-*.md 2>/dev/null | tail -3 || echo "(no prior estimates found)"`

---

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect:
- Team composition and size
- Methodology (Agile / Waterfall / Kanban)
- Sprint length if applicable
- Tech stack (affects complexity of specific tasks)

If PROJECT.md not found → ask user: "What is the team size and methodology for this estimate?"

---

## Content Map

| Section | When to read |
| ------- | ------------ |
| Step 0 | Always — detect team context first |
| Step 1: Scope Breakdown | Always — mandatory before estimating |
| Step 2: Complexity Points | Always — core estimation |
| Step 3: MD/MM Conversion | When team size and velocity are known |
| Step 4: Phase Ratios | When full project estimate is requested |
| Output | Always — mandatory artifact |

---

## Step 1: Scope Breakdown (WBS)

Decompose $ARGUMENTS into work items using this hierarchy:

```
Phase
  └── Module / Component
        └── Task (atomic unit — 1 person, 1-5 days max)
              └── Sub-tasks (optional — for ≥3 day tasks)
```

**Categories to cover**:
- Backend: schema, migration, service, controller, DTO, auth guard
- Frontend: component, state, form, routing, UI integration
- Tests: unit test cases, integration test cases
- DevOps: config, env, CI change (if applicable)
- Documentation: if required

---

## Step 2: Complexity Points

Assign story points to each task using this scale:

| Points | Meaning |
|--------|---------|
| 1 | Trivial — config change, rename, copy-paste template |
| 2 | Simple — single function, standard CRUD endpoint |
| 3 | Moderate — service with business logic, API with validation |
| 5 | Complex — multi-service interaction, non-trivial algorithm |
| 8 | Very Complex — architecture change, external integration |
| 13 | Epic — break down further before estimating |

**Rule**: If a task is 13 points, it MUST be broken down before proceeding.

---

## Step 3: MD/MM Conversion

Use the bundled calculator script for accurate results (avoids arithmetic drift):

```bash
python ${CLAUDE_SKILL_DIR}/scripts/calc_estimate.py \
  --points [space-separated story points from Step 2] \
  --team [number of developers] \
  --velocity 0.5
```

Example: `python ${CLAUDE_SKILL_DIR}/scripts/calc_estimate.py --points 3 5 8 2 3 --team 2 --velocity 0.5`

**Manual calculation (fallback):**

1. Sum all story points for the feature
2. Apply velocity factor (from PROJECT.md, or use default: 1 point ≈ 0.5 developer-days)
3. Calculate duration:
   - MD (man-days) = total points × 0.5
   - MM (man-months) = MD ÷ (working days per month, typically 20)
4. Add buffer per complexity tier:
   - Simple feature (≤20 pts): +10% buffer
   - Medium feature (21–60 pts): +20% buffer
   - Large feature (61+ pts): +30% buffer

---

## Step 4: Phase Ratio Distribution

If full project estimate requested, distribute effort using these ratios:

| Phase | Typical Ratio | Adjusted for this feature |
|-------|--------------|--------------------------|
| Requirements (G1) | 10% | |
| Design (G2, G3a, G3b) | 15% | |
| Implementation (G4+) | 45% | |
| Testing (G6, G7) | 20% | |
| Bug fix + delivery (G8) | 10% | |

Adjust ratios based on feature complexity and team familiarity.

---

## Output: Estimate Document

File: `docs/estimates/EST-[feature]-[YYYYMMDD].md`

```markdown
# Estimate: [feature-name]

**Date**: [YYYY-MM-DD]
**Team**: [size + roles]
**Methodology**: [Agile / Waterfall]
**Estimation basis**: WBS story points (1 pt ≈ 0.5 developer-days)

## Summary

| Metric | Value |
|--------|-------|
| Total story points | X |
| Raw effort (MD) | X man-days |
| Buffer applied | X% |
| Adjusted effort (MD) | X man-days |
| Adjusted effort (MM) | X man-months |
| Recommended team | X developers |
| Calendar duration | X weeks (with team above) |

## WBS Breakdown

| # | Phase | Module | Task | Points | Notes |
|---|-------|--------|------|--------|-------|
| 1 | ... | ... | ... | 3 | |

## Phase Ratio

| Phase | Points | MD | % |
|-------|--------|----|----|

## Assumptions

- [assumption 1]
- [assumption 2]

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
```

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Prerequisite | `analyze-requirement` | SRS should exist before estimating — provides clear scope |
| Prerequisite | `brainstorming` | Run first if feature scope is not yet defined |
| On success | `plan-writing` | Create implementation plan from the WBS |
| On success | `full-sdlc` | Use estimate to inform sprint planning |
| Related | `orchestrate` | Orchestrator may call estimate during Phase 0 triage |

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Estimate from feature title alone | Break down to task level first |
| Use single-point estimates | Acknowledge uncertainty with buffer |
| Ignore testing in estimates | Testing is 20% of effort |
| Estimate without team context | Team size and velocity matter |
| Treat estimate as commitment | Estimate is a forecast, not a contract |

---

## Reference

For a worked example of the expected output, see: `references/examples/EST-user-auth-example.md`

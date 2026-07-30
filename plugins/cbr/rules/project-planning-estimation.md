---
description: Standards for WBS decomposition, estimation methodology, and sprint planning. Governs WHEN and HOW to estimate. /estimate skill handles execution; this rule defines the process.
---

# Project Planning & Estimation — ClaudeBrew

> Work decomposition standards, estimation rules, and planning conventions. The `/estimate` skill executes estimation; this rule defines when, how, and what standards govern the process.

## 1. WBS Decomposition Hierarchy

```
EPIC (multi-wave, weeks-months)
  └── Feature (standalone deliverable, days-weeks)
        └── User Story (user-visible behavior, 1-8 SP)
              └── Task (atomic, 1 person, ≤4 hours estimated)
```

## 2. Granularity Rules

| Level | Max Size | If Exceeded |
|-------|----------|-------------|
| EPIC | No limit | Must decompose into Features (via WAVE plans) |
| Feature | 60 SP total | Must decompose into WAVE plan |
| User Story | 8 SP | Must split into smaller stories |
| Task | 4 hours | Must split into sub-tasks |

**No task > 4 hours.** If you cannot estimate confidently below 4h, it needs decomposition.

## 3. Story Point Scale (Fibonacci)

| SP | Meaning | Reference Example |
|----|---------|-------------------|
| 1 | Trivial | Config change, rename, env variable |
| 2 | Simple | Single CRUD endpoint, standard component |
| 3 | Typical | API endpoint with validation + business logic |
| 5 | Complex | Multi-service interaction, state management |
| 8 | Very Complex | External integration, architecture change |
| 13 | Needs decomposition | **MUST break down before estimating** |

## 4. Uncertainty Multiplier

Apply AFTER base estimation, based on technology familiarity:

| Tech Familiarity | Multiplier | When to Apply |
|-----------------|------------|---------------|
| Known (project already uses) | ×1.0 | Extending existing patterns |
| Familiar (team has used before) | ×1.3 | New module, same stack |
| New (first time in this project) | ×1.5 | New library/framework |
| Experimental (no team experience) | ×2.0 | Proof of concept needed |

## 5. Phase Effort Allocation

When estimating full feature lifecycle (not just implementation):

| Phase | % of Total | Maps to Gates |
|-------|-----------|---------------|
| Analysis + Requirements | 15% | G1 |
| Design (Basic + Detail) | 20% | G2, G3a, G3b |
| Implementation + Review | 35% | G4, G5 |
| Testing (UT + IT) | 20% | G6, G7 |
| Bug Fix + Delivery | 10% | G8 |

## 6. Estimation Triggers

| Trigger | Who Estimates | Output |
|---------|--------------|--------|
| New feature request | orchestrator (via `/estimate`) | `docs/estimates/EST-[feature]-[YYYYMMDD].md` |
| Scope change during development | orchestrator | Update existing EST |
| EPIC decomposition into WAVEs | orchestrator | EST per WAVE |
| Sprint planning | orchestrator | Sprint capacity check |
| 3-Strike escalation | affected agent | Re-estimate remaining work |

## 7. Re-estimation Triggers

MUST re-estimate when ANY of these occur:
- Scope change (requirements added or removed)
- Blocked task unblocked with different approach
- 3-Strike escalation → remaining work likely larger
- Actual effort exceeds estimate by >50% at mid-point
- Technology uncertainty resolved (adjust multiplier)

## 8. Sprint Planning Rules

When project uses sprints (declared in PROJECT.md):

- **Capacity** = team_size × sprint_days × 0.7 (70% utilization)
- **Velocity** = average SP completed in last 3 sprints (default: 1 SP ≈ 0.5 dev-days)
- **Sprint load** ≤ velocity × 0.9 (10% buffer for unplanned work)
- **Carry-over**: >20% carry-over for 2 consecutive sprints → reduce planned load by 15%

## 9. Dependencies and Critical Path

Every PLAN WBS MUST identify:
- **Blockers**: Tasks that cannot start until predecessor completes
- **Parallel paths**: Independent tasks that can run concurrently
- **Critical path**: Longest sequential chain (determines minimum calendar time)

Format in PLAN WBS table — add `Depends On` column:

```markdown
| ID | Task | SP | Depends On | Batch | Status |
|----|------|----|-----------|-------|--------|
| T-01 | User model | 2 | — | B1 | PENDING |
| T-02 | Auth service | 3 | T-01 | B1 | PENDING |
| T-03 | Login UI | 3 | — | B2 | PENDING |
| T-04 | Auth integration | 5 | T-02, T-03 | B2 | PENDING |
```

## 10. Estimation Accuracy Tracking

After feature delivery (G8 pass), orchestrator MUST record:

```markdown
## Estimation Accuracy (append to EST-[feature].md)
| Metric | Estimated | Actual | Variance |
|--------|-----------|--------|----------|
| Total SP | X | X | +/- X% |
| Calendar days | X | X | +/- X% |
| Rework rounds | X | X | — |
```

Feed variance into `docs/memory/PROJECT-MEMORY.md` for calibrating future estimates.

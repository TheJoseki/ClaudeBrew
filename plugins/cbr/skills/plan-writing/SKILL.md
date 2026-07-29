---
name: plan-writing
description: Creates clear, actionable implementation plans with task breakdowns and verification criteria. Trigger when planning features, creating sprint plans, writing work breakdown structures, or preparing multi-agent execution plans. NOT FOR: full end-to-end feature delivery from requirements to tests (use full-sdlc), quick bug fixes (use fix-bug).
allowed-tools: Read, Grep, Glob
argument-hint: "[feature or task to plan]"
metadata:
  version: "3.1"
  category: meta
---

# Plan Writing

$ARGUMENTS

---

## Task Breakdown Properties

| Property | Definition |
| -------- | ---------- |
| Small | Completable in one session |
| Focused | One deliverable per task |
| Verifiable | Concrete done condition |
| Independent | Can be picked up without verbal briefing |
| Ordered | Dependencies are explicit |

---

## Planning Principles

1. **Keep it short** — fits on one screen. If you need to scroll, simplify.
2. **Be specific** — name the file, function, or endpoint. Not "implement feature".
3. **Mark dependencies** — if Task B needs Task A, say so.
4. **Update as you go** — stale status is worse than no plan.
5. **Separate phases from tasks** — phases group; tasks are atomic.

---

## Plan Structure

```markdown
# Plan: [Feature Name]
**Date**: YYYY-MM-DD | **Status**: IN_PROGRESS

| Phase | Task | Input | Output | Status |
|-------|------|-------|--------|--------|
| Design | Write TECH spec | SRS doc | TECH-[f].md | PENDING |
| Implement | Backend service | TECH spec | Service + tests | PENDING |
| Review | Code review | DEV log | REVIEW report | PENDING |
| Test | Unit tests | UTC doc | UTR report | PENDING |

## Done Conditions
- All phases DONE
- Tests 100% PASS
- Code review PASS
```

---

## Multi-Agent Extension

Add agent assignments for parallel execution:

| Phase | Task | Agent | Status |
| ----- | ---- | ----- | ------ |
| 3a | Implementation | developer-agent | PENDING |
| 3b | Unit test cases | unit-test-agent | PENDING |
| 3c | Integration test cases | integration-test-agent | PENDING |

Phases 3a/3b/3c are parallel — launch all three in a single message.

---

## Status Values

`PENDING` | `IN_PROGRESS` | `BLOCKED` | `DONE` | `SKIPPED`

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Verbose task descriptions | One line per task |
| Generic names ("implement feature") | Name specific file/endpoint |
| No done condition | Verifiable completion criterion |
| Plan not updated | Update status immediately |
| All tasks parallel | Sequence dependent tasks |
| Plan for hypothetical needs | Plan current scope only |

Save plans to: `docs/plans/PLAN-[feature]-[YYYYMMDD].md`

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Prerequisite | `brainstorming` | Run first if task scope is unclear before planning |
| Prerequisite | `analyze-requirement` | Ensure SRS exists before writing implementation plan |
| On success | `implement-feature` | Execute the plan — design already done |
| On success | `full-sdlc` | For end-to-end delivery of the planned feature |
| On FAIL (requirements unclear) | `analyze-requirement` | Revisit requirements before retrying plan |
| Related | `orchestrate` | Orchestrator uses plan-writing to create PLAN artifacts |

---

## Reference

For a worked example of the expected output, see: `references/examples/PLAN-example.md`

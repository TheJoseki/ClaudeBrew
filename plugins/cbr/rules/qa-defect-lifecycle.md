---
description: Formal defect management process — test execution model, defect classification, fix-retest cycle, evidence requirements. Complements R5 retry loops in sdlc-conventions.md.
---

# QA Defect Lifecycle

> Defines the formal process for test execution, defect management, and fix-retest cycles. Individual agents know HOW to test — this file defines the PROCESS they must follow.

## 1. Test Execution Model (Run-All-First — MANDATORY)

```
WRONG: Run TC-001 → fail → fix → Run TC-002 → fail → fix → ...
RIGHT: Run ALL TCs → collect FULL defect list → batch fix → retest ALL
```

Every test round (R1..R5) follows this sequence:

1. **RUN ALL** — Execute every test case in the suite. No short-circuiting on first failure.
2. **COLLECT** — Document every failure in a structured defect list (see §3).
3. **CLASSIFY** — Assign severity and priority to each defect (see §2).
4. **FIX** — Fix all defects in the batch. No cherry-picking.
5. **REGRESSION** — Retest the ENTIRE suite, not just fixed items. New failures = new defects.
6. **REPORT** — Create UTR/ITR report with full pass/fail breakdown.

## 2. Round Progression (complements sdlc-conventions.md R5 limit)

| Round | Entry Condition | Expected Outcome |
|-------|----------------|------------------|
| R1 | First execution after code review PASS | Baseline — establish initial pass rate |
| R2 | R1 defects fixed | ≥70% pass rate |
| R3 | R2 defects fixed | ≥90% pass rate |
| R4 | R3 defects fixed | ≥95% pass rate |
| R5 | R4 defects fixed | 100% — GATE. If not → escalate to user |

**Between rounds**: Only bug fixes allowed. No refactoring, no new features, no scope changes.

## 3. Defect Classification

### Severity (impact on system)

| Level | Name | Criteria |
|-------|------|----------|
| S1 | Critical | System crash, data loss, security breach, auth bypass |
| S2 | Major | Feature broken, no workaround, CRUD fails, wrong data, role access wrong |
| S3 | Minor | Feature degraded, workaround exists, sorting/pagination off-by-one |
| S4 | Info | Cosmetic, typo in error message, verbose logs, improvement suggestion |

### Priority (urgency of fix)

| Level | Name | Action |
|-------|------|--------|
| P1 | Immediate | Fix before next round. S1 always; S2 if blocks other tests |
| P2 | High | Fix in current round. S2 standard; S3 if easy fix |
| P3 | Normal | Fix if time permits. S3 standard |
| P4 | Low | Defer to backlog. S4 always |

**Rule**: S1/S2 → always P1/P2. S4 → always P4. S3 → P2/P3 based on effort.

## 4. Defect Report Format

Every defect found during testing MUST be documented:

```markdown
### DEF-[round]-[nn]: [Short description]
- **Severity**: S[1-4] | **Priority**: P[1-4]
- **TC ID**: TC-UT-XXX or TC-IT-XXX
- **Steps**: [Minimal reproduction steps]
- **Expected**: [What should happen]
- **Actual**: [What happened — include error output]
- **Root Cause**: [After fix — category + causal chain]
- **Fix**: [File:line — what was changed]
- **Evidence**: [Test output showing fix works]
```

## 5. Root Cause Analysis (MANDATORY for every defect fix)

| RCA Field | Required | Purpose |
|-----------|----------|---------|
| Category | Yes | Logic, Validation, Auth, ORM, State, Config, Integration, Typo |
| Causal Chain | Yes | "X causes Y which manifests as Z" — trace to true root |
| Blast Radius | Yes | Grep for same pattern elsewhere. If found → fix ALL locations |
| Missing Test | Yes | What test case would have prevented this? Add it |
| Preventive Action | If recurring (2+) | Recommend lint rule, checklist item, or coding rule update |

## 6. Evidence Requirements

### For Every Test Round Report

| Evidence | Format | Required |
|----------|--------|----------|
| Pass/fail summary | Table: total, passed, failed, skipped, pass rate % | Always |
| Failed TC details | DEF entries per §4 format | When failures exist |
| Test command output | Actual terminal output (truncated if >50 lines) | Always |
| Coverage report | Statement/branch/function percentages | R3+ rounds |

### For Every Defect Fix

| Evidence | Required |
|----------|----------|
| Before state (error output or failing test) | Always |
| After state (passing test output) | Always |
| Regression check (full suite pass/fail count) | Always |

**Rule**: No fabricated evidence. Tests MUST be actually executed. Cannot run → report BLOCKED.

## 7. Regression Testing Mandate

After ANY code change during a fix round:
1. Run the FULL test suite — not just the affected test
2. New failures not in previous round = REGRESSIONS → auto S2/P1
3. Increasing regression count across rounds = STOP signal → escalate

## 8. Integration with Existing Rules

| Existing Rule | This Rule Adds |
|--------------|----------------|
| `sdlc-conventions.md` R5 retry loops | Formal round progression with expected pass rates |
| `sdlc-conventions.md` quality gates G6/G7 | Evidence and classification requirements for gate decisions |
| `agent-best-practices.md` 3-strike rule | Applies to individual bug fixes within a round |
| `agent-best-practices.md` completion status | UTR/ITR must use DONE/BLOCKED status with evidence per round |

## 9. Deferred Defects (P4 items)

S4/P4 defects not fixed within R5:
1. Append to `docs/plans/BACKLOG-REGISTRY.md` as `CODE_QUALITY` type
2. Reference in final test report under `## Deferred Items`
3. Not counted as failures for gate pass/fail — but MUST be documented

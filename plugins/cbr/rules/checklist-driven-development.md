---
description: Mandates checklist usage at coding and review stages. Enforces self-review before code review, evidence in work logs, and checklist update protocol.
---

# Checklist-Driven Development

> Mandates that checklists are USED (not just exist) at every coding and review stage. Templates exist in `docs/_templates/` — this file enforces their usage.

## 1. Checklist Lifecycle

```
design-function (Step D1)        → Creates/updates docs/CODING-CHECKLIST.md
implement-feature (self-review)  → Reviews code against CODING-CHECKLIST.md
review-code (audit)              → Reviews against CODING-CHECKLIST.md + CODE-REVIEW-CHECKLIST.md
Any stage (discovery)            → Updates checklist when new pattern found
```

## 2. CODING-CHECKLIST.md — Creation Rules

| Rule | Detail |
|------|--------|
| Who creates | `design-function` at Step D1 (after the TECH spec, before implementation) |
| Template | `docs/_templates/CODING-CHECKLIST.md` |
| Customization | ALL `[PROJECT_SPECIFIC]` placeholders replaced with actual values from PROJECT.md |
| Location | `docs/CODING-CHECKLIST.md` (project root docs/, one per project) |
| Update trigger | New feature adds new patterns not in checklist → `design-function` adds a section |
| Block if missing | `implement-feature` MUST NOT proceed to coding if this file is absent |

## 3. Developer Self-Review (MANDATORY before work log)

### Process
1. After coding is complete, BEFORE creating work log
2. Open `docs/CODING-CHECKLIST.md`
3. Check EVERY item against the code just written
4. Record results in work log under `## Self-Review Results`

### Evidence Format in Work Log

```markdown
## Self-Review Results
Checklist: docs/CODING-CHECKLIST.md
Date: [YYYY-MM-DD]

| Section | Items | Pass | Fail | N/A |
|---------|-------|------|------|-----|
| Security | 8 | 7 | 0 | 1 |
| Data Layer | 7 | 7 | 0 | 0 |
| API Layer | 6 | 6 | 0 | 0 |
| Frontend | 7 | 5 | 0 | 2 |
| Code Quality | 6 | 6 | 0 | 0 |

N/A Justifications:
- Security §1.5 (CSRF): N/A — API-only, no browser forms
- Frontend §4.5 (i18n): N/A — backend-only batch
```

### Rules
- Every N/A item MUST have a one-line justification
- Any FAIL item MUST be fixed before submitting — or flagged as BLOCKED with reason
- Zero evidence of self-review → code review agent flags as Major finding

## 4. Code Review Agent Audit (MANDATORY)

### Two-Checklist Review
1. **CODING-CHECKLIST.md** — Verify developer's self-review was thorough
2. **CODE-REVIEW-CHECKLIST.md** — Two-pass methodology (Critical pass + Informational pass)

### Process
1. Read developer's self-review results from work log
2. Spot-check: verify ≥3 items the developer marked PASS (are they really passing?)
3. Run full CODE-REVIEW-CHECKLIST.md (Pass 1: Critical, Pass 2: Informational)
4. If developer self-review is missing → auto-flag as Major finding

### Evidence Format in Review Report

```markdown
## Checklist Audit
### Developer Self-Review Verification
- Self-review present: YES/NO
- Spot-checked items: [list 3+ items verified]
- Spot-check result: CONFIRMED / DISCREPANCY FOUND

### Code Review Checklist
| Pass | Items | Pass | Fail |
|------|-------|------|------|
| Pass 1 (Critical) | 12 | 11 | 1 |
| Pass 2 (Informational) | 7 | 6 | 1 |
```

## 5. Self-Review ≠ Code Review

| Aspect | Self-Review (Developer) | Code Review (Reviewer) |
|--------|------------------------|----------------------|
| Who | Whoever wrote the code | `review-code`, via a fresh `cbr:reviewer` that did not write it |
| When | Before creating work log | After work log submitted |
| Checklist | CODING-CHECKLIST.md | CODING-CHECKLIST.md + CODE-REVIEW-CHECKLIST.md |
| Purpose | Catch own mistakes | Catch issues developer missed; verify spec adherence |
| Substitutable? | **NO** — both required | **NO** — both required |

## 6. Checklist Update Protocol

When any stage discovers a pattern that should be checked but is NOT in the checklist:

| Step | Action |
|------|--------|
| 1 | Note the pattern in the work log or review report |
| 2 | Append it to `docs/CODING-CHECKLIST.md` under the matching section |
| 3 | Surface it to the user at the current stage's gate, so the next feature inherits it |
| 4 | If the pattern is Critical (security/data loss): update the checklist immediately and raise it before the gate, not after |

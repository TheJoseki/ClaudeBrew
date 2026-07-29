# Phases 5–8 — Execution & Delivery Protocol

> Reference for orchestrator-agent. Loaded on-demand when entering Phase 5+.

## Step 5: Security Scan

```
Agent tool call:
  subagent_type: "security-tester-agent"
  description: "OWASP security scan for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    TASK: OWASP Top 10:2025 security scan on all feature code.
    INPUT: docs/work-logs/DEV-[feature]-B*.md (all batch work logs)
    OUTPUT: docs/security/SEC-[feature]-[YYYYMMDD].md
    Verdict: PASS (0 Critical/High) or FAIL.
```

PASS → G5 ✅, proceed. FAIL → developer-agent fixes → re-scan.

## Step 6: Unit Tests (EXECUTE)

```
Agent tool call:
  subagent_type: "unit-test-agent"
  description: "Execute unit tests R[n] for [feature]"
  prompt: |
    MODE: EXECUTE | ROUND: R[n]
    INPUT: docs/test-cases/UTC-[feature].md
    OUTPUT: docs/test-reports/UTR-[feature]-R[n].md
    Run test commands from PROJECT.md.
```

If FAIL → spawn bug-fix-agent with UTR Bug Reports section → re-run R[n+1]. Max R5.
R5 PASS → G6 ✅.

## Step 7: Integration Tests (EXECUTE)

```
Agent tool call:
  subagent_type: "integration-test-agent"
  description: "Execute integration tests R[n] for [feature]"
  prompt: |
    MODE: EXECUTE | ROUND: R[n]
    INPUT: docs/test-cases/ITC-[feature].md
    OUTPUT: docs/test-reports/ITR-[feature]-R[n].md
    UI CHECK: If docs/specs/requirements/SCREEN-[feature].md exists → MUST use Mode C (MCP) first.
    Run test commands from PROJECT.md.
```

Same fix loop as Step 6. Max R5. R5 PASS → G7 ✅.

## Bug Fix Spawn (Steps 6–7 failures)

```
Agent tool call:
  subagent_type: "bug-fix-agent"
  description: "Fix test failures R[n]"
  prompt: |
    INPUT: [UTR or ITR report] Bug Reports section
    DESIGN CONTEXT:
      1. docs/specs/detail-design/TECH-[feature].md
      2. docs/plans/DECISION-LEDGER.md
      3. .claude/agent-memory/developer-agent/MEMORY.md — Common Pitfalls
    Fix all listed bugs. Create docs/bug-reports/BUG-[YYYYMMDD]-[nn].md for each.
```

---

## Step 8: Delivery (self — do NOT use Agent tool)

### Pre-G8 Blocker Scan (MANDATORY)

1. **Open bugs**: Glob `docs/bug-reports/BUG-*.md` — any PENDING + HIGH/CRITICAL → BLOCK G8
2. **Test gates**: G6 + G7 both ✅ PASS → OK. Any ⏳/❌ → BLOCK
3. **Security gate**: G5 ✅ PASS → OK. ❌ → BLOCK
4. **Registry update**: PLAN-REGISTRY → COMPLETED. Read BACKLOG for wave N+1 items.

### Delivery Report

```markdown
## Delivery: [Feature Name] — [YYYY-MM-DD]

### Artifacts
| Artifact | Location |
|----------|----------|
| Plan | docs/plans/PLAN-[f]-[date].md |
| SRS | docs/specs/requirements/SRS-[f].md |
| Screen | docs/specs/requirements/SCREEN-[f].md |
| Tech | docs/specs/detail-design/TECH-[f].md |
| Work Logs | docs/work-logs/DEV-[f]-B*.md |
| Reviews | docs/reviews/REVIEW-[f]-B*.md |
| Security | docs/security/SEC-[f]-[date].md |
| UTC/ITC | docs/test-cases/UTC-[f].md, ITC-[f].md |
| UTR/ITR | docs/test-reports/UTR-[f]-R*.md, ITR-[f]-R*.md |

### Test Summary
- Unit Tests: 100% PASS (R[n])
- Integration Tests: 100% PASS (R[n])
- Code Review: PASS (all batches)
- Security: PASS (0 Critical/High)
```

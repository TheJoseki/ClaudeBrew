# Phase 4 — Implementation Protocol

> Reference for orchestrator-agent. Loaded on-demand when entering Phase 4.

## Step 4 Pre: Spawn UTC + ITC Agents in Background

Spawn BOTH in the **same message** with `run_in_background: true`:

### UTC Agent (background):

```
Agent tool call:
  subagent_type: "unit-test-agent"
  run_in_background: true
  description: "Create UTC document for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: CREATE
    COMPLEXITY: [Small | Medium | Large]
    OBJECTIVE: Create Unit Test Cases document.
    INPUT:
      1. docs/specs/detail-design/TECH-[feature].md (PRIMARY)
      2. docs/TEST_VIEWPOINT.md
    OUTPUT ARTIFACT: docs/test-cases/UTC-[feature].md
    For Large complexity: write layer by layer using Edit (append).
    TASK BOUNDARIES:
      IN SCOPE — test cases, ISTQB technique distribution, coverage matrix
      NOT IN SCOPE — executing tests, writing .spec files
```

### ITC Agent (background):

```
Agent tool call:
  subagent_type: "integration-test-agent"
  run_in_background: true
  description: "Create ITC document for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: CREATE
    COMPLEXITY: [Small | Medium | Large]
    OBJECTIVE: Create Integration Test Cases document.
    INPUT:
      1. docs/specs/detail-design/TECH-[feature].md (PRIMARY)
      2. docs/specs/requirements/SRS-[feature].md
    OUTPUT ARTIFACT: docs/test-cases/ITC-[feature].md
    For Large complexity: write workflow by workflow using Edit (append).
    TASK BOUNDARIES:
      IN SCOPE — workflow scenarios, RBAC isolation, API chains
      NOT IN SCOPE — executing tests, writing scripts
```

---

## Step 4 Main: Per-Batch Loop (sequential)

Repeat for Batch-1, Batch-2 (Medium/Large), Batch-3 (Large):

### 4a. Spawn developer-agent for Batch-N:

```
Agent tool call:
  subagent_type: "developer-agent"
  description: "Implement [feature] Batch-N"
  prompt: |
    FEATURE ID: [feature-name] | BATCH: Batch-N
    OBJECTIVE: Implement Batch-N scope.
    SCOPE: [list modules from WBS Batch-N]
    INPUT:
      1. docs/specs/detail-design/TECH-[feature].md
      2. docs/specs/requirements/SCREEN-[feature].md (if FE)
    OUTPUT: code files + docs/work-logs/DEV-[feature]-BN.md
    TASK BOUNDARIES:
      IN SCOPE — Batch-N files only
      NOT IN SCOPE — other batches, refactoring outside scope
    CROSS-BATCH (if N > 1): Read work log from Batch-(N-1), verify API dependencies.
```

### 4a.1 Input Pruning Protocol (TIGHT batches only)

When the Context Budget Estimate table in the PLAN file marks a batch as **TIGHT** (150–200K):

1. **Spec pruning**: Spawn prompt specifies "Read ONLY sections [X, Y] of TECH spec relevant to Batch-N modules: [module list]" — do NOT read the entire TECH spec
2. **Dependency reads**: "Read ONLY the exported interface/types from [shared-module], NOT the full implementation. Use Grep to find the export signature, then Read only that section"
3. **Skip non-essential docs**: Skip `ARCHITECTURE.md`, `API_DESIGN.md`, `CODING_CONVENTION.md` — these are already encoded in the TECH spec
4. **Add CONTEXT BUDGET to spawn prompt**: Include `CONTEXT BUDGET: TIGHT (~[N]K estimated)` so developer-agent adjusts its checkpoint granularity

### 4a.2 PARTIAL Continuation (if developer-agent returns STATUS: PARTIAL)

If developer-agent returns `STATUS: PARTIAL — checkpoint at [layer]`:

1. Read the partial work log → extract remaining scope from "Remaining scope" section
2. Create **continuation batch Batch-N.1** with only the remaining files
3. Re-estimate context budget for continuation (usually SAFE since scope is smaller)
4. Spawn developer-agent with:
   - Only the remaining files in scope
   - Reference to original work log for context (file paths completed, decisions made)
   - Pruned TECH spec sections for remaining modules only
5. After continuation completes → merge both work logs into review scope
6. Code review covers BOTH original + continuation files as one unit

### 4b. Spawn code-review-agent for Batch-N:

```
Agent tool call:
  subagent_type: "code-review-agent"
  description: "Review [feature] Batch-N"
  prompt: |
    FEATURE ID: [feature-name] | BATCH: Batch-N
    OBJECTIVE: Review Batch-N code quality and spec adherence.
    INPUT:
      1. docs/work-logs/DEV-[feature]-BN.md (scope)
      2. docs/specs/detail-design/TECH-[feature].md (verify design match)
    OUTPUT: docs/reviews/REVIEW-[feature]-BN.md
    TASK BOUNDARIES: files in this batch's work log ONLY
```

### 4c. If REVIEW FAIL → fix loop (max R2):

Spawn developer-agent to fix Critical + Major findings. Re-spawn code-review-agent.

**R2+ Reflection Protocol**: If Batch-N fails review twice:
1. Read all review artifacts for this batch
2. Identify recurring pattern (same category? same layer?)
3. Write FLAG to `docs/agent-comms/flags/` with the pattern
4. Add pattern as explicit pre-check in R3 spawn prompt

### 4d. Batch PASS → update WBS, proceed to next batch.

---

## Step 4 Wait

After all batches complete, verify background UTC/ITC artifacts:

- If `docs/test-cases/UTC-[feature].md` EXISTS → mark DONE
- If MISSING → re-spawn in foreground (fallback)
- Same check for `docs/test-cases/ITC-[feature].md`

---

## Phase 4.5: Integration Smoke Test (after ALL batches, before Phase 5)

Verify BE endpoints from work logs cover all FE API calls.
If Playwright MCP available → spawn integration-test-agent Mode C for ONE happy-path flow.
Record in PLAN: `Phase 4.5 Smoke Test: PASS/FAIL [date]`
FAIL → fix before Phase 5. Do NOT run security scan on broken integration.

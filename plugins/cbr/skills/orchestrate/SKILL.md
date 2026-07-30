---
name: orchestrate
description: "PM Orchestrator for any project. Triage + plan + delegate to specialized agents with artifact tracking. Project domain and tech stack detected from PROJECT.md/CLAUDE.md."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
argument-hint: "[feature or enhancement description]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# PM Orchestrator

Task to orchestrate:

$ARGUMENTS

---

> **How it works**: This skill uses the Agent tool to spawn real subagents.
> Each phase = 1 Agent tool call (isolated subprocess).
> Orchestrator verifies artifacts after each phase, does NOT do the work itself.

---

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect:
- Project name and domain
- Tech stack (backend/frontend/ORM/test framework)
- Existing docs structure

Do NOT assume domain-specific workflows not mentioned in PROJECT.md.

## STEP 0: Triage & Plan — Self-execute

**Read:**
- `PROJECT.md` or `CLAUDE.md` — project context
- `docs/REQUIREMENTS_ANALYSIS.md`, `docs/ARCHITECTURE.md`, `docs/CODING_RULES.md` (if exist)
- `docs/plans/walkthrough.md` (current progress, if exists)

**Registry Initialization (first run only):**
If `docs/plans/PLAN-REGISTRY.md` does not exist, create it from `docs/_templates/PLAN-REGISTRY.md`.
If `docs/plans/DECISION-LEDGER.md` does not exist, create it from `docs/_templates/DECISION-LEDGER.md`.
If `docs/plans/BACKLOG-REGISTRY.md` does not exist, create it from `docs/_templates/BACKLOG-REGISTRY.md`.

**Classify:**
- Type: `NEW_FEATURE | ENHANCEMENT | BUG_FIX | UI_CHANGE | REFACTOR`
- Complexity: `Simple | Medium | Complex | Critical`

**Planning Council — Agent Teams (Medium+ only):**

After classification, if complexity = `Medium | Large | Complex | Critical`:

1. **TeamCreate**: "council-[feature]-[YYYYMMDD]"
2. **Spawn teammates concurrently** (both in same message):
   - ba-agent: `CONTEXT: AGENT_TEAMS`, `MODE: PLANNING` → `docs/plans/COUNCIL-[feature]-BA.md`
     Role instructions: Read `${CLAUDE_PLUGIN_ROOT}/agents/ba-agent.md` for full role definition.
     TEAMMATE NAME: "architect" (use SendMessage for cross-agent questions)
   - architect-agent: `CONTEXT: AGENT_TEAMS`, `MODE: PLANNING` → `docs/plans/COUNCIL-[feature]-ARCH.md`
     Role instructions: Read `${CLAUDE_PLUGIN_ROOT}/agents/architect-agent.md` for full role definition.
     TEAMMATE NAME: "ba" (check conversation for messages from ba-agent)
3. **Wait** for both teammates idle (TeammateIdle notification)
4. **Read** both COUNCIL artifacts → incorporate domain risks + refined sizing into PLAN (include Contradiction Resolutions if councils diverge)
5. **TeamDelete**: cleanup

Skip council for `Simple` features — create PLAN directly.
**Simple does NOT skip**: CAO registry reads, context injection, registry updates, or memory updates. Only the council (ba + architect debate) is skipped.

> RESUME: If interrupted during step 2-3, check if COUNCIL artifacts exist → skip to step 4. Otherwise re-run (idempotent).

### Auto-Resume Detection (MANDATORY — before creating new plan)

After reading PLAN-REGISTRY:
1. Search for matching feature in PLAN-REGISTRY (by feature name, fuzzy match)
2. IF ACTIVE or SUSPENDED plan found:
   → Read existing PLAN file
   → Find first phase with status ⏳ PENDING
   → Present to user: "Found existing plan [X] at Phase [N]. Resume? (Y/N)"
   → IF Yes → skip to that phase (no duplicate plan creation)
   → IF No → mark old plan SUPERSEDED in registry, then create new
3. IF COMPLETED plan found → note "ENHANCEMENT" in new plan, reference previous
4. IF no match → proceed normally with new plan

**Create Plan file** `docs/plans/PLAN-[feature]-[YYYYMMDD].md` (use Write tool).

**Update Plan Registry:** Append new plan to `docs/plans/PLAN-REGISTRY.md` (create if not exists).

**Context Injection (automatic):**
The `SubagentStart` hook auto-injects CAO context (active plans, relevant decisions, backlog items, accumulated memory) into every `*-agent` spawn. No manual action needed.

**Choose workflow:**

```
NEW_FEATURE / Complex  → Full SDLC (Step 1→8)
BUG_FIX               → Bug Fix workflow (Step B)
ENHANCEMENT / Medium  → Gap → Design → Implement → Test
Simple                → Implement → Review
```

---

## WORKFLOW: Full SDLC

### Step 1: ba-agent
```
Agent tool:
  subagent_type: "ba-agent"
  prompt: |
    FEATURE ID: [feature] | TASK: Write SRS
    INPUT: docs/plans/PLAN-[f]-[date].md
    OUTPUT: docs/specs/requirements/SRS-[feature].md
```
→ Read SRS → present → pause for user approval → update PLAN

### Step 2: ui-designer-agent
```
Agent tool:
  subagent_type: "ui-designer-agent"
  prompt: |
    FEATURE ID: [feature] | TASK: Design SCREEN spec
    INPUT: docs/specs/requirements/SRS-[feature].md
    OUTPUT: docs/specs/requirements/SCREEN-[feature].md
```
→ Read SCREEN → present → pause for user approval → update PLAN

### Step 3a: architect-agent (BASIC_DESIGN — 基本設計)
```
Agent tool:
  subagent_type: "architect-agent"
  prompt: |
    FEATURE ID: [feature] | MODE: BASIC_DESIGN
    TASK: Design module structure, DB table list, API endpoint list
    INPUT: docs/specs/requirements/SRS-[f].md, docs/specs/requirements/SCREEN-[f].md
    OUTPUT: docs/specs/basic-design/BASIC-[feature].md
```
→ Read BASIC → present → pause for user approval (G3a) → update PLAN

### Step 3b: architect-agent (DETAIL_DESIGN — 詳細設計)
```
Agent tool:
  subagent_type: "architect-agent"
  prompt: |
    FEATURE ID: [feature] | MODE: DETAIL_DESIGN
    TASK: Design full ORM schema, service methods, DTOs, error handling
    INPUT: docs/specs/requirements/SRS-[f].md, docs/specs/requirements/SCREEN-[f].md, docs/specs/basic-design/BASIC-[f].md
    OUTPUT: docs/specs/detail-design/TECH-[feature].md
```
→ Read TECH → present → pause for user approval (G3b) → update PLAN

### Step 4: PARALLEL (3 agent calls at the same time, run_in_background: true)
```
#1 developer-agent: implement code + work log
#2 unit-test-agent (MODE=CREATE): UTC document
#3 integration-test-agent (MODE=CREATE): ITC document
```
→ Wait for all 3 → verify 3 artifacts → update PLAN

### Step 5: code-review-agent
```
Agent tool:
  subagent_type: "code-review-agent"
  prompt: |
    INPUT: work log + TECH spec
    OUTPUT: docs/reviews/REVIEW-[f]-[date].md
```
→ PASS: proceed | FAIL: developer-agent fix → re-review

### Step 5.5: security-tester-agent (Security Scan — after all batches + review PASS)
```
Agent tool:
  subagent_type: "security-tester-agent"
  prompt: |
    FEATURE ID: [feature] | MODE: Mode A (Feature Scan)
    INPUT: docs/reviews/REVIEW-[f]-[date].md, docs/specs/detail-design/TECH-[f].md
    OUTPUT: docs/security/SEC-[f]-[date].md
    Scan: source code, API endpoints, database models, config files.
```
→ PASS (no Critical/High): proceed to Step 6 | FAIL: developer-agent fix → re-scan

### Step 6: unit-test-agent (EXECUTE R1→R5)
```
Agent tool:
  subagent_type: "unit-test-agent"
  prompt: MODE=EXECUTE ROUND=R[n], OUTPUT: UTR-[f]-R[n].md
```
→ PASS: proceed | FAIL: bug-fix-agent → re-run R[n+1], max R5

### Step 7: integration-test-agent (EXECUTE R1→R5)
```
Agent tool:
  subagent_type: "integration-test-agent"
  prompt: MODE=EXECUTE ROUND=R[n], OUTPUT: ITR-[f]-R[n].md
```
→ Same loop as Step 6

### Step 8: Delivery (self-execute)

**Registry Updates:**
1. Update `docs/plans/PLAN-REGISTRY.md` — set current plan status → `✅ COMPLETED`
2. Read `docs/plans/BACKLOG-REGISTRY.md` — include any HIGH priority open items in Delivery Report warnings

Update PLAN + walkthrough → present Delivery Report (include BACKLOG warnings if any HIGH items exist)

---

## WORKFLOW: Bug Fix

### Step 0: Create Plan (type=BUG_FIX)

### Step B1: bug-fix-agent
```
Agent tool:
  subagent_type: "bug-fix-agent"
  prompt: |
    BUG: [description + error + steps to reproduce]
    INPUT (read in this order):
      1. Bug report / test failure details
      2. docs/specs/detail-design/TECH-[feature].md — design source of truth
      3. docs/plans/DECISION-LEDGER.md — check CONTESTED decisions
      4. .claude/agent-memory/bug-fix-agent/MEMORY.md — Common Pitfalls section
    OUTPUT: docs/bug-reports/BUG-[YYYYMMDD]-[nn].md + fixed code
    TASK BOUNDARIES:
      IN SCOPE — diagnose root cause, fix bug, verify fix, preventive action
      NOT IN SCOPE — refactoring, new features, scope creep
```

### Step B2: unit-test-agent (EXECUTE)
```
Agent tool:
  subagent_type: "unit-test-agent"
  prompt: MODE=EXECUTE ROUND=R1, output UTR-[f]-R1.md
```

### Step B3: code-review-agent
```
Agent tool:
  subagent_type: "code-review-agent"
  prompt: Review scope = fix files only, output REVIEW-[f]-[date].md
```

### Step B4: Update walkthrough DONE

---

## WORKFLOW: Enhancement

### Step 0: Context (MANDATORY — same CAO protocol as all workflows)
Read PLAN-REGISTRY, DECISION-LEDGER, BACKLOG-REGISTRY, PROJECT-MEMORY.
Context injection before EVERY agent spawn.

### Step E1: Gap Analysis (orchestrator — self-execute)
Read existing TECH spec for feature → identify what changes are needed.
If no TECH spec exists → route to architect-agent for design first.

### Step E2: architect-agent (DETAIL_DESIGN — delta only)
Design only the changed/new parts. Reference existing TECH spec.

### Step E3: developer-agent (implement changes)
Spawn with TECH spec (original + delta) + context injection.

### Step E4: code-review-agent → review changes

### Step E5: unit-test-agent (EXECUTE) → test changes

### Step E6: Delivery + PLAN-REGISTRY update + memory save

---

## WORKFLOW: Simple (1-2 files)

```
Step 0: Plan (complexity=Simple)
  0.1b: Registry init (if first run)
  0.2c: CAO Registry Read (MANDATORY) — read PLAN-REGISTRY, DECISION-LEDGER, BACKLOG-REGISTRY, PROJECT-MEMORY
  0.4:  Create PLAN (reference relevant decisions/backlog in plan)
  0.4b: Update PLAN-REGISTRY
Step 4a: developer-agent → implement + work log (with context injection in spawn prompt)
Step 5: code-review-agent → review (with context injection in spawn prompt)
Step 8: update walkthrough DONE + update PLAN-REGISTRY status → COMPLETED + agent memory update
```

**Simple skips ONLY**: Planning Council (Step 0.3). Everything else runs.

---

## Quality Gates (DO NOT SKIP)

| Gate | Pass condition | Action if FAIL |
|------|---------------|----------------|
| Phase 1-3 | User approval | Revise → re-spawn |
| Phase 5 | REVIEW = PASS | dev fix → re-review |
| Phase 5.5 | Security scan 0 Critical/High | dev fix → re-scan |
| Phase 6 | UTR 100% | bug-fix → R[n+1], max R5 |
| Phase 7 | ITR 100% | bug-fix → R[n+1], max R5 |

## Success Criteria
- All 8 phases complete with artifacts in `docs/`
- Code Review: PASS
- Security Scan: PASS (no Critical/High)
- Unit Tests: 100% pass rate (R5)
- Integration Tests: 100% pass rate (R5)

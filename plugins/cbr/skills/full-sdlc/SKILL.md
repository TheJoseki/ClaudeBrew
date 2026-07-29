---
name: full-sdlc
description: Orchestrate full SDLC lifecycle for any project. From requirement → UI design → technical design → implementation → code review → testing → bug fixing. Tech stack detected from PROJECT.md/CLAUDE.md. TRIGGER: user wants to build a complete new feature end-to-end from requirements to delivery. NOT FOR: quick bug fixes (use fix-bug), single-file changes, or already-designed features (use implement-feature).
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
argument-hint: "[feature description]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Full SDLC Lifecycle

Feature to develop:

$ARGUMENTS

---

> **How it works**: This skill runs in the current context (with Agent tool).
> Each phase = 1 Agent tool call spawning an independent subprocess.
> Orchestrator verifies artifact after each phase, does NOT do the work itself.

---

## PHASE 0: Plan — Self-execute + Optional Planning Council

**Read first:**
- `CLAUDE.md` or `PROJECT.md` — detect tech stack, project name, domain
- `docs/REQUIREMENTS_ANALYSIS.md`, `docs/ARCHITECTURE.md` (if exist)
- `docs/API_DESIGN.md`, `docs/SCREEN_DESIGN.md`, `docs/CODING_RULES.md` (if exist)
- `docs/plans/walkthrough.md` (current progress, if exists)

**Registry Initialization (first run only):**
If `docs/plans/PLAN-REGISTRY.md` does not exist → create from `docs/_templates/PLAN-REGISTRY.md`.
If `docs/plans/DECISION-LEDGER.md` does not exist → create from `docs/_templates/DECISION-LEDGER.md`.
If `docs/plans/BACKLOG-REGISTRY.md` does not exist → create from `docs/_templates/BACKLOG-REGISTRY.md`.
If `docs/memory/PROJECT-MEMORY.md` does not exist → create from `docs/_templates/PROJECT-MEMORY.md`.
Auto-create directories: `docs/memory/`, `docs/retros/` if missing.

**Triage:** Classify type (NEW_FEATURE/ENHANCEMENT/BUG_FIX) and complexity (Simple/Medium/Complex/Critical).

**Backlog Integration:** Read `docs/plans/BACKLOG-REGISTRY.md` → incorporate any HIGH priority OPEN items targeting this feature into the PLAN WBS.

### Planning Council — Agent Teams (Medium/Large/Complex/Critical only)

Skip for **Simple** features — create PLAN solo.

**P1:** TeamCreate: name = "council-[feature]-[YYYYMMDD]"

**P2:** Spawn ba-agent + architect-agent **concurrently** in same message.
→ Full spawn prompts: `references/spawn-templates.md` §Phase 0 Council

**P3:** Wait for both teammates idle (TeammateIdle notification — do NOT proceed until both are idle)

**P4:** Read artifacts and synthesize:
1. Read `docs/plans/COUNCIL-[feature]-BA.md`
2. Read `docs/plans/COUNCIL-[feature]-ARCH.md`
3. Check conversation for any SendMessage exchanges
4. Incorporate council insights into PLAN (domain risks, sizing, Contradiction Resolutions)

**P5:** TeamDelete: "council-[feature]-[YYYYMMDD]"

> RESUME: If session interrupted during P2-P3, Agent Teams teammates cannot be
> restored via /resume. Check if both COUNCIL artifacts exist → if yes, skip to P4.
> If missing, re-run P1-P3 (idempotent).

### Phase 0b: Sizing Analysis (MANDATORY — determines batch count)

After reading SRS, calculate sizing from deliverable count:

| Signal | Small | Medium | Large |
|--------|-------|--------|-------|
| Deliverables (screens / endpoints / jobs / workers) | ≤3 | 4–8 | 9+ |
| Modules | ≤3 | 4–8 | 9+ |
| API Endpoints | ≤10 | 11–25 | 26+ |

**Dev batch plan based on sizing:**

| Sizing | Dev Batches | Background Agents (pre-Phase 4) |
|--------|-------------|--------------------------------|
| **Small** | 1 batch (all modules) | 1 UTC + 1 ITC (background) |
| **Medium** | 2 batches (BE / FE split) | 1 UTC + 1 ITC (background) |
| **Large** | 3 batches (domain splits) | 1 UTC + 1 ITC (background) |

Record sizing decision in PLAN file.

### Auto-Resume Detection (MANDATORY — before creating new plan)

After reading PLAN-REGISTRY (Step 0.2c):
1. Search for matching feature in PLAN-REGISTRY (by feature name, fuzzy match)
2. IF ACTIVE or SUSPENDED plan found:
   → Read existing PLAN file
   → Find first phase with status ⏳ PENDING
   → Present to user: "Found existing plan [X] at Phase [N]. Resume? (Y/N)"
   → IF Yes → skip to that phase (no duplicate plan creation)
   → IF No → mark old plan SUPERSEDED in registry, then create new
3. IF COMPLETED plan found → note "ENHANCEMENT" in new plan, reference previous
4. IF no match → proceed normally with new plan

→ Create `docs/plans/PLAN-[feature]-[YYYYMMDD].md` using template: `references/plan-template.md`

**Update Plan Registry:** Append new plan entry to `docs/plans/PLAN-REGISTRY.md` with status `✅ ACTIVE`, type, and parent (if applicable).

**Append** checkpoint to `docs/plans/walkthrough.md` (if exists).

---

### Context Injection Protocol (applies to ALL phases below)

Before EVERY Agent tool call in Phases 1-7, invoke `context-inject` internally:
```
AGENT_ROLE: [agent being spawned]
FEATURE: [feature name]
PHASE: [current phase number]
DOMAIN_TAGS: [relevant domain tags from PLAN]
PLAN_FILE: docs/plans/PLAN-[feature]-[YYYYMMDD].md
```
Prepend the returned context block to the agent's spawn prompt. This ensures every agent starts with awareness of active plans, relevant decisions, backlog items, and accumulated memory.

---

## PHASE 1: Requirement Analysis

Spawn **ba-agent** → full prompt at `references/spawn-templates.md` §Phase 1

**After return:**
1. Read `docs/specs/requirements/SRS-[feature].md` → present to user
2. PAUSE — wait for user approval (G1)
3. If "Revise": re-spawn ba-agent with feedback
4. If "Approved": update PLAN `⏳` → `✅ DONE`, update walkthrough

---

## PHASE 2: UI/UX Design

Spawn **ui-designer-agent** → full prompt at `references/spawn-templates.md` §Phase 2

**After return:** Read artifact → present → pause for approval (G2) → update PLAN.

---

## PHASE 3a: Basic Design (基本設計)

**Standard** (Small/Medium features):
Spawn **architect-agent** (MODE: BASIC_DESIGN) → full prompt at `references/spawn-templates.md` §Phase 3a

**After return:** Read BASIC → present → pause for approval (G3a) → update PLAN T-03a ✅

**Voting Design (Complex/Critical only — 8+ endpoints OR 5+ tables):**
Spawn **2 architect-agents in parallel** with `run_in_background: true`
→ Full prompts + synthesis steps at `references/spawn-templates.md` §Phase 3a Enhanced

---

## PHASE 3b: Detail Design (詳細設計)

Spawn **architect-agent** (MODE: DETAIL_DESIGN) → full prompt at `references/spawn-templates.md` §Phase 3b

**After return:** Read TECH → present → pause for approval (G3b) → update PLAN T-03b ✅

---

## PHASE 3c: G3c Gate — Test Viewpoint Approval (MANDATORY before Phase 4)

> **Why this gate exists**: architect-agent's Step D2 fills in TEST_VIEWPOINT Section 0 with the actual
> test database, test runner, and E2E framework for this project. Proceeding without user approval means
> test agents may silently run against the wrong infrastructure — all tests pass, nothing real is verified.

**Self-execute (orchestrator):**

1. Read `docs/TEST_VIEWPOINT.md` Section 0 (written by architect-agent Step D2)
2. **If Section 0 is missing or still has `[PLACEHOLDER]` tokens** → re-spawn `architect-agent`:
   ```
   Agent tool → subagent_type: architect-agent
     MODE: DETAIL_DESIGN
     TASK: Step D2 only — fill TEST_VIEWPOINT Section 0 from PROJECT.md values. Do not rewrite TECH spec.
     INPUT: docs/specs/detail-design/TECH-[feature].md, docs/TEST_VIEWPOINT.md, PROJECT.md
   ```
3. Present Section 0 to user — highlight:
   - Integration test DB engine (must match `TEST_DB_ENGINE` in PROJECT.md)
   - E2E framework choice (`E2E_FRAMEWORK` — or "N/A" for backend-only)
   - Test runner per layer
4. **Wait for user approval**
5. On approval → update Section 0 status: `⏳ PENDING APPROVAL` → `✅ APPROVED`
6. Record in PLAN file: `G3c — Test Viewpoint: ✅ APPROVED [date]`
7. Update WBS: add row `| T-03c | 3c. Test Viewpoint | G3c Gate | orchestrator | TEST_VIEWPOINT.md §0 | - | ✅ |`

**Block condition**: Do NOT proceed to Phase 4 Pre (UTC/ITC spawn) until G3c is `✅ APPROVED`.

---

## PHASE 4: Incremental Implementation + Review per Batch

### Phase 4 Pre: Spawn UTC + ITC agents in background (simultaneously)

Spawn BOTH in the **same message** with `run_in_background: true`
→ Full prompts at `references/spawn-templates.md` §Phase 4 Pre

### Phase 4 Main: For each batch (sequential — Small=1, Medium=2, Large=3)

**Step 4a — Spawn developer-agent for Batch-N:**
→ Full prompt at `references/spawn-templates.md` §Phase 4 Dev

**Step 4b — Spawn code-review-agent for Batch-N (after dev done):**
→ Full prompt at `references/spawn-templates.md` §Phase 4 Review

**Step 4c — If REVIEW FAIL → fix loop (max R2 per batch):**
→ Spawn developer-agent to fix — prompt at `references/spawn-templates.md` §Phase 4 Fix
→ Re-spawn code-review-agent. Max R2 per batch total.

**Step 4d — Batch complete:** Update WBS task rows for this batch → `✅ DONE`. Proceed to Batch-N+1.

### Phase 4 Wait

After all batches complete, check for background UTC and ITC artifacts:

```
If docs/test-cases/UTC-[feature].md EXISTS → Update WBS T-08 → ✅ DONE.
If MISSING → Re-spawn foreground — prompt at references/spawn-templates.md §Phase 4 UTC Fallback

If docs/test-cases/ITC-[feature].md EXISTS → Update WBS T-09 → ✅ DONE.
If MISSING → Re-spawn foreground — prompt at references/spawn-templates.md §Phase 4 ITC Fallback
```

After all artifacts confirmed: Update walkthrough. Proceed to Phase 5.

---

## PHASE 5: Security Scan (after all batches + review PASS)

Spawn **security-tester-agent** → full prompt at `references/spawn-templates.md` §Phase 5

- **PASS** (no Critical/High) → update PLAN Phase 5b → `✅ DONE`, proceed Phase 6.
- **FAIL** (Critical or High) → spawn developer-agent to fix, then re-scan.

---

## PHASE 6: Unit Test Execution (R1 → R5)

Spawn **unit-test-agent** (MODE: EXECUTE) → full prompt at `references/spawn-templates.md` §Phase 6

- **PASS (100%)** → update PLAN → `✅ DONE`, proceed Phase 7.
- **FAIL** → spawn bug-fix-agent (prompt at `references/spawn-templates.md` §Phase 6 Bug Fix) → re-run R[n+1]. **Max R5.**
- If R5 still FAIL: escalate to user for decision.

---

## PHASE 7: Integration Test Execution (R1 → R5)

Spawn **integration-test-agent** (MODE: EXECUTE) → full prompt at `references/spawn-templates.md` §Phase 7

Same R1→R5 loop as Phase 6 (bug-fix → re-run until PASS or escalate at R5).

---

## PHASE 8: Delivery — Self-execute

Use Edit tool:

**Registry Updates (before marking DONE):**
1. Update `docs/plans/PLAN-REGISTRY.md` — set plan status → `✅ COMPLETED`, record completion date
2. Read `docs/plans/BACKLOG-REGISTRY.md` — list any remaining HIGH priority OPEN items as warnings in Delivery Report
3. If any CONTESTED decisions remain in `docs/plans/DECISION-LEDGER.md` → flag in Delivery Report

1. Update PLAN file: all `⏳` → `✅ DONE`, `Status: COMPLETED`
2. Update walkthrough: mark feature DONE

**Present Delivery Report:**
```markdown
## Delivery: [Feature Name] — [YYYY-MM-DD]

### Artifacts
| Artifact | Path |
|----------|------|
| Plan | docs/plans/PLAN-[f]-[date].md |
| SRS | docs/specs/requirements/SRS-[f].md |
| Screen | docs/specs/requirements/SCREEN-[f].md |
| Basic Design | docs/specs/basic-design/BASIC-[f].md |
| Tech (Detail Design) | docs/specs/detail-design/TECH-[f].md |
| Work Log B1 | docs/work-logs/DEV-[f]-B1.md |
| Work Log B2 | docs/work-logs/DEV-[f]-B2.md (Medium/Large) |
| Review B1 | docs/reviews/REVIEW-[f]-B1.md |
| Review B2 | docs/reviews/REVIEW-[f]-B2.md (Medium/Large) |
| UTC | docs/test-cases/UTC-[f].md |
| ITC | docs/test-cases/ITC-[f].md |
| Security | docs/security/SEC-[f]-[date].md |
| UTR | docs/test-reports/UTR-[f]-R[n].md |
| ITR | docs/test-reports/ITR-[f]-R[n].md |

### Quality Summary
- Code Review: PASS
- Security Scan: PASS (no Critical/High findings)
- Unit Tests: 100% PASS (R[n])
- Integration Tests: 100% PASS (R[n])
```

---

## PHASE 8.5: Retrospective — Auto-run after Phase 8

**Trigger**: Automatically after Phase 8 Delivery Report is presented.
**Purpose**: Multi-agent ceremony — each contributing agent reviews their own artifacts
and provides candid retrospective input. Orchestrator synthesizes 5 Why + Lesson Learned + Action Items.

Load and execute `/retro` skill:

```
MODE: feature
FEATURE: [feature-name]
SCOPE: full-feature (all phases)
```

**Spawn 5 contributing agents concurrently** (single message, `run_in_background: true`):
- `developer-agent` (RETRO) → work logs, blockers, scope drift
- `code-review-agent` (RETRO) → review patterns, recurring Critical findings
- `unit-test-agent` (RETRO) → test rounds, failure categories, coverage gaps
- `integration-test-agent` (RETRO) → E2E failures, integration assumptions
- `ba-agent` (RETRO) → requirement clarity, AC quality, gate reopens

**Follow the full `/retro` skill steps** (5 Why → Lesson Learned → Git Metrics → Action Items).

**Output**: `docs/retros/RETRO-feature-[feature]-[YYYYMMDD].md`

**Present to user**: Action Items table only. Full report available at output path.

---

## Success Criteria
- All 8 phases complete with artifacts in `docs/`
- Code Review: PASS
- Security Scan: PASS (no Critical/High)
- Unit Tests: 100% pass rate (R5)
- Integration Tests: 100% pass rate (R5)
- Retrospective: `docs/retros/RETRO-feature-[f]-[date].md` created with Action Items

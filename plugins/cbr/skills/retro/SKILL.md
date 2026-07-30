---
name: retro
description: "Multi-agent retrospective ceremony. Orchestrator invokes this after Phase 8 delivery (auto) or after any phase/sprint (manual). Spawns contributing agents concurrently to provide phase-specific perspectives, then synthesizes 5 Why root-cause analysis, Lesson Learned per category, git velocity metrics, and prioritized Action Items. Output saved to docs/retros/."
allowed-tools: Read, Grep, Glob, Bash, Agent, Write, Edit
disable-model-invocation: false
argument-hint: "[feature|phase|sprint name]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Retro

$ARGUMENTS

---

## Step 0: Mode Detection

Parse `$ARGUMENTS` to determine retro mode and scope:

| Pattern | Mode | Example |
|---------|------|---------|
| `feature [name]` | Full-feature retro (all phases) | `feature user-auth` |
| `phase [phase] [name]` | Single-phase retro | `phase Phase6 user-auth` |
| `sprint [date-range]` | Time-boxed sprint retro | `sprint 2026-03-01..2026-03-15` |
| *(no args)* | Prompt user to specify | — |

Determine `[feature-name]` and `[scope]` before proceeding.
Auto-create `docs/retros/` if it does not exist.

---

## Step 1: Spawn Contributing Agents Concurrently

Spawn ALL applicable contributing agents in a **single message** with `run_in_background: true`.

### Agent Selection by Mode

| Mode | Agents to Spawn |
|------|----------------|
| `feature` | developer + code-review + unit-test + integration-test + ba |
| `phase PhaseN` | Only agents relevant to that phase (see mapping below) |
| `sprint` | developer + code-review + unit-test + integration-test (skip ba) |

**Phase → Agent Mapping:**

| Phase | Contributing Agents |
|-------|-------------------|
| Phase 1 (Requirements) | ba-agent |
| Phase 2 (UI Design) | ui-designer-agent |
| Phase 3a/3b (Architecture) | architect-agent |
| Phase 4 (Implementation) | developer-agent + code-review-agent |
| Phase 5a/5b (Security) | security-tester-agent |
| Phase 6 (Unit Tests) | unit-test-agent |
| Phase 7a/7b (Integration) | integration-test-agent |

### Contributing Agent Spawn Prompts

**Agent 1 — developer-agent:**

```
OBJECTIVE: Contribute to retrospective for feature [feature-name].
  Review your own work artifacts and provide a candid assessment.
OUTPUT FORMAT: docs/retros/RETRO-contrib-dev-[feature]-[YYYYMMDD].md
  Required sections:
  ## Developer Perspective
  ### What Was Delivered (bullet list of key implementations)
  ### Blockers & Surprises (what slowed you down or was harder than expected)
  ### Scope Drift (anything added/changed outside original TECH spec)
  ### Self-Assessment (what you would do differently next time)
  ### Suggested Improvement (1-2 specific, actionable improvements for next feature)
TOOL HINTS: Read docs/work-logs/DEV-[feature]-*.md first. Then Read docs/specs/detail-design/TECH-[feature].md
  to compare planned vs actual. Use Glob to find all work log batches.
TASK BOUNDARIES:
  IN SCOPE — implementation challenges, work log blockers, scope drift vs TECH spec
  NOT IN SCOPE — test failures (unit-test handles that), security issues, requirements gaps
```

**Agent 2 — code-review-agent:**

```
OBJECTIVE: Contribute to retrospective for feature [feature-name].
  Analyze your review findings to identify systemic patterns worth improving.
OUTPUT FORMAT: docs/retros/RETRO-contrib-review-[feature]-[YYYYMMDD].md
  Required sections:
  ## Code Review Perspective
  ### Findings Summary (Critical count, Major count, total by batch)
  ### Recurring Patterns (issues that appeared in >1 batch or >1 file)
  ### Root Cause Hypothesis (why did these patterns occur — design, knowledge gap, time pressure?)
  ### Process Observation (was the CODING-CHECKLIST.md sufficient? what was missing?)
  ### Suggested Improvement (specific additions to CODING-CHECKLIST.md or coding standards)
TOOL HINTS: Read docs/reviews/REVIEW-[feature]-*.md (all batches). Grep for "Critical" and "Major".
  Use Glob to find all review files.
TASK BOUNDARIES:
  IN SCOPE — review findings patterns, checklist gaps, code quality trends
  NOT IN SCOPE — test failures, implementation details, requirements quality
```

**Agent 3 — unit-test-agent:**

```
OBJECTIVE: Contribute to retrospective for feature [feature-name].
  Analyze test execution rounds to identify testing effectiveness and gaps.
OUTPUT FORMAT: docs/retros/RETRO-contrib-ut-[feature]-[YYYYMMDD].md
  Required sections:
  ## Unit Test Perspective
  ### Rounds Summary (R1 result, R2 result, ..., final Rn — pass rate per round)
  ### Failure Categories (group test failures by type: null ref, auth, validation, business logic)
  ### Coverage Gaps (areas in TECH spec that had no test cases or thin coverage)
  ### Test Quality Observation (were UTC test cases precise enough? boundary cases covered?)
  ### Suggested Improvement (specific improvements to test case writing or test infrastructure)
TOOL HINTS: Read docs/test-reports/UTR-[feature]-R*.md (all rounds). Read docs/test-cases/UTC-[feature].md.
  Use Glob to find all UTR files.
TASK BOUNDARIES:
  IN SCOPE — unit test rounds, failure categories, UTC quality, coverage analysis
  NOT IN SCOPE — integration/E2E failures, code review findings, implementation issues
```

**Agent 4 — integration-test-agent:**

```
OBJECTIVE: Contribute to retrospective for feature [feature-name].
  Analyze integration/E2E test execution to identify workflow gaps and automation issues.
OUTPUT FORMAT: docs/retros/RETRO-contrib-it-[feature]-[YYYYMMDD].md
  Required sections:
  ## Integration Test Perspective
  ### Rounds Summary (R1–Rn pass rates for API + E2E separately)
  ### Failure Categories (auth flow, data consistency, cross-module assumptions, E2E timing)
  ### Environment Issues (anything that failed due to test env vs prod env differences)
  ### ITC Quality Observation (were test scenarios sufficient? what user journeys were missed?)
  ### Suggested Improvement (specific improvements to ITC scenarios or Playwright configuration)
TOOL HINTS: Read docs/test-reports/ITR-[feature]-R*.md (all rounds). Read docs/test-cases/ITC-[feature].md.
  Use Glob to find all ITR files.
TASK BOUNDARIES:
  IN SCOPE — integration/E2E test rounds, ITC scenario quality, env issues
  NOT IN SCOPE — unit test failures, code review findings, implementation details
```

**Agent 5 — ba-agent (feature mode only, skip for sprint):**

```
OBJECTIVE: Contribute to retrospective for feature [feature-name].
  Assess requirement quality and how well the SRS served the development team.
OUTPUT FORMAT: docs/retros/RETRO-contrib-ba-[feature]-[YYYYMMDD].md
  Required sections:
  ## Requirements Perspective
  ### Acceptance Criteria Quality (were ACs precise enough for testing? were any ambiguous?)
  ### Scope Stability (how many scope changes occurred after G1 gate? what triggered them?)
  ### Gate Reopens (list any gates that were REOPENED with root cause)
  ### Domain Risk Accuracy (did the Planning Council correctly identify the real risks?)
  ### Suggested Improvement (specific improvements to SRS template or AC writing process)
TOOL HINTS: Read docs/specs/requirements/SRS-[feature].md. Read docs/plans/PLAN-[feature]-*.md
  and check for REOPENED gates. Read docs/plans/COUNCIL-[feature]-BA.md if it exists.
TASK BOUNDARIES:
  IN SCOPE — requirement quality, AC precision, scope changes, gate reopens, Planning Council accuracy
  NOT IN SCOPE — implementation details, test execution, code review findings
```

**Wait for all agents to complete before proceeding to Step 2.**

---

## Step 2: Orchestrator Synthesis — 5 Why Analysis

After all contributing agents return, read all contribution files:

```bash
# Find all contribution files for this feature
ls docs/retros/RETRO-contrib-*-[feature]-*.md
```

**Identify Top Issues** (from agent contributions):
- Critical/High findings that appeared in code review
- Phases that required >R2 test rounds
- Gates that were REOPENED
- Blockers that caused scope drift

**For each of the top 3 issues, apply 5 Why:**

```markdown
### Issue #N: [Issue Title]
**Source**: [which agent reported this]
**Impact**: [what it caused — extra rounds, gate failure, scope drift]

| Step | Why? | Answer |
|------|------|--------|
| Why 1 | Why did [issue] occur? | [answer] |
| Why 2 | Why [answer from Why 1]? | [answer] |
| Why 3 | Why [answer from Why 2]? | [answer] |
| Why 4 | Why [answer from Why 3]? | [answer] |
| Why 5 | Why [answer from Why 4]? | [root cause] |

**Root Cause**: [concise statement]
**Action Item**: [specific, actionable change to prevent recurrence]
```

---

## Step 3: Lesson Learned Extraction

Synthesize insights from all agent contributions into 4 categories:

```markdown
### Lesson Learned

**Process:**
- [What process step was missing or insufficient]
- [What workflow change would prevent recurrence]

**Design:**
- [What architectural or design decision caused downstream issues]
- [What design pattern or checklist item should be added]

**Testing:**
- [What testing gap allowed bugs through to later rounds]
- [What test infrastructure or strategy change is needed]

**Security:**
- [Only if security findings occurred] What vulnerability pattern should be added to guardrails
```

---

## Step 4: Git Metrics Collection

Collect velocity and quality metrics from git. Use Bash (read-only git commands):

```bash
# Commit count and authors
git log --oneline --since="[feature-start-date or sprint-start]" --until="[end-date]"

# LOC added/removed
git diff --stat [start-commit]..[end-commit]

# Fix ratio (commits with "fix:" prefix vs total)
git log --oneline --since="[start]" | grep -c "^"
git log --oneline --since="[start]" | grep -c "^.*fix:"

# Delivery streak (days with at least 1 commit)
git log --format="%ad" --date=short --since="[start]" | sort -u | wc -l
```

Format metrics section:

```markdown
### Metrics

| Metric | Value |
|--------|-------|
| Commits | N |
| LOC added | +N |
| LOC removed | -N |
| Fix ratio | N% (M fix commits / N total) |
| Test rounds avg | R[n] |
| Gate reopens | N |
| Delivery streak | N active days |
```

**Note**: If git history is unavailable or start date is unknown, skip metrics and note "N/A — git baseline unavailable."

---

## Step 5: Output — Action Items + Final Report

Write the complete retro report to the canonical path.

**Output path convention:**

| Mode | Path |
|------|------|
| `feature [name]` | `docs/retros/RETRO-feature-[name]-[YYYYMMDD].md` |
| `phase [phase] [name]` | `docs/retros/RETRO-phase-[phase]-[name]-[YYYYMMDD].md` |
| `sprint [date-range]` | `docs/retros/RETRO-sprint-[YYYYMMDD].md` |

**Report structure:**

```markdown
# Retro: [Feature/Sprint Name] — [YYYY-MM-DD]

**Mode**: [feature | phase | sprint]
**Scope**: [phases covered]
**Facilitator**: orchestrator-agent

---

## 1. Delivery Summary
[2-3 sentences: what was delivered, gate results summary]

---

## 2. Agent Perspectives

### Developer
[Summary from RETRO-contrib-dev file]

### Code Review
[Summary from RETRO-contrib-review file]

### Unit Test
[Summary from RETRO-contrib-ut file]

### Integration Test
[Summary from RETRO-contrib-it file]

### Business Analysis
[Summary from RETRO-contrib-ba file, if applicable]

---

## 3. Top Issues — 5 Why Analysis

[Issue #1 block]
[Issue #2 block]
[Issue #3 block]

---

## 4. Lesson Learned

[Process / Design / Testing / Security]

---

## 5. Metrics

[Metrics table]

---

## 6. Action Items

| Priority | Action | Owner | Scope | Due |
|----------|--------|-------|-------|-----|
| HIGH | [specific action] | [agent or team] | next feature | [date] |
| MEDIUM | [specific action] | process | process-wide | [date] |
| LOW | [specific action] | [owner] | optional | — |
```

**After writing report:** Clean up contribution files (they've been synthesized):

```bash
rm docs/retros/RETRO-contrib-*-[feature]-*.md
```

**Present to user:** Show Action Items table only (not the full report). User can read full report in `docs/retros/`.

---

## Step 5b: Registry & Memory Feed-Forward

After writing the retro report and before presenting to user:

**Backlog Append:**
For each Action Item with Priority HIGH or MEDIUM from the retro report:
1. Read `docs/plans/BACKLOG-REGISTRY.md`
2. Check for duplicate (grep Action description keywords)
3. If no duplicate → append new entry:
   - Source: `RETRO-[type]-[feature/sprint]-[date]`
   - Type: `PROCESS`
   - Priority: match retro Action Item priority
   - Target: next feature/wave (or unassigned)
   - Status: `⏳ OPEN`

**Project Memory Append:**
For each Lesson Learned insight that is non-obvious and reusable:
1. Read `docs/memory/PROJECT-MEMORY.md`
2. Apply Mem0 dedup: EXTRACT → SEARCH existing entries → CLASSIFY (NOOP/UPDATE/ADD)
3. If ADD → append to appropriate section (Tech Stack / Testing / Domain Model)
   - Agent: `retro-synthesis`
   - Confidence: `MEDIUM` (verified in this feature's execution)

---

## Lifecycle Placement (Recommended Trigger Points)

This skill is invoked automatically by `full-sdlc` at Phase 8.5. It can also be invoked manually:

```
AUTOMATIC:
  Phase 8 (Delivery) → Phase 8.5 auto-trigger → /retro feature [name]

MANUAL (PM/EM invokes):
  After Phase 4 (optional mid-feature check)  → /retro phase Phase4 [feature]
  After Phase 6 (test quality review)         → /retro phase Phase6 [feature]
  End of sprint (bi-weekly)                   → /retro sprint [date-range]
  Post-incident review                        → /retro feature [affected-feature]
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Run retro while feature is still in progress | Wait for Phase 8 completion (or gate completion for phase retro) |
| Skip contributing agents to save time | Each agent's perspective is non-overlapping — all are needed for full picture |
| Write vague action items ("improve testing") | Write specific, ownable actions ("Add boundary tests for null input in UserService") |
| Keep contribution files after synthesis | Delete RETRO-contrib-* files after synthesis — report is the canonical artifact |
| Run 5 Why on every minor issue | Focus 5 Why on top 3 issues only — minor issues go directly to Action Items |
| Skip retro for "simple" features | Simple features often have the most surprising lessons — skip is a anti-pattern |

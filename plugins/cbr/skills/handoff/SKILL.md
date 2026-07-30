---
name: handoff
description: "Creates a session handoff document capturing feature state — what's done, what's pending, key decisions, open issues. TRIGGER: user says \"create handoff\", \"summarize progress for handoff\", \"I'm transferring this\", \"session is ending\", \"create context for next session\". NOT FOR: creating implementation plans (use plan-writing), or full retrospectives (use retro)."
allowed-tools: Read, Grep, Glob, Write, Edit
argument-hint: "[feature name]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Handoff — Session Continuity Document

Feature to document:

$ARGUMENTS

## Live Session Context (auto-injected)

- Recent commits: !`git log --oneline -7 2>/dev/null || echo "(no git history)"`
- Uncommitted changes: !`git status --short 2>/dev/null || echo "(no git context)"`

---

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect:
- Project name and domain
- Tech stack
- SDLC phase in progress

---

## Content Map

| Section | When to read |
| ------- | ------------ |
| Step 0 | Always — detect project context first |
| Step 1: Collect Artifacts | Always — find all relevant docs |
| Step 2: Assess State | Always — determine phase and status |
| Step 3: Open Items | Always — capture blockers and pending work |
| Step 4: Write Handoff | Always — mandatory output |

---

## Step 1: Collect Artifacts

Glob and Read the following (skip if not found — note as missing):

| Artifact | Path | Status |
|----------|------|--------|
| PLAN file | `docs/plans/PLAN-[feature]-*.md` | |
| SRS | `docs/specs/requirements/SRS-[feature].md` | |
| BASIC spec | `docs/specs/basic-design/BASIC-[feature].md` | |
| TECH spec | `docs/specs/detail-design/TECH-[feature].md` | |
| SCREEN spec | `docs/specs/requirements/SCREEN-[feature].md` | |
| Work logs | `docs/work-logs/DEV-[feature]-*.md` | |
| Review reports | `docs/reviews/REVIEW-[feature]-*.md` | |
| UTC | `docs/test-cases/UTC-[feature].md` | |
| ITC | `docs/test-cases/ITC-[feature].md` | |
| Bug reports | `docs/bug-reports/BUG-*.md` | |
| Agent flags | `docs/agent-comms/flags/FLAG-*-[feature].md` | |

**Registry & Memory State (CAO context):**

| Registry/Memory | Path | Status |
|-----------------|------|--------|
| Plan Registry | `docs/plans/PLAN-REGISTRY.md` | |
| Decision Ledger | `docs/plans/DECISION-LEDGER.md` | |
| Backlog Registry | `docs/plans/BACKLOG-REGISTRY.md` | |
| Project Memory | `docs/memory/PROJECT-MEMORY.md` | |
| Agent Memory | `.claude/agent-memory/*/MEMORY.md` | |

Read each if they exist. Extract:
- Active/Suspended plans from PLAN-REGISTRY
- CONTESTED or NEEDS RESOLUTION decisions from DECISION-LEDGER
- HIGH priority OPEN items from BACKLOG-REGISTRY

---

## Step 2: Assess Current State

From the PLAN file and collected artifacts, determine:

1. **Current SDLC phase**: Which phase is active? (G1 / G2 / G3a / G3b / G4 / G5a / G6 / G7 / G5b / G8)
2. **Last completed gate**: What is the last ✅ gate?
3. **Active work**: What task is currently `⏳ IN_PROGRESS`?
4. **Blockers**: Any `⚠️ REOPENED` gates or unresolved FLAGS?

---

## Step 3: Capture Open Items

From work logs, review reports, and flags:

1. **Unresolved findings**: Critical/Major findings not yet fixed
2. **Pending decisions**: Any ESCALATION TRIGGERS that haven't been resolved
3. **In-progress code**: Files modified but not committed or reviewed
4. **Test failures**: Any failing tests from last UTR/ITR run
5. **Known risks**: Items flagged as risk in PLAN or agent comms

---

## Step 4: Write Handoff Document

File: `docs/handoffs/HANDOFF-[feature]-[YYYYMMDD].md`

```markdown
# Handoff: [feature-name]

**Date**: [YYYY-MM-DD]
**Created by**: [who is handing off]
**Recipient**: [who is receiving — or "next session"]
**Feature**: [brief description]

---

## State Summary (5 bullets max)

- [DONE] [what was completed]
- [DONE] [what was completed]
- [PENDING] [what is actively in progress]
- [PENDING] [what is next after current work]
- [BLOCKED] [any blocker or decision pending]

---

## Current Phase

**Active phase**: [Phase N — e.g., Phase 6: Unit Tests]
**Last completed gate**: [Gate X — e.g., G4 Code Review ✅]
**Next required action**: [exact next step — e.g., "Run unit tests with: npx jest --testPathPattern=payment"]

---

## Artifacts Status

| Artifact | Path | Status |
|----------|------|--------|
| PLAN | docs/plans/PLAN-[feature]-[date].md | ✅ exists |
| SRS | docs/specs/requirements/SRS-[feature].md | ✅ exists |
| TECH spec | docs/specs/detail-design/TECH-[feature].md | ✅ exists |
| UTC | docs/test-cases/UTC-[feature].md | ⏳ in progress |

---

## Open Issues

| # | Type | Description | Severity | File/Location |
|---|------|-------------|----------|--------------|
| 1 | Review finding | [description] | Major | [file:line] |
| 2 | Test failure | [test name] | — | [file:line] |
| 3 | Blocked decision | [decision needed] | — | [context] |

---

## Key Decisions Made

| Decision | Rationale | Reference |
|----------|-----------|-----------|
| [what was decided] | [why] | [artifact or line] |

---

## CAO Registry State

### Active Plans
<!-- From PLAN-REGISTRY.md — list all ACTIVE and SUSPENDED plans -->
| Plan | Type | Status | Phase |
|------|------|--------|-------|

### Unresolved Decisions
<!-- From DECISION-LEDGER.md — only CONTESTED and NEEDS RESOLUTION -->
| ID | Domain | Decision | Status |
|----|--------|----------|--------|

### Open Backlog (HIGH priority)
<!-- From BACKLOG-REGISTRY.md — only HIGH + OPEN -->
| ID | Type | Description | Target |
|----|------|-------------|--------|

---

## Resume Instructions

```
@orchestrator-agent Resume feature [feature-name]
Plan file: docs/plans/PLAN-[feature]-[date].md
Continue from phase with status ⏳ PENDING

Context: See docs/handoffs/HANDOFF-[feature]-[date].md for full state summary.
Open issues: [count] — see Open Issues table above.
CAO Context: Registries (PLAN-REGISTRY, DECISION-LEDGER, BACKLOG-REGISTRY) contain
accumulated context. Context-injector will auto-retrieve relevant entries at agent spawn.
```

---

## Warnings

- [anything the next person should know — assumptions, fragile code, test environment issues]
```

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Prerequisite | Any in-progress skill | Complete or checkpoint current work before creating handoff |
| On resume | `orchestrate` | Use handoff as context when resuming session |
| Related | `plan-writing` | PLAN file is the primary input for handoff state assessment |
| Related | `retro` | After delivery: use retro instead of handoff for formal review |

---

## Anti-Patterns

| Don't | Do |
| ----- | -- |
| Write handoff from memory | Read artifacts first — state is in the docs |
| List every file touched | List only open items and what's next |
| Write for "any developer" | Write for the specific next action |
| Skip open issues | Open issues are the most critical part |
| Create handoff mid-implementation | Checkpoint at a stable point (phase boundary) |

---

## Reference

For a worked example of the expected output, see: `references/examples/HANDOFF-example.md`

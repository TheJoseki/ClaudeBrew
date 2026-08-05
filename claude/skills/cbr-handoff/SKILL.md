---
name: cbr-handoff
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

All per-feature artifacts live under the feature's stream folder
`docs/streams/[feature]-*/` (glob the `*` — the folder date is the stream-start
date). `STREAM.md` is the primary index; the paths below are its sub-folders.

| Artifact | Path | Status |
|----------|------|--------|
| Stream manifest | `docs/streams/[feature]-*/STREAM.md` (if present: use for membership + task board) | |
| PLAN file | `docs/streams/[feature]-*/plan/PLAN.md` | |
| SRS | `docs/streams/[feature]-*/requirements/SRS.md` | |
| BASIC spec | `docs/streams/[feature]-*/design/BASIC.md` | |
| TECH spec | `docs/streams/[feature]-*/design/TECH.md` | |
| SCREEN spec | `docs/streams/[feature]-*/requirements/SCREEN.md` | |
| Work logs | `docs/streams/[feature]-*/work-logs/DEV-*.md` | |
| Review reports | `docs/streams/[feature]-*/reviews/REVIEW-*.md` | |
| UTC | `docs/streams/[feature]-*/test-cases/UTC.md` | |
| ITC | `docs/streams/[feature]-*/test-cases/ITC.md` | |
| Bug reports | `docs/streams/[feature]-*/bug-reports/BUG-*.md` | |
| Gate verdicts | `docs/streams/[feature]-*/reviews/VERDICT-*.json`, `.../security/VERDICT-*.json`, `.../test-reports/VERDICT-*.json` | |

**Cross-cutting state:**

| Source | Path | Status |
|--------|------|--------|
| Plan | `docs/streams/[feature]-*/plan/PLAN.md` | |
| Decision records | `docs/streams/[feature]-*/design/decisions/ADR-*.md` (stream-scoped), `docs/decisions/ADR-*.md` (project-wide) | |
| Risk register | `docs/risks/RISK-*.md` (or the PLAN's Risk Register section) | |
| Agent memory | `.claude/agent-memory/*/MEMORY.md` | |

Read each if it exists. Extract:
- From `STREAM.md` (if present): the stream's artifact membership + task-board status. Treat its Gate
  Status zone as a derived snapshot only — re-derive gate state from the globbed artifacts/verdicts below.
- The active plan's open phases and their done conditions
- SUPERSEDED or unresolved decisions from the ADRs
- OPEN HIGH/CRITICAL risks from the risk register

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

File: `docs/streams/[feature]-*/handoffs/HANDOFF-[YYYYMMDD].md` — write into the
existing stream folder's `handoffs/` subfolder (brainstorming created the stream;
its folder date is the stream-start date, distinct from today's handoff date).

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
| PLAN | docs/streams/[feature]-[date]/plan/PLAN.md | ✅ exists |
| SRS | docs/streams/[feature]-[date]/requirements/SRS.md | ✅ exists |
| TECH spec | docs/streams/[feature]-[date]/design/TECH.md | ✅ exists |
| UTC | docs/streams/[feature]-[date]/test-cases/UTC.md | ⏳ in progress |

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

## Cross-Cutting State

### Active Plans
<!-- From docs/streams/*/plan/PLAN.md — list plans with unfinished phases -->
| Plan | Type | Status | Phase |
|------|------|--------|-------|

### Unresolved Decisions
<!-- From docs/streams/*/design/decisions/ADR-*.md and docs/decisions/ADR-*.md — only open or superseded-pending -->
| ID | Domain | Decision | Status |
|----|--------|----------|--------|

### Open Risks (HIGH priority)
<!-- From the risk register — only HIGH/CRITICAL + OPEN -->
| ID | Category | Risk | Response |
|----|----------|------|----------|

---

## Resume Instructions

```
Next stage: /cbr-[stage-skill] [feature-name]
Plan file: docs/streams/[feature]-[date]/plan/PLAN.md
Resume at the first phase still marked ⏳ PENDING.

Context: See docs/streams/[feature]-[date]/handoffs/HANDOFF-[date].md for the full state summary.
Open issues: [count] — see the Open Issues table above.
Last gate passed: [G-n]. The user starts the next stage; nothing cascades on its own.
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
| On resume | The stage skill named in Resume Instructions | Read the handoff first, then start that stage |
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

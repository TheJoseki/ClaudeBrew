---
name: fix-bug
description: "Bug Fix agent debugs and fixes issues for any project. Tech stack detected from PROJECT.md/CLAUDE.md. TRIGGER: user reports a bug, error, test failure, or unexpected behavior. NOT FOR: new features, refactoring, or performance optimization."
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Skill
argument-hint: "[error message + steps to reproduce]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Bug Fix

Bug to fix:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Do NOT hardcode framework assumptions when reproducing or fixing bugs.

## Step 1: Receive Bug Input

Read input from:
- UTR report: `docs/test-reports/UTR-[feature]-R[n].md` (section "Bug Reports")
- ITR report: `docs/test-reports/ITR-[feature]-R[n].md` (section "Bug Reports")
- Or direct user report

Required reading:
- `docs/CODING_RULES.md` — verify fix does not violate rules
- `docs/CODING_CONVENTION.md` — follow patterns when fixing
- `docs/specs/detail-design/TECH-[feature].md` — design source of truth; verify fix aligns with architecture
- `docs/specs/decisions/ADR-*.md` — a recorded decision may explain the root cause

## Step 2: Reproduce Bug

Run commands from PROJECT.md Build Commands section. Typical examples:

```bash
# Backend test for affected module
cd backend && [backend test command] --testPathPattern="[module]" --verbose

# Frontend test for affected file
cd frontend && [frontend test command] [test-file] --reporter=verbose

# Type check
cd backend && [backend type check command]
cd frontend && [frontend type check command]
```

## Step 3: Root Cause Analysis

Trace code flow, read full stack trace. Identify root cause by layer:
- Backend: auth/authorization middleware, input validation, ORM query, soft delete filter, audit columns
- Frontend: reactivity/state management, store access, i18n key missing, router guard, UI component prop
- Integration: API contract mismatch, auth token handling, CORS, response shape

## Step 4: Implement Fix

- **Minimal blast radius**: fix only the bug, do not refactor surrounding code
- Follow existing patterns from `docs/CODING_CONVENTION.md`
- Do not break soft delete filter or other project-wide conventions

## Step 5: Verify Fix

```bash
# Affected test — verify fix
cd backend && [backend test command] --testPathPattern="[file]" --verbose
cd frontend && [frontend test command] [file]

# Regression — verify no other tests broken
cd backend && [backend test command] --passWithNoTests
cd frontend && [frontend test command]
```

> **Auto-escalation rule**: If fix still FAILS after **2 rounds**, stop patching symptoms.
> Invoke the `systematic-debugging` skill using the Skill tool to find the true root cause:
> `Skill(skill: "systematic-debugging", args: "[bug symptoms + what was tried + why it failed]")`

## Step 6: Create Bug Report (MANDATORY — DO NOT SKIP)

Bug ID format: `BUG-[YYYYMMDD]-[nn]`

File: `docs/bug-reports/BUG-[YYYYMMDD]-[nn].md`

```markdown
# Bug Fix Report: [Bug ID]
**Bug ID**: BUG-[YYYYMMDD]-[nn]
**Feature**: [feature] | **Date**: [YYYY-MM-DD] | **Severity**: Critical/High/Medium/Low
**Source**: UTR-R[n] / ITR-R[n] / User | **TC ID**: [TC-UT-XXX or TC-IT-XXX]

## Root Cause
[1-2 sentences: WHY the bug occurred — not just symptoms]

## Fix Applied
| File | Change | Reason |
|------|--------|--------|

## Verification
- [ ] Affected test: PASS
- [ ] Full suite: PASS (no regression)
- [ ] Type check: PASS
```

## Common Bug Patterns

### Backend (adapt to project's framework)
- 401/403 → Check auth guard, role check, JWT/session payload
- 404 → Soft-deleted record — check soft delete filter in query
- 400 → Input validator/DTO decorator missing or misconfigured
- N+1 query → Add eager loading / include to ORM query

### Frontend (adapt to project's framework)
- UI not updating → Reactivity issue (e.g. `.value` on ref, `storeToRefs()` for Pinia, selector in Redux)
- Missing translation → Add key to all locale files
- Auth loop → Check token refresh interceptor logic
- Wrong display value → Check data mapping / status-to-label mapping

## Checklist before Done
- [ ] Root cause identified (not just symptoms)
- [ ] Fix minimal — no unnecessary code added
- [ ] Fix does not violate CODING_RULES.md (soft delete, guards, i18n)
- [ ] Affected test PASS
- [ ] Full suite PASS (no regression)
- [ ] Bug report `docs/bug-reports/BUG-[id]-[feature].md` CREATED ✅

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Escalate to | `systematic-debugging` | Bug is intermittent, fix failed 2+ rounds, or root cause still unclear |
| After this | `run-tests` | Always — full regression suite to confirm fix |
| Pairs with | `vulnerability-scanner` | Bug is security-related (auth bypass, injection, data exposure) |
| Called from | `run-tests` | When test FAIL has a clear, known root cause |

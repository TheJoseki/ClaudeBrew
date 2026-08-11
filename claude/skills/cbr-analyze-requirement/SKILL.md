---
name: cbr-analyze-requirement
description: "Business Analyst analyzes requirements and creates SRS specification for any project. TRIGGER: user asks to analyze requirements, write SRS, define user stories, acceptance criteria. NOT FOR: technical design, implementation, or code review."
allowed-tools: Read, Grep, Glob, Write, Edit
argument-hint: "[feature or requirement description]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Requirement Analysis

Feature to analyze:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect project domain, tech stack, and existing conventions before taking action.
Do NOT hardcode project-specific domain assumptions.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect project context first |
| Step 1: Read Input | Always — mandatory before analyzing |
| Step 2: Analyze | Always — core analysis work |
| Step 3: SRS File | Always — mandatory output artifact |
| Checklist | Before marking done |

## Step 1: Read Input (MANDATORY)

- `docs/REQUIREMENTS_ANALYSIS.md` — existing requirements (if exists)
- `docs/SCREEN_DESIGN.md` — UI mockups (if exists)
- `docs/API_DESIGN.md` — API endpoints (if exists)
- `docs/CODING_RULES.md` — domain rules (if exists)
- `docs/TEST_VIEWPOINT.md` — test scenarios to align AC (if exists)
- `design/` or `specs/` — source design files (if exists)
- Input plan file `docs/streams/[feature]-[YYYYMMDD]/plan/PLAN.md` (if one exists)

## Step 2: Analyze

1. Identify actors and roles involved
2. Extract user stories (Given-When-Then format)
3. Define acceptance criteria (testable — each AC must be writable as a test case)
4. Map to existing API endpoints and UI screens
5. Identify business rules and constraints
6. Flag dependencies and risks
7. Define edge cases: empty state, error, permission denied, deleted records

## Step 3: Create SRS File (MANDATORY — DO NOT SKIP)

File: `docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md`

> **Template**: See [`references/template.md`](references/template.md) for the full output document template.

## Checklist before Done
- [ ] User stories have clear Given-When-Then
- [ ] Acceptance criteria are testable (can write TC from each AC)
- [ ] Roles mapping matches permission matrix from PROJECT.md
- [ ] API refs match existing API design docs (if available)
- [ ] Screen refs match existing screen design docs (if available)
- [ ] Edge cases covered: empty state, error, permission denied, soft delete
- [ ] File `docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md` CREATED ✅

## Verification

**Skill triggers correctly when:**
- User says: "Analyze the requirements for user management"
- User says: "Write the SRS for the payment feature"
- User says: "Define user stories and acceptance criteria for the reporting module"

**Skill does NOT trigger for:**
- "Design the API schema for user management" (use design-function)
- "Implement the login feature" (use implement-feature)
- "Review the user management code" (use review-code)

**Expected outputs:**
- Artifact: `docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md`
- Quality gate: All acceptance criteria are testable (1:1 mapping with test cases)

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Prerequisite | `brainstorming` | Run first if requirements are ambiguous or undefined |
| On success | `design-screen` | After REQUIREMENT — design UI screens for the feature |
| On success | `design-function` | After REQUIREMENT — design API endpoints and ORM schema |
| On FAIL (scope unclear) | `brainstorming` | Revisit and scope requirements before retrying |

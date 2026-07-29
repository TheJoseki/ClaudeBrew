---
name: review-code
description: Code Review agent reviews code quality, security, and performance for any project. Standards detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to review code, check quality/security/performance of written code. NOT FOR: writing new code, fixing bugs, or creating test cases.
allowed-tools: Read, Grep, Glob, Write, Edit, Skill
argument-hint: "[feature name (optional)]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Code Review

Code to review:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Detect backend framework, frontend framework, ORM, and UI library.
Do NOT hardcode framework pattern expectations.

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect tech stack first |
| Step 1: Read Input | Always — mandatory |
| Step 2: Review Dimensions | Always — core review work |
| Step 3: Review File | Always — mandatory output artifact |
| Decision Rules | Always — determines PASS/FAIL verdict |

## Precondition Check (MANDATORY — stop if not met)

Required artifacts for this skill:

- [ ] Implementation code files must exist (Glob/Grep for feature-related source files)
- [ ] `docs/work-logs/DEV-[feature]-*.md` — preferred, but optional if code path is known

If implementation code **NOT FOUND**:
> STOP. Report: "Cannot review — no implementation found for this feature.
> Run `/implement-feature` first."

---

## Step 1: Read Input (MANDATORY)

- `docs/CODING_RULES.md` — all rules to verify
- `docs/CODING_CONVENTION.md` — patterns, templates, import order
- `docs/ARCHITECTURE.md` — system patterns, auth flow (if exists)
- Input DEV log: `docs/work-logs/DEV-[feature]-*.md` (see implemented files)
- Input TECH spec: `docs/specs/detail-design/TECH-[feature].md` (verify implementation matches design)

## Step 2: Review by Dimension

### Security (CRITICAL — blocks PASS if violated)
- Auth guards on all protected routes (middleware/guards per PROJECT.md pattern)
- Role-based access control applied correctly per permission matrix
- All user input validated via DTO/schema/serializer (no raw unvalidated input)
- ORM parameterized queries only (no raw SQL string concatenation)
- No secrets hardcoded in source files
- File upload: type/size validation if applicable
- Scope isolation: users can only access data they are permitted to

### Correctness
- Logic matches TECH spec
- Edge cases handled
- TypeScript strict (no `any`, no `@ts-ignore`) — or equivalent strictness for project language

### Backend Framework Standards (per PROJECT.md)
- Controllers/routes: thin, delegate to services/handlers
- Input validation: validators on all inputs
- Soft delete: deleted records excluded from all queries
- Audit columns: set on create and update
- API docs (Swagger/OpenAPI or equivalent): present on all endpoints

### Frontend Framework Standards (per PROJECT.md)
- Modern component pattern per PROJECT.md (e.g. Composition API for Vue, hooks for React)
- All strings via i18n — no hardcoded user-facing text
- Correct [UI_LIBRARY] API usage — no deprecated or wrong-version components
- No `any`, no `@ts-ignore`

## Step 3: Create Review File (MANDATORY — DO NOT SKIP)

File: `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md`

> **Template**: See [`references/template.md`](references/template.md) for the full output document template.

## Decision Rules
| Condition | Verdict |
|-----------|---------|
| Any Critical finding | FAIL |
| 3+ Major findings | FAIL |
| 1-2 Major findings | PASS (fix before merge) |
| Only Minor | PASS |

## Checklist before Done
- [ ] Read all files listed in DEV work log
- [ ] Compare implementation against TECH spec
- [ ] Security checklist complete
- [ ] All findings have file + line reference
- [ ] Verdict clear (PASS/FAIL) with justification
- [ ] File `docs/reviews/REVIEW-[feature]-[date].md` CREATED ✅

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Called from | `implement-feature` | Mandatory quality gate after each implementation batch — always run before next batch or PR |
| Called from | `full-sdlc` | Phase 4 Main — per-batch incremental review, spawned by orchestrator after each dev batch |
| On security findings | `vulnerability-scanner` | Any Critical/High security finding → deep OWASP audit |
| If FAIL (≤ R2 per batch) | `fix-bug` / developer-agent | Fix Critical + Major findings → re-review same batch |
| All batches PASS | `security-tester-agent` | Full OWASP scan on all implemented code (Phase 5) |
| After PASS + security | `create-pr` | All checks green — ready to create pull request |

**Input pattern (batch mode):**
```
BATCH: Batch-N
INPUT: docs/work-logs/DEV-[feature]-BN.md  ← scope list of files for this batch only
SCOPE: Review only files in DEV-BN work log, not previous batches
OUTPUT: docs/reviews/REVIEW-[feature]-BN.md
Reference: .claude/skills/review-code/references/leader-review-checklist.md
```

**Incremental review flow:**
```
Batch-1: developer-agent → code-review-agent (B1) → [fix if FAIL, max R2] → PASS
Batch-2: developer-agent → code-review-agent (B2) → [fix if FAIL, max R2] → PASS
...
All batches PASS → security-tester-agent (full OWASP) → unit-test-agent EXECUTE → integration-test-agent EXECUTE
```

## Verification

**Skill triggers correctly when:**
- User says: "Review the code for the payment feature"
- User says: "Check the security of the user management implementation"
- User says: "Do a code review on the order module"

**Skill does NOT trigger for:**
- "Fix the bug in the payment module" (use fix-bug)
- "Implement the user management feature" (use implement-feature)
- "Write unit tests for the order module" (use unit-test)

**Expected outputs:**
- Artifact: `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md`
- Quality gate: Verdict is clearly PASS or FAIL; all Critical/Major findings have file + line reference

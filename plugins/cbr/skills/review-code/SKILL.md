---
name: review-code
description: "Code Review agent reviews code quality, security, and performance for any project. Standards detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to review code, check quality/security/performance of written code. NOT FOR: writing new code, fixing bugs, or creating test cases."
allowed-tools: Read, Grep, Glob, Bash, Task, Agent, AskUserQuestion
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
| Step 2: Assemble the G4 checklist | Always — the criteria this skill owns |
| Step 3: Verdict (fresh eyes) | Always — spawn, validate, stop |

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

## Step 2: Assemble the G4 checklist (this skill owns the criteria)

This skill decides **what** is judged. A freshly spawned `cbr:reviewer` decides
**whether it passes**. Do not evaluate the code yourself here — assemble the
checklist, then hand it over in Step 3.

The checklist is the dimensions below **plus** the full tech-lead list at
`${CLAUDE_PLUGIN_ROOT}/skills/review-code/references/leader-review-checklist.md`.
Pass both to the reviewer by path; do not paste them into the prompt.

### Security (CRITICAL — any finding blocks the gate)
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

### Verdict rubric (hand to the reviewer verbatim)

| Condition | Verdict |
|-----------|---------|
| Any Critical finding | FAIL |
| 3+ Major findings | FAIL |
| 1-2 Major findings | PASS (fix before merge) |
| Only Minor | PASS |

The validator enforces only the hard floor — `decision` must be `PASS` and there
must be zero Critical findings. It does **not** count Majors, so the "3+ Major →
FAIL" rule lives entirely in the reviewer's judgment. That is why it must be
stated in the spawn prompt.

## Step 3: Verdict (fresh eyes) — MANDATORY

**This skill never writes its own verdict.** It holds no `Write` tool: grading
your own review is the failure mode this step exists to prevent.

**3.1 — Spawn one `cbr:reviewer`** (single `Agent` call). The prompt must carry:

- **Scope**: the exact files to review (from the DEV work log; in batch mode,
  that batch's files only — not previous batches).
- **Inputs**: the TECH spec + coding-rules paths from Step 1.
- **Checklist**: the Step 2 dimensions + the `leader-review-checklist.md` path.
- **Rubric**: the verdict table above, verbatim.
- **Outputs**, both mandatory:
  - Findings report → `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md`
    (template: [`references/template.md`](references/template.md))
  - Verdict artifact → `docs/reviews/VERDICT-[feature]-G4.json`, conforming to
    `${CLAUDE_PLUGIN_ROOT}/schemas/verdict-artifact.schema.json`, with
    `gate: "G4"` and `producedBy: "cbr:reviewer"`. A reviewer runs no build or
    test commands, so `verification` stays `[]`.
- **Posture**: assume the code was AI-written; look for what breaks, not for
  reasons to approve. Every finding cites `file:line`.

**3.2 — Validate the verdict** (never trust it unchecked):

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/verdict-gate.py" --gate G4 --artifact docs/reviews/VERDICT-[feature]-G4.json
```

Exit `0` = gate criteria objectively met. Exit `2` = BLOCK, with the reason on
stderr (FAIL decision, unresolved Critical, leaked secret, or a malformed /
missing artifact). The gate fails **closed** — no artifact means no pass.

**3.3 — Gate the user in:**

- **Exit 0** → report PASS, the artifact paths, and any Major/Minor findings
  still open. Then **stop**.
- **Exit 2, or `decision: FAIL`** → `AskUserQuestion` presenting the blocking
  reason and the Critical/Major findings (`file:line` each), with options along
  the lines of: *fix now via `/fix-bug`* · *re-review after manual fixes* ·
  *accept the risk and proceed anyway* · *stop here*.

**3.4 — Stop.** Whatever the user chooses, this skill does not act on it: no
automatic fix-loop, no re-spawn, no advancing to the next gate. The user
re-invokes `/fix-bug` and then `/review-code` themselves.

## Checklist before Done
- [ ] Scope assembled from the DEV work log (batch-scoped if in batch mode)
- [ ] Checklist + rubric handed to the reviewer by path, not re-judged here
- [ ] `cbr:reviewer` spawned fresh — this skill graded nothing itself
- [ ] `docs/reviews/REVIEW-[feature]-[date].md` written by the reviewer
- [ ] `docs/reviews/VERDICT-[feature]-G4.json` written by the reviewer
- [ ] `verdict-gate.py --gate G4` run, exit code reported
- [ ] On block: `AskUserQuestion` raised with findings — then STOPPED ✅

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Called from | `implement-feature` | Mandatory quality gate after each implementation batch — always run before next batch or PR |
| On security findings | `vulnerability-scanner` | Any Critical/High security finding → deep OWASP audit |
| If FAIL (≤ R2 per batch) | `fix-bug` | Fix Critical + Major findings → re-review same batch |
| All batches PASS | `vulnerability-scanner` | Full OWASP scan (G5a) on all implemented code — user starts it |

**Input pattern (batch mode)** — one gate run per batch, each ending in its own
user gate:
```
BATCH: Batch-N
INPUT: docs/work-logs/DEV-[feature]-BN.md  ← scope list of files for this batch only
SCOPE: Review only files in DEV-BN work log, not previous batches
OUTPUT: docs/reviews/REVIEW-[feature]-BN.md + docs/reviews/VERDICT-[feature]-BN-G4.json
Checklist: ${CLAUDE_PLUGIN_ROOT}/skills/review-code/references/leader-review-checklist.md
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
- Artifacts (both written by the spawned `cbr:reviewer`):
  `docs/reviews/REVIEW-[feature]-[YYYYMMDD].md` and
  `docs/reviews/VERDICT-[feature]-G4.json`
- Quality gate: G4 — `verdict-gate.py --gate G4` run and its exit code reported;
  all Critical/Major findings have file + line reference; on block, the user was
  asked and the skill stopped

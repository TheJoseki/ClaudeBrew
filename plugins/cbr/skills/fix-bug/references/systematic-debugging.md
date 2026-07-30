# Systematic Debugging — 4-Phase Evidence-Based Methodology

Load this reference when the direct fix path in `SKILL.md` is not enough: intermittent
issue, production incident, unknown root cause, a fix that was attempted but the bug
recurs, or a complex multi-layer issue. For a known bug with a clear location and a
quick fix, stay on the main `SKILL.md` steps — do not load this.

Work the four phases in order. Do not skip ahead.

---

## Phase 1: Reproduce

Before any fix attempt, establish a reliable reproduction case.

```markdown
## Reproduction Record
- Steps to reproduce:
  1. [Exact step]
  2. [Next step]
  3. Expected: [what should happen]
  4. Actual: [what happens instead]

- Environment: [local / staging / production]
- Reproduction rate:
  - [ ] Always (100%)
  - [ ] Often (50–90%)
  - [ ] Sometimes (10–50%)
  - [ ] Rare (<10%)

- Minimal reproduction: [smallest code/input that triggers it]
```

**Commands (detect from PROJECT.md Build Commands):**
```bash
# Run specific test to reproduce — use command from PROJECT.md
# e.g. Jest:  npx jest --testPathPattern="[module]" --verbose
# e.g. Vitest: npx vitest run [test-file] --reporter=verbose
# e.g. Pytest: pytest [module]/tests/ -v

# Type check (if TypeScript project)
# e.g. npx tsc --noEmit
```

**Rule**: Do NOT proceed to Phase 2 without a reproduction case. If you cannot reproduce, gather more information first.

---

## Phase 2: Isolate

Narrow the problem to the smallest possible scope.

```markdown
## Isolation Questions
- When did this start? (recent commit? deployment? config change?)
- What changed recently? (`git log --oneline -20`)
- Does it happen in all environments or only specific ones?
- Is it user-specific, data-specific, or universal?
- What is the smallest change that triggers it?
- What is the last known-good state?
```

**Layer-by-Layer Isolation Checklist (adapt to tech stack from PROJECT.md):**

| Layer | What to Check |
|-------|--------------|
| **Auth Guard** | Is authentication middleware/guard applied? Are role checks correct? |
| **Input Validation** | Are validators/serializers applied? Is validation active on the route? |
| **Data Access (ORM)** | Are soft-delete filters applied? Are relations/joins included? Are queries correct? |
| **Audit Columns** | Are created_by/updated_by/timestamps being set correctly? |
| **Frontend Reactivity** | Are reactive values accessed correctly? Is state mutated properly? |
| **i18n** | Are translation keys present in all locale files? |
| **Auth Token** | Is token expired? Is refresh/renewal happening? Is payload correct? |
| **External Service** | Is API token valid? Is endpoint/path correct? Are timeouts handled? |

**Commands:**
```bash
# Recent git changes
git log --oneline -20
git diff HEAD~5

# Search for pattern in codebase
# Use Grep tool instead of grep command
```

---

## Phase 3: Root Cause Analysis

Find the root cause, not just the symptom. Use the 5 Whys technique.

```markdown
## 5 Whys Analysis
1. Why: [First observed symptom — e.g., "API returns 403"]
2. Why: [Deeper — e.g., "RolesGuard denies the request"]
3. Why: [Deeper — e.g., "@Roles() decorator has wrong role name"]
4. Why: [Deeper — e.g., "Role enum value changed but decorator not updated"]
5. Why (Root Cause): [e.g., "No type-safe enum used for role strings — magic strings drift"]

## Root Cause Statement
[One clear sentence: X happens because Y, caused by Z]
```

**Anti-patterns to avoid:**
- Random changes: "Maybe if I change this..."
- Ignoring evidence: "That can't be the cause"
- Assuming without proof: "It must be X"
- Fixing blindly without reproducing first
- Stopping at the symptom layer

---

## Phase 4: Fix and Verify

Apply the minimal fix, then verify thoroughly.

```markdown
## Fix Plan
- Root cause: [from Phase 3]
- Fix: [minimal change to address root cause]
- Blast radius: [what else could be affected?]
- Rollback plan: [how to revert if fix causes regression]

## Verification Checklist
- [ ] Original bug no longer reproduces
- [ ] Related functionality still works
- [ ] No new issues introduced
- [ ] Regression test added to prevent recurrence
- [ ] Similar code elsewhere checked for same pattern
```

**Verification commands (use commands from PROJECT.md Build Commands):**
```bash
# Test the specific fix — use backend test command from PROJECT.md
# Run full regression suite — use test commands from PROJECT.md
# Type safety check — if TypeScript project, run tsc --noEmit
```

---

## Full Debugging Checklist

```markdown
## Before Starting
- [ ] Have a reliable reproduction case
- [ ] Know the expected vs actual behavior
- [ ] Have read the relevant TECH spec / CODING_RULES.md

## During Investigation
- [ ] Checked recent git log for relevant changes
- [ ] Checked all relevant layers (guard, DTO, service, Prisma, Vue, store)
- [ ] Added logging/console output if needed to trace data flow
- [ ] Formed and tested at least one hypothesis

## After Fix
- [ ] Root cause documented (not just "fixed the bug")
- [ ] Fix verified — original bug does not reproduce
- [ ] Full test suite passes (no regression)
- [ ] Regression test added
- [ ] Similar code checked for same issue
- [ ] Bug report created: docs/bug-reports/BUG-[YYYYMMDD]-[nn]-[feature].md
```

---

## Returning to the main workflow

| After | Do |
|-------|-----|
| Phase 3 (root cause identified) | Return to `SKILL.md` Step 4 and implement the minimal fix |
| Phase 4 (fix verified) | Run `validate-and-test` for the full regression suite, then write the bug report in `SKILL.md` Step 6 |
| Root cause is a security vulnerability | Pair with `vulnerability-scanner` before closing |

---

## Output Format

After completing all 4 phases, produce a structured summary:

```markdown
## Debug Summary: [Issue Description]

### Symptom
[What was observed]

### Root Cause
[Why it happened — the actual cause, not the symptom]

### Fix Applied
| File | Change | Reason |
|------|--------|--------|
| [file] | [what changed] | [why] |

### Verification
- Reproduction: FIXED (no longer reproduces)
- Regression: PASS (full suite)
- TypeScript: PASS

### Prevention
[How to avoid this class of bug in the future — coding rule, pattern, or test to add]
```

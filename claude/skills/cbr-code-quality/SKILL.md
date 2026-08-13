---
name: cbr-code-quality
description: "Clean-code principles and code-review checklists for any codebase. Covers SRP, DRY, KISS, YAGNI, naming, function rules, refactor guidance, AI coding style, plus comprehensive review checklists for correctness, security, performance, quality, and testing, with comment conventions and verdict criteria. TRIGGER: user wants clean-code principles, refactor guidance, coding standards, a code-review checklist, or review criteria to apply. NOT FOR: actively reviewing a specific diff or PR and producing findings/verdict (cbr-verify)."
allowed-tools: Read, Grep, Glob
metadata:
  version: "3.1"
  category: quality
---

# Code Quality

$ARGUMENTS

---

Two halves — use whichever the request calls for:

- **Writing code** — principles, naming, function and structure rules (refactoring, establishing standards).
- **Reviewing code** — checklist, comment conventions, verdict criteria (preparing a review, setting review standards).

The shared **Anti-Patterns** table and **Self-Check** apply to both.

---

## Part A — Writing Clean Code

### Core Principles

| Principle | Rule |
| --------- | ---- |
| SRP | One class/function = one reason to change |
| DRY | Extract duplication into a named abstraction |
| KISS | The simpler solution is almost always better |
| YAGNI | Do not implement what is not currently needed |
| Fail Fast | Validate inputs early; return/throw before the happy path |

### Naming Rules

| Context | Convention |
| ------- | ---------- |
| Boolean | `isActive`, `hasPermission`, `canDelete` |
| Functions | Verb + noun: `getUserById`, `sendWelcomeEmail` |
| Constants | `UPPER_SNAKE_CASE` for module-level constants |
| Collections | Plural nouns: `users`, `orderItems` |

Rules:
- No single-letter variables outside loop counters
- No abbreviations unless universally understood (`url`, `id`, `dto`)
- If you need a comment to explain a name, rename it

### Function Rules

1. **Do one thing** — if you need "and" to describe it, split it
2. **Max 3 parameters** — group related params into an object beyond that
3. **No flag parameters** — `sendEmail(user, true)` should be two functions
4. **Side effects must be obvious from the name**
5. **Return early** — use guard clauses to avoid deep nesting

### Code Structure

| Pattern | Apply |
| ------- | ----- |
| Guard Clauses | Early returns for edge cases |
| Flat > Nested | Max 2 levels of nesting |
| Composition | Small functions composed together |
| Colocation | Keep related code close |

**Comments:** Write code that does not need comments. Use comments only for:
- Why (not what) — business rationale, regulatory constraint
- Known limitation with a TODO referencing an issue tracker

### AI Coding Style

1. **Be direct** — write final code, not a draft
2. **Fix immediately** — spot a bug while implementing? Fix it in the same change
3. **No placeholders** — never commit `// TODO: implement this` or `...`
4. **Minimal blast radius** — change only what is necessary
5. **Preserve intent** — follow existing patterns rather than introducing new ones
6. **One abstraction level per function**

---

## Part B — Reviewing Code

### Review Checklist

#### Correctness

- [ ] Code does what it's supposed to do
- [ ] Edge cases handled
- [ ] Error handling in place
- [ ] No obvious bugs

#### Security

- [ ] Input validated and sanitized
- [ ] No SQL/NoSQL injection vulnerabilities
- [ ] No XSS or CSRF vulnerabilities
- [ ] No hardcoded secrets or credentials
- [ ] AI-specific: protection against prompt injection (if applicable)

#### Performance

- [ ] No N+1 queries
- [ ] No unnecessary loops or allocations
- [ ] Appropriate caching
- [ ] Bundle size impact considered

#### Code Quality

- [ ] Clear, descriptive naming
- [ ] DRY — no duplicate code
- [ ] SOLID principles followed
- [ ] Appropriate abstraction level
- [ ] No magic numbers

#### Testing

- [ ] Unit tests for new/changed code
- [ ] Edge cases tested
- [ ] Tests are readable and maintainable

#### Documentation

- [ ] Complex logic explained
- [ ] Public APIs documented
- [ ] README updated if needed

### Review Comment Conventions

| Prefix | Meaning | Blocking |
| ------ | ------- | -------- |
| BLOCKING | Must fix before merge | Yes |
| SUGGESTION | Recommended improvement | No |
| NIT | Minor style preference | No |
| QUESTION | Needs clarification | Maybe |

### Review Verdicts

| Verdict | Criteria |
| ------- | -------- |
| PASS | No blocking issues, ready to merge |
| NEEDS WORK | Has blocking issues, needs fixes |
| BLOCKED | Critical issues (security, data loss risk) |

---

## Anti-Patterns

| Anti-Pattern | Fix |
| ------------ | --- |
| Magic numbers (`price * 1.08`, `if status === 3`) | Named constant (`TAX_RATE = 0.08`, `Status.ACTIVE`) |
| God object | Split by responsibility |
| Deep nesting (>3 levels) | Guard clauses + early returns |
| Long functions (100+ lines) | Split into focused functions |
| Long parameter list (>3) | Parameter object |
| Boolean traps (`render(true, false)`) | Named options object |
| `any` type usage | Proper type definitions |
| Catch-all error handlers | Specific error handling |
| `console.log` in production | Proper logging framework |
| Dead code | Delete it — use version control |
| Inconsistent abstraction levels | Extract low-level to helper |

---

## Optional: Decision Log

If significant recommendations were made this session, write a brief decision
record — to the stream's `design/decisions/` when the analysis is scoped to one
feature's work-stream, or to project-level `docs/decisions/` when it spans
streams:

- `docs/streams/[feature]-[YYYYMMDD]/design/decisions/ADR-code-quality-[YYYYMMDD].md`, or
- `docs/decisions/ADR-code-quality-[YYYYMMDD].md`

```markdown
## Code Quality Review — [YYYYMMDD]

**Scope**: [file/module/feature analyzed]
**Top findings**: [3-5 key issues identified]
**Applied**: [changes made during this session]
**Deferred**: [recommendations NOT applied + reason]
**Re-check**: [suggest when to re-run — e.g., "after next feature addition to UserService"]
```

This log lets `cbr-verify` reference prior analysis and prevents duplicate work.

---

## Self-Check Before Completing

- [ ] Every name reveals intent
- [ ] No function does more than one thing
- [ ] No magic numbers
- [ ] No deeply nested conditionals
- [ ] No dead code or commented-out code
- [ ] No TODO placeholders left behind
- [ ] No DRY violations
- [ ] Comments explain why, not what

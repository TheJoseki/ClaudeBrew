---
name: clean-code
description: "Applies clean code principles to any codebase. Trigger when refactoring or establishing coding standards. Covers SRP, DRY, KISS, YAGNI, naming, function rules, and AI-specific coding style. TRIGGER: user wants clean-code principles / refactor guidance. NOT FOR: actively reviewing a specific diff or PR (review-code)."
allowed-tools: Read, Grep
metadata:
  version: "3.1"
  category: domain-guidance
---

# Clean Code

$ARGUMENTS

---

## Core Principles

| Principle | Rule |
| --------- | ---- |
| SRP | One class/function = one reason to change |
| DRY | Extract duplication into a named abstraction |
| KISS | The simpler solution is almost always better |
| YAGNI | Do not implement what is not currently needed |
| Fail Fast | Validate inputs early; return/throw before the happy path |

---

## Naming Rules

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

---

## Function Rules

1. **Do one thing** — if you need "and" to describe it, split it
2. **Max 3 parameters** — group related params into an object beyond that
3. **No flag parameters** — `sendEmail(user, true)` should be two functions
4. **Side effects must be obvious from the name**
5. **Return early** — use guard clauses to avoid deep nesting

---

## Code Structure

| Pattern | Apply |
| ------- | ----- |
| Guard Clauses | Early returns for edge cases |
| Flat > Nested | Max 2 levels of nesting |
| Composition | Small functions composed together |
| Colocation | Keep related code close |

**Comments:** Write code that does not need comments. Use comments only for:
- Why (not what) — business rationale, regulatory constraint
- Known limitation with a TODO referencing an issue tracker

---

## AI Coding Style

1. **Be direct** — write final code, not a draft
2. **Fix immediately** — spot a bug while implementing? Fix it in the same change
3. **No placeholders** — never commit `// TODO: implement this` or `...`
4. **Minimal blast radius** — change only what is necessary
5. **Preserve intent** — follow existing patterns rather than introducing new ones
6. **One abstraction level per function**

---

## Anti-Patterns

| Anti-Pattern | Fix |
| ------------ | --- |
| Magic numbers (`price * 1.08`) | Named constant (`TAX_RATE = 0.08`) |
| God object | Split by responsibility |
| Deep nesting (>3 levels) | Guard clauses + early returns |
| Long parameter list (>3) | Parameter object |
| Boolean traps (`render(true, false)`) | Named options object |
| Dead code | Delete it — use version control |
| Inconsistent abstraction levels | Extract low-level to helper |

---

## Optional: Decision Log

If significant recommendations were made this session, write a brief decision record to:
`docs/specs/decisions/ADR-clean-code-[YYYYMMDD].md`

```markdown
## Clean Code Review — [YYYYMMDD]

**Scope**: [file/module/feature analyzed]
**Top findings**: [3-5 key issues identified]
**Applied**: [changes made during this session]
**Deferred**: [recommendations NOT applied + reason]
**Re-check**: [suggest when to re-run — e.g., "after next feature addition to UserService"]
```

This log enables code-review-agent to reference prior analysis and prevents duplicate work.

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

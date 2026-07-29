---
name: code-review-checklist
description: Provides comprehensive code review checklists covering correctness, security, performance, code quality, and testing. Use when reviewing code, preparing for PR review, or establishing review standards.
allowed-tools: Read, Grep, Glob
metadata:
  version: "3.1"
  category: quality
---

# Code Review Checklist

$ARGUMENTS

---

## Quick Review Checklist

### Correctness

- [ ] Code does what it's supposed to do
- [ ] Edge cases handled
- [ ] Error handling in place
- [ ] No obvious bugs

### Security

- [ ] Input validated and sanitized
- [ ] No SQL/NoSQL injection vulnerabilities
- [ ] No XSS or CSRF vulnerabilities
- [ ] No hardcoded secrets or credentials
- [ ] AI-specific: protection against prompt injection (if applicable)

### Performance

- [ ] No N+1 queries
- [ ] No unnecessary loops or allocations
- [ ] Appropriate caching
- [ ] Bundle size impact considered

### Code Quality

- [ ] Clear, descriptive naming
- [ ] DRY — no duplicate code
- [ ] SOLID principles followed
- [ ] Appropriate abstraction level
- [ ] No magic numbers

### Testing

- [ ] Unit tests for new/changed code
- [ ] Edge cases tested
- [ ] Tests are readable and maintainable

### Documentation

- [ ] Complex logic explained
- [ ] Public APIs documented
- [ ] README updated if needed

---

## Anti-Patterns to Flag

| Pattern | Fix |
| ------- | --- |
| Magic numbers (`if status === 3`) | Named constants (`Status.ACTIVE`) |
| Deep nesting (`if a { if b { if c }}`) | Guard clauses / early returns |
| Long functions (100+ lines) | Split into focused functions |
| `any` type usage | Proper type definitions |
| Catch-all error handlers | Specific error handling |
| Console.log in production | Proper logging framework |

---

## Review Comment Conventions

| Prefix | Meaning | Blocking |
| ------ | ------- | -------- |
| BLOCKING | Must fix before merge | Yes |
| SUGGESTION | Recommended improvement | No |
| NIT | Minor style preference | No |
| QUESTION | Needs clarification | Maybe |

---

## Review Verdicts

| Verdict | Criteria |
| ------- | -------- |
| PASS | No blocking issues, ready to merge |
| NEEDS WORK | Has blocking issues, needs fixes |
| BLOCKED | Critical issues (security, data loss risk) |

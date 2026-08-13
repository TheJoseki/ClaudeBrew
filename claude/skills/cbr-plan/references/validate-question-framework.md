# Validation Question Framework

## Question categories (keyword → category)

| Category | Keywords to detect in the artifact |
|----------|------------------------------------|
| **Architecture** | approach, pattern, design, structure, database, API, ORM, schema |
| **Assumptions** | assume, expect, should, will, must, default |
| **Trade-offs** | trade-off, vs, alternative, option, choice, either/or |
| **Risks** | risk, might, could fail, dependency, blocker, concern |
| **Scope** | phase, MVP, future, out of scope, nice to have, stretch |

## Question format rules

- 2-4 concrete options each; mark the recommended one "(Recommended)"; "Other" is automatic.
- Surface an *implicit* decision the plan made silently — not a question the artifact already answers.
- Prioritize questions that could change the implementation significantly.

## Example questions

**[Architecture]** "TECH §2 designs the payment write path as a synchronous call. Should it be?"
1. Yes — synchronous is fine for this volume (Recommended)
2. No — make it async with a queue
3. Defer the decision to implementation

**[Assumptions]** "The plan assumes API rate limiting is out of scope. Correct?"
1. Yes — not needed this round
2. No — add basic rate limiting now (Recommended)
3. Defer to a follow-up stream

## Validation Log format

```markdown
## Validation Log

### Session {N} — {YYYY-MM-DD}
**Trigger:** {what prompted this validation}
**Questions asked:** {count}

#### Questions & Answers
1. **[{Category}]** {full question text — exact, not a summary}
   - Options: {A} | {B} | {C}
   - **Answer:** {user's choice}
   - **Custom input:** {verbatim "Other" text, if any}
   - **Rationale:** {why this decision affects implementation}

#### Confirmed Decisions
- {decision}: {choice} — {brief why}

#### Action Items
- [ ] {specific change needed}

#### Impact on Phases
- Phase {N}: {what needs updating and why}
```

## Recording rules

- Full question text (exact), all options presented, verbatim "Other" input, a rationale that
  explains the implementation impact, incrementing session number, and the trigger.

## Section mapping for propagation

| Change type | Target artifact section |
|-------------|-------------------------|
| Requirements | SRS Requirements / PLAN overview |
| Architecture | TECH design section |
| Scope | PLAN Overview / phase list |
| Risk | Risk Assessment / PLAN risk notes |
| Unknown | a new "Open Items" / Key Insights subsection |

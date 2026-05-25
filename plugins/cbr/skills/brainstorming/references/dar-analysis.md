# DAR — Decision Analysis & Resolution

DAR is a structured method (from the CMMI process area of the same name) for
making a defensible choice among alternatives instead of picking by gut. Use it
in Phase 4 whenever a decision has **real trade-offs** or is **hard to reverse**.

## When to run DAR (and when not to)

Run DAR when at least one is true:

- The choice is **hard or costly to reverse** (architecture, data model, primary
  framework, build-vs-buy, hosting/platform).
- The alternatives have **genuinely different trade-offs** — no obviously
  dominant option.
- The decision **materially shapes** scope, cost, risk, or downstream stages.

Skip DAR for minor, easily-reversible choices (naming, file layout, a library
with an obvious fit). When you skip it, say so explicitly in the artifact — "minor
and reversible, DAR not warranted" — so the skip is a recorded judgment, not a
silent gap.

## The method

1. **Frame the decision.** One sentence: what is being decided and why it matters.
2. **Identify evaluation criteria.** The dimensions that matter for *this*
   decision — e.g. performance, cost, time-to-build, maintainability,
   team familiarity, security, vendor lock-in, scalability.
3. **Weight the criteria.** Assign each a weight (e.g. 1-5) reflecting its
   importance to the goal. Weights come from the goals/constraints in the
   artifact — if a weight is itself uncertain, that is an uncertainty → ask the
   user (never-guess applies here too).
4. **List alternatives.** The 2-4 real candidate options. Back each with
   evidence from the research phase where possible.
5. **Score each alternative against each criterion** (e.g. 1-5).
6. **Compute weighted totals** (Σ weight × score) and identify the leader.
7. **Sanity-check (sensitivity).** Would a small, defensible change in weights
   flip the winner? If the result is fragile, say so and consider raising it with
   the user.
8. **Recommend** the winner with a short rationale, and note the strongest reason
   *against* it (honesty beats salesmanship).

## Scoring matrix template

```markdown
### Decision: <what is being decided>

| Criterion        | Weight | Option A | Option B | Option C |
|------------------|:------:|:--------:|:--------:|:--------:|
| <criterion 1>    |   5    |    4     |    3     |    5     |
| <criterion 2>    |   3    |    5     |    2     |    3     |
| <criterion 3>    |   2    |    2     |    5     |    4     |
| **Weighted total** |      | **39**   | **31**   | **42**   |

**Recommendation:** Option C — <one-line rationale>.
**Strongest counter-argument:** <the best reason against C>.
**Sensitivity:** <stable | flips if criterion X weight rises, etc.>
```

## Decision record (goes into the artifact)

Record each DAR in §8 of the artifact so the choice — and the reasoning behind it
— travels with the pipeline:

```markdown
#### DR-<n>: <decision title>
- **Decision:** <chosen option>
- **Alternatives considered:** <A, B, C>
- **Criteria & scores:** <the matrix above, or a link to it>
- **Rationale:** <why the winner won>
- **Evidence:** <research citations that informed the scores>
- **Revisit if:** <condition that would reopen this decision>
```

The `revisit if` line matters: it tells downstream stages the conditions under
which this decision should be reconsidered rather than treated as settled
forever.

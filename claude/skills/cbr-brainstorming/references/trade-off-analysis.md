# Trade-off Analysis — Choosing Among Alternatives

A structured way to make a **defensible** choice among alternatives instead of
picking by gut. Reach for this move whenever a decision has **real trade-offs** or is
**hard to reverse**.

## When to run it (and when not to)

Run a trade-off analysis when at least one is true:

- The choice is **hard or costly to reverse** (architecture, data model, primary
  framework, build-vs-buy, hosting/platform).
- The alternatives have **genuinely different trade-offs** — no obviously dominant
  option.
- The decision **materially shapes** scope, cost, risk, or downstream stages.

Skip it for minor, easily-reversible choices (naming, file layout, a library with an
obvious fit). When you skip it, say so explicitly in the artifact — "minor and
reversible, no trade-off analysis warranted" — so the skip is a recorded judgment,
not a silent gap.

## The method

1. **Frame the decision.** One sentence: what is being decided and why it matters.
2. **Name what actually matters here.** The few dimensions that decide *this* choice
   — e.g. performance, cost, time-to-build, maintainability, team familiarity,
   security, vendor lock-in, scalability. If *which* dimension matters most is itself
   uncertain, that is an uncertainty → ask the user (never-guess applies here too).
3. **List the alternatives.** The 2-4 real candidate options. Back each with evidence
   from the research phase where possible.
4. **Compare them honestly against what matters.** For each option, state where it is
   strong and where it is weak on the dimensions above — as a clear argument, not a
   scored grid. The output is a comparison you can defend, not a number.
5. **Recommend** the winner with a short rationale — *why it beats the runner-up* —
   and name the strongest reason *against* it (honesty beats salesmanship).
6. **Sanity-check.** Would a small, defensible shift in what you weighted most flip
   the choice? If the result is fragile, say so and consider raising it with the user.

## Decision record (goes into the artifact)

Record each significant decision in §8 of the artifact so the choice — and the
reasoning behind it — travels with the pipeline:

```markdown
#### DR-<n>: <decision title>
- **Decision:** <chosen option>
- **Alternatives considered:** <A, B, C>
- **Why it won:** <the trade-offs that decided it, over the runner-up>
- **Strongest counter-argument:** <the best reason against the choice>
- **Evidence:** <research citations that informed the comparison>
- **Revisit if:** <condition that would reopen this decision>
```

The `revisit if` line matters: it tells downstream stages the conditions under which
this decision should be reconsidered rather than treated as settled forever.

# Brainstorming Moves — Diverge, Debate, Converge

The craft behind the toolbox in SKILL.md. Brainstorming is two distinct motions
held apart: **diverge** (open the option space) then **converge** (narrow with
conviction). Collapsing them — judging while generating — is the classic failure
that yields one obvious answer and calls it done.

## Diverge — generate widely, judge later

The goal of the divergent motion is **quantity and range**, not correctness. Judgment
comes later; here it only kills ideas prematurely.

- **Defer judgment.** Do not evaluate, cost, or rank while generating. "That won't
  work because…" is a convergent thought — park it.
- **Go for quantity.** Aim for several genuinely different options, not two variants
  of one. The best option is often not in the first two you think of.
- **Force range.** Deliberately include:
  - the **obvious** option (the one the user probably expects),
  - a **minimal / do-less** option (what if we solved 80% with 20%? what if we built
    nothing and changed a default?),
  - an **inverted** option (flip a core assumption — buy instead of build, push
    instead of pull, batch instead of realtime),
  - a **wild** option (deliberately over-reaching — it stretches the space even when
    rejected).
- **Offer ideas the user did not ask for.** A brainstorm that only reacts to the
  user's single idea is weak. Your value is the alternative they dismissed too fast.

Present divergent options briefly (name + one-line essence), unjudged, then move to
converge. All of them land in artifact §8/§9 so the audit trail shows what was
considered, not just what won.

## Debate — steelman then attack

Before committing to a leading option, pressure-test it. Weak brainstorms fall for
the first plausible answer; strong ones try to break it.

1. **Steelman** — state the strongest version of the option, its best case, the
   conditions under which it clearly wins.
2. **Attack** — then turn on it: failure modes, hidden costs, second-order effects,
   what happens at 10× scale, what breaks on the unhappy path, who it makes worse off.
3. **Kill-criteria** — name what evidence or condition would make you drop it. An
   option with no kill-criteria has not been thought through.

For broad or high-stakes problems, run this with **independent lenses** rather than
one reasoner: product/UX, technical architecture, devil's-advocate. Spawn them as
`cbr:strategist` subagents (or a full agent team — `teammate-mode.md`) so the
critique is genuinely independent, not you marking your own homework. A position that
survives independent cross-examination is far more likely to be right.

## Converge — narrow with conviction

Converging is not "pick the highest score." It is committing to a direction you can
defend:

- **Land a recommendation**, not a menu. Say which option wins and *why it beats the
  runner-up* — the comparison is the point.
- **State what would change your mind** — the condition under which you would switch.
  This is honesty, and it tells the requirement stage what to watch.
- **Hard-to-reverse + real trade-offs → DAR** (`dar-analysis.md`). Reversible/minor →
  just recommend and move on (say it was minor).

### The convergence test

You are converged only when **both** hold:

1. The five exit-criterion answers exist (expected output, acceptance criteria, scope
   boundary, constraints, touchpoints — see SKILL.md).
2. **The user can restate the decision and why it beat the runner-up.** If they
   can't, the decision is yours, not theirs — keep going (invariant 5).

Only then write the artifact and hand off.

## Adaptive depth reminder

None of this is mandatory ceremony. A cheap, reversible question does not need a
four-lens debate — one good recommendation and a reason is enough. Spend the divergent
range and the adversarial debate where the decision is **wide or hard to reverse**.
Running the full craft on a trivial choice is its own failure mode.

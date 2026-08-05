# Problem-First Inversion

Use this move when the brainstorm starts from a **proposed solution** — a chosen
feature, a roadmap item, "we should build X", or an idea to triage. It is the
counter to solution-jumping: the most common way a brainstorm builds the wrong
thing well.

Concept adapted from George / prodmgmt.world (@nurijanian), *"problem-first: a
simple skill to invert bad ideas"* —
https://x.com/nurijanian/status/2063186118409929161 (treat as prior art, cite it
in the artifact's References when this move shapes the recommendation).

## The core move

Treat every proposed solution as a **compressed, imprecise confession of a problem**
the user senses but has not articulated. Do not reject the solution, and do not
start building it. Decompress it back into the problem underneath, then test whether
the proposed solution is one of several reasonable responses or a premature jump.

## When to reach for it

The user says something like:

- "We need to build X" / "add feature Y" / "the roadmap already says Z"
- "I have too many ideas, help me triage"
- "The team wants this solution but I'm not convinced"

If instead the user brings a genuine open problem (not a pre-chosen solution), you
are already problem-first — skip straight to diverging on solutions.

## The eight-section pattern

Produce these before debating implementation. Keep each tight.

1. **Solution-jumping diagnosis** — what signal made this solution feel necessary?
   What pain / failure / complaint / opportunity is hiding underneath?
2. **Underlying problem** — state the real user/business/system problem *without*
   naming the proposed solution as the answer.
3. **Assumption challenges** — the key assumptions behind the proposed solution;
   for each: risk-if-wrong + a validation test.
4. **Problem statement** — Users/context (who is affected) · Struggle (what breaks or
   slows) · Cause (why) · Consequence (what it costs) · Success (what would be
   observably better).
5. **Three alternative framings** — three different interpretations of the problem,
   each opening a *different* solution space (not three flavors of the same one).
6. **Evidence status** — `none` (vibes) · `weak` (one anecdote/opinion) · `medium`
   (repeated signal, tickets, data, interviews) · `strong` (converging qual + quant).
7. **Validation plan** — what data to inspect, who to interview, what experiment to
   run, and **what would kill the idea**.
8. **Draft stakeholder message** — a short, collaborative note that keeps momentum
   without blindly accepting the proposed solution (so the user can push back without
   sounding obstructionist).

For a lighter touch on a small idea, a concise equivalent of §1–§5 is enough — dial
depth to stakes. The artifact's §8 (Considered approaches) records the outcome.

## Reverse use — idea triage

For idea-heavy sessions: take each raw idea → extract the problem it claims to solve
→ assign an evidence status → **kill ideas with `none` unless they are cheap
experiments** → promote only ideas with real problem evidence.

## Rules

- Do not debate solution feasibility first. First ask: *what pain would make a
  reasonable person propose this?*
- Preserve momentum by using the existing solution as research evidence, not as a
  target to shoot down.
- Challenge assumptions with risk-if-wrong **and** a validation test.
- Generate **at least three** alternative problem framings before recommending one.
- Do **not** use this move to stall an obvious fix when the evidence is already
  strong — that is adaptive depth working against you.

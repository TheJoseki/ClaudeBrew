---
name: brainstorming
description: >-
  Stage 1 of the SDLC pipeline. Turns a raw idea or feature request into a
  validated, evidence-backed brainstorming artifact that the later SDLC stages
  (requirement, design, coding, testing, ship) consume as input. Its defining
  stance is "never guess": any uncertainty about intent, scope, a gap, a risk,
  or a conflict is surfaced to the user rather than silently assumed. Uses web
  and library research as source-of-truth evidence, runs DAR (Decision Analysis
  & Resolution) on real trade-offs, and supports both single-agent and
  agent-team ("teammate") brainstorming. Use this skill proactively at the very
  start of any new project or feature — whenever the user says "I have an idea",
  "help me think through", "let's design / explore / scope this", "we want to
  build X", "brainstorm", "where do I start", or describes something that does
  not exist yet and has not been specced. Use it BEFORE any requirement, design,
  or coding work. If the user jumps straight to "build me X" for something
  greenfield and under-specified, invoke this first to brainstorm before writing
  anything.
---

# Brainstorming — SDLC Stage 1

You turn a raw idea into a **validated, evidence-backed brainstorming artifact**
that downstream SDLC stages consume. You are the front door of the pipeline:
everything later (requirements, design, code, tests) inherits the quality of the
thinking you capture here. Cheap to ask a question now; expensive to discover a
wrong assumption after code is written.

## The hard gate

Do **not** write code, scaffold a project, create design or requirement
documents, or invoke any downstream SDLC skill (`requirement`, `design`,
`coding`, …) until **both** are true:

1. The brainstorming artifact is written to disk, and
2. The user has **explicitly approved** it.

This gate is the load-bearing constraint of the whole skill. Brainstorming that
slides into implementation defeats its purpose — half-baked solutions that miss
requirements are exactly what this stage exists to prevent. The only thing you
hand off is the approved artifact (see Phase 9).

## Core stance: never guess

This skill operates at the strictest threshold by design: **any uncertainty, no
matter how small, is surfaced — never silently assumed.** The reason it earns
that strictness: brainstorming is the front door of the pipeline, so a silent
assumption here is the most expensive kind — it propagates unexamined into
requirements, design, and code. Operationalize it with one heuristic:

> **If you would otherwise silently assume it, write the assumption down and ask
> about it. If you can name it, it is an uncertainty — and it goes to the user.**

This applies to unclear intent, unstated scope boundaries, gaps in the request,
risks, issues, conflicts between requirements, and any "I'll just pick the
common default" moment. Asking is not a failure — it is the product.

To keep "ask about everything" ergonomic rather than exhausting:

- **Batch related uncertainties** into a single `AskUserQuestion` call (up to 4
  questions per call), so the user answers a few fast multiple-choice rounds
  instead of an open-ended interrogation.
- **Pre-analyze every question.** Never ask a bare open question. Do the
  thinking first, then present 2-4 concrete options you derived, each with its
  trade-off, plus your recommendation. The user picks or overrides.
- See `references/clarify-loop.md` for the full playbook and worked examples.

## Workflow

```
0. Select mode (single vs team)   → verify: user confirmed the mode
1. Explore context                → verify: repo/docs read; no question already answered there
2. Research (evidence)            → verify: relevant sources fetched; URLs recorded
3. Analyze & clarify loop         → verify: every named uncertainty resolved by the user
4. DAR on trade-offs              → verify: each real trade-off has a decision record
5. Synthesize approaches          → verify: 2-3 approaches presented; sections approved
6. Scaffold stream & write artifact → verify: stream folder + STREAM.md exist; brainstorm file written under the stream
7. Self-review                    → verify: no placeholders/contradictions/open assumptions
8. User approval                  → verify: explicit "approved"
9. Handoff                        → verify: artifact location + carried-forward open questions stated
```

### Phase 0 — Select mode (single vs team)

Two modes exist:

- **Single** — you brainstorm directly with the user. Default for most requests.
- **Team (teammate)** — spawn a Claude Code **agent team** of teammates who
  explore the problem from distinct, deliberately adversarial angles (e.g.,
  product/UX, technical architecture, devil's-advocate/risk), debate to
  challenge each other's findings, and let the lead synthesize. Best for broad,
  ambiguous, high-stakes, or multi-domain problems where parallel exploration
  and structured disagreement beat a single line of reasoning.

**Recommend, never silently pick.** Assess the request's breadth, ambiguity, and
stakes; state your reasoning out loud; recommend single or team; and let the
user confirm or override before you spawn anything (teammates cost
significantly more tokens). Choosing the mode is itself a judgment call, so it
obeys the never-guess rule too.

For team mode, follow `references/teammate-mode.md`.

### Phase 1 — Explore context

Before asking the user anything, read what already answers your questions:
`CLAUDE.md`, `README.md`, existing files under `docs/`, prior specs, and the code
layout. The fastest way to violate "never guess" is to ask about something the
repo already states. Context first, questions second.

### Phase 2 — Research (evidence)

Brainstorming recommendations must rest on evidence, not vibes. This research
both informs your own analysis and gives the user references to evaluate.

- **Named library / framework / SDK / API?** Use **Context7**
  (`resolve-library-id` then `query-docs`) — it is enabled in this project and
  returns current docs.
- **Patterns, comparisons, prior art, best practices?** Use **WebSearch** /
  **WebFetch**.
- **Record every cited URL.** Each one goes into the artifact's *References*
  section as the source of truth backing a claim or recommendation. A
  recommendation with no citation is an opinion; with one, it is evidence.

### Phase 3 — Analyze & clarify loop (the never-guess engine)

This is the heart of the skill. Deeply read the user's input, then enumerate, in
writing, every:

- **Assumption** you would otherwise make (label each with confidence),
- **Gap** — something the request needs but does not specify,
- **Ambiguity** — wording that admits more than one reading,
- **Risk / issue** — anything that could derail the work,
- **Conflict** — requirements that pull against each other.

For each item you cannot resolve from context (Phase 1) or research (Phase 2),
raise it with the user via a batched, pre-analyzed `AskUserQuestion`. Do not
advance to synthesis while a named uncertainty remains open. See
`references/clarify-loop.md`.

### Phase 4 — DAR on trade-offs

When a decision has **real trade-offs** or is **hard to reverse** (architecture,
data model, build-vs-buy, framework choice, major scope forks), do not pick by
gut. Run **DAR — Decision Analysis & Resolution**: define criteria, weight them,
list alternatives, score against the criteria, and recommend the winner with its
rationale. Record each DAR as a decision record in the artifact. Full method and
template: `references/dar-analysis.md`. Minor, easily-reversible choices do not
need DAR — say so and move on.

### Phase 5 — Synthesize approaches

Propose **2-3 candidate approaches** with their trade-offs (never a single
take-it-or-leave-it option). Present the emerging design in **sections with
approval checkpoints** so the user validates incrementally rather than reacting
to a wall of text at the end. Apply **YAGNI** ruthlessly — strip anything not
required by the actual goal. If the request spans multiple independent
subsystems, flag it and decompose into ordered sub-topics, each warranting its
own brainstorm.

### Phase 6 — Scaffold the stream & write the artifact

Brainstorming **opens the work-stream**. Pick a short kebab-case `<slug>` for the
topic and today's date `<YYYYMMDD>`, then:

1. Create the stream folder `docs/streams/<slug>-<YYYYMMDD>/` (the folder name is
   the stream identity every later artifact inherits).
2. Scaffold its manifest `docs/streams/<slug>-<YYYYMMDD>/STREAM.md` from
   `docs/_templates/STREAM.md` — the stream's index + task board. `brainstorming`
   owns creating it; later stages only append their own rows.
3. Write the brainstorm to `docs/streams/<slug>-<YYYYMMDD>/brainstorm/BRAINSTORM.md`
   (the folder carries the slug, so the filename drops it). Follow
   `references/artifact-template.md` exactly — its field list is the **contract**
   the requirement stage reads, so every section matters.

### Phase 7 — Self-review

Before showing the user, re-read the artifact with fresh eyes and scan for:

- **Placeholders** ("TBD", "TODO", "<fill in>") — resolve or convert to an
  explicit open question.
- **Contradictions** — sections that disagree.
- **Unlabeled assumptions** — every assumption must carry a confidence label and
  a note on how it was validated (or that it is still open).
- **Unresolved uncertainties** — anything you named in Phase 3 but never closed.

Fix what you can; re-ask the user about what you cannot.

### Phase 8 — User approval

Present the artifact and ask for explicit approval. If the user requests changes,
loop back through the relevant phase. Approval is the gate from Phase 0 lifting.

### Phase 9 — Handoff

State plainly: where the artifact lives, that it is the **input to the
`requirement` stage**, and which **open questions are carried forward** for that
stage to close. The next stage should be able to start from this file alone.

Once the handoff is stated, **this skill ends.** Do not auto-invoke the
`requirement` skill or any other downstream stage — the user
decides when Stage 2 begins. Cascading the pipeline silently would take the
steering wheel away from the user between stages, which is exactly what the hard
gate exists to prevent.

## When the user steers: new angles & pivots

Brainstorming is a live dialogue, so the user will sometimes answer in ways your
options did not anticipate, or change direction entirely. Treat steering as
signal, never as noise to correct — the user usually knows something you do not.

- **A novel angle** (the user picks "Other", or adds a perspective you did not
  offer). This is often the most valuable input in the session. Adopt it as a
  first-class answer, then **re-enumerate** (re-run Phase 3): a new angle can
  invalidate earlier assumptions or open fresh uncertainties. If it conflicts
  with something already decided, surface the conflict and ask — never silently
  reconcile. If it competes with your prior direction on a real trade-off, that
  is a DAR.

- **A pivot** (the user changes or replaces the idea mid-stream). First *detect*
  it: the new input no longer fits the current problem framing. Do not keep
  quietly building on the old idea, and do not silently discard the old work.
  Then apply never-guess to the pivot itself — confirm which kind it is:
  - **Replacement** — the old idea is abandoned. Mark the current artifact
    superseded, carry over only still-relevant context, and restart the workflow
    (new topic slug, new artifact file) for the new idea.
  - **Branch** — explore the new direction *alongside* the old. Run a separate
    brainstorm, or set up a DAR between the two directions.
  - **Refinement** — same idea, shifted/narrowed scope. Update the current
    artifact in place and re-run only the affected phases.

  Preserve the audit trail in every case; a pivot is progress, not wasted effort.

## Reference files

- `references/clarify-loop.md` — the never-guess clarify loop: how to enumerate
  uncertainties and turn them into batched, pre-analyzed questions, with
  examples.
- `references/dar-analysis.md` — DAR method, scoring matrix, and decision-record
  template.
- `references/artifact-template.md` — the exact handoff artifact schema.
- `references/teammate-mode.md` — how to run team brainstorming with a Claude
  Code agent team.

# The Clarify Loop — Never-Guess Playbook

This skill operates at the strictest threshold by design: **any uncertainty, no
matter how small, is surfaced — never silently assumed.** This file shows how to
honor that without drowning the user in questions.

## The governing heuristic

> If you would otherwise silently assume it, write the assumption down and ask
> about it. If you can name it, it is an uncertainty.

The test is not "is this a big decision?" — it is "am I about to fill a blank the
user did not fill?" If yes, that blank becomes a question.

## Step 1 — Enumerate uncertainties

After exploring context and researching, list — in writing, for yourself — every
item in these five buckets. Naming them is what makes them askable.

| Bucket | Prompt to find them |
|---|---|
| **Assumptions** | What am I about to take for granted that the user never stated? |
| **Gaps** | What does this request need that it does not specify? |
| **Ambiguities** | What wording could be read more than one way? |
| **Risks / issues** | What could derail this, or has hidden cost? |
| **Conflicts** | Which stated wants pull against each other? |

Drop only the items that context or research has already answered — and note
where they were answered, so you can show your work.

## Step 2 — Turn uncertainties into questions

Two rules make "ask about everything" tolerable:

1. **Batch.** Group related uncertainties into one `AskUserQuestion` call (up to
   4 questions per call). Prefer a few multiple-choice rounds over a long single
   stream of questions.
2. **Pre-analyze.** Never ask a bare open question. Do the thinking first, then
   present 2-4 concrete options you derived — each a real, distinct choice with
   its trade-off — and mark your recommendation. The user picks fast or
   overrides. This converts "ask about everything" from an interrogation into a
   quick decision review.

Order questions so that answers which unlock other questions come first. If an
answer would make later questions moot, ask it in an earlier round.

## Step 3 — Loop until clean (but you may interleave)

Re-enumerate after each round — answers often reveal new uncertainties. Clarifying
is a **move, not a gate**: you do not have to close every uncertainty before you may
diverge or sketch. Park an uncertainty, generate an option, and let the option
resolve the uncertainty — that is how a person brainstorms. The one hard rule is
never-guess at **convergence**: no named uncertainty may still be open (silently
assumed) when you write the artifact. Anything deliberately deferred goes to the
artifact's §7 (open questions), which is different from an unresolved guess.

## What good questions look like

**Bad — bare and open (forces the user to do your thinking):**

> "How should authentication work?"

**Good — pre-analyzed options with a recommendation:**

> **Question:** "How should users authenticate?"
> - *Email + password with our own store* — full control, but we own password
>   security, resets, and breach risk.
> - *OAuth via Google/GitHub* (Recommended) — no password handling, fast
>   onboarding; depends on third-party availability and needs provider setup.
> - *Magic-link email* — no passwords, low friction; depends on email delivery
>   and adds a round-trip per login.

**Bad — silently assuming a default:**

> *(writes "the app will support English")* — never stated by the user.

**Good — naming the assumption and asking:**

> **Question:** "Which languages must the UI support at launch?"
> - *English only* (Recommended) — simplest; revisit i18n later.
> - *English + one more (specify)* — doubles copy + QA now.
> - *Full i18n framework from day one* — most flexible, most upfront cost.

## When something truly cannot be a multiple-choice question

Some uncertainties need a free-text answer (a name, a number, a URL, a domain
detail only the user knows). Still pre-frame it: state what you need, why it
matters, and the consequence of each plausible answer, then ask. The
`AskUserQuestion` tool always lets the user supply their own answer via "Other",
so you can offer your best-guess options and still capture anything you missed.

## When the user answers "Other" or supplies a new angle

The options you offer are your *best guesses*, not the menu. When the user goes
off-menu, that answer carries information your analysis missed — so it raises the
re-analysis bar, it doesn't lower it.

1. **Adopt it as a first-class answer** — never nudge the user back toward your
   original options.
2. **Re-enumerate** (Step 1 again) with the new angle in place. Ask: does this
   invalidate an assumption I'd recorded? Open a new gap? Conflict with an
   earlier answer?
3. **Surface any conflict** the new angle creates rather than quietly
   reconciling it.

**Example.** You ask "What platform first?" offering Web / Mobile / Both, and the
user answers *"Actually, it should be a Slack bot — my users live in Slack."*
That is not a fifth platform option; it reframes the product. Re-enumerate:
distribution shifts to the Slack app directory, "accounts" may now mean Slack
OAuth, the "streak heatmap" hero view may not fit a chat surface, and your
backend trade-offs change. Acknowledge the reframe, then re-open the questions
it disturbed — do not carry forward answers that the pivot has quietly outdated.

## When the user pivots the whole idea

If the new input replaces or substantially changes the idea (not just one
answer), follow the **"When the user steers"** protocol in SKILL.md: detect it,
then confirm whether it is a **replacement** (supersede the artifact, restart for
the new idea), a **branch** (explore alongside / run a trade-off analysis on the two), or a
**refinement** (update in place, re-run affected moves). Apply never-guess to
*which kind of pivot it is* — do not assume.

## When the user overrides the threshold

Real users will sometimes say "stop asking, just pick reasonable defaults" or
"this is taking too long." Honor it — user autonomy wins. But keep the
never-guess audit trail intact rather than silently caving:

- Record **every default you then pick** as a **low-confidence assumption** in §6
  of the artifact.
- List **every question you skipped** in §7 (open questions carried forward) so
  the `requirement` stage closes them instead of inheriting silent guesses.
- **Surface the count at handoff**, e.g. "I made 8 default choices and deferred 5
  questions to Stage 2."

This converts the override from a violation of never-guess into a *recorded
trade-off* — the user gets speed, and the pipeline still carries no invisible
assumptions.

## Anti-patterns to avoid

- **Assuming "the obvious default."** The whole point of this threshold is that
  obvious-to-you is not obvious-to-them. Name it and ask.
- **Asking everything at once with no analysis.** Twenty bare questions is worse
  than four well-analyzed rounds. Batch and pre-think.
- **Proceeding past an open uncertainty** because "it probably doesn't matter."
  If it truly doesn't matter, it isn't an uncertainty — and you can say so
  explicitly rather than silently deciding.

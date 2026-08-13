# Red-Team Workflow — `cbr-plan red-team {stream-slug}`

Adversarially review a plan/design artifact by spawning parallel reviewer agents that try to tear
it apart, each under a different hostile lens. You adjudicate the findings; the user decides which
to apply. This is the adversarial complement to `cbr-brainstorming/references/trade-off-analysis.md`
(which weighs alternatives), not a duplicate — red-team attacks a *chosen* plan for flaws.

**Mindset**: like hiring someone who hates the author and wants to destroy their work.

## Artifact resolution

The subcommand operates on one **work-stream**. Resolve it from `{stream-slug}`:

1. Glob `docs/streams/{slug}-*/`; if several match, ask which (never auto-pick).
2. Read that stream's `plan/PLAN.md` (the primary artifact) plus, if present,
   `requirements/SRS.md`, `design/BASIC.md`, `design/TECH.md` — the design chain a red-team of a
   `cbr-plan` output should attack as a whole, not just the plan.
3. No stream / no `PLAN.md` → tell the user to run `cbr-plan` first; do not fabricate a plan to attack.

## Step 1 — Read the artifacts

Read `plan/PLAN.md` and every design artifact present in the stream, in full. Reviewers read these
same files directly, by path — never paste their bodies into a spawn prompt.

## Step 2 — Scale the lens count by size

Count `PLAN.md`'s phases (fall back to `BASIC.md`'s module count when the plan is stream-light and
phase-free):

| Size | Reviewers | Lenses |
|------|-----------|--------|
| 1-2 phases | 2 | Security Adversary + Assumption Destroyer (one per agent type — see below) |
| 3-5 phases | 3 | + Failure Mode Analyst |
| 6+ phases | 4 | + Scope & Complexity Critic (all four) |

At the 2-lens tier, deliberately pick **one lens from each agent type** (Security Adversary →
`cbr-reviewer`, Assumption Destroyer → `cbr-strategist`) so both charter styles are represented
even at the smallest tier.

This lens-count scale is **separate from** the verification *tier* (Light/Standard/Full = 1-2/3-4/5+
phases, in [`verification-roles.md`](verification-roles.md)) that decides which verification role each
reviewer applies — compute both from the same phase count. A role applies only to a lens actually
spawned at the current lens-count tier, and at Standard the Contract-Verifier method is carried by
whichever spawned reviewer the tier-precedence rule assigns it to (`red-team-personas.md`), not by an
unspawned lens.

## Step 3 — Load the lens definitions

Load [`red-team-personas.md`](red-team-personas.md): the four lenses, the **agent-split table**
(which lens runs on `cbr-reviewer` vs `cbr-strategist`), the verification-role pairing, and the
reviewer prompt template.

## Step 4 — Spawn the reviewers (one message, concurrent)

Spawn all reviewers for this tier in a single message so they run concurrently. Per the D9 split:

- **Security Adversary, Failure Mode Analyst → `cbr-reviewer`** (its charter already mandates
  `file:line` evidence and carries Grep/Glob/Bash — the least prompt-engineering risk for an
  evidence-filtered audit).
- **Assumption Destroyer, Scope & Complexity Critic → `cbr-strategist`** (its skeptic / YAGNI-enforcer
  divergence role fits these lenses directly).

Each spawn prompt carries the four parts the template in `red-team-personas.md` requires: the
plan-document override, the lens + persona, the artifact **paths** to read, and the hostile
instructions with the assigned verification role. Reviewers return findings; they do **not** edit
the artifacts — the orchestrating `cbr-plan` applies accepted findings itself (which is why the
no-`Write` `cbr-strategist` is fine here).

## Step 5 — Collect, dedupe, cap

Collect all findings → dedupe overlapping ones aggressively → sort Critical → High → Medium →
**cap at 15**. Quality over quantity; a wall of Medium findings is noise.

## Step 5.5 — Evidence filter (before merit)

For each finding, check its `Evidence:` field for at least one `file:line`-shaped citation
(`path/to/file.ext:NNN`). **No citation → auto-Reject** with rationale "No codebase evidence" —
do not evaluate its merit. This is the mechanism that keeps a plausible-but-unfounded finding from
reaching the user.

## Step 6 — Adjudicate

For each finding that passed the evidence filter, decide **Accept** or **Reject** with a one-line
rationale citing the verification source (matching CBR's review-audit-self-decision discipline:
reject an audit concern only with a stated verification source).

## Step 7 — User decides (`AskUserQuestion`)

Present the accepted set via `AskUserQuestion` (batched, pre-analyzed — the contract's never-guess
rule, `{{CBR_ROOT}}/rules/agent-contract.md:13`):

- **"Apply accepted"** — apply all accepted findings.
- **"Review each"** — per-finding `AskUserQuestion`: *Yes, apply* / *No, reject* / *Modify* (the
  user's free-text via "Other" sets disposition "Accept (modified)").
- **"Reject all — plan is fine"** — apply nothing.

## Step 8 — Apply to the artifacts

For each accepted finding, edit the target artifact (`PLAN.md` or the design file it concerns)
inline. Then append a `## Red Team Review` section to `plan/PLAN.md` (format in
`red-team-personas.md` → "PLAN.md section format"). Do the mandatory stream upkeep afterward
(`{{CBR_ROOT}}/docs/references/sdlc-reference.md`): update `STREAM.md`'s board if the plan's phase
statuses changed.

## Step 9 — Whole-Plan Consistency Sweep (mandatory after any edit)

Load [`verification-roles.md`](verification-roles.md) → "Whole-Plan Consistency Sweep". A red-team
edit usually changes one artifact locally; this sweep stops a stale claim from surviving elsewhere
in the chain (SRS ↔ BASIC §6.5 ↔ TECH §4.3 ↔ PLAN). Append its result under `## Red Team Review`.
If unresolved contradictions remain, list them and **do not** present the plan as ready — this is a
hard gate, matching `cbr-plan`'s own no-cascade rule.

## Output

Report: total findings by severity, accepted vs rejected count, artifacts modified, the consistency
sweep result, and the key risks addressed. Then STOP — the user decides whether to run
`cbr-plan validate {slug}` next (sequencing: red-team before validate, since a red-team edit would
invalidate a prior validation) or proceed to `cbr-implement`.

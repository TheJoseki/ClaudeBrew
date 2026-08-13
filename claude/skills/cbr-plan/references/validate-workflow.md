# Validate Workflow — `cbr-plan validate {stream-slug}`

Interview the user with critical questions to confirm assumptions, decisions, and trade-offs in a
plan/design artifact *before* `cbr-implement` starts — the cheapest gate, surfacing unspecified
assumptions and hand-wavy phases while they are still cheap to fix.

## Artifact resolution

Same as red-team: resolve `{stream-slug}` → `docs/streams/{slug}-*/`, read `plan/PLAN.md` plus any
`requirements/SRS.md` / `design/BASIC.md` / `design/TECH.md`. No `PLAN.md` → run `cbr-plan` first.

## Sequencing

Run **red-team before validate** when both are wanted — a red-team edit changes the plan, and
validating a pre-red-team draft would be invalidated by the later edit. The Step 2.5 guard below
enforces the "don't double-verify" half of this.

## Step 1 — Read the artifacts

Read `PLAN.md` + every design artifact present, looking for decision points, assumptions, risks, and
trade-offs to probe.

## Step 2 — Extract question topics

Load [`validate-question-framework.md`](validate-question-framework.md) — the keyword→category map
(Architecture / Assumptions / Trade-offs / Risks / Scope) and the recording format.

## Step 2.5 — Verification pass (auto-scaled)

Load [`verification-roles.md`](verification-roles.md). Verify the artifact against the live codebase
before interviewing.

**Skip-guard**: if `## Red Team Review` already exists in `PLAN.md` with verification evidence, skip
to Step 3 — only resolve any remaining `[UNVERIFIED]` tags. (A red-team already fact-checked; don't
re-verify the same claims.)

1. **Tier** by phase count (1-2 → Light / Fact Checker; 3-4 → Standard / +Contract Verifier; 5+ →
   Full / all 4). All roles via `cbr-reviewer`.
2. For each active role, sample N claims/phase, run grep/glob, collect `VERIFIED | FAILED | UNVERIFIED`.
3. **Every FAILED becomes an additional interview question** in Step 4, with a glob-suggested
   alternative marked "(Recommended)". **Never auto-correct an artifact** — all corrections go through
   the interview.
4. Scan for planner-tagged `[UNVERIFIED]` claims; attempt to resolve.
5. Append a `### Verification Results` block to `## Validation Log`.

## Step 3 — Generate questions

Per detected topic, one concrete question with 2-4 options; mark the recommended one "(Recommended)".
Only genuine decision points — if the plan is simple, fewer than the minimum is fine.

## Step 4 — Interview (`AskUserQuestion`)

Use `AskUserQuestion`, **max 4 questions per call** — this is not a new convention, it is the
contract's existing never-guess / batch-related-uncertainties rule
(`{{CBR_ROOT}}/rules/agent-contract.md:13`). **Mandatory pre-question recap first**: output a brief
visible recap of the plan (phases, key decisions, the assumptions/risks the interview will probe —
5-10 bullets), because validate often runs in a *fresh session* where the user has not seen the plan
body this turn. Each question and option must stand alone (name the section/decision — don't assume
prior-turn context is on screen).

## Step 5 — Document answers

Append a `## Validation Log` section to `PLAN.md` in the format from `validate-question-framework.md`
(Session N header, trigger, per-question full-text + options + answer + verbatim custom input +
rationale, Confirmed Decisions, Action Items, Impact on Phases).

## Step 6 — Propagate to the artifacts

Auto-apply confirmed decisions to the affected artifact sections (mapping in
`validate-question-framework.md` → "Section Mapping"), tagging each edit
`<!-- Updated: Validation Session N — {change} -->`.

## Step 7 — Whole-Plan Consistency Sweep (mandatory after propagation)

Load [`verification-roles.md`](verification-roles.md) → "Whole-Plan Consistency Sweep". Re-read the
whole chain, reconcile any stale/contradictory claim the decisions introduced, append
`### Whole-Plan Consistency Sweep` under `## Validation Log`. Unresolved contradictions → ask the
user, do not recommend `cbr-implement`.

## Output & next steps

Report: questions asked, decisions confirmed, propagation results, sweep result, and a
proceed-or-revise recommendation. Then STOP. Only recommend `cbr-implement` when the Verification
Results show `Failed: 0` **and** the sweep shows zero unresolved contradictions — otherwise revise
first. (Best practice, matching claudekit: suggest the user `/clear` before a heavy implement run so
the fresh session isn't polluted by planning context.)

# CBR R3: Collapsing 10 SDLC Skills to 3 — and Almost Shipping a Security Regression

**Date**: 2026-08-12 23:45
**Severity**: Medium (design-time catch, zero production impact)
**Component**: SDLC skill architecture (`claude/skills/cbr-{analyze-requirement,design-screen,design-function,plan-writing,implement-feature,review-code,unit-test,integration-test,vulnerability-scanner,fix-bug}`)
**Status**: Resolved — plan validated, execution not started

## What Happened

CBR's SDLC is 10 separate, hard-gated stage-executor skills, and the user experiences using it as rigid
ceremony ("PDD tiêu cực") instead of collaboration. `claudekit-engineer` — the parent toolkit CBR was
imported from — solves the same problem with mode-flags (`--fast/--hard/--deep/--auto`) that scale rigor to
risk instead of forcing every stage through its own stop. `/ak-brainstorm` → `/ak:plan --hard` produced a
9-phase plan (`plans/260811-2321-cbr-r3-flexible-sdlc-core-skills/plan.md`) collapsing the 10 skills into a
merged core. The first draft targeted **2** skills: `cbr-plan` and `cbr-implement`.

A 4-lens red-team (Security Adversary, Failure Mode Analyst, Assumption Destroyer, Scope & Complexity
Critic) found 15 evidence-cited defects. Finding #2 was the one that mattered: merging `review-code` and
`vulnerability-scanner` into `cbr-implement` would fold a `Write`-holding skill together with skills that
**today hold no `Write`/`Edit` grant at all**. That's the entire mechanism that makes fresh-eyes review
impossible to self-grade — Claude Code has no per-phase tool scoping inside a single skill, so once
`cbr-implement` gets `Write`, every code path inside it, including the "review" path, has it too. The
2-skill design would have quietly turned a *mechanical* guarantee into a *prose* one ("please don't
self-grade") and shipped it as a refactor, not a security decision.

## The Brutal Truth

This is the finding that makes you slightly sick to read, because the failure mode is silent. Nothing
crashes, no test fails — the gate still runs, the verdict artifact still gets written, just by the same
tool-permission context that wrote the code. `verdict-gate.py` would pass a JSON blob that looks exactly as
legitimate as a real fresh-eyes verdict. A 2-skill merge that looked like a clean 24→16 win on paper was
actually a 24→16 win purchased by deleting a security control and not writing that down anywhere — the kind
of thing that ships in MINOR release notes as "simplified skill topology" and nobody notices for a year.

## Technical Details

- Original design: `cbr-plan` (4 merged) + `cbr-implement` (6 merged, including review-code +
  vulnerability-scanner) = 2 skills.
- Finding #2 (Critical): "never self-grade" is enforced today by `allowed-tools` frontmatter lacking
  `Write` on `review-code`/`vulnerability-scanner`; `producedBy` on the verdict artifact is unvalidated, so
  nothing else in the pipeline would have caught the merge either.
- 14 other findings in the same pass: a `next_action` bug generating `/cbr-cbr-plan` (double-prefixed,
  nonexistent skill), a `--no-test` mode silently skipping the UNIT/INTEGRATION verdict (violating the
  plan's own "no mode skips a verdict" invariant), and an undercounted blast radius — ~30+ files across
  evals, `_templates/`, and doc narrative still referencing the 10 retired skill names, one of which
  (`evals/test_opener_law.py`) would have crashed outright on a deletion it wasn't updated for.

## What We Tried

- **Considered**: patch `verdict-artifact.schema.json` with a "high-risk stop" flag to compensate for the
  merged skill's tool access. Rejected — a schema patch is *policy* layered on a broken *mechanism*; it
  doesn't stop the same context from writing both the code and its own passing grade.
- **Chosen**: split into **3** skills — `cbr-plan` (unchanged), `cbr-implement` (implement-feature +
  fix-bug + test-authoring, holds `Write`), `cbr-verify` (new — review-code + vulnerability-scanner +
  test-grading, **no** `Write`/`Edit`). Keeps the tool-grant boundary intact by construction, not convention.

## Root Cause Analysis

The 2-skill draft optimized for the visible goal (fewer skills, less ceremony) and treated "which tools
does the merged skill need" as an implementation detail to sort out later. It wasn't a detail — the
*absence* of `Write` on the two gate skills was already the load-bearing security control, just one nobody
had written down because it had always been implicit in the skill boundary. Merging skills without first
asking "what invariant is this boundary silently enforcing" is exactly how you delete a control while
writing "de-ceremony" in the commit message.

## Lessons Learned

- **A skill boundary can be a security boundary even when nothing calls it that.** Before merging skills,
  check what their *current* tool-grant difference is doing, not just what their prose says.
- **Red-team before build, not after.** All 15 findings, including this one, were caught before a single
  file changed — a 4-lens adversarial pass on the plan, not the diff.
- **"Fewer skills" is not automatically "less complexity."** 3 skills beats 2 here because the count of
  skills should follow the count of trust boundaries, not the other way round.

## Next Steps

- Owner: user, next session. `/ak:cook` Wave 1 (phases 1-4, 6, 8, 9 — the core 10→3 merge, ~10.5d) when
  ready, branching fresh off `origin/main` (already synced). Plan explicitly asks to confirm `--auto` before
  use.
- Wave 2 (phases 5, 7 — `cbr-plan red-team`/`validate` subcommands, task-hydration bridge, `--team`
  extension) is deferred to its own follow-up stream once Wave 1 ships as 0.12.0 — not bundled into this
  release.
- No code changed this session. This entry documents the decision record, not a code change.

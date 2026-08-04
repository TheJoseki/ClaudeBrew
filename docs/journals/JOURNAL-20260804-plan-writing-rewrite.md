# plan-writing Rewritten: Killing the Gating Risk Before Touching Prose, Not After

**Date**: 2026-08-04 22:08
**Severity**: Medium
**Component**: `plugins/cbr/skills/plan-writing/*` (SKILL.md + 2 new references), `rules/sdlc-conventions.md`, `docs/_templates/STREAM.md`, `plugins/cbr/skills/brainstorming/SKILL.md`, `CLAUDE.md`
**Status**: v0.7.0 shipped **in worktree only** — commit on hold for user review, not merged to `main`

## What Happened

`plan-writing` was an orphan: v3.1, `$ARGUMENTS`-driven, no input-contract, not stream-integrated — CBR had brainstorming as the only stream opener, so there was no coherent path for maintenance work on an existing codebase with no brainstorm. Executed `plans/260804-1829-rewrite-cbr-plan-writing-flexible-input-contract-plus-stream-light-brownfield-entry/` via `/ak-cook`: rewrote the skill into a 194-line "invariants + moves" stage (same house style as the brainstorming rewrite), added a **mandatory Step-1 input-contract** (`requirements/SRS.md → brainstorm/BRAINSTORM.md → research/RES-*.md → code`, ask the user when several exist, refuse to plan on nothing), and made `plan-writing` a **second stream opener** — brownfield "stream-light": scaffolds `STREAM.md` with `lane: brownfield`, writes `plan/PLAN.md`, does not force G1–G3.

## The Brutal Truth

The part of this plan that could have hurt is the gating question — does suppressing G1–G3 for a plan-only stream stay a convention, or does it force a change to `hooks/lib/sdlc_state.py`, the one file every gate in the suite trusts for authority? That question got a dedicated Phase 1 *spike*, run and closed **before a single line of the skill was rewritten**. I ran `sdlc_state.infer_gate_progress` against a scratchpad fixture with only a plan artifact present: gates read `pending`, not error; `_stream_archived` stayed `False` with the `lane: brownfield` marker sitting there inert. Confirmed empirically, not just by reading the code. That is the whole reason the rewrite shipped with **zero lines changed in `sdlc_state.py`** — the blast radius that would have forced folding this into the deferred "full lane" frame (Frame C) never materialized, because it was checked first instead of discovered mid-rewrite.

## Technical Details

- Input-contract lives in `references/input-contract.md`; SKILL.md stays under 300 lines by design (`plan-structure.md` carries the artifact template detail).
- `allowed-tools` expanded to `Read, Grep, Glob, Write, Edit, AskUserQuestion` — deliberately **no `Task`, no `Agent`, no `Bash`**. The no-cascade guarantee (plan-writing never triggers implementation) is enforced by what the tool allowlist physically cannot do, not by a "please don't" sentence in the prose.
- 5 structural gates green: `claude plugin validate`, `test_canonical_paths.py`, `test_release_docs.py` (7/7), `test_sdlc_state.py` (20/20), `test_lifecycle_hooks.py` (28/28).
- Independent behavioral dry-run (fresh-eyes code-reviewer subagent, not self-graded) ran all 6 evals: 6/6 PASS, but surfaced 5 non-blocking edge cases that would not have shown up in a static read — e.g. SoT detection needed scoping to *one* stream (a multi-stream repo could misfire the "which source?" ask), and "code-as-source" needed a hard definition (user-pointed, not scout-discovered) so a bare feature name couldn't get scouted into looking "familiar" and quietly dissolve the refuse-on-empty gate. All 5 fixed before release.

## What We Tried

The plan's own validation interview (Session 1) forced 4 fork decisions instead of letting the model default to the cheap option. On 3 of 4, the user picked the more ambitious path over YAGNI: user-selectable multi-SoT resolution (not auto-pick), a real frontmatter `lane:` marker (not convention-only prose), and the full invariants+moves rewrite (not a light input-contract patch). That's `cbr-optimal-over-yagni` in practice — this repo is a framework rebuild, and framework code that quietly auto-picks a source of truth for the user is exactly the kind of shortcut that erodes trust in a plan artifact later.

## Root Cause Analysis

The original `plan-writing` was orphaned because it predated the stream-first architecture entirely — it was never rewired when `brainstorming` and the gate machinery moved to `docs/streams/`. Nobody owned closing that gap until this plan made it explicit. The fix wasn't a patch; it required proving the new failure mode (gate suppression) was safe *before* investing in the rewrite, which is why the plan structured Phase 1 as a standalone go/no-go spike instead of bundling the risk check into implementation.

## Lessons Learned

Green structural gates prove the skill parses and lives in the right place — they say nothing about whether it does what it claims. The gates here (`plugin validate`, `canonical-paths`, `release-docs`, `sdlc_state`, `lifecycle_hooks`) all passed and still would have passed if the input-contract silently auto-picked a source or if refuse-on-empty had a hole in it. Only the independent behavioral dry-run caught those. Second lesson, reinforced from the brainstorming rewrite two days ago: run the highest-blast-radius risk check as its own gated phase *before* the rewrite, not folded into it — Phase 1 being GREEN is what let Phases 2–4 proceed without a mid-flight scope change.

## Next Steps

Commit is staged in the worktree, **on hold pending user review** — not pushed, no PR opened. Owner: user, this session or next. Two open follow-ups recorded in the plan, neither blocking: (a) the greenlit `explore`/scout skill is the next stream (Frame A) — the input-contract already lists `research/RES-*.md` so no further `plan-writing` change is needed when it lands; (b) suite-wide open question, not a plan-writing regression — is `docs/_templates/` guaranteed seeded before a brownfield "no CBR docs" repo opens a stream? Applies identically to `brainstorming`'s opener path, so it needs a suite-level decision, not a local fix.

## AgentWiki

AgentWiki publishing skipped — `agentwiki` CLI not found on PATH (`agentwiki whoami` → command not found) and no AgentWiki MCP tools are exposed in this session. Local journal entry is the source of truth.

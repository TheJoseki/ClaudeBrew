# CBR R3 Wave 1: 10 SDLC Skills Become 3, and the Cleanup Found More Bugs Than the Merge

**Date**: 2026-08-13 17:00
**Severity**: Medium (large surface-area refactor; caught real pre-existing bugs, shipped clean)
**Component**: `claude/skills/cbr-{plan,implement,verify}` (new) — retires `analyze-requirement`,
`design-screen`, `design-function`, `plan-writing`, `implement-feature`, `fix-bug`, `review-code`,
`unit-test`, `integration-test`, `vulnerability-scanner`; `hooks/lib/sdlc_state.py`; `claude/docs/`
**Status**: Implementation complete, PR #14 open awaiting review — not yet merged, not yet published to npm

## What Happened

Yesterday's session (2026-08-12) red-teamed and validated the R3 plan but implemented nothing. Today
executed it: all 7 Wave-1 phases of `plans/260811-2321-cbr-r3-flexible-sdlc-core-skills/plan.md`, on
`feat/r3-flexible-sdlc-core-skills` off `main`@`eacac55`. Ten hard-gated stage-executor skills collapsed
into three — `cbr-plan` (427 lines, merges requirement/screen/tech-design/plan-writing), `cbr-implement`
(220 lines, merges implement-feature/fix-bug/test-authoring, holds `Write`), `cbr-verify` (merges
review-code/vulnerability-scanner/test-grading, **holds no `Write`/`Edit` grant at all** — the mechanical
guarantee the 3-skill split existed to preserve, per yesterday's red-team finding). Skill count: 24 → 17,
verified by directory count, not assumed. Six commits, full suite green (13 Python test files + 44 Node
tests), PR #14 opened against `main` (not yet merged), version bumped to 0.12.0 locally.

## The Brutal Truth

The plan was already validated — the design work was done, the hard adversarial thinking happened
yesterday. Today should have been mechanical transcription. It wasn't. Nearly every phase turned up a
bug that had been sitting in the tree, unrelated to R3, waiting for someone to actually trace a citation
chain instead of skimming it:

- `cbr-design-function`'s TECH.md template link pointed at a 36-line stub instead of the real 157-line
  template — meaning the project's own Detail Design gate had been silently missing its §4.3 Business
  Flow → Implementation Mapping section for who knows how long, because nobody had reason to open that
  link and check.
- Three reference files in the implement path — most notably `design-fetch.md`, a working Figma/Pencil
  MCP design-context-fetch procedure — were completely orphaned. Their own headers claimed "Reference for
  implement-feature" and were lying; `implement-feature/SKILL.md` never actually cited them. Dead code
  that looked alive.
- Mode C (browser-live MCP testing) in the test-grading path was unreferenced from anywhere and nearly
  got lost again during *this* migration's own research pass, before being caught and promoted to a
  first-class step in `cbr-verify`.
- The skill count itself was wrong going in — 9 leftover empty directory shells from earlier `git mv`/`rm`
  operations were inflating "24" toward "26" until someone actually counted.

None of this is what R3 was supposed to be about. The honest read is that a monolith of 10 skills with
years — well, months — of incremental edits accumulates rot in exactly the places nobody re-reads: cross-
file citations, template links, "reference for X" headers nobody verifies. A merge forces every one of
those links to be re-walked, and every one of them that was silently broken surfaces at once. Satisfying
in the sense that it's real debt getting paid down; mildly alarming in the sense that a Detail Design gate
was checking against the wrong template and nothing failed loudly about it.

## Technical Details

- `hooks/lib/sdlc_state.py`'s `GATE_SKILL` dict was retrofitted per the plan's spec — but the spec as
  originally written would have produced `/cbr-cbr-plan` (double-prefixed, nonexistent). Caught before
  the retrofit landed; bare tokens (`plan`/`verify`/`implement`) used instead. `test_opener_law.py` was
  the one *expected* red test between phase 3 and phase 4 — it stayed red on purpose until `cbr-plan`
  existed to satisfy it.
- `cbr-verify`'s no-`Write` guarantee is now asserted mechanically, not just described in prose:
  `evals/test_fresh_eyes_mechanism.py` checks the `allowed-tools` frontmatter directly and checks that
  the skill can't self-spawn its own gate agent.
- New permanent regression guard: `evals/test_r3_retired_skill_refs.py` — fails on any surviving
  reference to one of the 10 retired skill names.
- Blast-radius sweep touched ~40 files (evals routing assertions, skill frontmatter NOT-FOR clauses,
  `claude/agents/cbr-{reviewer,tester}.md` identity text, 9 files under `claude/docs/_templates/` that
  ship into every installed user's own `docs/` root). Delegated to a subagent, then independently
  re-verified rather than trusted on report alone.
- Upgrade rehearsal against a pre-R3 payload (extracted from `eacac55`) through the installer's own
  `fullUpdate`: confirmed a real, narrow finding — a hand-edited retired skill file survives an update
  (never clobbered, correct), but its sibling reference/eval files get deleted, leaving it orphaned but
  still discoverable by Claude Code. Documented as a manual post-upgrade step in `CHANGELOG.md` instead
  of rushing a fix into `update.mjs`'s reconciliation logic under release pressure.

## What We Tried

- **Considered** silently trusting Phase 1's prior-session assumptions about which template files were
  safe to retire. **Rejected** — re-verified D4 against the live repo and found 2 of 3 flagged-ambiguous
  cases were backwards (`cbr-design-screen` and `cbr-integration-test`'s candidate templates were
  actually unlinked, opposite of the original guess). Planning-time guesses about file linkage don't
  survive contact with `grep`.
- **Considered** fixing the upgrade-rehearsal orphan-file finding directly in `update.mjs`. **Rejected**
  for this release — narrow scope, real but not urgent, surfaced to the user and deferred with a
  CHANGELOG note rather than expanding an already-large PR under time pressure.
- **Considered** also dropping the `LEGACY_GATE_NAME` shim that 0.11.0's release notes had explicitly
  promised for 0.12.0. **Surfaced to the user** rather than decided unilaterally — it was out of R3's
  actual scope even though the version number matched the promise. Deferred with a CHANGELOG note.

## Root Cause Analysis

The bugs found weren't caused by R3 — they predate it. They're what happens when a codebase of prose
skills grows by accretion: each stage skill was authored and tested in isolation, so a citation that
silently pointed at the wrong file, or a reference that was never actually wired into its own skill's
`SKILL.md` despite its header claiming otherwise, has no automated check to catch it. Nothing runs these
skills' internal link graph the way a compiler resolves imports. A merge is one of the few events that
forces a human (or an agent under a "surgical changes" mandate) to actually walk every citation instead of
skimming past it — and every broken one it finds is one that had been broken the whole time.

## Lessons Learned

- **A merge is a free link-checker.** If you have prose "skills" or docs with cross-file references and no
  automated citation validation, a consolidation pass will surface rot that's been invisible for months.
  Don't be surprised when it does — budget for it.
- **"Reference for X" in a file's own header is not evidence it's wired up.** Verify the citation exists
  in the consuming file before trusting a self-description. `design-fetch.md` had been claiming
  usefulness it wasn't delivering.
- **Delegate the mechanical sweep, but verify the delegate's work independently.** The ~40-file
  blast-radius pass went to a subagent specifically because it was large and mechanical, not because it
  was trusted blindly — the re-verification step is what turns delegation into leverage instead of risk.
- **Deferring a fix is a legitimate outcome, not a failure, when scope creep is the alternative.** The
  upgrade-rehearsal orphan-file issue and the `LEGACY_GATE_NAME` shim both got documented-and-deferred
  rather than shoehorned into a release that was already large. Two judgment calls, both surfaced to the
  user instead of decided silently — that's the right default under an SDLC contract that says "never
  guess."

## Next Steps

- PR #14 (github.com/TheJoseki/ClaudeBrew/pull/14) open against `main`, awaiting review/merge.
  npm publish has not happened — both merge and publish are explicitly the user's call, not automatic.
- Wave 2 remains explicitly deferred (unchanged from yesterday's plan, not a new deferral): Phase 5
  (`cbr-plan` red-team/validate subcommands) and Phase 7 (task-hydration bridge + `--team` multi-agent
  extension for `cbr-implement`). Owner: user, next planning session, whenever ready to `/ak:plan` Wave 2
  as its own stream.
- Manual step for anyone running `claudebrew update` from a pre-0.12.0 install: check for orphaned
  hand-edited files under the 10 retired skill directories after update — they survive but their
  reference/eval siblings don't. Documented in `CHANGELOG.md`; a code fix to `update.mjs`'s reconciliation
  logic is not scheduled.
- `LEGACY_GATE_NAME` shim removal (promised by 0.11.0's release notes for 0.12.0, out of R3's actual
  scope) is still outstanding — needs its own small follow-up, owner TBD.

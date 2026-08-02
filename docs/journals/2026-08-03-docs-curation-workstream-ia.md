# Docs Curation + Work-Stream IA: The Coverage Was 61% Because We Weren't Looking, Not Because It Was Untested

**Date**: 2026-08-03 00:30
**Severity**: Medium
**Component**: `plugins/cbr/docs/_templates/*`, `plugins/cbr/rules/sdlc-conventions.md`, `plugins/cbr/hooks/*`, `evals/*`
**Status**: Resolved — shipped as **v0.4.0**, PR #4 (7 commits), branch `feat/cbr-docs-workstream-ia` off merged `main` (`41a2f41`)

## What Happened

Cooked a combined plan (`/ak:cook --tdd`): curate the doc-template set (16 → 8) **and** establish the work-stream information architecture (Phase 1, additive), which share one authority file so they had to land together. Then ran a coverage eval loop to **96%** (goal: 95%). Five phases: baseline+authority → template curation (4 parallel rewrite agents) → `STREAM.md` keystone → skill/hook wiring (TDD) → validate+ship. `claude plugin validate` clean, 7/7 test suites green.

## The Brutal Truth

The hook coverage read **61%** and the honest reaction was "we have a testing hole." Wrong. Six modules showed **0%** not because they were untested but because their test suites invoke them as **subprocesses** (`subprocess.run([sys.executable, script])`), which in-process `coverage` can't instrument. The code was executing and passing — just not being *measured*. Enabling subprocess coverage (`.coveragerc` + a `sitecustomize` that calls `coverage.process_startup()`, inherited by the un-`env=`'d subprocesses) revealed the guards at their real 79–91% and jumped the total to 85% with zero new tests. Only **one** module (`compact-context-saver.py`, 63 stmts) was genuinely untested — that single real gap capped the achievable total at ~89% and was the actual work. Confusing "measurement artifact" with "test gap" would have sent us writing redundant tests for already-covered code.

## Technical Details

- **Template ship-gap closed.** The 16 templates were **untracked in every branch** yet referenced by `sdlc-conventions.md`/`coding-standards.md` — the plugin promised templates it never committed. Baseline-committed as-is first (untracked `rm` is irreversible; baseline makes deletions a reviewable, recoverable diff), then curated. Now git-tracked.
- **4 parallel rewrite agents, file-disjoint**, each with a shared mandatory-style spec (one placeholder syntax `[FIELD — e.g. value]`, single-layer headers, stack-neutral): `TEST_VIEWPOINT` 656→73 (fill-in skeleton with the G3c Section 0 + coverage field its consumers read), `CODING_CONVENTION` 1136→119 (+ per-stack snippets), `CODING_RULES` 391→270 (all rule IDs kept), `ARCHITECTURE`/`API_DESIGN` DRY'd.
- **`STREAM.md` keystone** — two *authored* zones (membership + task board = markdown-is-the-kanban) and one *derived* gate-status zone. **Gate authority stays with the glob** (`sdlc_state.py`); the manifest is never a second source of truth (the drift trap the ClaudeKit study flagged). `sdlc-conventions.md` gained an Artifact-Lifecycle governance table + a MANDATORY upkeep protocol placed in the **always-loaded rule** instead of editing 10 skills (DRY improvement over the plan).
- **TDD RED→GREEN** for the one bit of new logic: `sdlc_state.find_stream_manifest()` + a `session-init` "Stream board:" line — additive (existing 44 tests untouched, existing globs unchanged), +3 cases, then +10 for `compact-context-saver`. Final: 7 suites, hook coverage 96% (566 stmts, 25 miss — remainder are defensive `except` branches).

## What We Tried

Delegated the heavy template rewrites to parallel agents and the authority-change review to a `code-reviewer`. The reviewer returned **ISSUES**: 4 internal-consistency defects in the Artifact-Lifecycle table I had just authored — two `Updated by: —` cells that contradicted the file's own gate definitions (G5b is a re-scan; G4 review is an R5-rounds phase), a derived zone with no named producer, and an absolute "nothing created-but-unused" claim the table's own omissions falsified. All real, all fixed before commit.

## Root Cause Analysis

Two independent instances of "the artifact and reality disagree, quietly." The coverage number disagreed with reality because the measurement tool couldn't see subprocesses. The lifecycle table disagreed with the file's own gate rules because a hand-authored governance table has no compiler to cross-check it against the tables above it. Neither surfaced from careful reading — one needed the right coverage config, the other needed an adversarial reviewer.

## Lessons Learned

Before treating a low coverage number as a test gap, confirm the tests are being *measured*, not just *run* — subprocess-invoked code needs subprocess coverage or it reads as 0% while passing. A governance table you author yourself is exactly as trustworthy as one a stranger wrote: get it reviewed against the tables it must agree with. And additive-first (Phase 1: manifest + `stream:` field, no path relocation, no `sdlc_state.py` glob change) let a large IA change land with the 44 existing tests untouched — the cheap half of the work delivered the visibility without paying for the risky move.

## Next Steps

PR #4 open (v0.4.0). Deferred by design: **Phase 2** — physically relocate per-feature artifacts into `docs/streams/<id>/`, which *does* rewrite `sdlc_state.py`'s path layer + its tests + ~15 skills' path refs. Remaining coverage headroom (guards at 79–91%) is defensive `except`/`__main__` branches — low value to chase. Owner: whoever picks up Phase 2 after the manifest format proves out on a real feature.

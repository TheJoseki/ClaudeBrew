# Canonical Stream Layout v0.5.0: The Phase 2 We Said Was Deferred, Shipped Same Week

**Date**: 2026-08-03 16:49
**Severity**: High
**Component**: `plugins/cbr/rules/sdlc-conventions.md`, `hooks/lib/sdlc_state.py`, 17 skills + 2 agents, `evals/test_canonical_paths.py`
**Status**: v0.5.0 committed — PR #6 **open, awaiting merge** (6 commits `20b34cb`→`94df679`), branch `feat/canonical-stream-layout`

## What Happened

Yesterday's journal (v0.4.0) explicitly deferred "Phase 2 — physical relocation of artifacts into `docs/streams/<id>/`" to whoever picked it up later, citing YAGNI and migration cost. That someone was today, a few hours later. `docs/streams/<slug>-<YYYYMMDD>/` is now the **single canonical home** for every per-feature SDLC artifact — the type-first `docs/{specs,reviews,plans,work-logs,security,test-reports,test-cases,bug-reports,retros,handoffs}/` scheme is fully retired, not deprecated-alongside. Identity moved from filename into folder: sub-folder = type, filename drops the slug (`docs/specs/detail-design/TECH-payment.md` → `docs/streams/payment-20260801/design/TECH.md`); time-series artifacts keep date/round (`REVIEW-<date>.md`, `UTR-R<n>.md`). `hooks/lib/sdlc_state.py` was rewritten folder-based — active feature and G1–G8 gate progress are now *derived* from the stream folder, not from a filename pattern or a `status:` flag.

## The Brutal Truth

We wrote "deferred to a future Phase 2" into a committed journal entry and it didn't survive to see `git log`. The user rejected the deferral outright: *"Không cần solution rẻ, cần solution tối ưu cho long-term... làm chuẩn từ đầu"* (no cheap solution, need the optimal long-term one, do it right from the start). That's a legitimate call — cbr has zero production consumers, so "defer the expensive migration" was optimizing for a migration cost that doesn't exist yet. But it means the YAGNI reflex from the previous session was wrong for this specific codebase, and worse, it was wrong in a way that got written down as if it were settled. Lesson already banked as memory (`cbr-optimal-over-yagni`), but living it out meant redoing work we'd just finished shipping.

## Technical Details

- TDD RED→GREEN across 5 phases, each gated by a standing test: P1 authored `test_canonical_paths.py` RED-first against the new authority table — it correctly flagged **249 type-first path references**. P2 rewrote `sdlc_state.py`'s identity model folder-based (98/100/100% coverage) and, in doing so, fixed a real bug: slug resolution was prefix-matching (`payment-*` matched `payment-export-*`). P3 migrated ~52 files across 17 skills + 2 agents until the gate hit **249 → 0**. P4 re-pathed `compact-context-saver.py`, widened `enforce-worktree`'s exempt list (`docs/specs/*` → `docs/streams/*`, now covering non-md stream assets), and re-pathed the `STREAM.md` template to stream-relative sub-paths. P5 validated and shipped.
- Final state: 10/10 test suites green, `claude plugin validate` clean for both plugin and marketplace.

## What We Tried (and one thing we almost missed)

Ran an advisor consult mid-plan on whether the canonical-paths gate was actually complete. It caught that the gate only scanned `skills/` + `agents/`, with `rules/` checked by hand — and the by-hand check had missed **5 stale type-first paths in always-loaded rule files** (`dar-evaluation-protocol.md`, `project-planning-estimation.md`, `risk-issue-management.md`). That's the exact failure mode this framework exists to eliminate: a human "I checked it" standing in for a deterministic gate. Fixed the 5 paths, then widened the gate's scan roots to `skills + agents + rules + docs` in commit `94df679` so it can't recur silently.

## Root Cause Analysis

Two decisions compounded. First, **the deferral itself was premature** — "minimize migration cost" doesn't apply when there's no one to migrate; the right lens for a pre-1.0 framework rebuild is "build it correct," and the user corrected that lens explicitly rather than letting it stand. Second, going with **Option A (no in-place migrator)** followed directly from that same premise: no legacy consumers, no legacy artifacts to relocate, so ship the breaking change bare and document it in the CHANGELOG. That decision then propagated backward — it retroactively orphaned `slug_from_filename`, a helper an earlier phase (v0.4.0's Phase 1) had kept alive *solely* in anticipation of a migrator that was never built. Removed it, its 4 regexes, and its test in the final commit. Decisions don't just constrain what comes next; they can kill code that already shipped.

## Lessons Learned

Enforcement gates beat by-hand checks, full stop — the `rules/` blind spot is not a hypothetical, it happened here, on the same day the framework's whole thesis is "make the mandate a hook, not a markdown promise." Decisions propagate backward: before removing a "kept for later" helper, check what decision it was kept *for* — if that decision changed, the helper is dead code now, not later. And "verified" beats "assumed" even under time pressure: the advisor's three-way path-agreement concern (`sdlc_state` maps ↔ each gate skill's write path + `verdict-gate.py` arg ↔ `STREAM.md` template) was actually checked and came back clean — it would have been easy to wave through given the phase was already 4/5 done.

## Next Steps

PR #6 is open and awaiting merge (v0.5.0); the branch is 6 commits ahead of `origin/main`. No migrator exists by design (Option A) — if a real consumer ever accumulates type-first artifacts before adopting this version, a migrator is a new, scoped piece of work, not a resurrection of `slug_from_filename`. The three-way path agreement between `sdlc_state.py`, the gate skills' verdict paths, and the `STREAM.md` template has no automated cross-check yet — worth a follow-up gate if the layout changes again. Owner: next session touching artifact paths.

## AgentWiki

AgentWiki publishing skipped (CLI/MCP unavailable) — local journal entry is the source of truth.

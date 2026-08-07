# cbr-explore Ships — and Two Adversarial Passes Each Caught a Different Hole in the Same Rule

**Date**: 2026-08-07 15:06
**Severity**: Medium
**Component**: `claude/skills/cbr-explore/` (new) + stream-opener law across `cbr-brainstorming`, `cbr-plan-writing`, `cbr-researcher`
**Status**: Shipped to PR #11 (open, awaiting review), v0.9.0, commit `a02d21e`

## What Happened

`cbr-explore` fills a socket that's been sitting empty since the single-layer refactor: `cbr-researcher` already wrote `research/RES-[topic].md` and `plan-writing`'s input-contract already read it at priority 3, but nothing actually opened a stream and produced one — plan-writing's own refuse-script pointed users at "run the researcher agent... until the explore skill ships." Now it ships: scout code and/or user-pointed prior art into a re-runnable `research/RES-<topic>-R[n].md`, open-or-join a stream, stop. Landed alongside a cross-cutting rule change: all three stream openers (brainstorming, explore, plan-writing) now resolve "open vs. join" the same way, by topic-slug — and `brainstorming`, which used to open a stream unconditionally, gained its first JOIN branch.

## The Brutal Truth

The plan's own `/ak:plan validate` pass said this was ready to cook. It wasn't. Validate confirmed `resolve_active_feature()` *existed* and stopped there — it never read what the function actually did. Red-team did, and found the whole join mechanism was built on the wrong primitive. That's a full extra review cycle (12 accepted findings, 4 Critical) that a "the function exists" check should never have let through in the first place.

## Technical Details

`resolve_active_feature()` (`sdlc_state.py:94-116`) is topic-blind — it counts in-flight streams repo-wide, not by subject — and research/stream-light streams never reach G1/G3 so they never archive. Auto-join on that primitive would, after the second exploration ever run, silently file a new scout under an unrelated stream. It also has no CLI entrypoint, so a prose skill literally cannot call it. Fix: dropped the function entirely for this purpose, replaced with a plain prose topic-slug lookup — exact match → join, no match → open, >1 match → ask.

Second hole, found later by `review-code` on the actual code, not the plan: the decided security posture was "no autonomous web search," but explore doesn't fetch anything itself — it delegates to `cbr-researcher`, which holds `WebSearch`. The constraint was written into the `--parallel` spawn brief and forgotten in the sequential one, so the invariant lived in explore's own context but never reached the agent that actually does the fetching. One Major finding (M1), fixed before ship.

## What We Tried

`/ak:plan validate` (existence-level check) → passed, wrongly. `/ak:plan red-team` (3 adversarial reviewers: Assumption Destroyer, Failure Mode Analyst, Security Adversary) → caught the join mechanism (F1/F2/F3, all Accept) and the Meta-Rule-of-Two exposure (F7, Accept). `review-code` on the implemented skill → caught the sequential-spawn gap the plan-level review didn't, because the plan-level review can't see where a constraint is or isn't threaded through actual spawn code.

## Root Cause Analysis

Validate checks "does the referenced thing exist," not "does it do what the plan assumes." Those are different questions and only the second one is load-bearing. Separately: a security invariant declared once at the skill level doesn't automatically propagate to every code path that needs it — it has to be bound at each spawn site individually, and nothing forces that except a reader who checks both paths.

## Lessons Learned

A passing existence check on a cited function/mechanism is not a passing contract check — read the body, not just the signature, before a plan leans on it. And a rule is only enforced where the acting agent can actually read it: if a constraint lives in the parent skill's prose but the work happens in a spawned subagent, it has to be re-stated in *every* spawn brief that subagent can be launched from, not just the one someone happened to write first.

## Next Steps

None outstanding — all 12 accepted red-team findings landed, the one code-review Major is fixed, 5 Python gates + 38 Node tests are green. Watch the next skill that reuses the "spawn a capability agent with a security constraint" pattern (any future `--parallel` skill) and check both the parallel and sequential spawn briefs get the constraint, not just one.

## AgentWiki

AgentWiki publish skipped — `agentwiki` CLI not found on PATH (`command not found`, exit 127) and no AgentWiki MCP tool exposed in this session. This file is the source of truth.

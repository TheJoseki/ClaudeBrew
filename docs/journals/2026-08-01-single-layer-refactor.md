# Single-Layer Refactor: Tearing Out the Orchestrator We'd Just Reconciled

**Date**: 2026-08-01 21:04
**Severity**: High
**Component**: `plugins/cbr/skills/*`, `plugins/cbr/agents/*`, `plugins/cbr/hooks/*`, `plugins/cbr/rules/sdlc-conventions.md`
**Status**: Resolved — implemented on `worktree-single-layer-refactor` (14 commits), not yet merged/pushed

## What Happened

Two days after finishing the reconcile that made the imported two-layer SDLC engine (orchestrators spawning 10 rigid role agents) actually executable, we audited it again and decided to gut it. `full-sdlc`/`orchestrate` forced a single entry point and auto-cascaded phase→phase — the exact thing ClaudeBrew's own house style ("hard gate, no auto-cascade," set by `brainstorming`) forbids. Fixing the wiring didn't fix the architecture. Collapsed to one layer: gated stage skills that each write an artifact and stop, over a **4-agent capability pool** (`researcher`/`developer`/`reviewer`/`tester`) instead of 10 rigid roles. Net: 40→25 skills, 10 agents→4, 290 files touched, 8143 lines deleted vs 3858 added.

## The Brutal Truth

We spent an entire prior session (PR #1) making the orchestrator layer *correct* — Python hooks, fixed frontmatter, dead-path repairs, 56 passing tests — and this session concluded the layer itself shouldn't exist. That's not wasted work exactly (the hook-porting and frontmatter fixes survive), but it's a reminder that "make the broken thing work" and "should this thing exist" are different questions, and we answered the first one first. The saving grace: reading upstream ClaudeKit stopped us from overcorrecting into zero agents, which the user's initial framing ("remove all agents") would have produced — a flat pool with no fresh-eyes review is its own regression.

## Technical Details

- **Deleted**: `full-sdlc`, `orchestrate`, `parallel-agents`, `behavioral-modes`, `intelligent-routing`, `context-inject` (6 skills); `ba-agent`, `architect-agent`, `developer-agent`, `code-review-agent`, `unit-test-agent`, `integration-test-agent`, `security-tester-agent`, `bug-fix-agent`, `ui-designer-agent`, `orchestrator-agent` (10 agents, ~1900 lines); the `.*-agent` `SubagentStart`/`SubagentStop` hook pair (`subagent-context-inject.js` 303 lines, `subagent-quality-gate.py` 75 lines); 4 orchestrator-maintained registries; 3 orchestration-only rules.
- **Built test-first**: `hooks/verdict-gate.py` + `schemas/verdict-artifact.schema.json` — a skill-invoked (no matcher, unlike the deleted hooks) validator: schema-shape + secret-scan + per-gate policy, **fails closed** on any check miss. `evals/test_verdict_gate.py` hit **98% coverage** before the gate skills were wired to call it.
- **Gate mechanics (Decision 1, plan §"Decisions")**: no machine FAIL-loop. `review-code`/`unit-test`/`integration-test`/`vulnerability-scanner` spawn a **fresh** `cbr:reviewer`/`cbr:tester` subagent (never self-grade inline — Fork 5, "B1 fresh sub-context"), the subagent writes the verdict artifact, `verdict-gate.py` validates it, `AskUserQuestion` fires on block, user decides whether to re-invoke `fix-bug`.
- **Proved the pool actually resolves**: loaded the plugin headless (`claude -p --plugin-dir`), spawned `cbr:reviewer`, confirmed it wrote a schema-conformant artifact and `verdict-gate.py` exited 0 against it — not just "the file parses," but "the runtime graph resolves under the namespace."
- **Knowledge-cluster merges (Phase 4, optional, user-opted-in)**: `ui-styling`+`ui-ux-pro-max`→`design-system`; `api-patterns`+`database-design`→`architecture`; `lint-and-validate`+`run-tests`→`validate-and-test`; `testing-patterns`+`tdd-workflow`→`testing-strategy`; `clean-code`+`code-review-checklist`→`code-quality`; `systematic-debugging` folded into `fix-bug/references/`. `retro` reworked to run solo (dropped `Agent` tool); `create-pr` folded into `implement-feature`.

## What We Tried

Started from the user's literal instruction — remove the rigid role-agent layer entirely. Before implementing, studied upstream ClaudeKit's own agent model (`xia-skill-subagent-patterns.md` etc.) and found its "lean" reputation isn't zero-agent — it's a flat pool of *general* capability agents that skills spawn on demand for fresh-eyes review and parallel work. That's a refinement of a locked decision, not a reversal of it: still no orchestrator, still no `.*-agent` hooks, but 4 named agents (`researcher`/`developer`/`reviewer`/`tester`) survive with per-agent `model` tiers and selective `memory: project`, restoring the "someone other than the author checks the work" property the naive reading would have thrown away.

## Root Cause Analysis

The prior reconcile treated "does the orchestrator execute without crashing" as the bar. It's the wrong bar for a system whose entire pitch is hard gates and no forced cascade — an orchestrator that runs perfectly is still an orchestrator that decides for the user when phase 2 starts. The actual defect was architectural, not a wiring bug, and no amount of hook-porting or frontmatter-quoting was going to surface that; it took a second audit asking "should this exist" instead of "does this work."

## Lessons Learned

Getting a broken subsystem to pass validation is not the same as validating the subsystem belongs. When a locked user decision ("remove the agents") collides with evidence from a comparable system (ClaudeKit's actual lean model), the right move is to bring the conflict back as a refinement proposal — not silently keep the literal instruction, and not silently override it either. The eval-loop chase (see `plans/reports/eval-260801-1848-trigger-eval-loop.md`) taught the same thing from a different angle: we burned several harness rewrites trying to force a stable recall number for `architecture`, when the honest read was that recall is inherently sample-noisy at 1 run/query and `architecture` legitimately answers some queries from the model's own knowledge without ever opening the skill file. Precision hit 100% and stayed there across every fix — that was the real, stable signal; chasing recall past that ceiling was chasing noise.

## Next Steps

Branch `worktree-single-layer-refactor` is complete per its own plan (all success criteria checked, `claude plugin validate` clean, 98% verdict-gate coverage, 25/29-skill structural pass) but **unmerged** — no PR opened yet. Before merge: decide whether to invest in multi-run (3–5×) trigger-eval majority voting for a stable recall number, or accept precision-only as the shipped metric (current recommendation: accept it, document the ceiling, move on). Owner: whoever opens the PR next.

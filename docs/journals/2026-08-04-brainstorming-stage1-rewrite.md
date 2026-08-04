# Brainstorming, Rewired: Fluid Process, Rigid Contract — and the Gap "All Gates Green" Hides

**Date**: 2026-08-04 17:47
**Severity**: High
**Component**: `plugins/cbr/skills/brainstorming/*` (SKILL.md + 6 references), `plugins/cbr/agents/strategist.md`, `CLAUDE.md`/`README.md`, `plugins/cbr/.claude-plugin/plugin.json`
**Status**: v0.6.0 — **PR #7 MERGED** to `main`, branch `feat/brainstorming-rewrite` (commit `79d80b5`)

## What Happened

The user's read on Stage 1 was blunt: brainstorming "đang bị fix cứng và ko thể hiện đc cái brainstorming như 1 con người sẽ làm" — it runs a script, it doesn't think. We rebuilt the front door. The rigid 9-phase machine became **7 invariants + an adaptive toolbox of moves** the model selects by judgment: the missing **divergent** motion (generate widely, judge later), **problem-first inversion** (invert a proposed solution to its unstated problem), and **adaptive depth** (a sub-threshold question gets a recommendation with *no stream opened* — a person does not "brainstorm" a variable name). New `strategist` capability agent (pool 4→5; `sonnet`, non-gate) supplies divergence panels + adversarial critique. Shipped as v0.6.0.

## The Brutal Truth

I said "100% complete, all gates green" and it was misleading in two directions at once. First, three structural gates (`test_canonical_paths`, `test_release_docs`, `claude plugin validate`) passed — and an advisor consult *immediately* found **four** consistency defects none of them can see: a stale reference list in `CLAUDE.md` still naming the old four references, a description bloated to 1319 chars over the 1024 limit I had myself cited, a cross-skill `Status: approved` form mismatch, and a user-consent-before-spawning clause that fell out of the spine. "All gates green" had quietly stood in for "done." Second, the whole *point* of the change — does it brainstorm like a person? — was **completely unverified** at that moment; structural gates say nothing about behaviour. I was one keystroke from shipping the thesis untested.

## Technical Details

- **Frame that carried the whole rewrite: fluid process, rigid output-contract.** Everything *upstream* of the artifact write became improvisational; the write itself (`docs/streams/<slug>-<YYYYMMDD>/` + `stream:` frontmatter + `STREAM.md`) was frozen. That is why a near-total rewrite of the skill left `test_canonical_paths.py` green — the machine-read surface never moved.
- **Subagents add thinking, not contract surface.** `strategist` returns findings **inline as its final message** — no `Write` tool, no `sdlc-conventions` Artifact-Paths row, no lifecycle entry. Divergence panels produce many option-sets that all converge into the *one* `BRAINSTORM.md` the lead writes.
- **An invariant collided with the fix mid-cook.** Invariant 7 ("convergence always writes the artifact") contradicted adaptive-depth for a trivial naming question — forcing a stream artifact there is exactly the ceremony we were removing. Caught while drafting the eval, scoped invariant 7 to "a converged brainstorm on a feature/direction," carved out the sub-threshold case.

## What We Tried (and one thing we almost missed)

The advisor's four findings were all real and all fixed with evidence (`grep` for each, `python -c` to count the description and parse both frontmatter blocks). The one that stings: **I had moved `Status: approved` out of the bullets into lowercase YAML frontmatter — an embellishment nobody asked for.** Only `stream:` was required; moving `status` was scope creep, and it silently broke the `worktree` skill's Phase 1, which greps the prose form. The fix was to *revert my own gold-plating* and add only the required field. Then the dry-run: 3/3 differentiating scenarios passed — trivial→no-ceremony/no-stream, solution-jumping→problem-first (it refused to build notifications on zero evidence), pivot→detected + confirmed type + re-enumerated.

## Root Cause Analysis

Structural gates verify *structure*, not *consistency-with-the-rest-of-the-repo*. A large rewrite radiates silent drift into files **outside the edit scope** — a doc's reference list, a sibling skill's expectation of a field's form, a release blurb's agent count — and no gate that checks "does this file parse / is this path canonical" will ever catch it. The release-docs gate is deliberately *touch-forcing*, not semantic; it makes shipping stale docs a hard failure only for the anchor, by design. The behavioural gap has the same shape: the tests confirm the skill is well-formed, never that it behaves. Both blind spots share one cause — a gate answers the question it was built to answer, and "did the whole system stay coherent / does it actually work" was not that question.

## Lessons Learned

Adversarially read the whole repo after the gates go green, not just the diff — the advisor caught in one pass what three gates structurally cannot. Run the behavioural dry-run before claiming a behavioural win; "gates green" is necessary, never sufficient, and the differentiating scenarios (the ones the *old* skill would fail) are the only evidence that counts. And keep changes surgical: the `Status:` move was gold-plating that manufactured a cross-skill defect out of nothing — the required change was one line (`stream:`), and every keystroke beyond it was pure downside.

## Next Steps

PR #7 is **merged** (v0.6.0 on `main`). The `feat/brainstorming-rewrite` worktree can be removed (`git worktree remove`). Behavioural confidence rests on three dry-run data points, not a formal eval-suite run — the on-Windows trigger-eval (`evals/triggers/run_triggers.py`) measuring the new trimmed description's auto-fire reliability must be **user-initiated** (PowerShell classifier caveat) and has not been run. The three-way agreement between the skill's move descriptions, `teammate-mode.md`, and the `strategist` agent's two roles has no automated cross-check — worth watching if the agent's contract changes. Owner: next session touching Stage 1.

## AgentWiki

AgentWiki publishing skipped (CLI/MCP unavailable) — local journal entry is the source of truth.

# Phase 3 — Ripple Fixes, Docs, Validate

**Depends on:** Phase 1 + Phase 2 · **Goal:** make the tree internally consistent and green.

## Context
- Baseline blast radius (pre-refactor): 206 skill-name refs / 63 files (mostly `NOT FOR:` guards, connection tables, evals). Re-run the grep after P1/P2 to get the live list.

## 0. Artifact-gate — table entry only (built in P1)
The verdict schema + `verdict-gate.py` validator + its test are **built in Phase 1** (they have no dependency on the merges, and P2's gate skills call them). Here, only: add `verdict-artifact` to the `sdlc-conventions.md` Artifact Paths table (§1 below) and confirm the P2 gate skills' Bash-invocation lines resolve.

## 1. Re-point central tables (`rules/sdlc-conventions.md`)
- **Quality Gates table** "Decided By" column: replace agent names with skill names (`ba-agent`→`analyze-requirement`, `code-review-agent`→`review-code`, `security-tester-agent`→`vulnerability-scanner`, `unit-test-agent`→`unit-test`, `integration-test-agent`→`integration-test`, `architect-agent (DESIGN_REVIEW)`→`review-code`/`architecture`). User-approval gates unchanged.
- **Artifact Paths table** "Agent" column → owning **skill**; delete rows for `orchestrator-agent`, council/mailbox, agent-memory, agent progressive-disclosure.

## 2. Fix cross-references in surviving skills
Re-run: grep `plugins/cbr` for removed names `full-sdlc|orchestrate|parallel-agents|behavioral-modes|intelligent-routing|context-inject|create-pr|api-patterns|database-design|ui-styling|ui-ux-pro-max|<removed agents>`.
- Remove/repoint every `NOT FOR:` clause, `Skill Connections` "Called from full-sdlc/orchestrate" rows, and routing tables.
- Known hotspots from baseline grep: `analyze-requirement` (connection rows), `design-screen`/`design-function` (NOT FOR + design-intelligence refs), `fix-bug` refs, `browser-devtools`, `performance-profiling`, `implement-feature`, `review-code`.
- **Orchestrator-artifact dependents:** `estimate` and `handoff` reference PLAN files / registries (`PLAN-REGISTRY.md`, `DECISION-LEDGER.md`, `BACKLOG-REGISTRY.md`) that only the deleted orchestrators created. Rework these skills to **create their own artifact if absent** (self-sufficient) rather than assume an orchestrator seeded it.

## 3. Consolidate evals
- Each merged skill (`design-system`, `architecture`) ships ONE `evals/evals.json` (2 positive + 1 boundary), merging the absorbed skills' cases. Delete evals of removed skills.

## 4. Rewrite CLAUDE.md
- Section **"The SDLC engine"**: rewrite two-layer (orchestrator→agent) → **single-layer gated skills**. Remove agent/hook paragraphs describing `.*-agent` matcher, SubagentStart/Stop, orchestrator skills.
- Section **"Reconciliation status"** / **"Conventions inherited"**: update counts, drop agent references, note the pivot.
- Keep **Worktree isolation** + **brainstorming reference-core** sections (unchanged).
- Update the ASCII tree (`agents/`, orchestrator skills gone).

## 5. Version + changelog
- Bump `plugins/cbr/.claude-plugin/plugin.json` version (`0.2.0` → `0.3.0`, minor-breaking to layout).
- `CHANGELOG.md`: describe the single-layer pivot (removed orchestrators+agents, merged clusters).
- `docs/BACKLOG-REGISTRY.md` (2 refs): CLAUDE.md currently claims "no reconciliation gaps remain." This pivot **reopens** that — explicitly record the single-layer refactor as the new state (don't leave the stale "done" claim standing).

## Validation (the gate)
- `claude plugin validate ./plugins/cbr` → **0 errors**.
- `claude plugin validate .` (marketplace) → pass.
- Grep removed names across `plugins/cbr/` → 0 dangling functional refs (history/CHANGELOG allowed).
- `python evals/test_hook.py` → green.
- Optional: `python evals/triggers/run_triggers.py` on a couple merged skills (user-initiated per Windows caveat) to confirm triggering survived.

## Risks
- Missing a `NOT FOR:` repoint silently degrades triggering — the grep-clean criterion is the backstop; do it last and twice.

# xia Synthesis + Challenge — ClaudeKit patterns → ClaudeBrew plan

**Date:** 2026-07-31 · Consolidates: `xia-skill-subagent-patterns.md`, `xia-hooks-rules-patterns.md`, `xia-memory-artifact-patterns.md`.
**Mode:** learning/adapt (not a code port). Deliverable = plan updates + decision forks.

## What transplants cleanly (folded into plan — no conflict with locked decisions)

| Lesson | Evidence (ClaudeKit) | Plan phase |
|--------|----------------------|-----------|
| **Drop the 4 registries** (PLAN-REGISTRY/DECISION-LEDGER/BACKLOG-REGISTRY/PROJECT-MEMORY) | Whole-repo grep = 0 hits; `plan.md`+`phase-*.md` checkbox state IS project memory | P1 |
| **Session-resume = read the plan file**, not a registry lookup | `ck-plan` "read plan → first non-completed phase → continue" | P1 |
| **Artifact-by-path handoff** — stage skill closes with "written to `<path>`; next skill reads it, don't paste content" | `Task(prompt="...reports: [paths]")`, pointer file holds metadata only | P1 (this is the direct replacement for what orchestrators did) |
| **Explicit report size caps** in `sdlc-conventions.md` next to artifact table | researcher ≤150 lines, `plan.md` <80, MEMORY.md <200, injected ctx ~200 tok | P2/P3 |
| **Thin-hook + `lib/` + config-gate + fail-open** for any new hook | every `.cjs` = `try{}`→`isHookEnabled`→stdin→`lib/`→exit; `__tests__` mirror each lib | P1 |
| **Keep matchers general (tool/none), never `.*-agent`** | zero `.*-agent` matchers exist in ClaudeKit | P1 (validates deletion) |
| **Skill-anatomy conventions**: `<HARD-GATE-*>` tagged blocks (with "User override:" escape), Anti-Rationalization table, mermaid-as-authoritative-flow, **Required-Subagents/Activation table** (Phase\|role\|MUST/Optional), **Workflow-Position footer** | consistent across cook/fix/ck-plan | P2/P3 |
| **Don't over-trim rules** — ~12 right, not 6 | ClaudeKit's 6 rules carry no SDLC gate/artifact domain; ClaudeBrew's G1–G8 legitimately needs more surface | P1/P3 |
| **`cook-after-plan-reminder` nudge pattern** — a stop-event hook that prints the next-skill invocation string, never auto-invokes | `SubagentStop` matcher=`Plan` prints `/ck:cook <path>` | P2 (respects no-cascade) |
| **Audit line counts directly** — don't trust claimed caps | `ck-plan/SKILL.md` ≈541 lines, over its own "<300" rule | P3 |

## Challenge — where ClaudeKit does NOT transplant cleanly (needs user decision)

### Fork A — Capability-agent pool (REOPENS Decision Q2)
- **Finding:** ClaudeKit's single-layer model = flat pool of **13 general capability agents** (reviewer, tester, researcher, fullstack-developer, debugger…), spawned on-demand by skills, no orchestrator. NOT the rigid SDLC role agents ClaudeBrew is deleting.
- **What Q2's "zero agents" loses:** (1) fresh-eyes adversarial review — the implementer grading its own work is exactly what cook forbids; (2) per-role model tiering (opus planning / haiku mechanical) — `general-purpose` Task spawns inherit session model; (3) `memory: project` cross-session pattern learning — no host without agent files.
- **Reconcile:** "kill the rigid pipeline" (Q2 intent) and "keep a small capability pool" are compatible — a pool of general reviewers/testers is not an orchestrated role cascade and needs no `.*-agent` hooks.
- **Options:** (A1) keep a small pool of ~3-5 general capability agents that skills spawn on demand; (A2) ship zero agent files, bake personas into `Task(subagent_type="general-purpose", prompt=...)` templates (+ a `references/subagent-prompts.md` catalogue).

### Fork B — Fresh-eyes for the G4/G5a/G6/G7 verdict passes
- **Finding:** cook makes delegation of review/test a hard invariant ("0 Task calls = INCOMPLETE") specifically so the implementer never self-grades. Decision 1 (verdict + user gate) doesn't say WHERE the verdict is produced.
- **Options:** (B1) the review/test/security gate spawns a **fresh sub-context** (reviewer persona) so the verdict is not self-graded; (B2) allow inline self-grading in the invoking context (cheaper, but contaminated — the model just wrote/ran the thing it's judging).
- Note: B largely follows A — with a pool (A1) the fresh context is the `code-reviewer`/`tester` agent; with zero agents (A2) it's a fresh `general-purpose` spawn carrying the posture text.

### Fork C — Machine-checkable artifact-gate (hardening beyond Decision 1)
- **Finding:** ClaudeKit's `workflow-artifact-gate.cjs` = skill writes JSON artifacts → skill runs validator via `Bash` (schema + secret-scan + policy: hard stages require `review-decision===PASS` + passing verification + no unverified adversarial claims) → `AskUserQuestion` on block. Ships **disabled/manual**, no auto-hook, no agent matcher. This is Decision 1 "done deterministically."
- **Options:** (C1) build it now (one shared artifact schema + one validator script, skill-invoked); (C2) document as a future/backlog option (P4); (C3) never — stay skill-verdict-only permanently.

## Two smaller open questions (from reports, non-blocking)
- Report size cap uniform across stages, or per artifact type (SRS vs bug-report vs security-scan)? (default: one ceiling, override per type only if needed)
- Session-lifecycle resume (survive a `claude` restart via global session-state file) — out of scope for this refactor unless the user wants it.

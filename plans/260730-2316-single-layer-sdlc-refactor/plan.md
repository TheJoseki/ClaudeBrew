# Plan — Collapse ClaudeBrew to a Single-Layer Gated Skill Toolkit

**Slug:** single-layer-sdlc-refactor · **Created:** 2026-07-30 · **Branch target:** feature worktree (per `worktree` skill)
**Status:** ✅ COMPLETE (P1–P4) — executed & verified 2026-07-31 on branch `worktree-single-layer-refactor`; all success criteria met (plugin+marketplace validate pass, all evals pass, verdict-gate 98% coverage). Phase 4 knowledge merges also done (40→25 skills); the 3 new skills created via skill-creator `init_skill.py` + reviewed via `quick_validate`.
**Source audit:** `plans/reports/audit-260730-2316-skills-redundancy-merge.md`

---

## Goal

Remove the imported two-layer orchestrator→role-agent SDLC engine and keep **one layer of self-sufficient, gated stage skills** over a **flat pool of ~4–5 general capability agents** (reviewer/tester/researcher/developer) that skills spawn on demand — for fresh-eyes gate verdicts and `--parallel` work, never as an orchestrated pipeline. Each stage writes its artifact, applies its gate, and **stops** (house style: hard gate, no auto-cascade). No forced orchestrator entry point.

## Why (user decisions, 2026-07-30)

1. Orchestrators force entry + over-cascade → artifacts skipped if not invoked → **remove `full-sdlc` + `orchestrate`**.
2. **Merge UI cluster → `design-system`** (absorb `ui-styling` + `ui-ux-pro-max`).
3. **Remove `create-pr`**.
4. **Remove `parallel-agents`** → parallel becomes an argument mode in execution skills.
5. Fork Q1 → **Merge tech-design cluster** (`architecture`+`api-patterns`+`database-design`) into 1.
6. Fork Q2 → **Remove the rigid role-agent layer**: 10 SDLC role agents + `orchestrator-agent` + `.*-agent` hooks + orchestration-only rules. *(Refined 2026-07-31 by Fork 4 — a small pool of ~4–5 GENERAL capability agents is kept; see Decisions §4.)*

## Net effect

40 skills → **~29** (core plan) / ~25 (with optional Phase 4). **10 rigid role agents → ~4–5 general capability agents.** 16 rules → ~12. Two `.*-agent` hooks removed (matchers stay general); six general guards kept; **+1 skill-invoked artifact-gate validator**.

---

## ClaudeKit learnings folded in (xia, 2026-07-31)

Studied the upstream ClaudeKit-engineer toolkit; full analysis in `reports/xia-*.md` + `reports/xia-synthesis-and-challenge.md`. Non-conflicting lessons now part of scope:

- **P1 — Drop the 4 registries, don't port them.** ClaudeKit ships zero (PLAN-REGISTRY/DECISION-LEDGER/BACKLOG-REGISTRY/PROJECT-MEMORY); `plan.md`+`phase-*.md` checkbox state *is* project memory. Session-resume = read the plan file, not a registry.
- **P1 — Artifact-by-path handoff** replaces the orchestrator's "verify then invoke next agent": each stage skill closes with "artifact at `<path>`; next skill reads it, don't paste content into the next invocation."
- **P1 — Keep matchers general (tool/none), never `.*-agent`**; new hooks follow thin-entry + `lib/` pure-logic + config-gate + fail-open (extend the existing `evals/test_hook.py` shape).
- **P2/P3 — Explicit report size caps** in `sdlc-conventions.md` (ClaudeKit: researcher ≤150 lines, `plan.md` <80, MEMORY <200).
- **P2/P3 — Skill-anatomy conventions** to adopt across stage skills: `<HARD-GATE-*>` tagged blocks (each with a "User override:" escape), Anti-Rationalization tables, mermaid-as-authoritative-flow, a **Required-Subagents/Activation table** (Phase | role | MUST/Optional — makes delegation checkable), and a **Workflow-Position footer** (Typically follows/precedes/Related).
- **P2 — `cook-after-plan-reminder` nudge:** optional stop-event hook that prints the next-skill invocation string, never auto-invokes (respects no-cascade).
- **P1/P3 — Don't over-trim rules** below ~12; ClaudeKit runs on 6 but carries no G1–G8 gate/artifact domain.
- **P3 — Audit line counts directly** (ClaudeKit's own `ck-plan` is ~541 lines vs its stated <300 — claimed caps lie).

---

## Phases

| Phase | Title | Depends on | File |
|-------|-------|-----------|------|
| 1 | Collapse + curate pool + build gate (remove orchestrators + 10 rigid role agents + `.*-agent` hooks + orch rules + registries; **establish ~4–5 capability-agent pool**; **build C1 verdict schema + validator + test**; rework `retro`) | — | `phase-01-collapse-single-layer.md` |
| 2 | Skill merges + spawns (UI→design-system, tech-design→1, remove create-pr; `--parallel` via `cbr:developer`; **gate skills spawn fresh `cbr:reviewer`/`cbr:tester`**, call P1 validator) | P1 | `phase-02-skill-merges.md` |
| 3 | Ripple + docs + validate (gate/artifact tables incl. verdict-artifact path, cross-refs, evals, CLAUDE.md, version, validate) | P1, P2 | `phase-03-ripple-docs-validate.md` |
| 4 | **OPTIONAL** knowledge merges (testing, code-quality, lint+run-tests, systematic-debugging) — NOT user-confirmed | P1 | `phase-04-optional-knowledge-merges.md` |

> Phase 4 is a **recommendation from the audit, not a locked decision.** Execute only if the user opts in. Keep it isolated so the core refactor is independently shippable.

---

## Decisions (resolved 2026-07-31)

1. **G4–G7 enforcement model → (A) verdict + user gate.** Executor skill (`review-code`, `vulnerability-scanner`, `unit-test`, `integration-test`) writes its PASS/FAIL verdict + findings into its artifact and **stops**. The user reads it and decides whether to re-invoke `fix-bug` then re-run. `sdlc-conventions.md` gate table "Decided By" → "`<skill>` verdict + user". No machine FAIL-loop (matches anti-cascade intent). *(The deleted `SubagentStop` hook only enforced STATUS-reporting, never pass-criteria — nothing lost there.)*
2. **Parallel-mode mechanism → modeled on `ck:cook`.** Reference: `C:\Works\Tool\ClaudeKit.CC\claudekit-engineer\claude\skills\cook` (`SKILL.md` + `references/subagent-patterns.md`).
   - Execution skills gain the **`Task`/`Agent` tool** and expose **`--parallel`** as an argument mode (like cook's `argument-hint: [...] [--parallel]`).
   - In `--parallel`, the skill spawns **multiple `developer` capability-agent subagents (from the Fork-4 pool) with explicit file-ownership boundaries**, then synthesizes. *(Updated 07-31: use the pool's `developer` agent, not raw `general-purpose` — it carries the file-ownership persona + `model` tier. Fall back to `general-purpose` only if no pool.)* These are general implementation agents — **NOT** the deleted rigid role agents, and there are **no `.*-agent` hooks**.
   - **Divergence from cook (deliberate):** cook auto-cascades implement→review→test with mandatory review/test subagents. ClaudeBrew keeps **stop-after-stage** — `implement-feature` does NOT auto-spawn `review-code`/`unit-test`; the user runs the next stage. Adopt cook's spawn *mechanism*, not its cascade.
3. **Target name for merged tech-design skill (non-blocking).** Recommend **`architecture`** absorbs `api-patterns` + `database-design`. Alternative: `system-design`. Decide at Phase 2 start.

### Forks from the xia study (resolved 2026-07-31)

4. **Capability-agent pool → (A1) KEEP a small pool.** REFINES Q2 (not a full reversal): remove the 10 rigid SDLC role agents + orchestrators, but KEEP **~4–5 GENERAL capability agents** — `researcher`, `developer` (implementer), `reviewer` (code + security review), `tester` (unit + integration) — that skills spawn on demand. No orchestrator, no role-pipeline, **no `.*-agent` hooks**. Restores fresh-eyes review, per-agent `model` tiering, and selective `memory: project`. Model/memory per agent follows ClaudeKit (opus for reasoning, haiku for mechanical; `memory: project` only on reviewer/tester/researcher).
5. **Gate verdicts → (B1) fresh sub-context.** G4 review / G5a security / G6–G7 test verdicts are produced by a freshly-spawned pool agent (`reviewer`/`tester`), never self-graded inline. So `review-code`, `unit-test`, `integration-test`, `vulnerability-scanner` carry `Task`/`Agent` and spawn the pool agent, write the verdict artifact, then **stop** for the user gate.
6. **Artifact-gate → (C1) BUILD now.** One shared verdict-artifact JSON schema + one Python validator script, invoked by skill instruction via `Bash` (schema-shape + secret-scan + policy: hard gates require `decision === PASS` + passing verification). `AskUserQuestion` on block. Makes Decision 1's "verdict + user gate" deterministic and unfakeable. Registered nowhere as an auto-hook (no matcher) — pure skill-invoked, per ClaudeKit's `workflow-artifact-gate` shape.

> **Status: ✅ EXECUTED (P1–P4) & verified 2026-07-31.** All forks resolved and implemented on branch `worktree-single-layer-refactor`. Phase 4 knowledge merges completed (40→25 skills).

## Success criteria

- [x] `claude plugin validate ./plugins/cbr` → 0 errors; `claude plugin validate .` (marketplace) → pass.
- [x] `plugins/cbr/agents/` contains ONLY the ~4–5 general capability agents (`researcher`, `developer`, `reviewer`, `tester`[, `security`]); the 10 rigid SDLC role agents + `orchestrator-agent` are deleted. Each pool agent has a `model` tier + selective `memory: project`; **none uses a role-pipeline name matched by any hook**.
- [x] `hooks.json` has no `SubagentStart`/`SubagentStop` `.*-agent` blocks; `subagent-context-inject.js` + `subagent-quality-gate.py` deleted (any retained SubagentStart context-inject uses a general/no matcher).
- [x] **Artifact-gate built (C1):** one shared verdict-artifact JSON schema (`plugins/cbr/schemas/`) + one Python validator script; gate skills (`review-code`/`unit-test`/`integration-test`/`vulnerability-scanner`) write the verdict artifact and invoke the validator via `Bash`, with `AskUserQuestion` on block. Validator has an `evals/` unit test (extend `test_hook.py` shape).
- [x] Grep of removed skill/agent names across `plugins/cbr/` returns only intentional references (0 dangling `NOT FOR`/connection/routing rows).
- [x] `sdlc-conventions.md` gate + artifact tables re-point "Decided By"/owner columns from agents → skills; orchestration-only sections removed; **G4–G7 enforcement model (Decision 1) stated explicitly**, not silently downgraded.
- [x] Merged skills each ship one consolidated `evals/evals.json`; each SKILL.md < 500 lines with detail in `references/`.
- [x] Execution skills (`design-screen`, `design-function`, `implement-feature`, `unit-test`, `integration-test`) carry `Task`/`Agent` + a `--parallel` arg that spawns the pool's `developer` agent with file-ownership boundaries (cook-modeled); each still **stops after its stage** (no auto-cascade to review/test).
- [x] Gate skills produce their verdict in a **fresh sub-context** (B1): `review-code`/`vulnerability-scanner` spawn `reviewer`, `unit-test`/`integration-test` spawn `tester` — never self-grade inline.
- [x] `retro` runs solo (no `Agent` tool) reading artifacts + git.
- [x] CLAUDE.md "The SDLC engine" / hooks / reconciliation sections rewritten to single-layer; `plugin.json` version bumped; `CHANGELOG.md` updated.

## Risks / rollback

- **Do all edits in an isolated worktree on a feature branch** (`worktree` skill). The refactor is large and reversible only via git.
- **Validation is the gate** — do not merge until both `claude plugin validate` calls pass.
- Biggest correctness risk: dangling references to removed names breaking triggers → the grep success-criterion is the backstop.

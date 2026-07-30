# Phase 1 — Collapse to Single-Layer

**Depends on:** none · **Goal:** remove the orchestrator→agent engine; keep self-sufficient gated stage skills.

## Context
- Audit: `plans/reports/audit-260730-2316-skills-redundancy-merge.md` §9.
- Gates/artifacts live centrally in `plugins/cbr/rules/sdlc-conventions.md` — NOT in orchestrators (verified).
- Stage skills already self-sufficient (verified `analyze-requirement`: own Step 0→3 + G1 checklist, writes `SRS-[feature].md`).
- Only skills with `Agent` tool: `full-sdlc`, `orchestrate`, `parallel-agents`, `retro`.

## DELETE — skills (whole dirs)
- `plugins/cbr/skills/full-sdlc/`
- `plugins/cbr/skills/orchestrate/`  (also drops `references/spawn-templates.md`, `team-templates.md`)
- `plugins/cbr/skills/parallel-agents/`
- `plugins/cbr/skills/behavioral-modes/`  (7-mode meta; ORCHESTRATE mode now dead)
- `plugins/cbr/skills/intelligent-routing/`  (router obsolete in single-layer, house-style = direct invocation; stale anyway)
- `plugins/cbr/skills/context-inject/`  (already DEPRECATED)

## DELETE — the 10 rigid role agents
- `plugins/cbr/agents/` — delete the SDLC role agents welded to the pipeline: `ba-agent`, `ui-designer-agent`, `architect-agent`, `developer-agent`, `code-review-agent`, `unit-test-agent`, `integration-test-agent`, `security-tester-agent`, `bug-fix-agent`, `orchestrator-agent`.

## ESTABLISH — capability-agent pool (Fork 4 / A1)
Keep `plugins/cbr/agents/` but populate it with **~4–5 GENERAL capability agents** (adapt from ClaudeKit `claude/agents/`, NOT the deleted role agents). These are a flat toolbox skills spawn on demand — no orchestrator, no `.*-agent` hook binds them.

| Agent | Model | `memory` | Purpose | Adapt from |
|-------|-------|----------|---------|-----------|
| `researcher` | haiku | user | multi-source research reports (design/brainstorm support) | ClaudeKit `researcher.md` |
| `developer` | sonnet | — | implement one slice with strict file-ownership (`--parallel` worker) | ClaudeKit `fullstack-developer.md` |
| `reviewer` | inherit | project | adversarial code + security review, "don't rubber-stamp" posture (G4/G5a verdicts) | ClaudeKit `code-reviewer.md` |
| `tester` | haiku | project | run/validate unit + integration suites, coverage (G6/G7 verdicts) | ClaudeKit `tester.md` |
| `security` *(optional 5th)* | inherit | project | dedicated OWASP scan if `reviewer` proves too broad | split from `reviewer` |

- Frontmatter: `name`, `description` (double-quoted), `tools` allowlist, `model`, `memory` (only where listed). **No `permissionMode`** (ClaudeKit's 13 have none — gate via `tools`). **No name ending that a hook matches** — matchers stay general.
- **`subagent_type` resolution (VERIFY at execution):** plugin agents are namespaced — the deleted quality-gate hook's own comment referenced `cbr:developer-agent`. So skills spawn these as **`cbr:researcher`, `cbr:developer`, `cbr:reviewer`, `cbr:tester`** to avoid colliding with the session-global `researcher`/`tester`. Confirm the plugin-namespacing rule with a live spawn during P1 before wiring P2; write the resolved strings into the skills.
- **Procedure ownership (avoid two-copies drift):** the AGENT is a **general persona only** (e.g. `reviewer` = "assume AI-written, don't rubber-stamp" + output/verdict format). The **gate-specific checklist lives in the SKILL and is passed in the spawn prompt** (ClaudeKit pattern: `Task(prompt="Review against these MANDATORY checks: (a)…(e)…")`). One `reviewer` thus serves both G4 (review-code) and G5a (vulnerability-scanner) with different skill-supplied checklists — no duplicated "how to review."
- Bodies: lift persona + posture + output contract; delete all council/PLANNING/orchestrator-mode sections (those belonged to the pipeline).
- `retro` stays solo (below), does NOT spawn pool agents.

## BUILD — artifact-gate (Fork 6 / C1) — built here so P2 gate skills can call it
Skill-invoked validator (no auto-hook, no agent matcher), modeled on ClaudeKit `workflow-artifact-gate.cjs`.
- **Schema:** `plugins/cbr/schemas/verdict-artifact.schema.json` — `{ gate, decision: "PASS|FAIL", findings: [{severity, file, line, note}], verification: [{cmd, result}], secretsScanned, producedBy, timestamp }`.
- **Validator:** `plugins/cbr/hooks/verdict-gate.py` (thin entry + testable logic; fail-open on crash; exit 2 = block). Invoked via `Bash` (`python .../verdict-gate.py --gate <G> --artifact <path>`), never auto-registered.
- **Per-gate policy (do NOT use one rule for all):**
  - **G4 (code review) / G5a (security):** require `decision === "PASS"` + zero unresolved Critical findings. **No `verification` command required** — a reviewer doesn't run commands.
  - **G6 (unit) / G7 (integration):** require `decision === "PASS"` + ≥1 passing `verification` entry (the test run) + zero unresolved Critical.
  - All gates: secret-pattern scan (reuse `protect-files.py` regex bank) blocks on leak.
- **Test:** `evals/test_verdict_gate.py` — per-gate: PASS allows; FAIL / secret / (G6/G7) missing-verification blocks. Mirror `test_hook.py`.

## DELETE — hooks (agent-bound only)
In `plugins/cbr/hooks/hooks.json`: remove the `SubagentStart` and `SubagentStop` blocks (both `matcher: ".*-agent"`). **Keep** all `PreToolUse` guards, `PreCompact`, `PostCompact`, `SessionStart:compact`, `Stop`.
- Delete scripts: `hooks/subagent-context-inject.js`, `hooks/subagent-quality-gate.py`.
- **Note (verified):** `subagent-quality-gate.py` only enforces a `STATUS:`+`EVIDENCE:` reporting discipline on role agents — it is **not** the G4–G7 pass-criteria enforcer. The automated FAIL→fix→re-run enforcement lived in the orchestrator skill bodies (`PASS/FAIL` branches, R1→R5 loops), which are being deleted. **How G4–G7 are enforced post-pivot is plan Decision 1 — resolve before executing this phase.**

## DELETE / TRIM — rules
- DELETE `agent-comms-protocol.md` (inter-agent mailbox — no agents).
- DELETE `model-profiles.md` (agent-spawn cost tiers — no spawning).
- DELETE `agent-best-practices.md` (agent execution guidance) — salvage any universal "Think Before Acting" line into `coding-standards.md` only if not already covered; otherwise drop.
- TRIM `sdlc-conventions.md`: remove **Spawn Sizing**, **Context Budget Estimation**, **Adaptive Batch Sizing**, **Planning Council Trigger**, **Session Resume Pattern** (agent), **Interrupt Protocol** (orchestrator), **Spec Sync Protocol** (orchestrator+developer), **Team Lifecycle Convention**, **Progressive Disclosure Convention** (agent files). **KEEP** Quality Gates table, Artifact Paths table, Tech Stack Detection, Memory Tier (trim tier-2/3 agent rows), Defect Round Loop. *(Table column re-pointing happens in Phase 3.)*
- REVIEW `context-degradation-awareness.md` — keep if framed as general context safety; trim agent-spawn wording.

## REWORK — `retro` → solo skill
- Remove `Agent` from `retro/SKILL.md` `allowed-tools`.
- Replace the "spawn 5 contributing agents concurrently" ceremony with a solo procedure: read the feature's artifacts (SRS/TECH/REVIEW/UTR/ITR/SEC) + git history directly, then produce 5-Why + Lessons + git metrics + Action Items. Output path unchanged (`docs/retros/`).
- Remove "Orchestrator invokes this after Phase 8" framing → "user invokes after delivery."

## Validation
- `claude plugin validate ./plugins/cbr` → 0 errors (frontmatter/skill count).
- Grep `plugins/cbr` for `subagent_type|spawn-templates|orchestrator-agent` → only Phase-2/3 targets remain (ideally 0).
- `hooks.json` parses; `python evals/test_hook.py` still green (enforce-worktree untouched).

## Risks
- Removing `agent-best-practices.md` may drop a convention referenced elsewhere → grep before delete; fold survivors into `coding-standards.md`.
- `retro` rework is the only behavior rewrite in P1 — keep output contract identical.

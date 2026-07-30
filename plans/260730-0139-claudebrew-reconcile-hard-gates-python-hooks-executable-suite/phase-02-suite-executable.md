---
phase: 2
title: "Suite executable"
status: completed
priority: P1
effort: "1-2d"
dependencies: [1]
---

# Phase 2: Suite executable (audit tier P1)

## Overview
Make the imported SDLC pipeline actually run. Today it is not executable as written: `retro` lacks the tools it needs, `orchestrator-agent` reads files that live elsewhere or don't exist, orchestrators claim a security PASS with no security phase, and a deprecated skill is still mandated. Fix every dead path/tool/reference so the reconcile-to-ship decision holds.

## Requirements
- Functional: every orchestrator/agent reference resolves; retro can spawn+write; security phase executes; no double context-injection.
- Non-functional: internal consistency between the two orchestrators and the `sdlc-conventions.md` authority.

## Architecture
Two-layer pipeline: orchestrator skills (`orchestrate`, `full-sdlc`) spawn role agents via the `Agent` tool; the artifact is the contract. Fixes are surgical reference/tooling corrections, not redesign. Agent-name resolution is already sound (10/10 agents exist, `name:` matches bare spawn names) — do not touch that.

## Related Code Files
- Modify: `plugins/cbr/skills/retro/SKILL.md:4` — `allowed-tools` add `Agent, Write, Edit` (it spawns 5 agents at `:37` and writes reports at `:267`); `:6` **[RT-H4]** decide `context: fork` — but VERIFY FIRST against hook/skill docs whether a forked skill can spawn subagents at all. If fork blocks spawning, remove/restructure it. Do NOT assume adding tools alone fixes retro (§7 audit lesson: verify harness behavior, don't infer).
- Modify: `plugins/cbr/agents/orchestrator-agent.md:27-28,145-148` — repoint phase 4–8 Required Reading from `skills/orchestrate/references/phase-4-implementation.md` / `phase-5-8-execution.md` → `skills/full-sdlc/references/...` (Glob-confirmed they live there); `:115` — **[RT-M4]** create a minimal `skills/orchestrate/references/context7-prefetch.md` OR remove the phase 0.2f reference. Correction: `orchestrator-agent.md:115` is the ONLY caller (grep-verified) — `sdlc-conventions.md` does NOT cite it — so removal is equally valid; pick the cheaper.
- Modify: `plugins/cbr/skills/orchestrate/SKILL.md:110-198,292-294` — add a real security phase so the "Security Scan: PASS" success criterion maps to executed work (align with `full-sdlc` Phase 5).
- Modify: `plugins/cbr/skills/parallel-agents/SKILL.md:66-79` and `intelligent-routing/SKILL.md:60-68` — add `security-tester-agent` to the roster (currently omitted → never selectable).
- Modify: `context-inject/SKILL.md` (set `disable-model-invocation: true`) + remove the manual mandate at `full-sdlc/SKILL.md:111`, `orchestrate/SKILL.md:89`, `full-sdlc/references/spawn-templates.md:1-8`, `orchestrate/references/phase-0-council.md:117` (SubagentStart hook already auto-injects per `orchestrator-agent.md:122-124`).
- **[RT-C2]** Modify ONLY the 8 GENUINE plugin-path bugs (`.claude/…` → `${CLAUDE_PLUGIN_ROOT}/…`): `orchestrate/SKILL.md:57,60`; `orchestrate/references/phase-0-council.md:25,44`; `full-sdlc/references/spawn-templates.md:22,39`; `parallel-agents/SKILL.md:66`; `agents/code-review-agent.md:137`. **DO NOT TOUCH** `rules/sdlc-conventions.md:241` (describes the *user's* auto-loaded `.claude/rules/` memory tier — rewriting it deletes a legitimate authority row) or `:248` (convention prose about agent-def structure, not a runtime load path). Blind-rewriting these two is itself the "infer without verifying" bug the audit diagnosed.
- Modify: `full-sdlc/SKILL.md:80-84` vs `rules/sdlc-conventions.md:94-98` — reconcile UT/IT agent sizing (authority: Large = 3 UT + 2 IT).
- Create: registry templates the orchestrators copy from (bootstrapping gap) — e.g. `plugins/cbr/skills/orchestrate/references/templates/{PLAN-REGISTRY,DECISION-LEDGER,BACKLOG-REGISTRY,PROJECT-MEMORY}.md`; update the "create from docs/_templates/…" instructions to point at them.

## Implementation Steps
1. Fix `retro` frontmatter (tools + fork); dry-verify Phase 8.5 delegation from `full-sdlc:306` now has the tools it needs.
2. Repoint `orchestrator-agent.md` phase 4–8 paths; create or delete the `context7-prefetch.md` reference (single caller — removal and creation are equally valid; pick the cheaper).
3. Add/align the security phase in `orchestrate`; add `security-tester-agent` to both rosters; confirm the "Security Scan: PASS" criterion now maps to a real phase.
4. De-mandate `context-inject` (frontmatter flag + remove 4 mandate sites); leave one short note that injection is automatic via the hook.
5. **[RT-C2]** Fix the **8 genuine** `.claude/agents|rules/*` references → `${CLAUDE_PLUGIN_ROOT}/...`; leave `sdlc-conventions.md:241,248` untouched.
6. Reconcile UT/IT sizing to the authority table.
7. Add registry template files + repoint the "create from template" instructions.

## Success Criteria
- [x] The 8 genuine plugin-path refs use `${CLAUDE_PLUGIN_ROOT}`; the 2 legitimate user-dir refs (`sdlc-conventions.md:241,248`) are intentionally preserved (spot-checked, not blind-grepped to 0).
- [x] No orchestrator/agent reference points to a non-existent file (`context7-prefetch.md`, wrong-subdir phase files resolved).
- [x] `retro` frontmatter grants Agent/Write/Edit; retrospective phase is runnable.
- [x] `orchestrate` executes a security phase; `security-tester-agent` is reachable from routing.
- [x] `context-inject` is invoked once (hook only); no manual mandate remains.

## Risk Assessment
- **Shared file `sdlc-conventions.md`** is edited here and in Phase 3 (artifact paths) — sequential phases avoid conflict; do Phase 2 edits first.
- **Scope creep:** resist redesigning the pipeline; these are reference/tooling fixes only. If a fix reveals a deeper design gap, log it as a follow-up, don't expand this phase.
- **Verify, don't assume:** re-read each target `file:line` before editing — the audit line numbers are a snapshot and may shift after Phase 1 edits.

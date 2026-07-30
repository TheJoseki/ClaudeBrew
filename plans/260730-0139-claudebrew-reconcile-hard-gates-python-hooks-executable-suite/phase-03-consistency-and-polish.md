---
phase: 3
title: "Consistency and polish"
status: completed
priority: P2
effort: "1d"
dependencies: [2]
---

# Phase 3: Consistency and polish (audit tier P2)

## Overview
Unify the artifact-path convention (the pipeline's core "artifact = contract" depends on one scheme), finish the "ClaudeKit"→"ClaudeBrew" rename, and clear ship-hygiene debt (version, dev cruft, missing evals, trigger overlap). Lowest correctness risk, but required before the suite reads as one coherent product.

## Requirements
- Functional: one artifact-path scheme used everywhere; zero "ClaudeKit"; version reflects the expansion.
- Non-functional: knowledge/executor skills don't mis-route; trigger reliability is testable.

## Architecture
Canonical artifact path = `docs/specs/<stage>/<TYPE>-<slug>.md` (authority `sdlc-conventions.md`, already used by 33 files / 131 refs). The minority schemes migrate to it. Rename + hygiene are mechanical sweeps guarded by grep counts.

## Related Code Files
- Modify (adopt authority scheme): `brainstorming/SKILL.md` + references (currently `docs/specs/YYYY-MM-DD-<topic>-<stage>.md` → e.g. `docs/specs/brainstorms/BRAINSTORM-<slug>.md`); `clean-code/SKILL.md:97` (`docs/decisions/` → authority subdir). Update the authority table in `rules/sdlc-conventions.md` if it needs a `brainstorms/` row. **[RT-M5]** ALSO migrate `brainstorming/evals/evals.json:8` (asserts the OLD `docs/specs/<date>-…-brainstorm.md` path — a leftover assertion breaks the eval after migration). For `worktree/*`: touch ONLY artifact-path strings here — its opt-in docs were already rewritten in Phase 1 [RT-C3]; do not clobber those edits.
- Modify (rename): the 16 files containing "ClaudeKit" (31 occurrences) — `rules/*.md`, the ported hook scripts (`subagent-quality-gate` + `compact-context-saver`, whatever extension Phase 1 [RT-H1] left them / `subagent-context-inject.js`), `skills/vulnerability-scanner/scripts/run_audit.sh`, `lint-and-validate/scripts/detect_stack.sh`, `estimate/scripts/calc_estimate.py`, `design-system/scripts/generate-slide.py`, `design-screen/references/design-tool-reference.md`. **[RT-H1]** Grep by CONTENT across `plugins/cbr/hooks/*` regardless of extension, so a renamed script's "ClaudeKit" string is not missed.
- Modify: `plugins/cbr/.claude-plugin/plugin.json` version `0.1.0` → next (e.g. `0.2.0`); add/append `CHANGELOG.md`.
- Delete: `plugins/cbr/skills/ui-styling/scripts/.coverage` (dev cruft shipped to users); add a `.gitignore` rule.
- **[DISCOVERED at cook — HIGH, promote ahead of the rest of P2]** `claude plugin validate ./plugins/cbr` reports **33 skills/agents whose YAML frontmatter FAILS to parse** → they load with EMPTY metadata (name/description/allowed-tools/model/permissionMode all silently dropped). Root cause: unquoted `description:` scalars containing `: ` (colon-space) from the `TRIGGER:`/`NOT FOR:` convention (e.g. `analyze-requirement/SKILL.md:3`). Fix: quote every affected `description` (double-quote or `>-` block scalar) so the colon-space is literal. **Verify each fix by re-running `claude plugin validate` to 0 frontmatter errors.** Worst impact is on `agents/*-agent.md` — dropped `allowed-tools`/`permissionMode` means a declared-restricted agent runs unrestricted; treat the agent frontmatter fixes as belonging with Phase 2 (executability), skills with Phase 3.
- Modify: add `TRIGGER:` / `NOT FOR:` guards to overlapping knowledge skills (`design-system`/`ui-styling`/`ui-ux-pro-max`/`design-screen`; `testing-patterns`/`tdd-workflow`/`unit-test`/`integration-test`/`run-tests`; `clean-code`/`code-review-checklist`/`review-code`; `architecture`/`design-function`/`api-patterns`/`database-design`). **MUST quote the `description` scalar** — adding a bare `TRIGGER:`/`NOT FOR:` reproduces the parse failure above. Gate the change on `claude plugin validate` staying at 0 frontmatter errors.
- Create: `evals/evals.json` for the 38 skills lacking them (representative trigger prompts) — prioritize the SDLC executors + orchestrators.
- Modify: root `CLAUDE.md` — fix doc drift ("pixel-status-update.js in 5 places" → 4, removed in Phase 1) and refresh the "Reconciliation gaps" section. **[RT-M6]** ALSO update `CLAUDE.md:76` (still names `protect-files.sh`/`guard-bash.sh`/`guard-webfetch.sh` and lists both PostCompact+SessionStart reinject — stale the moment Phase 1 lands: guards are now `.py`, one reinject removed).

## Implementation Steps
1. Decide brainstorm's new canonical path; migrate `brainstorming`/`worktree`/`clean-code`; update `sdlc-conventions.md` table so all stages share the scheme.
2. Sweep-rename "ClaudeKit" → "ClaudeBrew" across the 16 files; `grep -rn ClaudeKit plugins/cbr` must return 0.
3. Bump `plugin.json` version; write CHANGELOG entry summarizing Phases 1-3.
4. Remove `.coverage`; add `.gitignore` entry for coverage artifacts.
5. Add trigger guards to overlapping knowledge skills.
6. Author `evals/evals.json` per skill (start with orchestrators + executors; knowledge skills can follow).
7. Update root `CLAUDE.md` (drift + reconciliation-gaps status).

## Success Criteria
- [x] One artifact-path scheme; no skill writes/reads a non-canonical `docs/specs/...` path.
- [x] `grep -rn "ClaudeKit" plugins/cbr` → 0.
- [x] `plugin.json` version bumped; CHANGELOG updated; `.coverage` gone.
- [x] Overlapping knowledge skills carry `TRIGGER:`/`NOT FOR:`; SDLC executor + orchestrator skills have evals.
- [x] `claude plugin validate ./plugins/cbr` and `claude plugin validate .` pass.

## Risk Assessment
- **Rename false-positives:** "ClaudeKit" may appear in URLs/store-ids that shouldn't change — review each hit, don't blind-sed.
- **Artifact-path migration churn:** touching `brainstorming` (committed core) risks its evals; re-run `brainstorming`/`worktree` evals after the path change.
- **[RT-M7] Eval authoring scope (no silent cap):** 38 evals is large; treat orchestrator + executor evals as the phase's done-bar. The remaining knowledge-skill evals MUST be written as a durable `docs/BACKLOG-REGISTRY.md` entry (not just this plan's risk note, which archives with the plan) so the audit's "eval coverage ~0" finding has a tracked home rather than quietly becoming a partial.

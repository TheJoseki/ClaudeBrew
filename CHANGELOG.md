# Changelog

All notable changes to ClaudeBrew (the `cbr` plugin) are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Session + subagent lifecycle context hooks** — two general hooks giving the single-layer suite ClaudeKit-parity lifecycle behavior with no orchestrator and no `.*-agent` matcher:
  - `session-init.py` (`SessionStart: startup|resume|clear`) reconstructs a gate-aware SDLC summary from committed `docs/` artifacts (the automatic form of `/cbr:handoff`), injects it as plain stdout, and builds a `.claude/sdlc-index.json` cache.
  - `subagent-context.py` (`SubagentStart`, no matcher — fires for every spawn) injects the active feature + gate + verdict path/schema + section pointers to pool agents, reading the cache with a glob fallback (cache is convenience; glob-on-canonical-path stays authority).
  - Shared `hooks/lib/sdlc_state.py` (state reconstruction). **100% test coverage** (`evals/test_sdlc_state.py`, `evals/test_lifecycle_hooks.py`; 39 cases). P1 firing empirically validated in a `--plugin-dir` session.
- Cross-session memory now **self-reconstructs from `docs/`** — no separate durable state file; the cache is an ephemeral per-session convenience.

### Changed
- Corrected the skill count in `CLAUDE.md` (~29 → 25) after the P4 knowledge merges.

### Fixed
- **Post-compaction context reinjection now actually reaches the model.** The rich reinject was wired to `PostCompact`, whose stdout is **log-only** (docs-verified) — so it never reached Claude. Compaction reinjection is folded into `session-init.py` on the injection-capable `SessionStart` (`…|compact`) path: PreCompact checkpoint + SDLC gate-state + PROJECT.md sections + an AskUserQuestion approval-gate reminder (the ClaudeKit mitigation). Removed the dead `post-compact-reinject.sh` and the now-redundant `re-inject-context.sh` (which also still read the removed `DECISION-LEDGER.md`). One `SessionStart` hook now handles new sessions and compaction alike.

## [0.3.0] — 2026-07-31

Single-layer pivot: collapsed the imported two-layer orchestrator→role-agent engine into one layer of self-sufficient, gated stage skills over a small pool of general capability agents. Refactor plan + ClaudeKit study under `plans/260730-2316-single-layer-sdlc-refactor/`.

### Removed
- **Orchestrators + meta-skills** — `full-sdlc`, `orchestrate`, `parallel-agents`, `behavioral-modes`, `intelligent-routing`, and the deprecated `context-inject`. They forced entry through an orchestrator and over-cascaded; the house style is hard-gate + no auto-cascade.
- **The 10 rigid SDLC role agents** (`ba-agent`, `architect-agent`, …, `orchestrator-agent`) and the `.*-agent` `SubagentStart`/`SubagentStop` hooks that bound to them (`subagent-context-inject.js`, `subagent-quality-gate.py`). Six general hook-guards remain.
- **Orchestration-only rules** (`agent-comms-protocol`, `model-profiles`, `agent-best-practices`) and the orchestrator-maintained registries; `plan.md`/`phase-*.md` are the project memory.

### Added
- **Capability-agent pool** — a flat toolbox skills spawn on demand: `researcher`, `developer`, `reviewer`, `tester` (general personas with per-agent `model` tiering + selective `memory: project`). No orchestrator, no role-pipeline.
- **`--parallel` mode** on execution skills — spawns `cbr:developer` workers under strict file-ownership.
- **Verdict gate (`hooks/verdict-gate.py` + `schemas/verdict-artifact.schema.json`)** — gate skills spawn a fresh `cbr:reviewer`/`cbr:tester` for a no-self-grade verdict, then run the validator (schema + secret-scan + per-gate policy; fail-closed) with `AskUserQuestion` on block. Skill-invoked, no matcher. 98% test coverage.

### Changed
- **Merged knowledge clusters** — UI (`ui-styling` + `ui-ux-pro-max` → `design-system`) and technical-design (`api-patterns` + `database-design` → `architecture`), each one lean SKILL.md + references. `retro` reworked to run solo. `create-pr` folded into `implement-feature`.
- **Further knowledge consolidation** — `lint-and-validate` + `run-tests` → `validate-and-test`; `testing-patterns` + `tdd-workflow` → `testing-strategy`; `clean-code` + `code-review-checklist` → `code-quality`; `systematic-debugging` folded into `fix-bug/references/`. Net skills: 40 → 25.

## [0.2.0] — 2026-07-30

Reconcile release: made the advertised "hard gates" real, ported hooks to Python, and made the imported SDLC suite executable. Reconcile audit + plan under `plans/`.

### Fixed
- **Security guards were no-ops.** `protect-files`, `guard-bash`, `guard-webfetch` (PreToolUse) read a non-existent `$CLAUDE_TOOL_INPUT` env var and never fired. Ported to Python reading stdin JSON so they actually block (secrets incl. case-insensitive + AWS creds, dangerous shell patterns, URL shorteners).
- **33 frontmatter parse failures.** Skills/agents had unquoted `description` scalars containing `: ` (from the `TRIGGER:`/`NOT FOR:` convention) → YAML failed to parse → they loaded with empty metadata (role agents lost `tools`/`model`/`permissionMode`). Quoted the scalars; `claude plugin validate` now passes.
- **Imported orchestration not executable.** Repointed dead `orchestrator-agent` phase-4–8 reads, removed the dead `context7-prefetch` reference, gave `retro` its `Agent`/`Write`/`Edit` tools, added `security-tester-agent` to routing rosters, corrected `.claude/` plugin paths to `${CLAUDE_PLUGIN_ROOT}`.

### Changed
- **Hooks ported bash→Python** (guards, SubagentStop quality gate, PreCompact saver) — drop the `bash`/`jq` dependency that failed on stock Windows/macOS. Removed 4 dead `pixel-status-update.js` calls.
- **Worktree gate is now OPT-IN** via `/cbr:setup` (registers `enforce-worktree.py` into the user's `settings.json`) instead of always-on — a plugin cannot ship harness settings, and always-on would hard-deny edits in every repo. Default = no gate.
- Dropped the deprecated manual `context-inject` mandate (a SubagentStart hook auto-injects). Renamed remaining "ClaudeKit" → "ClaudeBrew"; removed shipped `.coverage` cruft.

### Consistency
- Unified artifact-path to `docs/specs/<stage>/<TYPE>-<slug>.md` (brainstorms/worktrees/decisions folded into the authority table). Authored `evals/evals.json` for all 40 skills (was 2). Added quoted `TRIGGER:`/`NOT FOR:` guards to overlapping knowledge skills.

## [0.1.0] — 2026-05-26

First packaged release. ClaudeBrew is now a distributable Claude Code plugin (`cbr`) served from a marketplace in this repo, installable via `/plugin marketplace add` → `/plugin install`.

### Added
- **Plugin + marketplace packaging**: `.claude-plugin/marketplace.json` (catalog `claudebrew`) and `plugins/cbr/.claude-plugin/plugin.json` (plugin `cbr`).
- **`setup` skill** (`/cbr:setup`) — applies the harness-level settings a plugin cannot bundle (agent-teams env var, `teammateMode`, `worktree.baseRef`).
- `brainstorming` (Stage 1) and `worktree` (Stage 1.5) skills, now shipped inside the plugin and namespaced as `/cbr:brainstorming` and `/cbr:worktree`.

### Changed
- The worktree gate (`enforce-worktree.py`) is now registered by the plugin's `hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}`, so it is active whenever the `cbr` plugin is enabled (previously a standalone `.claude/settings.json` registration).
- Dev-only tooling (trigger/behavioral evals, the hook unit test) moved to `evals/`; sample artifacts moved to `examples/` — both outside the shipped plugin.

# Changelog

All notable changes to ClaudeBrew (the `cbr` plugin) are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

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

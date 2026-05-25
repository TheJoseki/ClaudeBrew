# Changelog

All notable changes to ClaudeBrew (the `cbr` plugin) are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-26

First packaged release. ClaudeBrew is now a distributable Claude Code plugin (`cbr`) served from a marketplace in this repo, installable via `/plugin marketplace add` → `/plugin install`.

### Added
- **Plugin + marketplace packaging**: `.claude-plugin/marketplace.json` (catalog `claudebrew`) and `plugins/cbr/.claude-plugin/plugin.json` (plugin `cbr`).
- **`setup` skill** (`/cbr:setup`) — applies the harness-level settings a plugin cannot bundle (agent-teams env var, `teammateMode`, `worktree.baseRef`).
- `brainstorming` (Stage 1) and `worktree` (Stage 1.5) skills, now shipped inside the plugin and namespaced as `/cbr:brainstorming` and `/cbr:worktree`.

### Changed
- The worktree gate (`enforce-worktree.py`) is now registered by the plugin's `hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}`, so it is active whenever the `cbr` plugin is enabled (previously a standalone `.claude/settings.json` registration).
- Dev-only tooling (trigger/behavioral evals, the hook unit test) moved to `evals/`; sample artifacts moved to `examples/` — both outside the shipped plugin.

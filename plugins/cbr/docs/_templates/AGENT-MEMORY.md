---
type: AGENT_MEMORY_FORMAT_GUIDE
description: Recommended format for native agent memory files at .claude/agent-memory/<agent-name>/MEMORY.md
---

# Agent Memory Format Guide

> This template defines the recommended structure for native agent memory files.
> Location: `.claude/agent-memory/<agent-name>/MEMORY.md` (managed by Claude Code `memory: project`).
> Claude Code auto-loads the first 200 lines at agent startup — no manual injection needed.

## Codebase Patterns (this project)

<!-- Non-obvious patterns about how this project's code is structured -->
<!-- Example: Service layer uses constructor injection via NestJS DI — never manual instantiation -->

## Common Pitfalls (learned from execution)

<!-- Mistakes or edge cases discovered during work -->
<!-- Example: Forgot to add DTO validation pipe on new endpoints → causes 500 instead of 400 -->

## Spec Interpretation Notes

<!-- How to interpret ambiguous spec language in this project's context -->
<!-- Example: "Soft delete" means deletedAt timestamp column, not isDeleted boolean -->

## Rules

1. Claude Code auto-saves to `.claude/agent-memory/<agent-name>/MEMORY.md` — no manual file creation needed
2. Only save project-specific, non-obvious patterns — not general programming knowledge
3. Mem0-style dedup: Check existing entries before adding — UPDATE if refinement, skip if duplicate
4. Staleness check: If an entry references a file/function, verify it still exists
5. Cross-agent insights go to `docs/memory/PROJECT-MEMORY.md` instead (shared via context-inject)

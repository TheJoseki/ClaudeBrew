---
name: setup
description: >-
  Post-install configurator for ClaudeBrew (the `cbr` plugin). Applies the
  harness-level settings that a plugin cannot ship inside its own package — the
  agent-teams env var, in-process teammate mode, and `worktree.baseRef` — by
  idempotently merging them into the user's `.claude/settings.json`, and can
  persist the worktree-isolation policy into CLAUDE.md/memory so the worktree
  stage is authorized to run proactively. Run this once right after installing the
  `cbr` plugin, or whenever the user says "set up ClaudeBrew", "cbr setup",
  "configure cbr", "finish installing cbr", or reports that teammate mode or the
  worktree branch base isn't behaving. Without it, brainstorming's team mode and
  the worktree stage's `baseRef` behavior are unconfigured.
---

# Setup — configure the ClaudeBrew harness

A Claude Code plugin can ship skills, agents, and hooks, but **its own
`settings.json` only honors `agent` and `subagentStatusLine`** — so the
harness-level settings ClaudeBrew relies on cannot travel inside the `cbr`
package. This skill is the one mechanism that applies them: it merges them into
the user's *own* `.claude/settings.json`. Run it once after install.

## What it configures

| Key | Value | Why ClaudeBrew needs it |
|---|---|---|
| `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `"1"` | Enables agent-team ("teammate") brainstorming — the multi-agent mode `cbr:brainstorming` uses for complex, multi-domain problems. |
| `teammateMode` | `"in-process"` | The lifecycle `cbr:brainstorming` drives (`TeamCreate` → spawn → `SendMessage` → shutdown). |
| `worktree.baseRef` | `"head"` | `cbr:worktree` branches from local HEAD so the just-committed (possibly unpushed) approved spec is captured. The default `fresh` branches from `origin/<default>` and would miss it. |

Optional (offer, don't force): `env.MCP_TIMEOUT="30000"`, `env.MCP_TOOL_TIMEOUT="60000"`
— more headroom for Context7/other MCP calls during evidence-gathering.

> The worktree **gate** (the `PreToolUse` hook) is *not* configured here — the
> plugin auto-registers it via `hooks/hooks.json` whenever `cbr` is enabled. Setup
> only handles the keys a plugin cannot ship.

## Workflow

```
1. Choose scope        → verify: user (~/.claude/settings.json) vs project (.claude/settings.json), confirmed
2. Read current state  → verify: existing settings parsed; note which target keys are already present/correct
3. Show the merge      → verify: present the exact keys to add/change; never overwrite unrelated keys
4. Apply (idempotent)  → verify: keys merged; pre-existing values not duplicated or clobbered
5. Persist policy      → verify: offer (recommended) to persist worktree-isolation instruction to CLAUDE.md/memory
6. Confirm             → verify: re-read settings; report what changed and what was already correct; note a restart may be needed for env vars
```

### 1 — Choose scope

Default to **user scope** (`~/.claude/settings.json`) so ClaudeBrew works in every
repo. Offer **project scope** (`.claude/settings.json`, committed) when the user
wants the config to travel with one repo / their team. State which you'll use and
confirm — `worktree.baseRef: head` changes how *all* worktrees in scope branch, so
the user should know the blast radius before you write it globally.

### 2 — Read current state

Read the target settings file (it may not exist yet — treat missing as `{}`).
Identify which of the target keys are already set and whether their values already
match. This is what makes the skill **idempotent**: re-running it is a no-op when
everything is already correct.

### 3 — Show the merge

Present the precise additions/changes as a small diff or list before writing.
**Never silently mutate a user's settings file**, and never touch keys outside the
table above. You may delegate the actual edit to the `update-config` skill (it
specializes in safe `settings.json` changes) or apply it directly with `Edit`.

### 4 — Apply (idempotent)

Merge the keys, preserving all existing content and formatting as much as
possible. Deep-merge nested objects (`env`, `worktree`) — do not replace the whole
`env` block and drop the user's other variables.

### 5 — Persist the worktree-isolation policy (recommended)

`cbr:worktree` uses the native `EnterWorktree` tool, whose contract authorizes the
move when "the user or project instructions (CLAUDE.md/memory)" call for it.
Invoking the worktree skill is already such an instruction, but **recommend**
persisting an always-on, proactive policy so the move is authorized in every
future session without re-prompting. With the user's explicit confirmation (it
edits their own docs), add a short line to the project `CLAUDE.md` or a memory:
*"Development of an approved approach is done in an isolated git worktree on a
feature branch (the `cbr:worktree` skill performs the move)."* This is the
belt-and-suspenders that guarantees `EnterWorktree` authorization even where the
skill body alone might be treated as insufficient. Only skip it if the user
declines.

### 6 — Confirm

Re-read the file and report exactly what changed vs. what was already correct.
Remind the user that **env-var changes take effect on the next Claude Code
session** (the agent-teams flag in particular), and point them to
`cbr:brainstorming` as the entry point to the pipeline.

## Notes

- **Idempotent by design** — safe to run repeatedly; it only writes deltas.
- **Surgical** — touches only the keys in the table; everything else is left alone.
- **Honest** — if a key is already set to a *different* value the user clearly
  chose on purpose, surface the conflict and ask rather than overwriting.

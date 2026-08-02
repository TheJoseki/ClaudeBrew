---
name: setup
description: >-
  Post-install configurator for ClaudeBrew (the `cbr` plugin). Applies the
  harness-level settings that a plugin cannot ship inside its own package — the
  agent-teams env var, in-process teammate mode, and `worktree.baseRef` — by
  idempotently merging them into the user's `.claude/settings.json`; on opt-in it
  also installs the worktree base-branch gate (`enforce-worktree.py`), which the
  plugin cannot register itself; and it can persist the worktree-isolation policy
  into CLAUDE.md/memory so the worktree stage is authorized to run proactively.
  Run this once right after installing the `cbr` plugin, or whenever the user says
  "set up ClaudeBrew", "cbr setup", "configure cbr", "finish installing cbr",
  "install the worktree gate", or reports that teammate mode or the worktree
  branch base isn't behaving. Without it, brainstorming's team mode and the
  worktree stage's `baseRef` behavior are unconfigured and no worktree gate is
  active.
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

Also configured on **opt-in** (offer, don't force — see Step 5):

| Component | What | Why it can't ship in the plugin |
|---|---|---|
| Worktree gate | A `PreToolUse` registration of `enforce-worktree.py` in the user's `.claude/settings.json` | A plugin's own `settings.json` only honors `agent`/`subagentStatusLine`, so it **cannot** register a harness hook. Without this step there is no base-branch gate (the accepted default). |

> The worktree **gate** is *not* shipped active and the plugin **cannot**
> auto-register it — this skill is the only mechanism that installs it, and only
> when the user opts in. Everything here is a key or hook a plugin cannot ship.

## Workflow

```
1. Choose scope        → verify: user (~/.claude/settings.json) vs project (.claude/settings.json), confirmed
2. Read current state  → verify: existing settings parsed; note which target keys are already present/correct
3. Show the merge      → verify: present the exact keys to add/change; never overwrite unrelated keys
4. Apply (idempotent)  → verify: keys merged; pre-existing values not duplicated or clobbered
5. Install worktree gate (opt-in) → verify: offer; if accepted — python doctor passes, hook copied to a stable path, settings_merge.py registered it
6. Persist policy      → verify: offer (recommended) to persist worktree-isolation instruction to CLAUDE.md/memory
7. Ignore hook artifacts → verify: project .gitignore lists the ephemeral lifecycle-hook caches (idempotent; create if missing)
8. Confirm             → verify: re-read settings; report what changed and what was already correct; note a restart may be needed for env vars
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

### 5 — Install the worktree gate (opt-in)

The base-branch gate (`enforce-worktree.py`) is the one thing the plugin **cannot
register itself** (a plugin's `settings.json` only honors `agent`/
`subagentStatusLine`). Installing it here is **opt-in — offer, don't force**, and
warn about the blast radius first: once registered, feature-code edits on
`main`/`master` are **denied** in *every* repo in that settings scope. **Recommend
project scope** (`.claude/settings.json`) so the denial is confined to this repo;
a user-scope registration hits repos that never installed `cbr`. If the user
declines, skip this step — the accepted default is no gate.

If accepted, do three things in order:

**(a) Resolve an absolute hook path.** Neither `${CLAUDE_PLUGIN_ROOT}` nor
`${CLAUDE_PROJECT_DIR}` resolves inside a user `settings.json`, so the
registration needs a concrete absolute path. First locate the plugin root — prefer
`$CLAUDE_PLUGIN_ROOT` if set, else glob the install cache:

```bash
# Plugin root: env var if present, else the marketplace cache copy.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/cbr 2>/dev/null | head -1)}"
```

Then **copy** the hook to a stable location you control and register *that* path:

```bash
# Trade-off (copy vs. cache-path glob): we copy to a stable, documentable path
# rather than baking in the versioned cache path. The cache path can move on a
# plugin/marketplace update and would leave a dangling registration; the stable
# copy survives that. Cost: the copy can drift from the shipped hook, so re-run
# /cbr:setup after a plugin update to refresh it. The hook is self-contained
# (reads stdin, shells to git), so a copy runs identically.
mkdir -p ~/.claude/cbr/hooks
cp "$PLUGIN_ROOT/hooks/enforce-worktree.py" ~/.claude/cbr/hooks/enforce-worktree.py
ABS_HOOK="$HOME/.claude/cbr/hooks/enforce-worktree.py"   # absolute; expand ~ yourself on Windows
```

**(b) Doctor: is a Python interpreter available?** The registration runs `python
"<abs path>"`, so `python` (or `py -3`) must be on `PATH` — otherwise the harness
treats the erroring hook as non-blocking and the gate is silently off.

```bash
python --version 2>/dev/null || py -3 --version 2>/dev/null || echo "WARN: no python/py -3 on PATH — the gate will not run until Python is installed"
```

Warn the user if neither resolves; proceed to register anyway (they may fix PATH
later), but tell them the gate is inert until Python is available.

**(c) Register via `settings_merge.py`.** It is idempotent and preserves unrelated
settings (including the shipped `protect-files.py` entry, which uses a different
matcher and coexists):

```bash
python "$PLUGIN_ROOT/hooks/settings_merge.py" <target .claude/settings.json> "$ABS_HOOK"
```

Use the settings file for the scope chosen in Step 1 (project recommended for the
gate). Re-running is safe — the helper adds the registration only if absent.

### 6 — Persist the worktree-isolation policy (recommended)

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

### 7 — Ignore ephemeral hook artifacts

The lifecycle context hooks write **derived, per-session** files into the project's
`.claude/`: `sdlc-index.json` (the `session-init.py` SDLC-state cache) and
`compact-checkpoint.md` (the pre-compact checkpoint). They are rebuilt every session
and must never be committed. Idempotently ensure the **project** `.gitignore` lists
them (create `.gitignore` if missing; skip any line already present; never remove
existing entries):

```gitignore
# ClaudeBrew ephemeral hook caches (derived, not source)
.claude/sdlc-index.json
.claude/compact-checkpoint.md
```

This is project-scoped hygiene — do it regardless of the settings scope chosen in
Step 1, since the caches are written into whatever repo the hooks run in.

### 8 — Confirm

Re-read the file and report exactly what changed vs. what was already correct.
If the gate was installed, confirm the registration is present, the copied hook
path exists, and Python resolved — only then call the gate active; otherwise say
it is off. Remind the user that **env-var changes take effect on the next Claude
Code session** (the agent-teams flag in particular), and point them to
`cbr:brainstorming` as the entry point to the pipeline.

## Notes

- **Idempotent by design** — safe to run repeatedly; it only writes deltas
  (`settings_merge.py` adds the gate registration only if absent).
- **Surgical** — touches only the keys in the table, on opt-in the single
  worktree-gate `PreToolUse` registration, and the project `.gitignore` cache
  entries (append-only); everything else is left alone.
- **Honest** — if a key is already set to a *different* value the user clearly
  chose on purpose, surface the conflict and ask rather than overwriting.

# Enforcement — the deterministic gate

This is the layer that makes worktree isolation a **certainty** rather than a
hope. The skill body (`SKILL.md`) is read by the model and *usually* obeyed; this
hook is run by the Claude Code harness and *always* runs. When you need a rule to
hold 100% of the time, you move it out of the model's attention and into the
harness's control flow.

## Table of contents

1. How the hook blocks (mechanism)
2. What it blocks vs. exempts (scope)
3. The doctor (precondition checks)
4. Installing the hook
5. Windows execution notes
6. Honest residual limitations

## 1. How the hook blocks (mechanism)

The gate is a `PreToolUse` hook. Per the Claude Code docs, a `PreToolUse` hook
can block a tool call two ways:

- **Exit code 2** — Claude Code ignores stdout; stderr is fed back to Claude as
  the error.
- **Exit 0 + JSON on stdout** — Claude Code parses stdout for a decision. This is
  what `enforce-worktree.py` uses, because it lets the hook hand Claude a precise,
  actionable reason instead of an opaque failure:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "…enter a worktree first, then retry this edit."
  }
}
```

`permissionDecision` accepts `allow`, `deny`, `ask`, `defer`. The hook receives,
on stdin, a JSON payload including `tool_name`, `tool_input` (with `file_path` or
`notebook_path`), and `cwd` — enough to decide based on the current branch and
the path being edited.

Source: https://code.claude.com/docs/en/hooks.md

## 2. What it blocks vs. exempts (scope)

Registered with matcher `Edit|Write|NotebookEdit` — the tools that write code.
**`Bash` is deliberately excluded**: tooling commands (`npm install`, `git
worktree …`, the skill's own setup) must run on the base branch.

The hook denies an edit only when **all** are true: current branch is a base
branch (`main`/`master`), and the target path is **not** in the exemption set.

Exemptions (defined in `${CLAUDE_PLUGIN_ROOT}/hooks/enforce-worktree.py` as `EXEMPT_GLOBS`):

| Glob | Why it's exempt |
|---|---|
| `docs/specs/*` | SDLC handoff artifacts every stage reads/writes |
| `.claude/*` | Skills, settings, hooks — harness config, never the product |
| `*.md` | Documentation, at any depth |
| `.gitignore`, `.worktreeinclude` | Repo/worktree configuration |

The exemptions are **scope, not an opt-out**: they encode "what is not feature
code". The load-bearing reason they exist — without `docs/specs/*` and
`.claude/*`, the hook would block the `brainstorming` stage from writing its own
artifact on the base branch, breaking the pipeline it is meant to protect.

> Note on `fnmatch`: Python's `fnmatch` treats `*` as matching across `/`, so
> `.claude/*` already covers any depth under `.claude/`. (This differs from shell
> globbing — verified by the hook's unit tests.)

## 3. The doctor (precondition checks)

Run these in Phase 0 before claiming isolation is enforced:

1. **Git repo?** `git rev-parse --show-toplevel` succeeds.
2. **Already in a worktree?** `git rev-parse --abbrev-ref HEAD` is not a base
   branch and the path is under `.claude/worktrees/` → the move is already done.
3. **Gate active?** The `cbr` plugin auto-registers the `PreToolUse` hook via its
   `hooks/hooks.json`, so the gate is live whenever the plugin is enabled. If the
   plugin is disabled (`/plugin`), the guarantee is not real.
4. **Base ref correct?** Set `worktree.baseRef: head` so the worktree branches
   from local HEAD — which includes the just-committed approved spec. The default
   `fresh` branches from `origin/<default-branch>`, so it requires a remote *and*
   would miss local-only commits (the approved spec, if not yet pushed).

## 4. How the hook is registered (the plugin mechanism)

The gate only enforces if the harness is told to run it. As a plugin component,
that registration is **automatic**: the `cbr` plugin ships `hooks/hooks.json`,
and Claude Code loads it whenever the plugin is enabled — no edit to the user's
`settings.json` is required.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/enforce-worktree.py"],
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installed location in the cache
(`~/.claude/plugins/cache/...`). It is required because an installed plugin runs
from that copy, not from the repo — a `${CLAUDE_PROJECT_DIR}` path would not
resolve in a user's project. Everything the hook touches must therefore live
**inside the plugin directory**; `enforce-worktree.py` is self-contained (it only
reads stdin and shells out to `git`), so it ships cleanly.

`worktree.baseRef: head` is *not* in this file — a plugin's own `settings.json`
only honors `agent`/`subagentStatusLine`, so harness-level keys cannot ride along
in the package. `/cbr:setup` applies `baseRef` (plus the agent-teams env var and
`teammateMode`) to the user's `settings.json` instead.

### Lifecycle: the gate is bound to the plugin

Because the registration lives in the plugin's `hooks/hooks.json`, the gate's
lifecycle *is* the plugin's lifecycle: enabled plugin → gate live; disabled
plugin → gate gone (along with the skills). This is a deliberate, coherent
coupling — there is no separate `settings.json` registration to drift out of
sync, and no orphaned script path to fail open. The one thing to be honest about:
"disable the `cbr` plugin" now also means "disable the worktree gate", which is
why the skill's doctor confirms the plugin is enabled before claiming enforcement.

> Historical note: when ClaudeBrew was standalone `.claude/` config, the script
> lived in canonical `.claude/hooks/` and was registered in `.claude/settings.json`
> so the gate survived even if the skill folder was removed. Packaging as a plugin
> supersedes that reasoning — the plugin is the unit of both distribution and
> enablement, so bundling the hook in `hooks/hooks.json` is simpler *and* the only
> mechanism that travels with the package and auto-registers on enable.

## 5. Windows execution notes

The handler uses the **exec form** (`command: "python"` + `args: [...]`) rather
than a shell string. This sidesteps PowerShell/Git-Bash quoting entirely — the
script is spawned directly with `python` (which must be on `PATH`, as it is for
this repo's other helpers). The docs also expose a `shell: "powershell"` handler
option if a `.ps1` is ever preferred, but Python keeps the gate cross-platform
and matches the repo's existing helper convention.

Source: https://code.claude.com/docs/en/hooks.md , https://code.claude.com/docs/en/settings.md

## 6. Honest residual limitations

A safety gate should be honest about its edges:

- **`Bash` write bypass.** Because the matcher excludes `Bash`, a determined
  agent could still write a file via shell redirection (`echo > file`). This is
  accepted: guarding `Bash` would block legitimate tooling on the base branch,
  and in practice the agent writes code through `Edit`/`Write`, which are gated.
- **Broad `*.md` exemption.** All markdown is treated as docs/SDLC artifacts. For
  a project whose *product* is markdown, tighten this glob.
- **Fail-open by design.** If git state can't be read, the hook allows the edit.
  A gate that bricks unrelated work is worse than one with a narrow, documented
  bypass. The bypass only triggers when we genuinely cannot tell where we are.
- **Base-branch list.** Only `main`/`master` count as base. A repo using a
  differently-named trunk must extend `BASE_BRANCHES` in the hook.

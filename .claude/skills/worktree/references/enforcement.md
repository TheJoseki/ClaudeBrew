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

Exemptions (defined in `.claude/hooks/enforce-worktree.py` as `EXEMPT_GLOBS`):

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
3. **Hook registered?** `.claude/settings.json` contains a `PreToolUse` entry
   pointing at `enforce-worktree.py`. If absent, the guarantee is not real.
4. **Base ref correct?** Set `worktree.baseRef: head` so the worktree branches
   from local HEAD — which includes the just-committed approved spec. The default
   `fresh` branches from `origin/<default-branch>`, so it requires a remote *and*
   would miss local-only commits (the approved spec, if not yet pushed).

## 4. Installing the hook

The hook only enforces if it is registered in `settings.json`. A skill should not
silently rewrite a user's settings — present this and confirm (or delegate to the
`update-config` skill):

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
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/enforce-worktree.py"],
            "timeout": 10
          }
        ]
      }
    ]
  },
  "worktree": { "baseRef": "head" }
}
```

`${CLAUDE_PROJECT_DIR}` resolves to the project root. Project-scoped
`.claude/settings.json` is committed, so the rule travels with the repo and every
SDLC stage inherits it.

### Why the script lives in `.claude/hooks/`, not in the skill

The *registration* must be in a settings file regardless — that is the only
mechanism that makes a hook always-on (a hook declared in skill frontmatter is
active only *while that skill is loaded*, which would reopen the probabilistic
gap this gate exists to close). Given the registration lives in `settings.json`,
the *script* is deliberately placed in the canonical `.claude/hooks/` rather than
inside `skills/worktree/`, for one concrete reason: the gate's lifecycle is
**independent of the skill**. If the script lived in the skill and the skill were
later disabled or removed, the `settings.json` registration would point at a
missing file → the hook fails to run → it fails open → the hard-mandatory gate
silently disappears. Decoupling the script keeps the gate alive regardless of the
skill's state. (If ClaudeBrew is ever distributed as a *plugin*, bundle the hook
via the plugin's `hooks/hooks.json` instead — that is the only mechanism that both
travels with the package and auto-registers when enabled.)

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

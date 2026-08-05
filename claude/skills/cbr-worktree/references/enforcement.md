# Enforcement — the deterministic gate

This is the layer that can make worktree isolation a **certainty** rather than a
hope — **once it is opted in**. The skill body (`SKILL.md`) is read by the model
and *usually* obeyed; this hook, when registered, is run by the Claude Code
harness before every write. When you need a rule to hold every time, you move it
out of the model's attention and into the harness's control flow.

The deliberate default: **the gate is not shipped active.** An always-on
base-branch gate would deny edits in every repo CBR is installed into, so the base
install never registers it. The gate is **opt-in** —
`claudebrew install --gate` registers `enforce-worktree.py` in the user's settings. **By default — the user never runs `claudebrew install --gate`,
e.g. headless `claude -p` or CI — there is no harness gate**, and isolation rests
on the skill alone. That default is an accepted posture, not a bug; this document
describes what the gate does *when opted in*.

## Table of contents

1. How the hook blocks (mechanism)
2. What it blocks vs. exempts (scope)
3. The doctor (precondition checks)
4. Registering the hook (opt-in, via `claudebrew install --gate`)
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

Exemptions (defined in `{{CBR_ROOT}}/hooks/enforce-worktree.py` as `EXEMPT_GLOBS`):

| Glob | Why it's exempt |
|---|---|
| `docs/streams/*` | SDLC work-stream artifacts every stage reads/writes |
| `.claude/*` | Skills, settings, hooks — harness config, never the product |
| `*.md` | Documentation, at any depth |
| `.gitignore`, `.worktreeinclude` | Repo/worktree configuration |

The exemptions are **scope, not an opt-out**: they encode "what is not feature
code". The load-bearing reason they exist — without `docs/streams/*` and
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
3. **Gate registered? (opt-in — off by default)** The gate only denies once
   `claudebrew install --gate` has registered `enforce-worktree.py`. Check **all three** settings
   files the harness merges — `~/.claude/settings.json` (user),
   `.claude/settings.json` (project), `.claude/settings.local.json`
   (project-local) — for a `PreToolUse` entry whose command contains
   `enforce-worktree`. Absent from all three → the gate is off (the default), and
   the guarantee is not real. Registration is necessary but not sufficient: also
   confirm the registered absolute path exists and `python`/`py -3` resolves, or
   the harness treats the erroring hook as non-blocking. Only claim enforcement
   when all three checks pass.
4. **Base ref correct?** Set `worktree.baseRef: head` so the worktree branches
   from local HEAD — which includes the just-committed approved spec. The default
   `fresh` branches from `origin/<default-branch>`, so it requires a remote *and*
   would miss local-only commits (the approved spec, if not yet pushed).

## 4. How the hook is registered (opt-in, via `claudebrew install --gate`)

The gate only enforces if the harness is told to run it, and the base install
deliberately does **not** register it. An always-on base-branch gate would deny
edits in *every* repo CBR is installed into — the wrong default — so the gate is a
separate opt-in step (`claudebrew install --gate`), never part of the base install.

On opt-in, the installer merges one `PreToolUse` entry into the user's settings
(project scope → `.claude/settings.local.json` by default; user scope →
`~/.claude/settings.json`), through the same deep-merge that provisions the other hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:/Users/<you>/.claude/hooks/enforce-worktree.py\""
          }
        ]
      }
    ]
  }
}
```

Two things to note about this entry:

- **The path is absolute, and must be.** Inside a settings file a
  `${CLAUDE_PROJECT_DIR}`-anchored or repo-relative path does not resolve — the
  harness runs the hook with no reliable CWD. The installer therefore bakes the
  concrete absolute path of the installed hook
  (`<abs>/.claude/hooks/enforce-worktree.py`) as it merges. The registration is
  provenance-tracked, so `claudebrew uninstall` removes exactly it.
- **It is a separate registration from the shipped `protect-files.py`.** The base
  install's `PreToolUse` entry uses matcher `Edit|Write`; this opt-in entry uses
  `Edit|Write|NotebookEdit`. Different matcher strings, so they are two independent
  registrations, and on an `Edit`/`Write` **both** hooks run. The gate neither
  replaces nor rides inside the base entry.

`worktree.baseRef: head` is applied by the base install (with the agent-teams env
var and `teammateMode`) — harness-level keys the installer ships and merges directly.

## 5. Windows execution notes

The installer registers the hook as the command string `<python> "<abs path>"`,
where `<python>` is the interpreter its doctor resolved. This is why `claudebrew
install` runs a `python`/`py -3` availability doctor and **fails the install** if
none resolves: a registration whose interpreter is missing makes the harness treat
the hook as non-blocking, so the gate would be silently off. The quoted
absolute path tolerates spaces (e.g. `C:\Users\...`). Python keeps the gate
cross-platform and matches the repo's existing helper convention.

Source: https://code.claude.com/docs/en/hooks.md , https://code.claude.com/docs/en/settings.md

## 6. Honest residual limitations

A safety gate should be honest about its edges:

- **Opt-in by default — no gate unless `claudebrew install --gate` ran.** The base install
  does not register the gate active. If the user never
  opts in — the common case for headless `claude -p` and CI — there is no
  harness-level denial at all, and isolation rests entirely on the skill (a
  probabilistic constraint). This is the accepted default posture, not a defect.
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

# Enforcement — the deterministic gate

This is the layer that can make worktree isolation a **certainty** rather than a
hope — **once it is opted in**. The skill body (`SKILL.md`) is read by the model
and *usually* obeyed; this hook, when registered, is run by the Claude Code
harness before every write. When you need a rule to hold every time, you move it
out of the model's attention and into the harness's control flow.

The catch a plugin cannot escape: **the gate is not shipped active.** A plugin
cannot register harness hooks, and an always-on base-branch gate would deny edits
in every repo the user installs `cbr` into. So the gate is **opt-in** —
`/cbr:setup` registers `enforce-worktree.py` in the user's `.claude/settings.json`
(via `hooks/settings_merge.py`). **By default — the user never runs `/cbr:setup`,
e.g. headless `claude -p` or CI — there is no harness gate**, and isolation rests
on the skill alone. That default is an accepted posture, not a bug; this document
describes what the gate does *when opted in*.

## Table of contents

1. How the hook blocks (mechanism)
2. What it blocks vs. exempts (scope)
3. The doctor (precondition checks)
4. Registering the hook (opt-in, via `/cbr:setup`)
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
   `/cbr:setup` has registered `enforce-worktree.py`. Check **all three** settings
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

## 4. How the hook is registered (opt-in, via `/cbr:setup`)

The gate only enforces if the harness is told to run it — and **a plugin cannot
tell it to.** A plugin's own `settings.json` only honors `agent`/
`subagentStatusLine`, so a plugin cannot register a `PreToolUse` hook. The
plugin's shipped `hooks/hooks.json` therefore does **not** register
`enforce-worktree.py` at all. (It registers unrelated hooks — e.g. a
`protect-files.py` secrets guard on `Edit|Write` — but nothing that gates the base
branch.) An always-on gate would also be the wrong default: it would deny
base-branch edits in *every* repo the user installs `cbr` into.

So registration is **opt-in**. `/cbr:setup` merges an entry into the **user's**
`.claude/settings.json` (via `hooks/settings_merge.py`, which is idempotent):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:/Users/<you>/.claude/cbr/hooks/enforce-worktree.py\""
          }
        ]
      }
    ]
  }
}
```

Two things to note about this entry:

- **The path is absolute, and must be.** Inside a *user* `settings.json`, a
  `${CLAUDE_PROJECT_DIR}`-anchored or repo-relative path does not resolve — the
  harness runs the hook with no reliable CWD, not from the user's settings dir.
  The install step therefore resolves a concrete absolute path. It **copies** `enforce-worktree.py` to a
  stable location it controls (`~/.claude/cbr/hooks/enforce-worktree.py`) and
  registers that, rather than baking in the glob-resolved plugin cache path
  (`~/.claude/plugins/cache/<marketplace>/cbr/hooks/...`). The trade-off: the
  stable copy is a real, documentable path that survives cache moves, but it can
  drift from the shipped hook — re-running `/cbr:setup` after a plugin update
  refreshes it. (The hook is self-contained — it only reads stdin and shells out
  to `git` — so a copy runs identically to the original.)
- **It is a separate registration from the shipped `protect-files.py`.** The
  shipped `hooks.json` already has a `PreToolUse` entry with matcher `Edit|Write`;
  this opt-in entry uses matcher `Edit|Write|NotebookEdit`. Different matcher
  strings, so they are two independent registrations, and on an `Edit`/`Write`
  **both** hooks run. The gate neither replaces nor rides inside the shipped
  entry.

`worktree.baseRef: head` is applied the same way — `/cbr:setup` writes it (plus
the agent-teams env var and `teammateMode`) into the user's `settings.json`,
because those harness-level keys cannot ride inside the plugin package either.

## 5. Windows execution notes

`settings_merge.py` registers the hook as the command string `python "<abs
path>"` — the interpreter `python` must be on `PATH`. This is why `/cbr:setup`
runs a `python`/`py -3` availability doctor before registering and warns if
neither resolves: a registration whose interpreter is missing makes the harness
treat the hook as non-blocking, so the gate would be silently off. The quoted
absolute path tolerates spaces (e.g. `C:\Users\...`). Python keeps the gate
cross-platform and matches the repo's existing helper convention.

Source: https://code.claude.com/docs/en/hooks.md , https://code.claude.com/docs/en/settings.md

## 6. Honest residual limitations

A safety gate should be honest about its edges:

- **Opt-in by default — no gate unless `/cbr:setup` ran.** The plugin does not
  ship the gate active (a plugin cannot register harness hooks). If the user never
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

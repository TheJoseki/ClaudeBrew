# Worktree mechanics — best practices & the `EnterWorktree` tool

How to create, enter, populate, and eventually tear down the isolated worktree,
with the git-worktree best practices behind each step.

## Table of contents

1. Why worktrees for agentic development
2. Layout & naming
3. The `EnterWorktree` tool (the switch)
4. `baseRef` — where the branch starts
5. Carrying the approved spec across
6. Bootstrapping untracked files (.env, deps)
7. Lifecycle & cleanup

## 1. Why worktrees for agentic development

"A working directory holds one train of thought at a time." A worktree gives an
approach (or an agent) its **own** working files on its **own** branch while
sharing the repo's history/objects. This buys isolation (no clobbering the base
branch or other in-flight work), easy throwaway (delete the worktree, the history
stays), and parallel safety (multiple approaches/agents at once). It is the
recommended pattern for AI coding.

Sources: https://code.claude.com/docs/en/worktrees ,
https://towardsdatascience.com/ai-agents-need-their-own-desk-and-git-worktrees-give-it-one/ ,
https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees

## 2. Layout & naming

Claude Code's native convention nests worktrees **inside** the repo at
`.claude/worktrees/<name>/` on branch `worktree-<name>`, branched from the base
ref. Keep `.claude/worktrees/` in `.gitignore` (the worktree's own working files
should not be tracked by the parent).

Naming rules (enforced by `EnterWorktree`): each "/"-separated segment may contain
only letters, digits, dots, underscores, and dashes; ≤64 chars total. Use the
brainstorm's topic slug — short, lowercase, hyphenated, descriptive
(`auth-jwt`, not `branch1` or a 60-char sentence). Mirroring the slug across the
brainstorm artifact, the branch, and the worktree dir keeps the trail readable.

Sources: https://code.claude.com/docs/en/worktrees ,
https://www.gitworktree.org/guides/best-practices , https://git-scm.com/docs/git-worktree

## 3. The `EnterWorktree` tool (the switch)

`EnterWorktree` is the **only** mechanism that switches the live session's
working directory into the worktree — a `git worktree add` subprocess cannot
change its parent session's CWD. Behavior:

- **Create + enter:** pass `name`. It creates `.claude/worktrees/<name>/` on a new
  branch (base per `worktree.baseRef`) and switches the session in.
- **Enter existing:** pass `path` (must be a registered worktree of this repo,
  e.g. one created earlier with `git worktree add`). `ExitWorktree` will not
  remove a worktree entered this way.
- **Preconditions:** must be in a git repo (or have WorktreeCreate/Remove hooks);
  must **not** already be in a worktree.
- **Authorization:** the tool may be used only when the user or CLAUDE.md/memory
  explicitly directs worktree use. This project's CLAUDE.md does, and invoking the
  `worktree` skill is that instruction.
- **Subagent limitation (verified):** `EnterWorktree` refuses from a subagent or
  any session with a cwd override ("it would mutate the parent session's
  process-wide working directory"). It therefore works only from a top-level
  session — which is the normal place this skill runs. From a teammate/subagent,
  fall back to `git worktree add` and hand the *path* to a top-level session to
  enter; see SKILL.md "When things go sideways".

## 4. `baseRef` — where the branch starts

Set by `worktree.baseRef` in settings:

- `fresh` (default) — branch from `origin/<default-branch>`. **Requires a remote.**
- `head` — branch from the current local HEAD. Use when you want to build on the
  local state — including commits not yet pushed (e.g. the just-committed approved
  spec). Required when there is no remote.

For the SDLC flow the worktree must branch from the just-approved local state:
the approved spec is committed locally and may be unpushed. So `head` is the
correct default here — even with a remote, `fresh` would branch from
`origin/<default-branch>` and miss that commit.

Source: https://code.claude.com/docs/en/worktrees

## 5. Carrying the approved spec across

A worktree branches from a **commit**; uncommitted working-copy files do not
appear in it. The approved `…-brainstorm.md` was written on the base branch and
is likely uncommitted, so it must be made reachable from the new branch:

- **Default — commit it first.** Commit the approved spec to the base branch
  before `EnterWorktree`. A tracked file is visible on every branch, and approval
  is a natural commit milestone (it dogfoods "approved artifact = milestone").
- **Alternative — `.worktreeinclude`.** Add `docs/specs/*` so the native worktree
  flow copies the untracked artifact across. Use when an auto-commit is unwanted.

State which you used in the handoff artifact.

## 6. Bootstrapping untracked files (.env, deps)

A fresh worktree starts clean — no `.env`, no `node_modules`, no build cache.
Two complementary tools:

- **`.worktreeinclude`** (gitignore syntax) lists *untracked* files to copy into
  new worktrees — e.g. `.env`, `.env.local`, local secrets, `.claude/settings.local.json`.
- **Dependencies** are reinstalled per worktree (`npm install` / `pnpm install`);
  `pnpm`'s content-addressable store dedupes across worktrees to save disk.

Source: https://code.claude.com/docs/en/worktrees

## 7. Lifecycle & cleanup

Out of scope for this stage (cleanup belongs to a later `ship` stage), but for
reference:

- **List:** `git worktree list` (`--porcelain` for scripts).
- **Leave mid-session:** `ExitWorktree` with `action: "keep"` (preserve) or
  `"remove"` (delete dir + branch; needs `discard_changes: true` if dirty). It
  only acts on worktrees created by `EnterWorktree` this session.
- **Remove manually:** `git worktree remove <path>` (never `rm -rf` — that leaves
  stale metadata), then `git worktree prune`.

Sources: https://git-scm.com/docs/git-worktree , https://www.gitworktree.org/tutorial/prune

# ClaudeBrew (`cbr`)

A full software-development lifecycle as a suite of Claude Code skills — one per stage, each handing a structured artifact to the next:

```
brainstorming → worktree → requirement → design → coding → testing → ship
```

## Skills

| Skill | Stage | What it does |
|---|---|---|
| `/cbr:setup` | — | Applies harness-level settings this plugin can't bundle (agent-team mode, `worktree.baseRef`). **Run once after install.** |
| `/cbr:brainstorming` | 1 | Turns a raw idea into a validated, evidence-backed brainstorm artifact. Never guesses; surfaces every uncertainty. |
| `/cbr:worktree` | 1.5 | Moves an approved approach into an isolated git worktree on a feature branch. Hard-mandatory, enforced by a `PreToolUse` hook. |

(Stages `requirement` → `ship` are in progress.)

## After installing

```
/cbr:setup
```

Then restart your session (so the agent-team environment variable takes effect) and start with `/cbr:brainstorming`.

## The worktree gate

This plugin registers a `PreToolUse` hook (`hooks/enforce-worktree.py`) that **denies feature-code edits on `main`/`master`** — development of an approved approach must happen in an isolated worktree. The gate is active whenever this plugin is enabled. SDLC artifacts (`docs/specs/*`), config (`.claude/*`), and docs (`*.md`) stay editable on the base branch.

Full documentation: https://github.com/TheJoseki/ClaudeBrew

# ClaudeBrew (`cbr`)

A full software-development lifecycle as a suite of Claude Code skills — one per stage, each handing a structured artifact to the next:

```
brainstorming → worktree → requirement → design → coding → testing → ship
```

## Skills

| Skill | Stage | What it does |
|---|---|---|
| `/cbr:setup` | — | Applies harness-level settings this plugin can't bundle (agent-team mode, `worktree.baseRef`) and, on opt-in, installs the worktree gate. **Run once after install.** |
| `/cbr:brainstorming` | 1 | Turns a raw idea into a validated, evidence-backed brainstorm artifact. Never guesses; surfaces every uncertainty. |
| `/cbr:worktree` | 1.5 | Moves an approved approach into an isolated git worktree on a feature branch. The move is hard-mandatory; an opt-in `PreToolUse` gate (installed by `/cbr:setup`) can enforce it deterministically. |

(Stages `requirement` → `ship` are in progress.)

## After installing

```
/cbr:setup
```

Then restart your session (so the agent-team environment variable takes effect) and start with `/cbr:brainstorming`.

## The worktree gate (opt-in)

This plugin ships a `PreToolUse` hook (`hooks/enforce-worktree.py`) that **denies feature-code edits on `main`/`master`** — so development of an approved approach happens in an isolated worktree. It is **opt-in**, not shipped active: a plugin cannot register harness hooks, and an always-on gate would deny base-branch edits in every repo you install `cbr` into. Run `/cbr:setup` to register it in your `.claude/settings.json`. **By default (setup not run — e.g. headless `claude -p` or CI) there is no gate**, and isolation rests on the `/cbr:worktree` skill alone. When installed, SDLC artifacts (`docs/specs/*`), config (`.claude/*`), and docs (`*.md`) stay editable on the base branch.

Full documentation: https://github.com/TheJoseki/ClaudeBrew

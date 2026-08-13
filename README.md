# ClaudeBrew

<!-- release: 0.12.0 -->

**A full software-development lifecycle, delivered as a suite of Claude Code skills.**

ClaudeBrew (`cbr`) turns a raw idea into shipped software through one skill per SDLC stage, each handing a structured, reviewed artifact to the next:

```
brainstorming → worktree → requirement → design → implement → review → test → security → delivery → retro
```

Every stage **never guesses** (uncertainty is surfaced, not assumed), is **evidence-backed** (library docs via Context7, prior art via web search, every source cited), and **stops at a hard gate** — it writes its artifact, waits for your approval, and never silently cascades into the next stage.

> **Status:** the full single-layer SDLC suite ships — 25 stage/knowledge skills over a 5-agent capability pool (`researcher`/`developer`/`reviewer`/`tester`/`strategist`), each stage writing a gated artifact. `brainstorming` (Stage 1) and `worktree` (Stage 1.5) are the reference implementations every sibling matches.

## Install

ClaudeBrew installs into your Claude Code environment with a single command — no plugin, no marketplace:

```
npx claudebrew install
```

That provisions the skills, agents, rules, and hooks into your project's `.claude/` (or `~/.claude/` with `--scope user`), merges the harness settings a plugin can't ship (agent-team mode, worktree base ref), and writes a managed rules block into your project memory. **Python 3 is required** — every hook is Python, and the installer fails loudly if no interpreter is on `PATH`.

Manage the install later:

```
claudebrew update           # pull a new version without clobbering your edits
claudebrew uninstall        # remove everything it added (settings un-merged, files removed)
claudebrew install --gate   # also register the opt-in base-branch worktree gate
```

Project-scope settings merge into the gitignored `settings.local.json` by default (per-machine); pass `--shared` to target the tracked `settings.json`. Then restart your session so the agent-team environment variable takes effect.

## Use

Start the pipeline by describing something you want to build:

- **`/cbr-brainstorming`** — turn an idea into a validated, evidence-backed brainstorm artifact. (It also triggers automatically when you say things like "I have an idea…", "help me scope X", or "where do I start?")
- **`/cbr-worktree`** — once a brainstorm is approved, move development into an isolated git worktree on a feature branch. The move is the skill's mandate; the deterministic `PreToolUse` gate that denies feature-code edits on `main`/`master` is **opt-in** — enable it with `claudebrew install --gate`.

Each stage writes its artifact into your repo under `docs/` (canonical paths live in `.claude/docs/references/sdlc-reference.md`), and a per-work-stream manifest at `docs/streams/<slug>-<date>/STREAM.md` links every artifact of one feature with a kanban-style task board — so a stream's brainstorm, spec, plan, reviews and tests read as one unit instead of scattering.

## What makes it different

- **Never-guess** at the strictest setting — any ambiguity becomes a batched, pre-analyzed question, never a silent assumption.
- **Deterministic isolation** — worktree discipline is enforced by a harness hook, not merely requested in prose.
- **DAR** (Decision Analysis & Resolution) on hard-to-reverse trade-offs — weighted criteria, a scoring matrix, a recorded decision.
- **Agent teams** — complex brainstorms can spin up a team of specialist sub-agents that challenge each other.
- **One work-stream, one tree** — every feature's artifacts are linked from a `STREAM.md` manifest with a task board and a derived gate-status snapshot; an **Artifact Lifecycle** table records who creates/updates/closes each artifact, so nothing is generated-and-forgotten.
- **Agent-consumable templates** — the shipped `docs/_templates/` set is written to be *filled by an agent*, not read like a manual (one grep-able placeholder syntax; framework specifics come from your `PROJECT.md`).

## Develop / contribute

This repo is both the npm package and the dev workspace. The shipped payload is authored under `claude/` (installed as the user's `.claude/`); everything else (`evals/`, `examples/`, the dev config) stays out of the package.

```
node bin/claudebrew.mjs install --dev        # dogfood: sync claude/ into this repo's .claude/; re-run after edits
node --test scripts/*.test.mjs               # installer unit + integration tests
python evals/test_replatform_invariants.py   # structural gate: no plugin-isms, tokens present, Python-only hooks
python evals/test_release_docs.py            # release-docs gate: version <-> CHANGELOG + doc anchors
python evals/test_canonical_paths.py         # canonical stream-first artifact paths
python evals/test_hook.py                    # unit-test the worktree gate
```

See [CLAUDE.md](CLAUDE.md) for the full architecture, conventions, ship process, and Windows caveats.

## Also from Joseki

[**Clawform**](https://clawform.thejoseki.com) — safe AWS CloudFormation
workflows for Claude Code. Same idea applied to infrastructure: rules the agent
reads before it writes, a CLI that runs every change through a change set you
approve, and a hook that refuses the commands nobody should run by accident.
Commercial, one-time licence.

ClaudeBrew is MIT and stays MIT. This is a pointer, not a bundle.

## License

MIT — see [LICENSE](LICENSE).

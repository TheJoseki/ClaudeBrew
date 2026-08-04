# ClaudeBrew

<!-- release: 0.7.0 -->

**A full software-development lifecycle, delivered as a suite of Claude Code skills.**

ClaudeBrew (`cbr`) turns a raw idea into shipped software through one skill per SDLC stage, each handing a structured, reviewed artifact to the next:

```
brainstorming → worktree → requirement → design → implement → review → test → security → delivery → retro
```

Every stage **never guesses** (uncertainty is surfaced, not assumed), is **evidence-backed** (library docs via Context7, prior art via web search, every source cited), and **stops at a hard gate** — it writes its artifact, waits for your approval, and never silently cascades into the next stage.

> **Status:** the full single-layer SDLC suite ships — 25 stage/knowledge skills over a 5-agent capability pool (`researcher`/`developer`/`reviewer`/`tester`/`strategist`), each stage writing a gated artifact. `brainstorming` (Stage 1) and `worktree` (Stage 1.5) are the reference implementations every sibling matches.

## Install

ClaudeBrew ships as a Claude Code plugin. From inside Claude Code:

```
/plugin marketplace add TheJoseki/ClaudeBrew
/plugin install cbr@claudebrew
/cbr:setup
```

`/cbr:setup` applies the harness-level settings a plugin can't bundle itself (agent-team mode and the worktree branch base). Run it once after installing, then restart your session so the environment variables take effect.

## Use

Start the pipeline by describing something you want to build:

- **`/cbr:brainstorming`** — turn an idea into a validated, evidence-backed brainstorm artifact. (It also triggers automatically when you say things like "I have an idea…", "help me scope X", or "where do I start?")
- **`/cbr:worktree`** — once a brainstorm is approved, move development into an isolated git worktree on a feature branch. This is **hard-mandatory**: a `PreToolUse` hook denies feature-code edits on `main`/`master`, so building always happens in isolation. The gate is active whenever the `cbr` plugin is enabled.

Each stage writes its artifact into your repo under `docs/` (canonical paths live in `sdlc-conventions.md`), and a per-work-stream manifest at `docs/streams/<slug>-<date>/STREAM.md` links every artifact of one feature with a kanban-style task board — so a stream's brainstorm, spec, plan, reviews and tests read as one unit instead of scattering.

## What makes it different

- **Never-guess** at the strictest setting — any ambiguity becomes a batched, pre-analyzed question, never a silent assumption.
- **Deterministic isolation** — worktree discipline is enforced by a harness hook, not merely requested in prose.
- **DAR** (Decision Analysis & Resolution) on hard-to-reverse trade-offs — weighted criteria, a scoring matrix, a recorded decision.
- **Agent teams** — complex brainstorms can spin up a team of specialist sub-agents that challenge each other.
- **One work-stream, one tree** — every feature's artifacts are linked from a `STREAM.md` manifest with a task board and a derived gate-status snapshot; an **Artifact Lifecycle** table records who creates/updates/closes each artifact, so nothing is generated-and-forgotten.
- **Agent-consumable templates** — the shipped `docs/_templates/` set is written to be *filled by an agent*, not read like a manual (one grep-able placeholder syntax; framework specifics come from your `PROJECT.md`).

## Develop / contribute

This repo is both the marketplace and the dev workspace. The shipped plugin is `plugins/cbr/`; everything else (`evals/`, `examples/`, the dev config) stays out of the package.

```
claude --plugin-dir ./plugins/cbr     # load the plugin in place; /reload-plugins after edits
claude plugin validate ./plugins/cbr  # validate the plugin
claude plugin validate .              # validate the marketplace
python evals/test_hook.py             # unit-test the worktree gate
python evals/test_release_docs.py     # release-docs gate: version <-> CHANGELOG + doc anchors
python evals/test_english_docs.py     # English-only gate: no CJK in shipped skill prose
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

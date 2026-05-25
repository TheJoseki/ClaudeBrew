# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ClaudeBrew** is a harness-engineering toolkit that implements a **full software-development lifecycle (SDLC) as a suite of Claude Code skills** — one skill per stage, each handing a structured artifact to the next:

```
brainstorming → (worktree) → requirement → design → coding → testing → ship
```

`brainstorming` (Stage 1) is built and is the **reference implementation** every sibling skill imitates. `worktree` (Stage 1.5 — the isolation gate between an approved brainstorm and any implementation) is also built; see "Worktree isolation" below. The remaining stages are not yet created.

This is not a conventional application: there is no build system, dependency manifest, or test runner — don't hunt for `package.json` or a lint command. The "source" is the skills under `plugins/cbr/skills/`, authored in Markdown (plus small Python helpers). "Testing" a skill means evaluating how well Claude follows it, not running unit tests.

### How ClaudeBrew ships: one plugin, one marketplace

ClaudeBrew is distributed as a **single Claude Code plugin** named `cbr`, served from a **plugin marketplace** rooted in this repo. Layout:

```
ClaudeBrew/                          # repo root = marketplace catalog + dev workspace
├── .claude-plugin/marketplace.json  # the catalog: lists the cbr plugin (source ./plugins/cbr)
├── .claude/settings.json            # DEV-ONLY harness settings (dogfooding; not shipped)
├── plugins/cbr/                      # ── THE SHIPPED UNIT (copied to users' plugin cache) ──
│   ├── .claude-plugin/plugin.json    # name "cbr", displayName "ClaudeBrew", version (source of truth)
│   ├── skills/<stage>/SKILL.md       # the SDLC skills, plus the `setup` skill
│   └── hooks/{hooks.json, enforce-worktree.py}  # the worktree gate, auto-registered
├── evals/                            # DEV-ONLY trigger/behavioral evals + the hook unit test
└── examples/                         # sample artifacts (e.g. a brainstorm output)
```

Everything under `plugins/cbr/` is copied wholesale into each user's `~/.claude/plugins/cache` on install, so **nothing dev-only lives there** — evals, examples, and this CLAUDE.md stay at the repo root, outside the shipped unit. Installed skills are namespaced: `/cbr:brainstorming`, `/cbr:worktree`, `/cbr:setup`.

**Users install** (the marketplace's relative `source` requires a git add, not a raw `marketplace.json` URL):
```
/plugin marketplace add TheJoseki/ClaudeBrew
/plugin install cbr@claudebrew
/cbr:setup           # applies the harness-level settings a plugin can't ship (see below)
```

**Develop** with the plugin loaded in place, then `/reload-plugins` after edits:
```
claude --plugin-dir ./plugins/cbr
```
Validate before committing: `claude plugin validate ./plugins/cbr` (the plugin) and `claude plugin validate .` (the marketplace). **Ship** by bumping `version` in `plugins/cbr/.claude-plugin/plugin.json` (leave `version` out of the marketplace entry so there's one source of truth), updating `CHANGELOG.md`, and pushing to GitHub; users pull it via `/plugin marketplace update` → `/plugin update`.

**A plugin cannot ship harness settings.** A plugin's own `settings.json` only honors `agent`/`subagentStatusLine`, so the agent-teams env var, `teammateMode`, and `worktree.baseRef` cannot live in the package — the `/cbr:setup` skill merges them into the *user's* `.claude/settings.json` post-install. This repo's own `.claude/settings.json` already carries them, for dogfooding.

### Skill anatomy (the pattern every stage follows)

```
plugins/cbr/skills/<stage>/
├── SKILL.md          # workflow spine + frontmatter (name + the triggering description)
├── references/*.md   # progressive-disclosure detail, loaded only when needed
└── evals/evals.json  # representative test prompts
```

SKILL.md stays lean (<500 lines); deep procedure lives in `references/` and is pulled in on demand (for `brainstorming`: `clarify-loop.md`, `dar-analysis.md`, `artifact-template.md`, `teammate-mode.md`). **Read `plugins/cbr/skills/brainstorming/SKILL.md` and its references first** — that is the house style to match before authoring a sibling skill.

### Conventions inherited across the suite

When building `requirement`, `design`, etc., follow what `brainstorming` established:

- **Plain stage names** (`brainstorming`, not `sdlc-brainstorming`); once installed they namespace to `/cbr:<stage>`.
- **Handoff artifacts** at `docs/specs/YYYY-MM-DD-<topic>-<stage>.md` (in the *user's* repo, not this one). Each stage's artifact is the contract the next stage consumes — completeness there is the entire point of the stage.
- **Hard gate + no auto-cascade**: a stage does no downstream work and does not invoke the next skill until its artifact is written and the user explicitly approves; then it **stops** so the user decides when the next stage begins. Cascading silently is a bug, not a feature.
- **Never-guess at the strictest setting**: any uncertainty is surfaced, never silently assumed. Kept ergonomic by *batching* related uncertainties into pre-analyzed multiple-choice questions, not by relaxing the bar.
- **Evidence-backed**: use Context7 for library/framework docs and WebSearch for patterns/prior art; cite every URL in the artifact.
- **DAR** (Decision Analysis & Resolution) for trade-offs that are hard to reverse — weighted criteria, scoring matrix, recorded decision.

### Worktree isolation (hard-mandatory, Stage 1.5)

Once a brainstorm is approved, **development of that approach is hard-mandatory in an isolated git worktree on a feature branch** — never on the base branch (`main`/`master`). The `worktree` skill performs the move; a `PreToolUse` hook makes it non-negotiable.

- **The 100% gate.** `plugins/cbr/hooks/enforce-worktree.py` is registered as a `PreToolUse` hook (matcher `Edit|Write|NotebookEdit`) by the plugin's `hooks/hooks.json`, referenced via `${CLAUDE_PLUGIN_ROOT}`. On a base branch it **denies** edits to feature code. The point: a markdown rule is probabilistic (the model may forget); a harness-run hook is deterministic. Because the registration ships in the plugin, **the gate is active whenever the `cbr` plugin is enabled** (disabling the plugin removes the skills and the gate together) — see `worktree/references/enforcement.md`. Exempt paths (not "feature code"): `docs/specs/*`, `.claude/*`, `*.md`, `.gitignore`, `.worktreeinclude`. For dogfooding, *this* repo's `.claude/settings.json` also registers the same script via `${CLAUDE_PROJECT_DIR}/plugins/cbr/hooks/enforce-worktree.py`, so the gate is on for contributors even without `--plugin-dir`.
- **`EnterWorktree` authorization travels in the skill, not in CLAUDE.md.** The native `EnterWorktree` tool may only be used when the user or project instructions (CLAUDE.md/memory) call for worktree use. An installed plugin runs in repos with no ClaudeBrew CLAUDE.md, so the `worktree` skill body carries its own authorization — invoking that skill *is* the instruction. `/cbr:setup` can also persist the policy into the user's CLAUDE.md/memory for the always-on case. `EnterWorktree` is the only mechanism that switches the live session's CWD into the worktree (a script cannot).
- **`worktree.baseRef: head`** so worktrees branch from local HEAD (capturing the just-committed approved spec, which may be unpushed); the default `fresh` would branch from `origin/<default>` and miss it. Applied to users by `/cbr:setup` (it cannot ship inside the plugin).
- **No opt-out.** There is no "stay on main" path for feature code; the only runtime choice the skill offers is the branch name.

### Agent-team ("teammate") mode

Team brainstorming requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and `teammateMode: in-process` — applied to users by `/cbr:setup`, and already present in this repo's dev `.claude/settings.json`. Verified lifecycle the lead drives: `TeamCreate` → spawn teammates with the `Agent` tool (`team_name` + role `name`, all in one message so they run concurrently) → coordinate/challenge via `SendMessage` → shut each down with a `shutdown_request` → `TeamDelete` once all members have terminated. Full detail in `brainstorming/references/teammate-mode.md`.

### Evaluating a skill's triggering (Windows caveats)

`evals/triggers/run_triggers.py` measures how reliably a description fires: it runs the queries in `trigger-eval.json` through `claude -p` and detects whether the skill is invoked (by the `brainstorming` substring, which also matches the namespaced `cbr:brainstorming`).

```
python evals/triggers/run_triggers.py <eval.json> <out.json> <runs_per_query> <workers>
```

Keep `workers` low (2–3) — high concurrency throttles the headless `claude -p` sessions into timeouts. Two Windows gotchas that will otherwise cost you time:

- `claude` resolves to `claude.ps1`, which Python's `subprocess` cannot launch directly; `run_triggers.py` shells through `powershell.exe` to work around it.
- The auto-mode classifier blocks the **agent** from spawning PowerShell (it reads it as bypassing the disabled PowerShell tool) and from self-granting that permission. So a trigger-eval run must be **initiated by the user** (e.g. the `!` prefix) or pre-authorized in settings. The vendored skill-creator description optimizer (`run_loop.py`/`run_eval.py`) does **not** run on Windows for the same reasons (plus `select()` on pipes) — use `run_triggers.py` instead.

---

# Engineering guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

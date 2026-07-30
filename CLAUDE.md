# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ClaudeBrew** is a harness-engineering toolkit that implements a **full software-development lifecycle (SDLC) as Claude Code skills + role agents** — each stage handing a structured artifact to the next:

```
brainstorming → (worktree) → requirement → UI/tech design → implement → review → test → security → delivery → retro
```

Two bodies of work sit side by side in the tree — know which one you're touching:

- **The reference core.** `brainstorming` (Stage 1) and `worktree` (Stage 1.5 — the isolation gate between an approved brainstorm and any implementation) set the house style every sibling is meant to imitate — read them first. See "Worktree isolation" below.
- **An imported SDLC engine (now reconciled).** The tree also carries ~40 skills, 10 role **agents** (`plugins/cbr/agents/*-agent.md`), and 16 **rules** (`plugins/cbr/rules/*.md`) that together form an orchestrated multi-agent pipeline (`full-sdlc`, `orchestrate`). This suite was imported from a sibling project and has since been adapted to ClaudeBrew's plugin layout — renamed from **"ClaudeKit"**, frontmatter fixed, hooks ported to Python, so `claude plugin validate ./plugins/cbr` now passes. A few conventions are still being unified: see "The SDLC engine", "Reconciliation status" below, and `docs/BACKLOG-REGISTRY.md`.

This is not a conventional application: there is no build system, dependency manifest, or test runner — don't hunt for `package.json` or a lint command. The "source" is the skills under `plugins/cbr/skills/`, authored in Markdown (plus small Python helpers). "Testing" a skill means evaluating how well Claude follows it, not running unit tests.

### How ClaudeBrew ships: one plugin, one marketplace

ClaudeBrew is distributed as a **single Claude Code plugin** named `cbr`, served from a **plugin marketplace** rooted in this repo. Layout:

```
ClaudeBrew/                          # repo root = marketplace catalog + dev workspace
├── .claude-plugin/marketplace.json  # the catalog: lists the cbr plugin (source ./plugins/cbr)
├── .claude/settings.json            # DEV-ONLY harness settings (dogfooding; not shipped)
├── plugins/cbr/                      # ── THE SHIPPED UNIT (copied to users' plugin cache) ──
│   ├── .claude-plugin/plugin.json    # name "cbr", displayName "ClaudeBrew", version (source of truth)
│   ├── skills/<name>/SKILL.md        # ~40 skills: brainstorming+worktree (reference), setup, + imported SDLC suite
│   ├── agents/<role>-agent.md        # 10 role subagents spawned by the orchestrator skills
│   ├── rules/*.md                    # 16 always-loaded convention files (gates, artifact paths, standards)
│   └── hooks/{hooks.json, *.py, *.js, *.sh}  # Python guards+gate, JS/bash context hooks — see "The SDLC engine"
├── evals/                            # DEV-ONLY trigger/behavioral evals + the hook unit test
└── examples/                         # sample artifacts (e.g. a brainstorm output)
```

Everything under `plugins/cbr/` is copied wholesale into each user's `~/.claude/plugins/cache` on install, so **nothing dev-only lives there** — evals, examples, and this CLAUDE.md stay at the repo root, outside the shipped unit. Installed skills are namespaced, e.g. `/cbr:brainstorming`, `/cbr:worktree`, `/cbr:orchestrate`, `/cbr:full-sdlc`, `/cbr:setup`.

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

### The SDLC engine (imported suite — how the pieces fit)

The imported half turns the flat skill list into a **two-layer, artifact-driven pipeline**. To understand it, read `orchestrate/SKILL.md`, `full-sdlc/SKILL.md`, `rules/sdlc-conventions.md`, and a couple of `agents/*.md` together — no single file shows the whole shape.

- **Layer 1 — orchestrator skills** (`full-sdlc`, `orchestrate`) run in the *main* context. Each SDLC phase is **one `Agent` tool call** that spawns an isolated role agent; the orchestrator verifies that phase's artifact, pauses at human-approval gates, and **never does the work itself**. `intelligent-routing` picks a skill/agent from a raw request; `parallel-agents` and `retro` are multi-agent patterns the orchestrator invokes.
- **Layer 2 — role agents** (`agents/*-agent.md`: ba, ui-designer, architect, developer, code-review, unit-test, integration-test, security-tester, bug-fix, orchestrator). Each has frontmatter (`tools`, `model`, `permissionMode`, `memory: project`) and a spec-driven body. Names ending in `-agent` are **load-bearing**: the `.*-agent` matcher in `hooks.json` is what binds the `SubagentStart` context-injection and `SubagentStop` quality-gate hooks to them.
- **The contract is the artifact, written into the *user's* `docs/`** (not this repo). `rules/sdlc-conventions.md` is the authority — it holds the **canonical artifact-path table** (`docs/specs/requirements/SRS-*`, `docs/specs/detail-design/TECH-*`, `docs/reviews/`, `docs/test-reports/`, …) and the **CMMI-style quality gates G1–G8** (each gate's pass criteria + who decides). Trust that file over any single skill's inline paths.
- **State lives in project-level registries** the orchestrators create in the user's repo: `docs/plans/PLAN-REGISTRY.md`, `DECISION-LEDGER.md`, `BACKLOG-REGISTRY.md`, `docs/memory/PROJECT-MEMORY.md` — plus a 4-tier memory convention (core rules → project registries → per-agent `.claude/agent-memory/` → session work-logs).
- **Skill categories** (buckets, not an exhaustive list — the 40 names rot fast): *orchestrators* (full-sdlc, orchestrate, intelligent-routing, retro…), *stage executors* (analyze-requirement, design-screen/function, implement-feature, review-code, unit/integration-test, fix-bug, create-pr…), *knowledge/reference* (architecture, clean-code, database-design, testing-patterns, ui-ux-pro-max, vulnerability-scanner…), and *infrastructure* (setup, lint-and-validate, run-tests; `context-inject` self-marked DEPRECATED).

Its **hooks** (`hooks.json`) go well beyond the committed gate. The security/gate hooks are **Python**, reading the tool payload from stdin JSON: `SubagentStop` (matcher `.*-agent`) runs `subagent-quality-gate.py`; `PreToolUse` runs `protect-files.py` (on `Edit|Write`, and on `Read` with a `read` arg — a secrets/lock-file guard), `guard-bash.py` (`Bash`), and `guard-webfetch.py` (`WebFetch`); `PreCompact` runs `compact-context-saver.py`. Context re-injection stays in JS/bash: `SubagentStart` (matcher `.*-agent`) runs `subagent-context-inject.js`; `PostCompact`/`SessionStart:compact` re-inject via `post-compact-reinject.sh`/`re-inject-context.sh`; `Stop` runs `post-edit-reminder.sh`. (The earlier `.sh` guards read a non-existent `$CLAUDE_TOOL_INPUT` and never fired — they were deleted; the dead `pixel-status-update.js` calls are gone.)

### Reconciliation status (imported suite)

The imported suite has been reconciled to ClaudeBrew's layout — `claude plugin validate ./plugins/cbr` passes with 0 errors. Resolved:

- **"ClaudeKit" fully renamed to "ClaudeBrew"** — 0 remaining references under `plugins/cbr/`.
- **Agent/rule paths fixed** to `${CLAUDE_PLUGIN_ROOT}/...`. The two `.claude/` references at `rules/sdlc-conventions.md:241,248` are intentional and correct — they describe the *user's own* `.claude/` dir (their rules/agent files), not this plugin's tree.
- **Frontmatter parses.** 33 skills/agents had an unquoted `description:` whose `TRIGGER:`/`NOT FOR:` text carried a `: ` that broke YAML; the `description` scalar is now double-quoted. Keeping it quoted is load-bearing — unquoting reintroduces the 33 parse failures.
- **Hooks ported to Python** (see the hooks paragraph above); the dead `pixel-status-update.js` calls were removed.
- **`plugin.json` bumped `0.1.0` → `0.2.0`**; stray `.coverage` cruft removed.

Remaining gaps (tracked in `docs/BACKLOG-REGISTRY.md`):

- **Two artifact-path conventions still coexist.** `brainstorming` writes `docs/specs/YYYY-MM-DD-<topic>-<stage>.md`, `clean-code` writes `docs/decisions/`, and the imported suite writes `docs/specs/requirements/SRS-<feature>.md` etc. Not yet unified.
- **Most skills lack evals.** Only `brainstorming` and `worktree` ship `evals/evals.json`; ~38 skills don't, so their trigger reliability is unverified.
- **`TRIGGER:`/`NOT FOR:` guards pending** on overlapping knowledge skills (must keep the `description` scalar double-quoted).

### Conventions inherited across the suite

ClaudeBrew's house style, set by `brainstorming` (the reference implementation). Reconciled skills should follow these; the **imported suite still diverges on a few** — artifact paths especially (see "Reconciliation status" and `docs/BACKLOG-REGISTRY.md`):

- **Plain stage names** (`brainstorming`, not `sdlc-brainstorming`); once installed they namespace to `/cbr:<stage>`.
- **Handoff artifacts** at `docs/specs/<stage>/<TYPE>-<slug>.md` (e.g. `brainstorms/BRAINSTORM-`, `worktrees/WORKTREE-`, `requirements/SRS-`, `detail-design/TECH-`; in the *user's* repo, not this one). Each stage's artifact is the contract the next stage consumes — completeness there is the entire point of the stage.
- **Hard gate + no auto-cascade**: a stage does no downstream work and does not invoke the next skill until its artifact is written and the user explicitly approves; then it **stops** so the user decides when the next stage begins. Cascading silently is a bug, not a feature.
- **Never-guess at the strictest setting**: any uncertainty is surfaced, never silently assumed. Kept ergonomic by *batching* related uncertainties into pre-analyzed multiple-choice questions, not by relaxing the bar.
- **Evidence-backed**: use Context7 for library/framework docs and WebSearch for patterns/prior art; cite every URL in the artifact.
- **DAR** (Decision Analysis & Resolution) for trade-offs that are hard to reverse — weighted criteria, scoring matrix, recorded decision.

### Worktree isolation (hard-mandatory, Stage 1.5)

Once a brainstorm is approved, the `worktree` skill mandates **development of that approach in an isolated git worktree on a feature branch** — never on the base branch (`main`/`master`). Deterministic *enforcement* of that mandate is an **opt-in** `PreToolUse` hook.

- **The gate (opt-in, deterministic).** A markdown rule is probabilistic — the model may forget; a harness-run `PreToolUse` hook is deterministic — on a base branch it **denies** edits to feature code. `enforce-worktree.py`'s exempt paths (not "feature code"): `docs/specs/*`, `.claude/*`, `*.md`, `.gitignore`, `.worktreeinclude`. See `worktree/references/enforcement.md`. **The gate is opt-in by design — this is resolved, not a gap:**
  - *Not in the shipped plugin.* `plugins/cbr/hooks/hooks.json` does **not** register `enforce-worktree.py` (the file ships, unwired). The plugin's `Edit|Write` slot runs `protect-files.py`, a **secrets/lock-file guard, not a branch gate**. So a fresh install has **no base-branch denial** until the user opts in — the accepted default.
  - *Opted in via `/cbr:setup`.* Setup registers `enforce-worktree.py` into the *user's* `.claude/settings.json` (merged by `settings_merge.py`) on `Edit|Write|NotebookEdit`. A plugin can't ship harness `settings.json`, so the gate travels through setup, not the package.
  - *This repo (dogfooding).* Contributors' `.claude/settings.json` already registers the gate via `${CLAUDE_PROJECT_DIR}/plugins/cbr/hooks/enforce-worktree.py`, so it is live here even without `--plugin-dir`.
  - *Test coverage.* `evals/test_hook.py` validates `enforce-worktree.py` against a throwaway repo on `main` plus a feature branch.
- **`EnterWorktree` authorization travels in the skill, not in CLAUDE.md.** The native `EnterWorktree` tool may only be used when the user or project instructions (CLAUDE.md/memory) call for worktree use. An installed plugin runs in repos with no ClaudeBrew CLAUDE.md, so the `worktree` skill body carries its own authorization — invoking that skill *is* the instruction. `/cbr:setup` can also persist the policy into the user's CLAUDE.md/memory for the always-on case. `EnterWorktree` is the only mechanism that switches the live session's CWD into the worktree (a script cannot).
- **`worktree.baseRef: head`** so worktrees branch from local HEAD (capturing the just-committed approved spec, which may be unpushed); the default `fresh` would branch from `origin/<default>` and miss it. Applied to users by `/cbr:setup` (it cannot ship inside the plugin).
- **Skill-level mandate, opt-in enforcement.** The `worktree` skill itself offers no "stay on main" path for feature code — the only runtime choice it surfaces is the branch name. The *deterministic* hook that would block base-branch edits is opt-in (above); without `/cbr:setup` the mandate rests on the skill instruction alone.

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

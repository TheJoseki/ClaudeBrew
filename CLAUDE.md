# CLAUDE.md

<!-- release: 0.4.0 -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ClaudeBrew** is a harness-engineering toolkit that implements a **full software-development lifecycle (SDLC) as one layer of self-sufficient, gated Claude Code skills** over a small pool of general capability agents — each stage handing a structured artifact to the next:

```
brainstorming → (worktree) → requirement → UI/tech design → implement → review → test → security → delivery → retro
```

Two bodies of work sit side by side in the tree — know which one you're touching:

- **The reference core.** `brainstorming` (Stage 1) and `worktree` (Stage 1.5 — the isolation gate between an approved brainstorm and any implementation) set the house style every sibling is meant to imitate — read them first. See "Worktree isolation" below.
- **The single-layer SDLC skills.** The tree carries 25 stage/knowledge **skills**, a **4-agent capability pool** (`plugins/cbr/agents/{researcher,developer,reviewer,tester}.md`), and ~13 **rules** (`plugins/cbr/rules/*.md`). This suite was imported from a sibling project ("ClaudeKit") as a two-layer orchestrator→role-agent engine, then **collapsed to a single layer** (the v0.3.0 pivot — see `plans/260730-2316-single-layer-sdlc-refactor/`): the orchestrators and 10 rigid role agents were removed; each stage skill is now self-sufficient, writes its artifact, applies its gate, and **stops**. Skills spawn pool agents on demand (fresh-eyes gate verdicts, `--parallel` workers) — a flat toolbox, not an orchestrated pipeline. `claude plugin validate ./plugins/cbr` passes. See "The SDLC engine" below.

This is not a conventional application: there is no build system, dependency manifest, or test runner — don't hunt for `package.json` or a lint command. The "source" is the skills under `plugins/cbr/skills/`, authored in Markdown (plus small Python helpers). "Testing" a skill means evaluating how well Claude follows it, not running unit tests.

### How ClaudeBrew ships: one plugin, one marketplace

ClaudeBrew is distributed as a **single Claude Code plugin** named `cbr`, served from a **plugin marketplace** rooted in this repo. Layout:

```
ClaudeBrew/                          # repo root = marketplace catalog + dev workspace
├── .claude-plugin/marketplace.json  # the catalog: lists the cbr plugin (source ./plugins/cbr)
├── .claude/settings.json            # DEV-ONLY harness settings (dogfooding; not shipped)
├── plugins/cbr/                      # ── THE SHIPPED UNIT (copied to users' plugin cache) ──
│   ├── .claude-plugin/plugin.json    # name "cbr", displayName "ClaudeBrew", version (source of truth)
│   ├── skills/<name>/SKILL.md        # 25 skills: brainstorming+worktree (reference), setup, + single-layer SDLC stages
│   ├── agents/<name>.md              # 4 general capability agents (researcher/developer/reviewer/tester) skills spawn on demand
│   ├── rules/*.md                    # ~13 always-loaded convention files (gates, artifact paths, standards)
│   ├── schemas/verdict-artifact.schema.json  # shape of a gate verdict (verdict-gate.py input)
│   └── hooks/{hooks.json, *.py, *.sh}  # Python guards + skill-invoked verdict-gate, bash context hooks — see "The SDLC engine"
├── evals/                            # DEV-ONLY trigger/behavioral evals + the hook unit test
└── examples/                         # sample artifacts (e.g. a brainstorm output)
```

Everything under `plugins/cbr/` is copied wholesale into each user's `~/.claude/plugins/cache` on install, so **nothing dev-only lives there** — evals, examples, and this CLAUDE.md stay at the repo root, outside the shipped unit. Installed skills are namespaced, e.g. `/cbr:brainstorming`, `/cbr:worktree`, `/cbr:implement-feature`, `/cbr:review-code`, `/cbr:setup`.

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
Validate before committing: `claude plugin validate ./plugins/cbr` (the plugin) and `claude plugin validate .` (the marketplace). **Ship** by bumping `version` in `plugins/cbr/.claude-plugin/plugin.json` (leave `version` out of the marketplace entry so there's one source of truth), updating `CHANGELOG.md`, **stamping the `<!-- release: X.Y.Z -->` anchor in `CLAUDE.md` and `README.md`** (which forces you to open and review both for the release), and pushing to GitHub; users pull it via `/plugin marketplace update` → `/plugin update`. **`evals/test_release_docs.py` enforces this** (ported from clawform's packaging tests): a version bump with no matching `## [X.Y.Z]` CHANGELOG section, or a stale `CLAUDE.md`/`README.md` anchor, fails the release-docs gate. It is a *touch-forcing* gate, not a semantic-freshness one — it makes shipping stale docs a hard failure, not a hope.

**A plugin cannot ship harness settings.** A plugin's own `settings.json` only honors `agent`/`subagentStatusLine`, so the agent-teams env var, `teammateMode`, and `worktree.baseRef` cannot live in the package — the `/cbr:setup` skill merges them into the *user's* `.claude/settings.json` post-install. This repo's own `.claude/settings.json` already carries them, for dogfooding.

### Skill anatomy (the pattern every stage follows)

```
plugins/cbr/skills/<stage>/
├── SKILL.md          # workflow spine + frontmatter (name + the triggering description)
├── references/*.md   # progressive-disclosure detail, loaded only when needed
└── evals/evals.json  # representative test prompts
```

SKILL.md stays lean (<500 lines); deep procedure lives in `references/` and is pulled in on demand (for `brainstorming`: `clarify-loop.md`, `dar-analysis.md`, `artifact-template.md`, `teammate-mode.md`). **Read `plugins/cbr/skills/brainstorming/SKILL.md` and its references first** — that is the house style to match before authoring a sibling skill.

### The SDLC engine (single layer — how the pieces fit)

The SDLC is a **flat set of self-sufficient, artifact-driven stage skills** — no orchestrator. To understand it, read `rules/sdlc-conventions.md` (the authority), a stage skill (`analyze-requirement/SKILL.md`), and a gate skill (`review-code/SKILL.md`) together.

- **Stage skills do the work in the main context.** Each stage (`analyze-requirement`, `design-screen`, `design-function`, `implement-feature`, `review-code`, `unit-test`, `integration-test`, `vulnerability-scanner`, `fix-bug`, …) reads its input artifact, does its work, writes its output artifact, applies its gate, and **stops** for the user. No skill auto-invokes the next — the user drives stage-to-stage (house style: hard gate, no auto-cascade).
- **The capability pool** (`agents/{researcher,developer,reviewer,tester}.md`) is a flat toolbox skills spawn **on demand**, not a pipeline. General personas with per-agent `model` tiering + selective `memory: project`. Two uses: (1) `--parallel` mode spawns `cbr:developer` workers under strict file-ownership; (2) **gate skills spawn a *fresh* `cbr:reviewer`/`cbr:tester`** to produce the verdict so the implementer never self-grades. Agent names are NOT matched by any hook (no `.*-agent` matcher exists anymore).
- **Gates are "verdict + user".** A gate skill spawns the fresh pool agent, which writes a **verdict artifact** (JSON, `schemas/verdict-artifact.schema.json`). The skill then runs `hooks/verdict-gate.py --gate <G> --artifact <path>` via `Bash` (schema + secret-scan + per-gate policy; **fails closed**), and `AskUserQuestion` on block. No automatic FAIL→fix loop — the user decides (e.g. re-invoke `fix-bug`).
- **The contract is the artifact, written into the *user's* `docs/`** (not this repo). `rules/sdlc-conventions.md` is the authority — it holds the **canonical artifact-path table** and the **CMMI-style quality gates G1–G8** (each gate's pass criteria + who decides; "Decided By" is now the owning skill's verdict + user). Trust that file over any single skill's inline paths. Project memory is just the `plan.md`/`phase-*.md` files — the old orchestrator registries (`PLAN-REGISTRY`, `DECISION-LEDGER`, `BACKLOG-REGISTRY`, `PROJECT-MEMORY`) were dropped with the orchestrators.
- **Work-stream grouping + lifecycle governance (v0.4.0).** Each feature's artifacts are linked from a `docs/streams/<slug>-<YYYYMMDD>/STREAM.md` manifest — two *authored* zones (artifact membership + a kanban task board) and one *derived* gate-status snapshot; **gate authority stays with the glob in `hooks/lib/sdlc_state.py`, never the manifest** (the manifest is never a second source of truth). Every per-feature artifact carries a persistent `stream:` frontmatter id. `sdlc-conventions.md` also holds the **Artifact Lifecycle** table (created/updated/consumed/closed-at) + a mandatory upkeep protocol, so no artifact is generated-and-forgotten. The reference doc-template set under `plugins/cbr/docs/_templates/` is now **shipped and git-tracked** (curated to 8 agent-consumable templates; the plugin previously referenced templates it never committed). Physical relocation of artifacts into the stream folder is a deferred Phase 2 — today the manifest links the canonical type-first paths, additively (no change to `sdlc_state.py`'s existing globs).
- **Skill categories** (buckets, not exhaustive): *stage executors* (analyze-requirement, design-screen/function, implement-feature, review-code, unit/integration-test, vulnerability-scanner, fix-bug), *knowledge/reference* (architecture [absorbs api/db design], clean-code, testing-patterns, design-system [absorbs ui-styling + ui-ux-pro-max], code-review-checklist…), and *infrastructure* (setup, lint-and-validate, run-tests, retro).

Its **hooks** (`hooks.json`) are all **general** (tool/event matchers, never a `.*-agent` matcher). Python, reading the tool payload from stdin JSON: `PreToolUse` runs `protect-files.py` (on `Edit|Write`, and on `Read` with a `read` arg — a secrets/lock-file guard), `guard-bash.py` (`Bash`), `guard-webfetch.py` (`WebFetch`); `PreCompact` runs `compact-context-saver.py` (writes the `.claude/compact-checkpoint.md` snapshot). **Lifecycle context hooks (Python): `SessionStart` (`startup|resume|clear|compact`) runs `session-init.py`, and `SubagentStart` (no matcher — every spawn) runs `subagent-context.py`.** Both reconstruct SDLC state from committed `docs/` artifacts (active feature + gate progress G1–G8, the automatic form of the `handoff` skill), inject a summary, and share `hooks/lib/sdlc_state.py`; `session-init.py` writes a `.claude/sdlc-index.json` cache that `subagent-context.py` reads (convenience only — glob-on-canonical-path stays the fail-loud authority). On `compact`, `session-init.py` reinjects the richer post-compaction context (checkpoint + SDLC state + PROJECT.md sections + an approval-gate reminder). **`SessionStart` is the injection-capable compaction event; `PostCompact` stdout is log-only (docs-verified) and never reaches the model — so the old `PostCompact`/`SessionStart:compact` scripts (`post-compact-reinject.sh`, `re-inject-context.sh`) were removed and their job folded into `session-init.py`.** This general `SubagentStart` re-couples to no agent name, so it does **not** reintroduce the removed `.*-agent` hook. `Stop` runs `post-edit-reminder.sh`. Separately, **`verdict-gate.py` is a *skill-invoked* validator, not a registered hook** — it needs no matcher and works regardless of who wrote the artifact. (The former `.*-agent` `SubagentStart` context-inject + `SubagentStop` quality-gate hooks were removed with the role agents.)

### Single-layer pivot (v0.3.0) — what changed

The imported suite was first *reconciled* (v0.2.0: renamed ClaudeKit→ClaudeBrew, fixed `${CLAUDE_PLUGIN_ROOT}` paths, ported hooks to Python, double-quoted 33 `description` scalars) and then **collapsed from two layers to one** (v0.3.0). `claude plugin validate ./plugins/cbr` passes with 0 errors. The pivot:

- **Removed** the orchestrator skills (`full-sdlc`, `orchestrate`, `intelligent-routing`, `parallel-agents`, `behavioral-modes`, deprecated `context-inject`), the **10 rigid role agents**, the `.*-agent` `SubagentStart`/`SubagentStop` hooks, three orchestration-only rules, and the 4 project registries.
- **Added** the 4-agent capability pool, `--parallel` mode on execution skills, and the skill-invoked verdict gate (`hooks/verdict-gate.py` + `schemas/verdict-artifact.schema.json`, 98% test coverage in `evals/test_verdict_gate.py`).
- **Merged** knowledge clusters: `ui-styling`+`ui-ux-pro-max`→`design-system`; `api-patterns`+`database-design`→`architecture`. `retro` runs solo; `create-pr` folded into `implement-feature`.
- **Load-bearing invariant (unchanged):** every skill/agent `description:` scalar stays **double-quoted** — its `TRIGGER:`/`NOT FOR:` text carries a `: ` that breaks YAML unquoted (would reintroduce parse failures).

Plan + ClaudeKit study: `plans/260730-2316-single-layer-sdlc-refactor/`.

### Conventions inherited across the suite

ClaudeBrew's house style, set by `brainstorming` (the reference implementation). All single-layer skills follow these:

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

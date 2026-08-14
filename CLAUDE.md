# CLAUDE.md

<!-- release: 0.13.0 -->

> **Packaging (0.8.0 re-platform):** ClaudeBrew moved from a Claude Code **plugin/marketplace** to a
> standalone **`npx claudebrew` npm installer** that provisions the payload into the user's `.claude/`.
> The payload is authored under **`claude/`** (not `plugins/cbr/`); the installer CLI lives in `bin/` +
> `scripts/lib/`; `package.json` is the version source of truth. The install/develop/ship command blocks
> below are current; some deeper architecture narrative further down still describes the plugin era and is
> being migrated — trust `plans/260804-2315-cbr-re-platform-plugin-to-npm-installer-cli/` and the code.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ClaudeBrew** is a harness-engineering toolkit that implements a **full software-development lifecycle (SDLC) as one layer of self-sufficient, gated Claude Code skills** over a small pool of general capability agents — each stage handing a structured artifact to the next:

```
brainstorming → (worktree) → requirement → UI/tech design → implement → review → test → security → delivery → retro
```

Two bodies of work sit side by side in the tree — know which one you're touching:

- **The reference core.** `brainstorming` (Stage 1) and `worktree` (Stage 1.5 — the isolation gate between an approved brainstorm and any implementation) set the house style every sibling is meant to imitate — read them first. See "Worktree isolation" below.
- **The single-layer SDLC skills.** The tree carries 17 stage/knowledge **skills**, a **5-agent capability pool** (`claude/agents/cbr-{researcher,developer,reviewer,tester,strategist}.md`), and a **one-file resident contract** (`claude/rules/agent-contract.md`) backed by on-demand references (`claude/docs/references/*.md`). This suite was imported from a sibling project ("ClaudeKit") as a two-layer orchestrator→role-agent engine, then **collapsed to a single layer** (the v0.3.0 pivot — see `plans/260730-2316-single-layer-sdlc-refactor/`): the orchestrators and 10 rigid role agents were removed; each stage skill is now self-sufficient, writes its artifact, applies its gate, and **stops**. **The R3 merge (v0.12.0) then collapsed the 10 SDLC stage-executor skills into 3** (`cbr-plan`, `cbr-implement`, `cbr-verify` — see "The SDLC engine" below), for the same reason the single-layer pivot removed the orchestrators: fewer moving pieces to invoke and keep synchronized, without weakening any gate. Skills spawn pool agents on demand (fresh-eyes gate verdicts, `--parallel` workers) — a flat toolbox, not an orchestrated pipeline. See "The SDLC engine" below.

Two things live in this repo — don't conflate them. The **installer** is a real Node program (`package.json`, `bin/`, `scripts/lib/`, `node --test scripts/*.test.mjs`) with unit + integration tests. The **payload** is skills-as-prose: the "source" is the Markdown skills under `claude/skills/cbr-*/` (plus small Python hooks), and "testing" a skill means evaluating how well Claude follows it (trigger/behavioral evals under `evals/`), not running unit tests.

### How ClaudeBrew ships: an npm installer, one payload

ClaudeBrew is distributed as a **standalone npm package** (`claudebrew`) whose `npx claudebrew install` CLI **provisions** the payload into the user's Claude Code environment — no plugin, no marketplace. Layout:

```
ClaudeBrew/                          # repo root = npm package + dev workspace
├── package.json                     # name "claudebrew", bin, files, version (single source of truth)
├── .claude/settings.json            # DEV-ONLY dogfood harness settings (tracked; not shipped)
├── bin/claudebrew.mjs               # the installer CLI entry (install|update|uninstall + flags)
├── scripts/lib/*.mjs                # installer internals: paths, token-bake, deep-merge, doctor, rules block
├── scripts/*.test.mjs               # installer unit + integration tests (node --test)
├── claude/                          # ── THE SHIPPED PAYLOAD (installed as the user's .claude/) ──
│   ├── settings.json                 # harness settings DEEP-MERGED into the user's config (never copied as a file)
│   ├── skills/cbr-<name>/SKILL.md    # 17 cbr-namespaced skills: brainstorming+worktree (reference) + 3 merged SDLC stages (cbr-plan/cbr-implement/cbr-verify) + knowledge/infra
│   ├── agents/cbr-<name>.md          # 5 capability agents (researcher/developer/reviewer/tester/strategist) skills spawn on demand
│   ├── rules/agent-contract.md       # THE resident layer — one contract, @-imported via CLAUDE.local.md
│   ├── docs/references/*.md          # on-demand references (loaded by a skill when its task needs them)
│   ├── docs/_templates/*.md          # 8 agent-consumable doc templates, seeded into the user's docs/
│   ├── schemas/verdict-artifact.schema.json  # shape of a gate verdict (verdict-gate.py input)
│   └── hooks/*.py                    # Python guards + skill-invoked verdict-gate + lifecycle context hooks
├── evals/                           # DEV-ONLY structural/trigger evals + the Python hook unit tests
└── examples/                        # sample artifacts (e.g. a brainstorm output)
```

The `files` array ships only `claude/ bin/ scripts/` + the root docs; evals, examples, plans, and the dev `.claude/` stay out of the tarball. At install the CLI copies the six payload subdirs into the target `.claude/`, **bakes** every residual `{{CBR_ROOT}}` token to an absolute path, **deep-merges** `claude/settings.json` into the user's settings (fail-closed, provenance-tracked), and writes a managed rules `@`-import block into `CLAUDE.local.md` (project) or `~/.claude/CLAUDE.md` (user). **The directory decides what is resident, not that block:** the client auto-loads `.claude/rules/**` *recursively* and independently of the `@`-imports (probe-verified), so `rules/` holds the contract and nothing else, and every on-demand reference ships under `docs/references/` — cited as `{{CBR_ROOT}}/docs/references/<name>.md` so the bake resolves it. `orchestrate.test.mjs` asserts that `rules/` stays a one-file directory, which is what actually caps the per-turn (and per-subagent-spawn) cost. Installed skills invoke as `/cbr-brainstorming`, `/cbr-worktree`, `/cbr-plan`, `/cbr-implement`, `/cbr-verify`. **Python 3 is a hard prerequisite** (every hook is Python); the doctor fails the install if none resolves.

**Users install** (no plugin, no marketplace):
```
npx claudebrew install       # provisions .claude/, merges settings, writes the CLAUDE.local.md rules block
claudebrew install --gate    # also register the opt-in base-branch worktree gate
```
Python 3 is a hard prerequisite (every hook is Python); the installer's doctor fails the install if none resolves. Project scope merges into the gitignored `settings.local.json` by default (`--shared` for the tracked `settings.json`); `--scope user` targets `~/.claude/`.

**Develop** by dogfooding the payload into this repo's own `.claude/`, re-run after edits:
```
node bin/claudebrew.mjs install --dev   # copy claude/ -> .claude/ (the same tree a real install lays down)
node --test scripts/*.test.mjs          # installer unit + integration tests
```
Validate before committing: `python evals/test_replatform_invariants.py` (structural: no plugin-isms, tokens present, Python-only hooks) and the retargeted gate suite. **Ship** by bumping `version` in `package.json` (the single source of truth — `plugin.json` is retired), updating `CHANGELOG.md`, **stamping the `<!-- release: X.Y.Z -->` anchor in `CLAUDE.md` and `README.md`** (which forces you to open and review both for the release), and publishing to npm / pushing to GitHub; users pull it via `claudebrew update`. **`evals/test_release_docs.py` enforces this**: a version bump with no matching `## [X.Y.Z]` CHANGELOG section, or a stale `CLAUDE.md`/`README.md` anchor, fails the release-docs gate. It is a *touch-forcing* gate, not a semantic-freshness one — it makes shipping stale docs a hard failure, not a hope.

**A plugin cannot ship harness settings.** A plugin's own `settings.json` only honors `agent`/`subagentStatusLine`, so the agent-teams env var, `teammateMode`, and `worktree.baseRef` cannot live in the package — the `/cbr:setup` skill merges them into the *user's* `.claude/settings.json` post-install. This repo's own `.claude/settings.json` already carries them, for dogfooding.

### Skill anatomy (the pattern every stage follows)

```
claude/skills/cbr-<stage>/
├── SKILL.md          # workflow spine + frontmatter (name + the triggering description)
├── references/*.md   # progressive-disclosure detail, loaded only when needed
└── evals/evals.json  # representative test prompts
```

SKILL.md stays lean (<500 lines); deep procedure lives in `references/` and is pulled in on demand (for `brainstorming`: `clarify-loop.md`, `moves.md`, `problem-first.md`, `dar-analysis.md`, `artifact-template.md`, `teammate-mode.md`). **Read `claude/skills/cbr-brainstorming/SKILL.md` and its references first** — that is the house style to match before authoring a sibling skill.

### The SDLC engine (single layer — how the pieces fit)

The SDLC is a **flat set of self-sufficient, artifact-driven stage skills** — no orchestrator. To understand it, read `claude/docs/references/sdlc-reference.md` (the authority), the plan skill (`cbr-plan/SKILL.md`), and the gate skill (`cbr-verify/SKILL.md`) together.

- **Three merged stage skills do the work in the main context (the R3 merge, v0.12.0 — 10 stage-executors collapsed into 3).** `cbr-plan` (absorbs the former analyze-requirement, design-screen, design-function, plan-writing) runs the Requirement → Screen → Basic-Design → Tech-Design → Plan internal phases. `cbr-implement` (absorbs the former implement-feature, fix-bug, and the test-*authoring* half of unit-test/integration-test) writes code, authors UTC.md/ITC.md, and runs the fix-loop — it holds `Write`/`Edit` and produces **no verdicts**. `cbr-verify` (absorbs the former review-code, vulnerability-scanner, and the test-*execution* half of unit-test/integration-test) runs the Review/Security/Unit/Integration gate phases — its `allowed-tools` grant has **no `Write`/`Edit`**, which is the mechanical (not prose) guarantee that self-grading is impossible: every verdict is written by a freshly spawned `cbr-reviewer`/`cbr-tester` that did not author the code under test. Each of the 3 skills reads its input artifact, does its work, writes its output artifact, applies its gate, and **stops** for the user — no skill auto-invokes the next (house style: hard gate, no auto-cascade; `--auto` mode is the sole, explicit exception, invoking the next skill via the `Skill` tool). **`cbr-plan` is also the brownfield entry-point** (absorbed from `plan-writing`): a mandatory input-contract auto-detects the source of truth to plan from (`SRS → brainstorm → research/RES-* → code`; it *asks* the user when several exist and *refuses to plan on nothing*, with a 5th case for `cbr-plan` producing its own SRS), and when no stream exists it **opens one stream-light** (no forced REQUIREMENT/DESIGN checkpoints) — so `brainstorming` opens the greenfield stream and `cbr-plan` the brownfield one.
- **The capability pool** (`agents/{researcher,developer,reviewer,tester,strategist}.md`) is a flat toolbox skills spawn **on demand**, not a pipeline. General personas with per-agent `model` tiering + selective `memory: project`. Three uses: (1) `--parallel` mode spawns `cbr:developer` workers under strict file-ownership; (2) **`cbr-verify` spawns a *fresh* `cbr:reviewer`/`cbr:tester`** to produce the verdict so `cbr-implement` never self-grades; (3) **`brainstorming` spawns a fresh `cbr:strategist`** for divergence panels + adversarial critique (inline advice, non-gate). Agent names are NOT matched by any hook (no `.*-agent` matcher exists anymore).
- **Checkpoints are "verdict + user", not a numbered gate taxonomy (v0.11.0).** A checkpoint-owning skill spawns the fresh pool agent, which writes a **verdict artifact** (JSON, `schemas/verdict-artifact.schema.json`). The skill then runs `hooks/verdict-gate.py --gate <REVIEW|SECURITY|UNIT|INTEGRATION> --artifact <path>` via `Bash` (schema + secret-scan + per-checkpoint policy; **fails closed**), and `AskUserQuestion` on block. No automatic FAIL→fix loop — the user decides (e.g. re-invoke `cbr-implement --phase fix`). Stream completion is a separate, authored fact (`STREAM.md` `status: done`) — never inferred from checkpoint state, which fixed a real bug where a stream-light stream could never close.
- **The contract is the artifact, written into the *user's* `docs/`** (not this repo). `claude/docs/references/sdlc-reference.md` is the authority — it holds the **canonical artifact-path table** and the **stage checkpoints**: six code-tracked (`REQUIREMENT`, `DESIGN`, `REVIEW`, `SECURITY`, `UNIT`, `INTEGRATION` — each checkpoint's pass criteria + who decides) plus several process-only stops (UI Design, Test Viewpoint, Design Review, Pre-Delivery Security Re-scan, Delivery) that hard-gate the same way without their own row in derived state. "Decided By" is the owning skill's verdict + user. Trust that file over any single skill's inline paths. Project memory is just the `plan.md`/`phase-*.md` files — the old orchestrator registries (`PLAN-REGISTRY`, `DECISION-LEDGER`, `BACKLOG-REGISTRY`, `PROJECT-MEMORY`) were dropped with the orchestrators.
- **Work-stream grouping + lifecycle governance (v0.4.0; canonical layout v0.5.0).** Each feature's artifacts live **inside** a `docs/streams/<slug>-<YYYYMMDD>/` folder and are linked from its `STREAM.md` manifest — two *authored* zones (artifact membership + a kanban task board) and one *derived* gate-status snapshot; **gate authority stays with the glob in `hooks/lib/sdlc_state.py`, never the manifest** (the manifest is never a second source of truth). Every per-feature artifact carries a persistent `stream:` frontmatter id. `claude/docs/references/sdlc-reference.md` also holds the **Artifact Lifecycle** table (created/updated/consumed/closed-at) + a mandatory upkeep protocol, so no artifact is generated-and-forgotten. The reference doc-template set under `claude/docs/_templates/` is now **shipped and git-tracked** (curated to 9 agent-consumable templates; the plugin previously referenced templates it never committed). **v0.5.0 made the stream folder the *single canonical* home**: the type-first `docs/{specs,reviews,plans,work-logs,…}/` scheme was retired wholesale — folder = identity, sub-folder = type, filename drops the slug (time-series keep date/round). `sdlc_state.py` resolves identity + gate state from the folder; `test_canonical_paths.py` fails any skill that reintroduces a type-first path. Being pre-1.0 with no consumers, this breaking change ships with no in-place migrator.
- **Skill categories** (buckets, not exhaustive): *stage executors* (`cbr-plan`, `cbr-implement`, `cbr-verify` — the R3-merged trio), *knowledge/reference* (architecture [absorbs api/db design], code-quality [clean-code + review checklists], testing-strategy, design-system [absorbs ui-styling + ui-ux-pro-max]…), and *infrastructure* (worktree, handoff, retro, validate-and-test, performance-profiling, browser-devtools, deployment-procedures, documentation-templates).

Its **hooks** (`hooks.json`) are all **general** (tool/event matchers, never a `.*-agent` matcher). Python, reading the tool payload from stdin JSON: `PreToolUse` runs `protect-files.py` (on `Edit|Write`, and on `Read` with a `read` arg — a secrets/lock-file guard), `guard-bash.py` (`Bash`), `guard-webfetch.py` (`WebFetch`); `PreCompact` runs `compact-context-saver.py` (writes the `.claude/compact-checkpoint.md` snapshot). **Lifecycle context hooks (Python): `SessionStart` (`startup|resume|clear|compact`) runs `session-init.py`, and `SubagentStart` (no matcher — every spawn) runs `subagent-context.py`.** Both reconstruct SDLC state from committed `docs/` artifacts (active feature + checkpoint progress, the automatic form of the `handoff` skill), inject a summary, and share `hooks/lib/sdlc_state.py`; `session-init.py` writes a `.claude/sdlc-index.json` cache that `subagent-context.py` reads (convenience only — glob-on-canonical-path stays the fail-loud authority). On `compact`, `session-init.py` reinjects the richer post-compaction context (checkpoint + SDLC state + PROJECT.md sections + an approval-gate reminder). **`SessionStart` is the injection-capable compaction event; `PostCompact` stdout is log-only (docs-verified) and never reaches the model — so the old `PostCompact`/`SessionStart:compact` scripts (`post-compact-reinject.sh`, `re-inject-context.sh`) were removed and their job folded into `session-init.py`.** This general `SubagentStart` re-couples to no agent name, so it does **not** reintroduce the removed `.*-agent` hook. `Stop` runs `post-edit-reminder.sh`. Separately, **`verdict-gate.py` is a *skill-invoked* validator, not a registered hook** — it needs no matcher and works regardless of who wrote the artifact. (The former `.*-agent` `SubagentStart` context-inject + `SubagentStop` quality-gate hooks were removed with the role agents.)

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
- **Handoff artifacts** inside the stream folder `docs/streams/<slug>-<YYYYMMDD>/<subdir>/<TYPE>.md` (e.g. `brainstorm/BRAINSTORM.md`, `requirements/SRS.md`, `design/TECH.md`, `reviews/REVIEW-<date>.md`; in the *user's* repo, not this one — canonical table in `claude/docs/references/sdlc-reference.md`). Each stage's artifact is the contract the next stage consumes — completeness there is the entire point of the stage.
- **Hard gate + no auto-cascade**: a stage does no downstream work and does not invoke the next skill until its artifact is written and the user explicitly approves; then it **stops** so the user decides when the next stage begins. Cascading silently is a bug, not a feature.
- **Never-guess at the strictest setting**: any uncertainty is surfaced, never silently assumed. Kept ergonomic by *batching* related uncertainties into pre-analyzed multiple-choice questions, not by relaxing the bar.
- **Evidence-backed**: use Context7 for library/framework docs and WebSearch for patterns/prior art; cite every URL in the artifact.
- **Trade-off analysis** for decisions that are hard to reverse — compare alternatives on what matters, record the decision and why it won.

### Worktree isolation (hard-mandatory, Stage 1.5)

Once a brainstorm is approved, the `worktree` skill mandates **development of that approach in an isolated git worktree on a feature branch** — never on the base branch (`main`/`master`). Deterministic *enforcement* of that mandate is an **opt-in** `PreToolUse` hook.

- **The gate (opt-in, deterministic).** A markdown rule is probabilistic — the model may forget; a harness-run `PreToolUse` hook is deterministic — on a base branch it **denies** edits to feature code. `enforce-worktree.py`'s exempt paths (not "feature code"): `docs/streams/*`, `.claude/*`, `*.md`, `.gitignore`, `.worktreeinclude`. See `worktree/references/enforcement.md`. **The gate is opt-in by design — this is resolved, not a gap:**
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

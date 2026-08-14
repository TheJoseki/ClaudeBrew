# Changelog

All notable changes to ClaudeBrew (installed by the `claudebrew` CLI) are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.14.0] — 2026-08-14

**Retires the pre-0.11.0 verdict-filename read-compat shim** and refreshes the README for the R3
3-skill SDLC.

### Removed
- **`LEGACY_GATE_NAME` shim** (`hooks/lib/sdlc_state.py`). Verdict lookup now keys strictly on the
  current `VERDICT-<REVIEW|SECURITY|UNIT|INTEGRATION>.json` names; the one-release compatibility read
  of old `VERDICT-G4/G5a/G6/G7.json` files (and the `(legacy)` progress-display marker) is gone. 0.11.0
  promised this for 0.12.0; it was carried an extra release because 0.12.0/0.13.0 shipped to `main` but
  not to npm, so users are only now upgrading past the rename. ⚠️ **Migration**: a stream still carrying
  only old-G-named verdict files now reads `pending` at that checkpoint — re-run the checkpoint to write
  a current-named verdict. Stream open/closed is unaffected (it keys on `STREAM.md` `status:`, never on
  verdict files). The two docs that described the shim (`sdlc-reference.md`, `verdict-artifact.schema.json`)
  are updated; the two shim unit tests are removed.

### Fixed
- **README refreshed.** The `## Use` section now lists the three merged SDLC stage skills
  (`cbr-plan`/`cbr-implement`/`cbr-verify`) — previously only `brainstorming`/`worktree` appeared, so the
  actual pipeline was invisible. Corrected a stale "DAR (Decision Analysis & Resolution) — weighted
  criteria, a scoring matrix" bullet (that apparatus was retired for plain trade-off analysis back in
  0.10.0's de-framework pass) and broadened the agent-teams note to include `cbr-implement --team`.
- **`sdlc_state.py`'s `infer_gate_progress` docstring** no longer names the retired `fix-bug` /
  `vulnerability-scanner` skills (the R3 blast-radius sweep scanned `.md`/`.json`, not `.py`) — its
  `next_action` has emitted `cbr-implement --phase fix` / `cbr-verify --phase security` since 0.12.0.

## [0.13.0] — 2026-08-14

**Wave 2 of the R3 plan — the EXPANSION-scope stretch items on top of the 0.12.0 skill merge.** Adds
adversarial plan review + validation to `cbr-plan`, a task-hydration bridge between `cbr-plan` and
`cbr-implement`, and a real multi-agent `--team` mode for `cbr-implement` — plus a correctness fix to
the shipped `cbr-brainstorming` team mode.

### Added
- **`cbr-plan red-team {slug}` and `cbr-plan validate {slug}` subcommands.** Optional, user-invoked
  reviews of a stream's `plan/PLAN.md` (+ SRS/BASIC/TECH). `red-team` scales hostile-lens reviewers by
  phase count, spawns them per a charter split (Security Adversary + Failure Mode → `cbr-reviewer`;
  Assumption Destroyer + Scope Critic → `cbr-strategist`), evidence-filters findings (`file:line` or
  auto-reject *before* merit), caps at 15, user adjudicates, then a Whole-Plan Consistency Sweep.
  `validate` runs a tiered verification pass against the live repo (skipped when a red-team already
  fact-checked), a batched interview, and propagates decisions to a `## Validation Log`. Both stop —
  no cascade to `cbr-implement`. Five new `cbr-plan/references/` files.
- **Task-hydration bridge.** `cbr-plan`'s Plan phase hydrates one live task per `PLAN.md` phase on
  write (3-Task Rule skips <3-phase plans and `--fast`); `cbr-implement` picks them up at Step 1
  (same-session `TaskList`, cross-session re-hydrate from unchecked `[ ]`, plan-file fallback if the
  Task tools error) and syncs `[x]` back at Step 4/Hand-off with a full-plan backfill sweep. New
  `cbr-plan/references/task-management.md`.
- **`cbr-implement --team N` — real agent-team execution.** N *named* `cbr-developer` teammates with
  live coordination (`SendMessage` + Task tools), optional `isolation:"worktree"`, file-ownership
  boundaries, and `shutdown_request` teardown — heavier than `--parallel`'s unnamed fire-and-collect.
  Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; stops with a clear message if unset (never
  silently degrades to `--parallel`). Optional adversarial fix-loop variant (competing root-cause
  teammates), gated sequential-after-teardown (no nested teams). New
  `cbr-implement/references/team-mode.md`; `SendMessage`/`Task*` added to `cbr-implement`'s
  `allowed-tools` to match what its body now invokes.

### Fixed
- **`cbr-brainstorming/references/teammate-mode.md` reconciled to the verified agent-team mechanism.**
  An empirical spike established that in this harness a *named* `Agent` spawn is what enrols a teammate
  (injecting `SendMessage`/Task tools) — there is no `TeamCreate`/`TeamDelete`, and `shutdown_request`
  alone is the teardown. The doc previously described a `TeamCreate`→`TeamDelete` lifecycle as
  "verified"; it is now **capability-aware** — `TeamCreate`/`TeamDelete` used only "if your harness
  exposes them," named-spawn + `shutdown_request` otherwise — so it works across harness versions
  rather than asserting tools that may be absent.

## [0.12.0] — 2026-08-13

**The R3 merge — 10 SDLC stage-executor skills collapse into 3.** `cbr-plan` (analyze-requirement +
design-screen + design-function + plan-writing), `cbr-implement` (implement-feature + fix-bug + the
test-*authoring* half of unit-test/integration-test), and `cbr-verify` (review-code +
vulnerability-scanner + the test-*execution* half of unit-test/integration-test). Total skill count
24 → 17. This was a red-teamed, validated architecture change, not a find-and-replace: an initial
2-skill draft was rejected mid-plan specifically because a merged implement+verify skill could never
mechanically deny itself `Write` during a review/security/test-execution phase — Claude Code skills
have no per-internal-phase tool scoping. The 3-skill split exists to preserve that control as a
*capability* fact, not a *prose* one: `cbr-verify`'s `allowed-tools` grant has no `Write`/`Edit`,
identical to today's `review-code`/`vulnerability-scanner` grant, so self-grading stays mechanically
impossible rather than merely discouraged. Plan: `plans/260811-2321-cbr-r3-flexible-sdlc-core-skills/`.

### Changed
- **BREAKING — `next_action` hints and slash-command names.** `sdlc_state.py`'s `GATE_SKILL` values
  become the bare tokens `plan`/`verify` (REQUIREMENT/DESIGN → `plan`; REVIEW/SECURITY/UNIT/INTEGRATION
  → `verify`; a FAIL routes to `implement`). `next_action` now carries a `--phase <hint>` suffix, e.g.
  `/cbr-verify payment-20260812 --phase security`. Old commands (`/cbr-review-code`,
  `/cbr-unit-test`, …) no longer exist.
- **`cbr-plan`'s internal phases replace 4 separate skill invocations** with one: Scope Challenge →
  Requirement (SRS) → Screen (SCREEN, FE-only, no hard stop) → Basic-Design (BASIC, cheap-checkpoint
  stop preserved) → Tech-Design (TECH, DESIGN stop) → Plan (PLAN.md). Same 4 user-facing stop count as
  before (REQUIREMENT/BASIC/DESIGN/PLAN), one skill instead of four. The SRS → BASIC §6.5 → TECH §4.3
  business-flow traceability chain — the most structurally load-bearing cross-artifact link in the
  SDLC — survives verbatim across the merge.
- **`cbr-verify`'s Mode C (browser-live MCP testing) promoted from a dead file to a first-class,
  prioritized step.** It previously lived only in an unreferenced `mode-c-browser.md` that no
  `Content Map` listed — nearly lost during this very migration's own research. It now takes priority
  over scripted Mode B for any UI feature with an available browser MCP, stated explicitly rather than
  as a footnote.
- **`cbr-implement`'s fix-loop** folds `fix-bug`'s direct-fix path and its 2-round escalation to
  `systematic-debugging.md`, invoked as `cbr-implement --phase fix`. Kept deliberately distinct from
  the project's 3-strike rule (different metric, same numbers coincidentally close).
- **Shared Mode-A/Mode-B templates promoted to `claude/docs/references/`** (`utc-template.md`,
  `itc-template.md`, `script-templates.md`, alongside the existing `parallel-mode.md`), since
  `cbr-implement` (authors) and `cbr-verify` (executes/grades) both need the same template — matching
  the existing `parallel-mode.md` precedent rather than forking two copies.
- New `claude/docs/references/severity-vocabulary.md`: the canonical Critical/Major/Minor/Info scale,
  the OWASP High→Major mapping, and the per-gate blocking table (REVIEW blocks on Critical only, plus a
  prose-only "3+ Major→FAIL" reviewer rule the validator doesn't enforce; SECURITY blocks on Critical
  **or** Major; UNIT/INTEGRATION require ≥1 passing verification entry) — cited instead of re-derived
  in each of `cbr-verify`'s four gate phases.

### Fixed
- **Several genuinely orphaned reference files, unlinked from their own skill despite claiming
  otherwise, are now actually wired up.** `design-fetch.md` (Figma/Pencil MCP context-fetch during
  frontend implementation — the gap meant `cbr-implement`'s frontend step never used the MCP tool
  sequence the SCREEN spec's own template already documented), `coding-patterns.md`, and
  `work-log-template.md` (adopted for its richer context-checkpoint and self-review mechanics, with its
  stale `DEV-BN.md` batch-only naming corrected to the canonical `DEV-[YYYYMMDD].md`). Also fixed:
  `cbr-design-function`'s TECH.md template link pointed at a thin 36-line stub instead of the 157-line
  template with the §4.3 Business Flow → Implementation Mapping section the project's own Detail Design
  gate requires; a pre-existing Step-6A–6E numbering drift in the screen design-tool reference (never
  matched any real `SKILL.md` step) renumbered to match `cbr-plan`'s own phase numbering; a dead
  `ux-intelligence.md` citation.
- Six more duplicate/orphaned template files retired after confirming zero references anywhere in the
  repo (not just the invoking skill): `srs-template.md`, `screen-spec-template.md`, two
  `test-templates.md`, `review-template.md` (also carried a stale weighted 1–5 review score model
  superseded by the PASS/FAIL rubric already authoritative elsewhere), and a design-function `template.md`
  stub. One more found and retired during the `cbr-verify` build: `self-review-checklist.md` —
  developer-side content misplaced in the reviewer's own skill, already superseded by the
  `CODING-CHECKLIST.md` self-review mechanism.
- Blast-radius sweep across ~40 surviving files (evals.json routing assertions, skill frontmatter
  `NOT FOR` clauses, pool-agent identity docs in `claude/agents/`, and the 9 `claude/docs/_templates/`
  files shipped into every user's own `docs/` root) — every reference to one of the 10 retired skill
  names now points at `cbr-plan`/`cbr-implement`/`cbr-verify`. Two new structural evals
  (`test_r3_retired_skill_refs.py`, `test_fresh_eyes_mechanism.py`) guard both the sweep and the
  no-Write mechanism itself against future regression.

### Deferred
- **The `LEGACY_GATE_NAME` shim** (`VERDICT-G4.json` etc. read-compatibility, `sdlc_state.py`) was
  slated to be removed in this release per 0.11.0's own note. It is **not** removed here — it fell
  outside this release's actual scope (the R3 skill merge) and removing it was never planned,
  red-teamed, or validated alongside this change. Tracked for a follow-up release.
- **EXPANSION-scope stretch items** from the R3 plan — `cbr-plan`'s `red-team`/`validate` subcommands
  and task-hydration + `--team` multi-agent extension for `cbr-implement` — did not ship in this
  release. They were explicitly scoped as deferrable at plan-validation time and remain a natural
  follow-up stream, not a regression.

**No migrator.** Pre-1.0, no external consumers. Verified by a two-case upgrade rehearsal: a
pristine pre-R3 install updates cleanly, all 10 retired skill directories emptied completely. ⚠️
**If you had hand-edited any of the 10 retired skill files** (`cbr-analyze-requirement`,
`cbr-design-screen`, `cbr-design-function`, `cbr-plan-writing`, `cbr-implement-feature`,
`cbr-fix-bug`, `cbr-review-code`, `cbr-unit-test`, `cbr-integration-test`,
`cbr-vulnerability-scanner`) before upgrading, `claudebrew update` correctly never clobbers that
edit — but it does delete that skill's now-unedited sibling files (`references/*.md`,
`evals/evals.json`), leaving the edited `SKILL.md` alone in its directory. Claude Code discovers
skills by directory scan, so that orphaned file **stays live and keeps triggering**, with dead
links to the files it lost — manually delete that skill's directory under `.claude/skills/`
after upgrading. This is a narrow case (requires having edited one of these 10 specific files),
and the underlying `update.mjs` question — how a retired file should behave when it breaks its
skill directory's identity, not just its own content — is real but deliberately out of scope for
this release; it deserves its own considered design pass, not a change bolted onto an
already-large release under time pressure.

## [0.11.0] — 2026-08-10

**The G1–G8 gate taxonomy is retired — stage-is-the-gate.** Six checkpoints are now code-tracked by
function name (`REQUIREMENT`, `DESIGN`, `REVIEW`, `SECURITY`, `UNIT`, `INTEGRATION`); everything else
(UI Design, Test Viewpoint, Design Review, Pre-Delivery Security Re-scan, Delivery) is a process-only
stop — still a hard gate, just not its own row in derived state. This is a state-model redesign, not a
find-and-replace: three real defects in the old model were fixed in the same pass, per
`plans/260807-1828-.../reports/r2-state-model-design.md` (the design doc approved before this shipped).

### Changed
- **BREAKING — verdict filenames and the `gate` field rename.** `VERDICT-G4.json` → `VERDICT-REVIEW.json`,
  `VERDICT-G5a.json` → `VERDICT-SECURITY.json`, `VERDICT-G6.json` → `VERDICT-UNIT.json`,
  `VERDICT-G7.json` → `VERDICT-INTEGRATION.json` (per-batch form unchanged: `VERDICT-B[n]-<NAME>.json`).
  `verdict-gate.py --gate` only accepts the four new names. **A pre-0.11.0-named verdict is still read**
  for one release via a dual-glob shim and marked `(legacy)` in the progress display — display-only; see
  the completion-predicate fix below for why it can't corrupt gate state. **The shim window closes in
  0.12.0** — re-run any checkpoint still showing `(legacy)` before then.
- **Stream completion is now authored, never inferred — fixes a real bug.** A stream closes only when
  its `STREAM.md` frontmatter is stamped `status: done` (the template already had this value; nothing
  read it before). Previously, closure required every one of `G1/G3/G4/G5a/G6/G7` to read "pass" — a
  stream-light brownfield stream, which by design never writes an SRS or TECH spec, could **never**
  satisfy that predicate and stayed "in flight" forever, however long ago the maintenance work actually
  finished. ⚠️ **Migration consequence**: a pre-existing stream that was already all-pass under the old
  predicate has no `status:` stamp yet, so it will show as in-flight once after this upgrade. Stamp
  `status: done` on it (or let the next stage skill's stop-gate do it) to silence the one-time notice.
- **SECURITY hardened**: now requires ≥1 passing `verification` entry (the audit command the scanner
  already runs), and blocks on an unresolved *Major* finding in addition to Critical — the schema has
  no separate "High" value, so the scanner's old workaround of inflating High findings to Critical
  severity is retired along with the criterion it was compensating for. REVIEW/UNIT/INTEGRATION are
  unaffected (Critical-only).
- **The deleted "re-scan after every fix" mandate is now a code-enforced staleness check.** A SECURITY
  verdict older than the stream's newest `work-logs/DEV-*.md` **or** `bug-reports/BUG-*.md` entry shows
  `STALE` in the progress display and routes back to `vulnerability-scanner` — covering a fix made via
  `fix-bug` alone, which never touches the DEV log.
- Approval remains conversational, not a derived-state field — a deliberate non-change, re-verified: a
  persisted "approved" marker would let a stale one survive a compaction or a long gap, which
  `session-init.py`'s existing re-confirm-don't-assume policy exists to prevent.
- `verdict-artifact.schema.json` documents the shape `verdict-gate.py` enforces by hand; it was never
  loaded by the validator and stays that way — wiring real JSON-Schema validation would be a new
  dependency for a ~10-line shape check.

### Fixed
- `session-init.py` needed no source edit for this rename (it carried zero gate-vocabulary tokens —
  pure passthrough of `sdlc_state.py`'s output) and neither did `design-function`'s BASIC mid-stop
  (`sdlc_state.py` only ever indexed `BASIC.md` for section-pointers, never gate-checked it) — both
  smaller blast radius than the plan estimated.
- **`status: done` had a reader but no writer.** The completion-predicate fix above shipped
  `sdlc_state.py` reading the stamp, but no skill ever wrote it — every stream would have stayed
  in-flight forever regardless of the fix. `cbr-retro` now stamps `status: done` on `STREAM.md` as a
  matter of course for a `feature`-mode run (the design doc's own stated behavior); the upkeep
  protocol in `sdlc-reference.md` documents that any stage MAY do the same at its own user-confirmed
  terminal stop, for stream-light streams that never reach `retro`. The `STREAM.md` template's
  `status:` comment also listed only `pending|in-progress|done|blocked`, omitting the `archived` and
  `abandoned` values the code already recognized as closing — corrected.

## [0.10.0] — 2026-08-08

**The rules layer went from 13 always-on files to one contract — resident cost 76,657 → 4,622 payload bytes (≈20K → ≈1.1K tokens, −94%; the installed copy is a few hundred bytes larger once the three citation paths bake absolute).** That text was loaded on every turn *and* inherited by every spawned subagent, so the saving compounds. What was cut was apparatus, not judgment: prescriptive process taxonomies (CMMI/ISTQB/PMP branding, per-round pass-rate ladders, severity/priority grids, story points and velocity, risk P×I scoring, weighted decision matrices, checklist evidence tables). What survives moved into `claude/rules/agent-contract.md` — the invariants and interfaces an agent must hold on every turn — or into three references a skill opens when its task needs them.

### Changed
- **BREAKING — the shipped rule set is replaced.** The 13 files under `claude/rules/` are gone, replaced by `agent-contract.md` (never-guess, hard-gate/no-auto-cascade, evidence-over-assertion, surgical changes, trust boundary, Rule of Two, confirm-before-irreversible) plus the SDLC map. On `claudebrew update` an old rule file you never edited is deleted; one you *did* edit is **retired** — kept on disk, dropped from the `@`-import block. ⚠️ A retired file left under `.claude/rules/` is **still loaded**: the client auto-loads that directory recursively regardless of the block. Delete it by hand to get the full saving.
- **On-demand references live outside the rules layer**, at `.claude/docs/references/` — `sdlc-reference.md` (gate table, canonical artifact paths, artifact lifecycle, the stream open-or-join law, memory tiers), `security-reference.md` (trust boundary, injection patterns, pre-Bash checklist, skill-authoring checklist), `ship-practices.md` (pre-deploy gate, expand/migrate/contract migrations, rollback, smoke tests, SemVer). A fresh-session probe confirmed the directory — not the `@`-import block — is what makes a file resident; `orchestrate.test.mjs` now asserts `rules/` holds exactly one file, so the saving cannot silently regress.
- **Trade-off analysis replaces "DAR".** The method is unchanged — compare real alternatives, record what won and why — but the label and the weighted-scoring matrix are gone.
- **`TEST_VIEWPOINT.md` is a one-page risk-first judgment prompt** instead of a fixed-threshold template. Its machine-read Section 0 line and the gate mapping are preserved verbatim.

### Removed
- **The `cbr-estimate` skill**, with its story-point/WBS/velocity apparatus.

### Fixed
- Dangling citations of the retired `sdlc-conventions.md` across `README.md`, `CLAUDE.md` and the doc templates now resolve. `evals/test_rule_crossrefs.py` guards every rule/reference citation, and treats a reference cited from inside the rules layer as a failure — so re-parking a reference where it would become resident breaks the build.

## [0.9.1] — 2026-08-07

**`update` now propagates rules-set changes.** Previously the rules `@`-import block in `CLAUDE.local.md` (or `~/.claude/CLAUDE.md`) was written only at install: an update that added or removed rule files landed on disk but the block kept loading the old set — silently. This patch is a prerequisite for the upcoming rules re-architecture.

### Fixed
- **`claudebrew update` regenerates the rules `@`-import block** from the new payload's `rules/` listing (`fullUpdate` in `orchestrate.mjs`), preserving the original rules-file provenance (`created` flag) so uninstall still cleans up correctly. If an install predates provenance tracking, update now WARNS instead of silently skipping.
- **`install --force` no longer poisons settings provenance.** A forced reinstall over a live install used to re-derive provenance against settings that already contained CBR's values; a later `uninstall` would then "restore" CBR's own values — leaving hooks registered for deleted files. The original provenance (the true pre-CBR state) is now carried through.

### Changed
- **Removed-upstream + user-edited files are now *retired***: kept on disk but moved from the managed `files` manifest to a new `retired` section — reported once (`retired: <path> …`), excluded from the regenerated rules block, and no longer re-reported on every subsequent update. A later re-ship of the same path will not silently overwrite the user's edited copy (a copy reverted to its installed content is safely re-adopted; `--force` overrides). `uninstall` leaves retired files in place (even with `--force`) and reports them. The `retired` section survives `install --force`.
- **Accepted trade-off:** with the provenance fix, no command re-merges *shipped settings* over an existing install any more (`install --force` deliberately skips the merge; `update` never merged). Refreshing shipped settings on an existing install requires `uninstall` + `install`. If a future version ships new settings/hook registrations, its release notes must say so explicitly — the file side will update, the settings side will not.
- **`install --force` now validates the existing manifest first** and refuses with an actionable error when `metadata.json` is unreadable or its `settings.provenance` is malformed — previously this could throw mid-flight and roll back the payload of a working install while leaving merged settings behind.

## [0.9.0] — 2026-08-07

**New `cbr-explore` discovery / scout skill + a three-opener stream law.** `explore` is the SDLC's research front-door: it scouts existing code and/or user-pointed prior art into a re-runnable, cited `research/RES-<topic>-R[n].md` that `plan-writing` consumes, opens or joins a work-stream, then STOPS. Validated + red-teamed before build (3 adversarial reviewers; 12 findings applied).

### Added
- **`cbr-explore` skill** (`/cbr-explore`) — codebase scout + user-pointed prior-art gather → one cited `research/RES-<topic>-R[n].md` (re-runnable / time-series). Spawns `cbr-researcher` for fetch/distil; `--parallel` fans out N angle-workers under file-ownership (round-scoped, index-prefixed paths — disjoint by construction) converged by a final researcher pass. No gate (research is pre-G1) — it STOPS for the user.
- **`evals/test_opener_law.py`** — structural gate asserting every opener resolves the stream by topic-slug and none uses `resolve_active_feature()` as the join mechanism.

### Changed
- **All three stream openers now obey one law — open-if-none / join-if-exists, resolved by topic-slug** (`rules/sdlc-conventions.md`). **`cbr-brainstorming` gains a JOIN branch (behavior change):** it no longer opens a stream unconditionally — when a stream already matches the topic slug (e.g. one `explore` opened), it JOINS strictly additively (never re-scaffolds `STREAM.md`, never overwrites `BRAINSTORM.md`); a genuinely new idea still opens a new stream. `plan-writing` is reconciled to the same law.
- **`cbr-researcher` default report path → `research/RES-[topic]-R[n].md`** (was `RES-[topic].md`); the spawning skill owns the round.
- **`sdlc-conventions.md`:** openers 2 → 3 (adds `explore`), new RES artifact-path + Artifact-Lifecycle rows; `plan-writing`'s "future explore" prose retired (the skill now ships).

### Security
- `cbr-explore` does **no autonomous web search** — web intake is limited to user-supplied URLs (`WebFetch`) + Context7 for a user-named library, and the constraint is bound into every `cbr-researcher` spawn brief. Carries the "fetched content = data, not instructions" invariant and reduces every topic / subtopic to a sanitized `[a-z0-9-]` slug before any path / shell / spawn use (path-traversal + injection guard).

## [0.8.0] — 2026-08-05

**Re-platform: Claude Code plugin → standalone `npx claudebrew` npm installer.** ClaudeBrew is no longer a marketplace plugin; a zero-runtime-dependency Node CLI provisions the skills/agents/rules/hooks into the user's `.claude/`, merges harness settings, and writes a managed rules block into project memory. One-way-door, suite-wide.

### Migration
- **The plugin install flow is retired** (`/plugin marketplace add … → /plugin install cbr@claudebrew → /cbr:setup`). Install with **`npx claudebrew install`**. `/cbr:setup` is gone — its job (settings merge, rules loading, opt-in worktree gate, Python doctor) is now the installer's.
- **Skills/agents renamed `cbr:<name>` → `cbr-<name>`** (the personal-skill namespace form). Invoke `/cbr-brainstorming`, `/cbr-worktree`, etc.
- **Python 3 is now a hard prerequisite** — every hook is Python (the one bash hook was ported). The installer fails loudly if no interpreter resolves.

### Changed
- **Payload moved `plugins/cbr/` → `claude/`** (installed as `.claude/`); `marketplace.json` + `plugin.json` dropped; **`package.json` is the single version source of truth**.
- **Two-tier path resolution:** intra-skill refs are skill-relative; residual refs (schema, hooks, cross-skill, Bash-invoked scripts, template sources) carry a `{{CBR_ROOT}}` token the installer bakes to an absolute path at install — **dissolving the `docs/_templates/` seeding gap**. Zero `${CLAUDE_PLUGIN_ROOT}` remain.
- **Settings ship in-package** (`claude/settings.json`) and are deep-merged (fail-closed, provenance-tracked), not applied by a second step. The worktree gate is opt-in (`claudebrew install --gate`, default off).
- **Rules load via a managed relative `@`-import block** in `CLAUDE.local.md` (project, gitignored per-machine) or `~/.claude/CLAUDE.md` (user scope).

### Added
- **`claudebrew install | update | uninstall`** backed by a hash manifest: `update` preserves user edits (skips + reports; `--force` overrides); `uninstall` un-merges settings, strips the rules block, and removes files, leaving a sibling `worktrees/` and user files untouched.
- **Installer test suites** (`scripts/*.test.mjs`, 19 tests) + a `test_replatform_invariants.py` structural gate; the plugin/marketplace gates were retargeted to `claude/` + `package.json`.

### Notes
- Pre-1.0: the fresh installer will churn; no 1.0 stability promise yet. Some deeper `CLAUDE.md` architecture narrative still describes the plugin era and is being migrated.

## [0.7.0] — 2026-08-04

`plan-writing` rewritten from an orphan `$ARGUMENTS` skill into a **stream-integrated stage** with a mandatory input-contract and a brownfield entry-point — the same **invariants + adaptive moves** house style as the brainstorming rewrite. This gives CBR a coherent way to plan from an **existing codebase** (maintenance), not only from a spec chain.

### Changed
- **`plan-writing/SKILL.md` rewritten** around 7 invariants + a move toolbox (no `$ARGUMENTS`, no fixed script). The load-bearing new part is a **mandatory Step-1 input-contract**: it detects the source of truth by priority `requirements/SRS.md → brainstorm/BRAINSTORM.md → research/RES-*.md → code`, **asks the user which to plan from when several exist** (user-selectable, never auto-pick), and **refuses to plan on nothing** (points at the scout/`researcher`) rather than fabricating scope. Greenfield is preserved — a present SRS is the top-priority input, so the brainstorm→SRS→plan flow is unchanged. Frontmatter `allowed-tools` expanded to `Read, Grep, Glob, Write, Edit, AskUserQuestion`; `description` stays double-quoted with `TRIGGER:`/`NOT FOR:`. Deep detail pushed to `references/input-contract.md` + `references/plan-structure.md` (SKILL.md < 300 lines).
- **`plan-writing` is a second stream opener.** When maintenance work starts on a repo with **no** stream, it **opens one stream-light**: creates the stream folder, scaffolds `STREAM.md`, marks `lane: brownfield`, and writes `plan/PLAN.md` **without** an SRS/design or forced G1–G3. Gate authority is unchanged — a stream-light stream's design gates read `pending` (benign), which was **proven against `hooks/lib/sdlc_state.py` before the rewrite** (missing `SRS.md`/`TECH.md` = `pending`, not error; the `lane:` marker is inert to `_stream_archived`/`resolve_active_feature`). No hook change.
- **Reconciled the "sole opener" prose** across the authority layer now that there are two openers: `sdlc-conventions.md` (new *Stream openers & lanes* subsection + Work-Stream/lifecycle rows), the `STREAM.md` template intro, `brainstorming/SKILL.md`'s stream-scaffold step, and `CLAUDE.md`'s SDLC-engine stage list — all now say `brainstorming` (greenfield) **or** `plan-writing` (brownfield stream-light).

### Added
- **`lane:` frontmatter marker** in `docs/_templates/STREAM.md` — `greenfield` (default, inherited unchanged by `brainstorming`) or `brownfield` (stream-light). Descriptive metadata only; not read by any hook.
- **Rewrote `plan-writing/evals/evals.json`** to exercise the input-contract + stream-light: greenfield-no-regression (SRS consumed first), brownfield code-only (plan from code + open stream-light), research-fed (reuse `RES-*`), refuse-on-empty (no fabricated scope), multi-SoT user-selectable (asks which), plus the retained end-to-end-delivery boundary negative.

### Notes
- Forward-compatible with the greenlit **`explore`/scout skill** (next stream): the input-contract already lists `research/RES-*.md` as a source, so a dedicated scout front-door drops in without a further `plan-writing` change.

## [0.6.0] — 2026-08-04

Brainstorming (SDLC Stage 1) rewritten from a rigid 9-phase machine into **invariants + an adaptive toolbox of moves**, so it brainstorms like a person. Fluid process, **unchanged output-contract** — the stream artifact write is untouched.

### Changed
- **`brainstorming/SKILL.md` restructured** around 7 invariants + a move toolbox the model selects by judgment (no fixed phase order; backtracking allowed). Adds the missing **divergent** motion (generate widely, judge later) and **adaptive depth** (rigor dialed to reversibility; a sub-threshold question gets a recommendation with no stream opened). The artifact + `stream:` id + `STREAM.md` write, the hard gate (no build / no cascade before approval), and never-guess are all preserved. Adds an explicit scope + untrusted-content (prompt-injection) note for the research move.
- Reworked references: `clarify-loop.md` (clarify is a move, not a sequence-lock), `dar-analysis.md` (fires only for one-way-doors), `artifact-template.md` (adds the required `stream:` frontmatter; captures the divergent option range + what-would-change-my-mind), `teammate-mode.md` (lenses spawn from `cbr:strategist`).

### Added
- **`problem-first.md`** move — invert a proposed solution back to its unstated problem (≥3 problem framings before solution framings); the counter to solution-jumping.
- **`moves.md`** — the diverge / steelman-then-attack / converge craft, plus the convergence test.
- **`strategist` capability agent** (pool 4→5; `model: sonnet`, non-gate) — CTO-level divergence + adversarial critique; spawned inline by `brainstorming` (returns findings as its message, writes no artifact) and usable as a team lens.

## [0.5.0] — 2026-08-03

Canonical stream-first artifact layout. **Breaking layout change** (minor bump, pre-1.0).

### Changed
- **`docs/streams/<slug>-<YYYYMMDD>/` is now the single canonical home for every per-feature SDLC artifact**, retiring the type-first `docs/{specs,reviews,plans,work-logs,security,test-reports,test-cases,bug-reports,retros,handoffs}/` scheme. Identity moved from the filename into the **folder**: sub-folder = type, filename drops the slug (`docs/specs/detail-design/TECH-payment.md` → `docs/streams/payment-20260801/design/TECH.md`); time-series artifacts keep their date/round (`REVIEW-<date>.md`, `UTR-R<n>.md`).
- **`hooks/lib/sdlc_state.py` rewritten folder-based** — active feature and gate progress (G1–G8) are *derived* from the stream folder (in-flight, gate not all-pass, not archived), not from a filename or a `status:` flag. Fixed a slug prefix-collision in stream resolution (`payment-*` no longer matches `payment-export-*`).
- **Re-pathed the whole suite to the canonical layout**: 17 skills + 2 capability agents (writes use `docs/streams/[feature]-[YYYYMMDD]/…`, reads glob `docs/streams/[feature]-*/…`), the lifecycle/context hooks (`session-init`, `subagent-context`, `compact-context-saver`), the `enforce-worktree` exempt list (`docs/specs/*` → `docs/streams/*`, now covering non-md stream assets), and the `STREAM.md` manifest template (stream-relative sub-paths).
- `sdlc-conventions.md` artifact-path table + Artifact-Lifecycle table rewritten stream-first; every retired prefix maps to a canonical destination. Project-wide ADRs/risks stay at `docs/` root.

### Added
- **Canonical-paths gate** (`evals/test_canonical_paths.py`) — fails any skill/agent that reintroduces a retired type-first `docs/…/` path. Makes the layout stick the same way the English-only and release-docs gates do.

### Notes
- Pre-1.0 with no consumer projects, so this breaking change ships **with no in-place migrator** — there is no legacy artifact data to relocate. A migrator can be added later if a real consumer with type-first artifacts appears.

## [0.4.1] — 2026-08-03

### Changed
- **Language unified to English** across shipped skill prose — stripped Japanese SDLC terms (`BD書`, `DD書`, `基本設計書`, `背景・目的`, `業務フロー`, …) from `srs-template`, `basic-design-template`, `tech-spec-template`, and `sdlc-conventions.md`; translated the Chinese icon-fallback rule and Bauhaus gloss in two `design-system/data` CSVs.

### Removed
- Two dead, unreferenced non-English design-system data files (`design.csv`, `draft.csv`, ~216 KB) — not in the live corpus (`ux-intelligence.md`), and `draft.csv` self-declared "not read by the CLI".

### Added
- **English-only gate** (`evals/test_english_docs.py`, ported from clawform's `english-docs` test) — fails if CJK (Han/Hiragana/Katakana) reappears in any shipped `plugins/cbr/**/*.md` (skill prose, references, rules, templates; data CSVs intentionally excluded). Makes the EN unification stick.

## [0.4.0] — 2026-08-03

Doc-template curation + work-stream information architecture (Phase 1), folding in the previously-unreleased lifecycle context hooks.

### Added
- **Work-stream information architecture (Phase 1, additive)** — a per-stream manifest `docs/streams/[slug]-[YYYYMMDD]/STREAM.md` (template in `docs/_templates/STREAM.md`) with two *authored* zones (artifact membership + task board) and one *derived* gate-status zone regenerated by `handoff`/`session-init` (gate authority stays with `hooks/lib/sdlc_state.py`; the manifest is never a second source of truth). Every per-feature artifact carries a persistent `stream:` frontmatter id. `sdlc-conventions.md` gains the manifest path, an **Artifact Lifecycle** governance table (created/updated/consumed/closed-at), and a mandatory Work-Stream Upkeep protocol. New `sdlc_state.find_stream_manifest()` + a `session-init` "Stream board:" line. Additive: existing type-first artifact paths are unchanged and `sdlc_state.py`'s existing globs untouched (physical relocation deferred to a future Phase 2).
- **Curated agent-consumable doc-template set**, now git-tracked in `docs/_templates/` — the plugin previously referenced templates it never committed (ship-gap closed). Standardized `[FIELD — e.g. value]` placeholder syntax + single-layer provenance headers across the set.
- **Hook test coverage raised to 96%** across 7 Python suites (added `evals/test_compact_saver.py` for the previously-untested PreCompact hook; subprocess-coverage measurement config in `.coveragerc`).
- **Release-docs gate** (`evals/test_release_docs.py`, ported from clawform's packaging tests) — fails a version bump that leaves `CHANGELOG.md` without a `## [version]` section or `CLAUDE.md`/`README.md` with a stale `<!-- release: -->` anchor. A touch-forcing gate that stops the recurring "docs never updated on release" drift.
- **Session + subagent lifecycle context hooks** — two general hooks giving the single-layer suite ClaudeKit-parity lifecycle behavior with no orchestrator and no `.*-agent` matcher:
  - `session-init.py` (`SessionStart: startup|resume|clear`) reconstructs a gate-aware SDLC summary from committed `docs/` artifacts (the automatic form of `/cbr:handoff`), injects it as plain stdout, and builds a `.claude/sdlc-index.json` cache.
  - `subagent-context.py` (`SubagentStart`, no matcher — fires for every spawn) injects the active feature + gate + verdict path/schema + section pointers to pool agents, reading the cache with a glob fallback (cache is convenience; glob-on-canonical-path stays authority).
  - Shared `hooks/lib/sdlc_state.py` (state reconstruction). **100% test coverage** (`evals/test_sdlc_state.py`, `evals/test_lifecycle_hooks.py`; 39 cases). P1 firing empirically validated in a `--plugin-dir` session.
- Cross-session memory now **self-reconstructs from `docs/`** — no separate durable state file; the cache is an ephemeral per-session convenience.

### Changed
- Corrected the skill count in `CLAUDE.md` (~29 → 25) after the P4 knowledge merges.
- **Curated `docs/_templates/` 16 → 8**: rebuilt `TEST_VIEWPOINT` (656→73, fill-in skeleton exposing the G3c Section 0 + coverage-threshold field), slimmed `CODING_CONVENTION` (1136→119 + per-stack `coding-convention-snippets/`), neutralized `CODING_RULES` (391→270, all rule IDs kept), DRY'd `ARCHITECTURE`/`API_DESIGN` (shared API contract now lives in ARCHITECTURE; API_DESIGN is a per-endpoint catalog).

### Removed
- **8 orphan doc templates** — the 4 dropped orchestrator registries (`PLAN-REGISTRY`, `DECISION-LEDGER`, `BACKLOG-REGISTRY`, `PROJECT-MEMORY`) plus `AGENT-MEMORY`, `IMPLEMENTATION_PLAN`, `QA-ISSUE-TAXONOMY`, `WALKTHROUGH` (zero consumers in the single-layer suite; QA severity/categories already canonical in `rules/qa-defect-lifecycle.md`).

### Fixed
- **Post-compaction context reinjection now actually reaches the model.** The rich reinject was wired to `PostCompact`, whose stdout is **log-only** (docs-verified) — so it never reached Claude. Compaction reinjection is folded into `session-init.py` on the injection-capable `SessionStart` (`…|compact`) path: PreCompact checkpoint + SDLC gate-state + PROJECT.md sections + an AskUserQuestion approval-gate reminder (the ClaudeKit mitigation). Removed the dead `post-compact-reinject.sh` and the now-redundant `re-inject-context.sh` (which also still read the removed `DECISION-LEDGER.md`). One `SessionStart` hook now handles new sessions and compaction alike.

## [0.3.0] — 2026-07-31

Single-layer pivot: collapsed the imported two-layer orchestrator→role-agent engine into one layer of self-sufficient, gated stage skills over a small pool of general capability agents. Refactor plan + ClaudeKit study under `plans/260730-2316-single-layer-sdlc-refactor/`.

### Removed
- **Orchestrators + meta-skills** — `full-sdlc`, `orchestrate`, `parallel-agents`, `behavioral-modes`, `intelligent-routing`, and the deprecated `context-inject`. They forced entry through an orchestrator and over-cascaded; the house style is hard-gate + no auto-cascade.
- **The 10 rigid SDLC role agents** (`ba-agent`, `architect-agent`, …, `orchestrator-agent`) and the `.*-agent` `SubagentStart`/`SubagentStop` hooks that bound to them (`subagent-context-inject.js`, `subagent-quality-gate.py`). Six general hook-guards remain.
- **Orchestration-only rules** (`agent-comms-protocol`, `model-profiles`, `agent-best-practices`) and the orchestrator-maintained registries; `plan.md`/`phase-*.md` are the project memory.

### Added
- **Capability-agent pool** — a flat toolbox skills spawn on demand: `researcher`, `developer`, `reviewer`, `tester` (general personas with per-agent `model` tiering + selective `memory: project`). No orchestrator, no role-pipeline.
- **`--parallel` mode** on execution skills — spawns `cbr:developer` workers under strict file-ownership.
- **Verdict gate (`hooks/verdict-gate.py` + `schemas/verdict-artifact.schema.json`)** — gate skills spawn a fresh `cbr:reviewer`/`cbr:tester` for a no-self-grade verdict, then run the validator (schema + secret-scan + per-gate policy; fail-closed) with `AskUserQuestion` on block. Skill-invoked, no matcher. 98% test coverage.

### Changed
- **Merged knowledge clusters** — UI (`ui-styling` + `ui-ux-pro-max` → `design-system`) and technical-design (`api-patterns` + `database-design` → `architecture`), each one lean SKILL.md + references. `retro` reworked to run solo. `create-pr` folded into `implement-feature`.
- **Further knowledge consolidation** — `lint-and-validate` + `run-tests` → `validate-and-test`; `testing-patterns` + `tdd-workflow` → `testing-strategy`; `clean-code` + `code-review-checklist` → `code-quality`; `systematic-debugging` folded into `fix-bug/references/`. Net skills: 40 → 25.

## [0.2.0] — 2026-07-30

Reconcile release: made the advertised "hard gates" real, ported hooks to Python, and made the imported SDLC suite executable. Reconcile audit + plan under `plans/`.

### Fixed
- **Security guards were no-ops.** `protect-files`, `guard-bash`, `guard-webfetch` (PreToolUse) read a non-existent `$CLAUDE_TOOL_INPUT` env var and never fired. Ported to Python reading stdin JSON so they actually block (secrets incl. case-insensitive + AWS creds, dangerous shell patterns, URL shorteners).
- **33 frontmatter parse failures.** Skills/agents had unquoted `description` scalars containing `: ` (from the `TRIGGER:`/`NOT FOR:` convention) → YAML failed to parse → they loaded with empty metadata (role agents lost `tools`/`model`/`permissionMode`). Quoted the scalars; `claude plugin validate` now passes.
- **Imported orchestration not executable.** Repointed dead `orchestrator-agent` phase-4–8 reads, removed the dead `context7-prefetch` reference, gave `retro` its `Agent`/`Write`/`Edit` tools, added `security-tester-agent` to routing rosters, corrected `.claude/` plugin paths to `${CLAUDE_PLUGIN_ROOT}`.

### Changed
- **Hooks ported bash→Python** (guards, SubagentStop quality gate, PreCompact saver) — drop the `bash`/`jq` dependency that failed on stock Windows/macOS. Removed 4 dead `pixel-status-update.js` calls.
- **Worktree gate is now OPT-IN** via `/cbr:setup` (registers `enforce-worktree.py` into the user's `settings.json`) instead of always-on — a plugin cannot ship harness settings, and always-on would hard-deny edits in every repo. Default = no gate.
- Dropped the deprecated manual `context-inject` mandate (a SubagentStart hook auto-injects). Renamed remaining "ClaudeKit" → "ClaudeBrew"; removed shipped `.coverage` cruft.

### Consistency
- Unified artifact-path to `docs/specs/<stage>/<TYPE>-<slug>.md` (brainstorms/worktrees/decisions folded into the authority table). Authored `evals/evals.json` for all 40 skills (was 2). Added quoted `TRIGGER:`/`NOT FOR:` guards to overlapping knowledge skills.

## [0.1.0] — 2026-05-26

First packaged release. ClaudeBrew is now a distributable Claude Code plugin (`cbr`) served from a marketplace in this repo, installable via `/plugin marketplace add` → `/plugin install`.

### Added
- **Plugin + marketplace packaging**: `.claude-plugin/marketplace.json` (catalog `claudebrew`) and `plugins/cbr/.claude-plugin/plugin.json` (plugin `cbr`).
- **`setup` skill** (`/cbr:setup`) — applies the harness-level settings a plugin cannot bundle (agent-teams env var, `teammateMode`, `worktree.baseRef`).
- `brainstorming` (Stage 1) and `worktree` (Stage 1.5) skills, now shipped inside the plugin and namespaced as `/cbr:brainstorming` and `/cbr:worktree`.

### Changed
- The worktree gate (`enforce-worktree.py`) is now registered by the plugin's `hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}`, so it is active whenever the `cbr` plugin is enabled (previously a standalone `.claude/settings.json` registration).
- Dev-only tooling (trigger/behavioral evals, the hook unit test) moved to `evals/`; sample artifacts moved to `examples/` — both outside the shipped plugin.

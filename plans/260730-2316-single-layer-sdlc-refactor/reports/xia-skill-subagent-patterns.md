# ClaudeKit-engineer: Skill anatomy + subagent patterns

Source: `C:/Works/Tool/ClaudeKit.CC/claudekit-engineer/claude/`. Read-only research, no source edits.

## 1. Skill anatomy — the conventions

**Frontmatter** (`claude/schemas/skill-schema.json`): required `name` (kebab, often `ck:`-prefixed), `description` (≤512 chars, "pushy"/trigger-heavy), `when_to_use` (≤1024 chars, extra invocation context — a *second* trigger field, not just decoration), `user-invocable: true` (const — shipped skills must stay user-invocable, no hidden skills). Optional: `argument-hint`, `arguments`, `license`, `allowed-tools` (string|array, only used by `review-pr` for a narrow `glab`/`git` Bash allowlist — most skills omit it = full tool access), `model`, `effort` (low/medium/high/xhigh/max), `context`, `agent` (skill-level subagent override), `category` (closed enum incl. dev-tools/utilities/security/etc.), `keywords` (≤15), `requires`/`related` (skill-name deps, informational), `maturity` (experimental/beta/stable), `metadata.{author,version,attribution,tags}`. In practice, shipped skills use a small subset: `name`, `description`, `user-invocable`, `when_to_use`, `category`, `keywords`, `argument-hint`, `metadata.{author,version}`.

**Size discipline (aspirational, not always honored):** skill-creator states SKILL.md <300 lines, each `references/*.md` <300 lines, description <200 chars — but real skills exceed this: `cook/SKILL.md` ≈238 lines (ok), `ck-plan/SKILL.md` ≈541 lines (**violates its own stated 300-line rule**). Lesson for ClaudeBrew: don't trust the source's own size guidance as proof of compliance — audit line counts directly (ClaudeBrew's plan already sets a stricter <500-line criterion; keep it, verify it at Phase 3, don't assume ClaudeKit is a clean exemplar).

**Structure:** `SKILL.md` (required) + optional `scripts/` (deterministic code, no line limit, executed without loading into context — Python/Node preferred, "avoid Bash"), `references/` (progressive disclosure, loaded on demand, grep-discoverable), `agents/` (eval-only templates: grader/comparator/analyzer, distinct from `claude/agents/`), `assets/` (output templates, never loaded into context).

**Recurring authored patterns inside SKILL.md bodies** (not in the schema, but consistent house style across `cook`, `fix`, `ck-plan`):
- **`<HARD-GATE-*>` pseudo-tag blocks** — named, hard-coded non-negotiable rules (e.g. `<HARD-GATE>`, `<HARD-GATE-SCOUT-FIRST>`, `<HARD-GATE-EXACT-REQUIREMENTS>`, `<HARD-GATE-NO-SIDE-EFFECTS>`), each stating the rule, why, and an explicit "User override:" escape hatch. This is how ClaudeKit encodes ClaudeBrew's own "hard gate" house style — via inline tagged blocks in prose, not a separate rules file per skill.
- **"Anti-Rationalization" tables** — Thought vs Reality, pre-empting the model's own excuses to skip a gate ("This is too simple to plan" → "Simple tasks have hidden complexity").
- **Mermaid flowchart marked authoritative** — "This diagram is the authoritative workflow... If prose conflicts with this flow, follow the diagram." Puts the actual control-flow contract in a diagram, prose is just elaboration.
- **"Required Subagents" / "Skill Activation Matrix" tables** — `Phase | Subagent | Requirement (MUST/Optional)`. This is the concrete, auditable mechanism for delegation decisions (see §3).
- **"Workflow Position" footer** on every skill — `Typically follows:` / `Typically precedes:` / `Related:` — cheap, per-skill cross-routing metadata in prose, separate from any central routing rule file.

## 2. Subagent definitions — the 13 agents

All at `claude/agents/*.md`. Table (tools abbreviated; all 13 also get `TaskCreate/TaskGet/TaskUpdate/TaskList/SendMessage` for team-mode):

| Agent | Model | Memory | Extra tools | Purpose |
|---|---|---|---|---|
| `brainstormer` | (inherit) | — | Glob/Grep/Read/Bash/WebFetch/WebSearch | Evaluate architecture options, debate trade-offs pre-implementation |
| `planner` | opus | project | +Edit/Write/Task(Explore)/Task(researcher) | Research → comprehensive implementation plan; can itself spawn researchers |
| `researcher` | haiku | user | Glob/Grep/Read/Bash/WebFetch/WebSearch | Multi-source research reports |
| `fullstack-developer` | sonnet | — | +Edit/Write/Task(Explore) | Execute one phase from a parallel plan, strict file-ownership |
| `code-reviewer` | (inherit) | project | Glob/Grep/Read/Bash/WebFetch/WebSearch (no Edit) | Adversarial production-readiness review, scout-based edge cases |
| `code-simplifier` | opus | — | +Edit/Write/Task(Explore) | Post-implementation simplify pass, preserve behavior |
| `debugger` | sonnet | project | +Edit/Write/Task(Explore) | Root-cause investigation, log/perf analysis |
| `tester` | haiku | project | +Edit/Write/Task(Explore) | Run/validate test suites, coverage |
| `ui-ux-designer` | inherit | — | +Edit/Write/Task(Explore)/Task(researcher) | Design + implement UI |
| `docs-manager` | haiku | — | +Edit/Write/Task(Explore) | Keep `./docs` in sync with code changes |
| `git-manager` | haiku | — | Glob/Grep/Read/Bash only (no Edit) | Commit/push/MR, isolates verbose git output |
| `journal-writer` | haiku | — | +Edit/Write (no Bash WebFetch) | Write journal entries, incl. honest failure/incident logs |
| `project-manager` | haiku | — | LS/BashOutput/KillBash/ListMcpResourcesTool/ReadMcpResourceTool (no Bash!) | Cross-plan progress sync, no direct shell execution |

These are **capability/role agents by persona**, invoked as `Task(subagent_type="<name>", prompt="...", description="...")` — the `subagent_type` string is literally the agent file's `name:` frontmatter. Notably: no `permissionMode` field exists on any of the 13 (contradicts ClaudeBrew's CLAUDE.md description of its own imported agents having `permissionMode` — ClaudeKit's agents gate access via `tools:` allowlist only). Also notable: `scout` is **not** one of the 13 named agents — the `scout` skill spawns the harness built-in `Explore` subagent type directly (or external Gemini/OpenCode CLI), never a custom "scout" persona file.

**Cost/model tiering is deliberate**: opus for reasoning-heavy/creative roles (planner, code-simplifier), sonnet for mid-weight execution (fullstack-developer, debugger), haiku for high-volume/mechanical/isolate-output roles (docs-manager, git-manager, journal-writer, project-manager, researcher, tester), `inherit` for roles that should match session model context (ui-ux-designer). Memory (`memory: project|user`) is granted selectively — only to roles that benefit from cross-session learning of recurring patterns (planner, code-reviewer, debugger, tester get `project`; researcher gets `user`) — one-shot executors (git-manager, journal-writer, docs-manager, fullstack-developer, project-manager) get none.

## 3. Subagent-vs-inline decision — explicit + inferred criteria

No single rule file states this outright; `claude/rules/orchestration-protocol.md` gives generic delegation hygiene (Task tool prompt must include task/files-to-read/files-may-modify/acceptance-criteria/constraints/paths; "Use parallel subagents only when file ownership is clear and integration points are known"; status protocol DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT). The actual **decision logic is inferred from which skills delegate and which don't**:

**Spawn a subagent when:**
1. **Context isolation from verbose/noisy output** — `git/SKILL.md:30`: "Execute git workflows via `git-manager` subagent to isolate verbose output." The persona doesn't matter here as much as keeping the main thread's context clean.
2. **Independent/adversarial review that must not be self-graded** — `code-reviewer.md`'s "Review Posture": "Assume the implementation may have been written by another AI coding agent unless proven otherwise... Do not rubber-stamp." `cook/SKILL.md:219-223` makes this an enforced invariant: "DO NOT implement testing, review, or finalization yourself - DELEGATE... If workflow ends with 0 Task tool calls, it is INCOMPLETE." The point isn't capability (the main thread could review its own diff) — it's avoiding the implementer grading its own work.
3. **Parallelizable, independent-scope work** — `scout` splits directories across parallel `Explore` agents; `fix --parallel` and `cook --parallel` spawn multiple `fullstack-developer` agents per independent phase/issue with strict file-ownership; `ck-plan --hard/--deep/--parallel/--two` spawns 2-3 `researcher`s on different angles. Ties directly to orchestration-protocol.md's file-ownership-clarity rule.
4. **Enforced quality gates, table-annotated as MUST** — the "Required Subagents" table pattern (§1) is the actual authoring mechanism: a table column literally says MUST vs Optional per phase, making delegation a checkable fact (a Task() call either happened or didn't) rather than a fuzzy prose suggestion.

**Stay inline when:**
5. **Single continuous flow, no parallel branches, isolation buys nothing** — `review-pr/SKILL.md` does its *entire* review (read MR, diff, standards/duplicate/strategic gates, findings) directly in the invoking context via Bash/Read/Grep — zero `Task()` calls for the review itself. It only invokes *other skills* (`ck:fix --auto`, `ck:git cp`) for the fix-loop, not raw subagents. Rationale: the skill's whole context already *is* the reviewer persona; there's no second voice needed and no parallelizable sub-piece.
6. **Below a coordination-overhead threshold** — several skills explicitly gate subagent/Task infra by size: scout skips `TaskList`/`TaskCreate` when "Agent count ≤ 2 (overhead exceeds benefit)"; `fix` skips Task Orchestration for Quick workflow ("<3 steps, overhead exceeds benefit"); `ck-plan`'s "3-Task Rule": "<3 phases → skip task creation." Same principle applied to subagent spawn decisions generally: don't pay coordination tax for trivial work.
7. **Extreme case — the skill IS just a named trigger for one subagent** — `journal/SKILL.md` is 26 lines total: "Use the `journal-writer` subagent to explore the memories and recent code changes, and write some journal entries." Nearly 100% of the actual work happens in the subagent; the skill exists only to give it a name/trigger/entry point.

**Heuristic distilled:** delegate when you need (a) noise/context isolation, (b) a genuinely separate persona for an adversarial/QA role, or (c) real parallelism across clear-ownership scopes — and encode that as a checkable table (MUST/Optional), not prose. Stay inline for single-threaded, low-noise, non-parallel work where the invoking skill's own context already is the right persona, and skip the whole Task apparatus below a size threshold.

## 4. Apply to ClaudeBrew plan

Plan already read: `plans/260730-2316-single-layer-sdlc-refactor/plan.md`. Key existing constraint (Decision 2, plan.md:46): ClaudeBrew ships **no agent files** — `--parallel` spawns harness `general-purpose` subagents with file-ownership boundaries, cook-modeled mechanism only, not cook's cascade.

1. **(P1)** Adopt the "Required Subagents" table pattern (`Phase | Subagent-role | Requirement: MUST/Optional`) inside each execution skill (`implement-feature`, `unit-test`, `integration-test`, `review-code` if kept as executor) instead of prose delegation language — makes the plan's Decision-1 verdict-writing step checkable the same way cook makes delegation checkable ("0 Task calls = incomplete").
2. **(P1/P2)** Since no named agent files ship, bake the *persona* (review posture, behavioral checklist, output format) directly into the `Task(subagent_type="general-purpose", prompt="...")` string, mirroring `cook/references/subagent-patterns.md`'s inline "Adversarial Validation"/"Domain-Risk Review" prompt templates. Keep one `references/subagent-prompts.md` per execution skill (or one shared under `_shared/`) cataloguing these, so the persona isn't rewritten ad hoc each invocation.
3. **(P2, flag as real cost)** Per-role model tiering (opus for planning, haiku for git/docs/journal-style mechanical work) is only available via a named agent file's `model:` frontmatter — `general-purpose` Task() spawns inherit the parent's model. ClaudeBrew's "no agent files" decision means it loses this cost lever entirely; every parallel subagent runs at whatever model the invoking skill/session is on. Recommend the plan state this trade-off explicitly (it's implied by Decision 2 but not called out) rather than silently losing it.
4. **(P1)** For gate-owning executor skills, follow criterion #2 above: even though Decision 1 already has the executor write its own verdict + stop (no auto-loop), still spawn a `general-purpose` subagent for the verdict-writing pass itself, carrying `code-reviewer.md`'s "Review Posture" language verbatim ("assume this may have been AI-written, don't rubber-stamp") — gets the fresh-eyes benefit without needing a named agent file, since the persona lives in the prompt text.
5. **(P2)** For `implement-feature --parallel`, lift `fullstack-developer.md`'s "File Ownership Rules" clause verbatim into the Task() prompt template: "NEVER modify files not listed in phase's File Ownership section... If file conflict detected, STOP and report immediately." ClaudeBrew's plan currently only gestures at "file-ownership boundaries" (plan.md:46) — this is the concrete, already-battle-tested wording to reuse.
6. **(P1)** Don't force every stage skill through Task()/Agent-tool machinery — reserve it for `--parallel` mode and gate-owning verdict passes, matching what the plan's own success criteria already scope (only `design-screen/design-function/implement-feature/unit-test/integration-test` get `Task`/`Agent`; `retro` explicitly runs solo). This mirrors criterion #5/#6 above (`review-pr`/`journal` staying thin or fully inline).
7. **(P3, docs)** Adopt the "Workflow Position" footer (`Typically follows:`/`Typically precedes:`/`Related:`) on every ClaudeBrew stage skill's `SKILL.md` — cheap, low-maintenance, complements (doesn't replace) `sdlc-conventions.md`'s central artifact-path table.
8. **(P3, validation)** Don't trust ClaudeKit's own "<300 line" claim as evidence its skills comply (`ck-plan/SKILL.md` is ~541 lines, over its own stated limit) — audit ClaudeBrew's own merged-skill line counts directly at Phase 3 rather than assuming the imported source models good discipline.

## Unresolved questions

- Whether ClaudeBrew wants any equivalent of `memory: project` on subagent-equivalent prompts (Decision 2 has no persistent per-role agent-memory dir since there are no agent files) — worth a explicit yes/no in Phase 2, since it's a capability ClaudeKit's role agents get for free (recurring-pattern learning) that a prompt-only `general-purpose` spawn cannot replicate without its own file-based memory convention.
- Whether the plan's Decision-1 "verdict + user gate" model should mandate a subagent spawn for the verdict pass (recommendation #4) or allow the executor skill to self-grade inline — not settled in the read plan.md, flagging for explicit decision rather than silent default.

Status: DONE
Summary: Extracted ClaudeKit's skill-frontmatter/HARD-GATE/Required-Subagents-table conventions, catalogued all 13 capability agents (model/memory/tools tiering), and derived the subagent-vs-inline heuristic (isolate noise, adversarial/QA separation, real parallelism, checkable MUST-tables → delegate; single-threaded/low-noise/below-threshold → inline) with 8 concrete recommendations tied to ClaudeBrew's plan phases.
Concerns/Blockers: None — two open questions listed above for the lead to resolve, not blockers.

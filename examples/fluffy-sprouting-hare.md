# Build the `requirement` skill (SDLC Stage 2) — Phase A

> Supersedes the previous plan in this file (the plugin-restructure, now merged to `main`).

## Context

ClaudeBrew's pipeline is `brainstorming → worktree → **requirement** → design → coding → testing → ship`. Stages 1 and 1.5 are built; **`requirement` (Stage 2) is next.** Its job: take the **approved brainstorm artifact** and turn it into a precise, testable, fully-traced **requirement specification** that the `design` stage consumes as its contract. It must *close* the brainstorm's open questions and *validate* its low-confidence assumptions — it elaborates the agreed "what," it does not invent new scope.

The user's full request also includes a cross-cutting **orchestration layer** (coordinate/planner/swarm/planning/deep-dive skills + lifecycle hooks). **Decision (confirmed): build the requirement stage first; scope the orchestration as a deferred Phase B** — you cannot build/test a stage-chaining coordinator before ≥2 stages exist to chain.

## Decisions (defaults — change any at approval)

| # | Decision | Default | Why |
|---|----------|---------|-----|
| 1 | Scope of THIS plan | **Phase A: `requirement` skill + the 4 sub-agents it uses** | Confirmed by user. Phase B (orchestration + hooks) scoped below, built later. |
| 2 | Agents location/format | **`plugins/cbr/agents/<name>.md`** → ids `cbr:<name>`; frontmatter `name, description, tools, model` | Docs-verified. First agents in the plugin (greenfield `agents/` dir). |
| 3 | "swarm" mechanism | **Delegated one-shot `Task` workers**, NOT a `TeamCreate`/`SendMessage` debate team | `Task` subagents are one-shot and can't drive `AskUserQuestion`; lead runs the clarify loop. |
| 4 | Default mode | **Single-agent**; recommend swarm only for broad/multi-domain specs | Requirement swarm = parallelized analysis (no debate payoff); single is the cheap default. |
| 5 | Verifier | **Run `cbr:verifier` via `Task` even in single mode** | Independent audit; the lead shouldn't grade only its own work. |
| 6 | Clarify exit bar ("diamond rule") | **Zero open *decisions* (the "what") at handoff** | Stricter than brainstorming (which may defer questions). Only the "how" may defer to `design`. |
| 7 | `explore` agent model | **haiku** | User-specified; fast retrieval. `analyze`/`architecture`/`verifier` = sonnet. |
| 8 | Auto-cascade (Phase B) | **Gated by default; opt-in `--autonomous` flag per run** | Reconciles the requested "auto-chain" with CLAUDE.md's "no auto-cascade, user approves each stage." |
| 9 | Hooks (Phase B) | **Deferred; event names + I/O re-verified against live docs before building** | Phase A needs no new hooks. The 31-event list I have is an unverified small-model doc summary. |

## Phase A — files to create

```
plugins/cbr/skills/requirement/
├── SKILL.md                       # Stage-2 spine + frontmatter (lean <500 lines)
├── references/
│   ├── artifact-template.md       # the requirement schema = the contract `design` consumes (net-new)
│   ├── clarify-loop.md            # FORK of brainstorming's, + stricter exit + seed list + "lead runs questions"
│   ├── dar-analysis.md            # FORK, unchanged (method is stage-agnostic)
│   └── swarm-mode.md              # net-new: delegated-Task swarm (when to use, spawn-prompt contents, verify loop, single fallback)
└── evals/evals.json               # 3–4 trigger/behavioral prompts + notes
plugins/cbr/agents/                 # NEW dir — first agents in the plugin
├── explore.md                     # cbr:explore   — model haiku;  tools Read,Grep,Glob,WebSearch,WebFetch
├── analyze.md                     # cbr:analyze   — model sonnet; tools Read,Grep,Glob
├── architecture.md                # cbr:architecture — model sonnet; tools Read,Grep,Glob
└── verifier.md                    # cbr:verifier  — model sonnet; tools Read,Grep,Glob
```
All four agents are **read-only** (no Write/Edit/Bash) — only the lead writes the artifact. Each body is self-contained (subagents don't inherit lead context), so the spawn prompt must pass the brainstorm path + relevant § sections + research URLs. `verifier.md` must specify its **PASS/FAIL checklist output schema** so the lead loops deterministically. Reuse = physical copy (plugin install copies each skill's `references/` independently; no shared import).

**Design lens:** these four are **pipeline assets, not requirement-only.** Design each agent's spawn-prompt schema (what context a caller must pass) and `verifier`'s output schema for **cross-stage reuse** by `design`/`coding`/`testing`/`ship` — so later stages reuse them rather than fork per stage.

Optional follow-up (non-blocking): one line in repo `CLAUDE.md` documenting `plugins/cbr/agents/<name>.md → cbr:<name>`.

## Phase A — `SKILL.md` workflow

Mirror the brainstorming/worktree house style (frontmatter `name` + long trigger `description`; numbered workflow with `→ verify:`; per-phase sections; "When the user steers"; "When things go sideways"; "Reference files").

```
0. Preconditions (doctor)            → verify: approved brainstorm exists; session INSIDE the worktree (not base); cbr plugin enabled
1. Confirm input + select mode       → verify: brainstorm Status=approved located; single vs swarm confirmed by user
2. Ingest the brainstorm             → verify: read §12 handoff FIRST, then enumerate §9, §7, §6 low-conf, §4 scope, §3 goals, §5, §8, §10
3. Research (explore)                → verify: case studies / prior art / NFR benchmarks fetched; every URL recorded
4. Analyze & clarify loop (diamond)  → verify: every §7 question CLOSED; every §6 low/med-conf assumption validated; zero open decision remains
5. DAR on residual trade-offs        → verify: each hard-to-reverse requirement-level trade-off has a decision record
6. Business analysis (analyze)       → verify: system overview, use cases, user+business flow (text+mermaid) drafted & section-approved
7. Technical analysis (architecture) → verify: NFRs (measurable), screen flow + role matrix (mermaid or "N/A — reason"), constraints approved
8. Write the artifact                → verify: docs/specs/YYYY-MM-DD-<topic>-requirement.md exists with all sections
9. Verify & self-review (verifier)   → verify: verifier checklist all PASS (no placeholders; FR/NFR unique-IDed/testable; bidirectional traceability)
10. User approval & handoff          → verify: explicit "approved"; state path + what's deferred to design; then STOP (no auto-invoke of design)
```

Key per-phase notes: **Phase 0** mirrors worktree's doctor (if on base branch → point back to `worktree`; if no approved brainstorm → point back to `brainstorming`). **Phase 3** prefers **authoritative/trusted sources** (official docs, recognized industry references) over arbitrary search hits — `cbr:explore`'s body instructs it to flag and de-rank low-trust sources (the user named "trusted/famous sites" explicitly). **Phase 4** is the engine — seed the enumeration with each §7 question + each §6 low/med-conf assumption + new uncertainties from research/agents; resolve via batched, pre-analyzed `AskUserQuestion`; in swarm mode agents return uncertainty lists and the **lead** asks. **Phase 10** handoff includes a brief "what `design` will do" note (full next-stage *planning* is Phase B's orchestrator).

**"When the user steers"** must cover work-item #4: **out-of-scope input is a scope-change signal, not a clarification.** Detect → name → ask Replacement / Branch / Refinement / Defer / Accept, **defaulting to recommend looping back to `brainstorming`** to amend the approved artifact. (Reuse brainstorming's pivot pattern with a citation.)

## Phase A — requirement artifact template (`design` consumes this)

Header: `# Requirement: <Topic>` + Date, Stage 2, Mode, Status, Author, **Source brainstorm (path + approved)**.

- **§0 Traceability summary** — table: every brainstorm §3 goal + §4 in-scope item → covering FR/NFR IDs; disposition of every §7 question + §6 low-conf assumption. (Proves the diamond held.)
- **§1 System overview** ("the ideal") — purpose, capabilities, boundaries, actors, environment; from §9. No implementation.
- **§2 Use cases** — `UC-001…`: actor, preconditions, main success scenario, alternates/exceptions, goal served.
- **§3 User flow & business flow** — TEXT + a fenced ` ```mermaid ` block (flowchart/sequence). Text and diagram must agree.
- **§4 Screen flow & role matrix** — mermaid screen-flow + role/permission table; or `Not applicable — <reason>` for headless systems.
- **§5 Functional requirements** — `FR-001…` (monotonic), "The system shall…" (testable), MoSCoW priority, Given/When/Then acceptance, **`Traces:`** to goal/scope/UC. Atomic, no compound FRs.
- **§6 Non-functional requirements** — `NFR-001…`, grouped (perf/scale/security/availability/a11y/usability/compliance/observability), each **measurable** (number+unit+condition) with acceptance + `Traces:`.
- **§7 Decisions (DAR records)** — requirement-level DARs, or "settled in brainstorm §8".
- **§8 Assumptions & constraints (validated)** — brainstorm §6 as they now stand (confirmed/validated-by-research[cite]/changed/dropped — **none low-confidence open**) + new constraints.
- **§9 Open items deferred to design (the "how", NOT decisions)** — strictly elaboration of an already-decided "what".
- **§10 References** — every cited URL as a tagged markdown link.
- **§11 Handoff notes** — one paragraph for `design`: load-bearing FRs/NFRs, riskiest requirements, what's deferred.

**Quality bar (enforced by `cbr:verifier`):** zero placeholders; zero unresolved uncertainties / open decisions; every FR/NFR uniquely IDed (no gaps), testable, **bidirectionally** traceable (FR→goal AND every goal/scope item→≥1 FR/NFR); mermaid present & valid for §3 (always) and §4 (unless justified N/A); §9 holds only how-elaboration. If brainstorm goals aren't numbered, assign G-IDs in §0 and note it.

## Phase B — deferred & scoped (do NOT build now)

The cross-cutting orchestration layer, to build after `design` (Stage 3) exists so it has ≥2 stages to coordinate:
- **Skills:** `coordinate` (orchestrator — sequences stages/handoffs; **gated by default**, optional per-run `--autonomous` to chain without stopping), `planning` (WBS/task breakdown + handoff), `deep-dive` (deep analysis of a task/issue), `swarm` (reusable agent-team mode generalizing requirement's local swarm — note this Phase-B *skill* is a distinct artifact from Phase A's `references/swarm-mode.md` doc, despite the shared name).
- **Agent:** `planner` (orchestrator that coordinates agents + stages).
- **Hooks (re-verify against live docs first):** candidates — `SessionStart`/`SessionEnd` (context-in / handoff-out), `SubagentStart`/`SubagentStop` (subagent context-in / handoff-out), `TaskCreated`/`TaskCompleted`, teammate spawn/close. **Treat all as unverified** until confirmed against `code.claude.com/docs/en/hooks`; map any that don't exist natively to `PreToolUse`/`PostToolUse` matchers.
- **Auto-cascade reconciliation** is the load-bearing Phase-B design constraint: orchestration automates *plumbing* (artifact passing, spawning the right agents), the human approval gate between stages stays unless the user explicitly opts into an autonomous run.

## Risks / tensions (carried from design review)

1. **Reference duplication debt** — `dar-analysis.md`/`clarify-loop.md` forked per stage (no shared include); drift risk grows with more stages. Flag, don't solve now.
2. **`agents/` is a new, unproven plugin surface** — validate with `claude plugin validate ./plugins/cbr` + an `@agent-cbr:verifier` smoke test before relying on swarm; single-mode fallback hedges it.
3. **Diamond rule vs user fatigue** — batching + pre-analysis mitigate; the override valve must warn that deferring *decisions* weakens the design contract more than deferring *questions* did at brainstorm.
4. **Verifier independence in single mode** — mitigated by running `cbr:verifier` via `Task` regardless of mode.

## Verification (Phase A, end-to-end)

- `claude plugin validate ./plugins/cbr` passes (new skill + 4 agents load).
- `claude --plugin-dir ./plugins/cbr` → `/cbr:requirement` listed; `/agents` shows `cbr:explore|analyze|architecture|verifier`; `/reload-plugins` after edits.
- **Smoke run:** in a worktree with an approved `*-brainstorm.md`, run `/cbr:requirement` → produces `docs/specs/<date>-<topic>-requirement.md` with all sections; mermaid blocks valid; every FR/NFR uniquely IDed + `Traces:`; `cbr:verifier` returns PASS; skill STOPS at handoff (no auto-cascade to design).
- **Pivot test:** feed out-of-scope input → skill recommends looping back to `brainstorming`, does not silently expand scope.
- **Trigger eval:** `evals/triggers/run_triggers.py` currently **hardcodes the substring `"brainstorming"`** as the detected skill — first **parameterize the detected name** (CLI arg / env var; preferred) or fork to `run_triggers_requirement.py`, then run user-initiated (Windows caveats): `! python evals/triggers/run_triggers.py plugins/cbr/skills/requirement/evals/evals.json out.json 2 2` with the detector keyed on `requirement` / `cbr:requirement`.

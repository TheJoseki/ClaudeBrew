# Memory + Artifact Patterns — ClaudeKit-engineer → ClaudeBrew

Source (read-only): `C:/Works/Tool/ClaudeKit.CC/claudekit-engineer/`. All paths below relative to that root unless noted.

## 1. Memory model

ClaudeKit has **no orchestrator-maintained project registries**. Grep for `PLAN-REGISTRY|DECISION-LEDGER|BACKLOG-REGISTRY|PROJECT-MEMORY` across the whole repo returns zero hits. Three mechanisms replace ClaudeBrew's 4-tier convention:

**a) Native agent memory (opt-in per role).** `claude/agents/*.md` frontmatter carries `memory: user` or `memory: project` — this is Claude Code's *native* auto-load feature (matches the mechanism already documented in ClaudeBrew's `sdlc-conventions.md` Tier 3: `.claude/agent-memory/<agent-name>/MEMORY.md`, auto-loaded, ~200 lines). Only 5 of 12 agents use it: `researcher` (user), `planner`/`tester`/`debugger`/`code-reviewer` (project). The other 7 (`project-manager`, `code-simplifier`, `docs-manager`, `fullstack-developer`, `git-manager`, `journal-writer`, `ui-ux-designer`) have **no memory field** — memory is selective per role, not universal. Each agent body ends with a "Memory Maintenance" section (2-3 bullets on what to save + "Keep MEMORY.md under 200 lines. Use topic files for overflow.") — self-enforced by instruction, not a hook.

**b) Session-state (cross-session resume, global, not project-scoped).** `claude/hooks/lib/session-state-manager.cjs` persists a single markdown file to `~/.claude/session-states/{md5(cwd)}/latest.md` (global home dir, keyed by cwd hash — explicitly avoids polluting the project tree). Written on `Stop`/`SubagentStop`, read back on `SessionStart` (source `startup`/`compact`). Content = todos (from transcript `TodoWrite`/native Task blocks) + modified files (`git diff --name-only HEAD`, capped 20) + per-agent completion stamps. 7-day auto-expire, 5 rotating archives, atomic write (`tmp` + rename), fully fail-open (every function wrapped in try/catch returning null/false). This is the *entire* substitute for a "session tier" — no PLAN checkpoint section, no INTERRUPT protocol.

**c) Ephemeral per-session cache (OS tmpdir, not persistent).** `ck-config-utils.cjs` keeps a lockfile-guarded JSON blob at `os.tmpdir()/ck-session-{sessionId}.json` for statusline/activity data and dedup markers (e.g. "was this reminder already injected this session"). Explicitly throwaway — never read across sessions.

**Plan files themselves are the persistent project memory.** No separate DECISION-LEDGER/BACKLOG-REGISTRY — decisions and rationale live inline in `plan.md`/`phase-*.md` (frontmatter `blockedBy`/`blocks` for cross-plan deps, `## Risk Assessment` sections for decisions). Resume works by re-reading the plan file's checkbox/status state, not a separate ledger (`ck-plan/SKILL.md` "Session Resume Pattern": read `plan.md` → find first non-completed phase → continue).

## 2. Artifact flow (path-passing, not inlining)

Every cross-skill/agent handoff passes a **path string**, never inlined content:
- `subagent-patterns.md`: `Task(subagent_type="planner", prompt="Create implementation plan based on reports: [reports]. Save to [path]")` — the prompt carries report *paths*, planner re-reads them itself.
- `workflow-artifacts.md`: a tiny pointer file `.claude/workflow-artifacts.json` (metadata only — `artifactDir`, `planPath`, `skill`, `mode`, `updatedAt`) tells `ck:fix`/`ck:cook` where the real JSON artifacts live; the pointer is never the payload.
- `artifact-locator.cjs` `resolveArtifactDir()`: deterministic 4-step resolution — explicit flag → env var (`CK_WORKFLOW_ARTIFACT_DIR`) → pointer file → single-match directory heuristic under `plans/*/reports/harness/`. Path-based, sandboxed (`safeResolve` rejects paths escaping cwd or containing NUL), never returns content.
- Plan directory layout (`plan-organization.md`) separates `research/` (raw researcher reports), `reports/` (scout/other reports), and `plan.md`/`phase-*.md` (synthesized) — downstream consumers (planner, cook) read the synthesized files, not the raw research dump.

## 3. Context-window protection — concrete size caps

| Artifact | Cap | Source |
|---|---|---|
| Researcher report | ≤150 lines, "keep reports ≤150 lines with citations" | `cook/references/subagent-patterns.md:12,15` |
| `plan.md` body | "Keep generic and under 80 lines" (detail lives in `phase-*.md`) | `ck-plan/references/plan-organization.md:211` |
| Agent `MEMORY.md` | <200 lines, "use topic files for overflow" | every agent body's Memory Maintenance section |
| Subagent definition file | 3-level structure: frontmatter (~10 lines, always) / body (protocol, always at spawn) / `references/*.md` (unlimited, on-demand `Read`) | matches ClaudeBrew's own Progressive Disclosure Convention (`sdlc-conventions.md:249-259`) — same pattern, already adopted |
| SubagentStart injected context | Target ~200 tokens (down from ~350, per code comment) | `hooks/subagent-init.cjs:8` — literally the hook that generated *this agent's own* injected context block |
| Workflow JSON artifacts | Structured fields only, "Command output must be summarized," secrets redacted before write | `_shared/references/workflow-artifacts.md` Redaction Policy |

Other techniques: `context-engineering/SKILL.md` "Four-Bucket Strategy" (Write/Select/Compress/Isolate) is the stated philosophy; `context-fundamentals`/`context-degradation` refs cover attention-curve and lost-in-middle theory (didn't inspect — generic knowledge-base content, not toolkit-specific mechanics). Subagent isolation is explicit: `context-builder.cjs:431` injects "Advisory subagents report findings and do not mutate plan/code unless explicitly tasked" directly into every session's context — a standing instruction to keep subagents read-only/summary-returning by default.

## 4. Apply to ClaudeBrew plan

1. **Drop the 4 orchestrator-maintained registries (PLAN-REGISTRY/DECISION-LEDGER/BACKLOG-REGISTRY/PROJECT-MEMORY) rather than porting them.** ClaudeKit proves a mature, shipped toolkit runs a full plan→implement→test lifecycle with zero such files — plan.md/phase-*.md frontmatter + checkbox state is sufficient project memory once orchestrators are gone. **Tie to P1** (the phase collapsing the two-layer engine) — deleting these registries removes exactly the maintenance burden that had no owner post-orchestrator.
2. **Keep Tier 3 (native `.claude/agent-memory/<role>/MEMORY.md`) as-is** — it's not orchestrator-dependent, it's a Claude Code native feature already correctly documented in `sdlc-conventions.md`. Make it **opt-in per agent**, not mandatory for all 10 roles — mirror ClaudeKit's 5-of-12 selectivity (only roles that accumulate durable cross-session knowledge: architect, developer, code-review, unit-test/integration-test analogues). **Tie to P1/P2** (agent frontmatter pass).
3. **Adopt an explicit report size cap.** Set stage-executor reports (ba/architect/dev/test/security outputs) to a stated ceiling — ClaudeKit's ≤150 lines for researcher reports is the closest analogue; ClaudeBrew's own generic hook default (this report's assigned naming pattern) has no cap today. Put the number in `rules/sdlc-conventions.md` next to the Artifact Paths table. **Tie to P2** (skill merges) since it affects every stage skill's output contract.
4. **Replace registry-based session resume with plan-file resume.** Adopt ClaudeKit's pattern verbatim: "read `docs/plans/PLAN-[feature].md`, find first phase not `completed`, continue" — already partially present in ClaudeBrew's Session Resume Pattern section; just delete the now-redundant PLAN-REGISTRY lookup step since single-layer skills can read the one plan file directly. **Tie to P1.**
5. **Formalize artifact-by-path, not by-content, in stage handoffs.** When one stage skill hands to the next (e.g. ba → architect), the orchestrator's job today is "verify artifact, then invoke next agent with the artifact path" — keep that contract even after orchestrators collapse: a stage-skill's own closing instructions should say "artifact written to `<path>`; the next stage skill reads it, do not paste content into the next invocation." **Tie to P1** (this is the direct replacement for what Layer-1 orchestrators used to do).
6. **Consider a lightweight pointer file only if multiple concurrent stage runs need disambiguation** (ClaudeKit's `.claude/workflow-artifacts.json`) — likely YAGNI for ClaudeBrew's single-user, single-plan-at-a-time flow; skip unless P3 surfaces a real ambiguity case (e.g., resuming after interruption with 2 candidate artifact dirs).
7. **Do not port the global `~/.claude/session-states/` cross-session-resume file** — it solves "resume this repo after `claude` restarts," a Claude Code session-lifecycle concern orthogonal to the SDLC-stage-artifact problem this refactor is scoped to. Out of scope for P1-P3 unless the plan already commits to it elsewhere.
8. **Reuse the "advisory subagents don't mutate" framing** for any stage skill that spawns a sub-role for read-only research/review (e.g., architect's DESIGN_REVIEW mode) — one line in the shared rules file, no new mechanism needed.

## Unresolved questions
- Does ClaudeBrew intend session-lifecycle resume (surviving a Claude Code restart) as in-scope anywhere in P1-P3? If yes, recommendation 7 should flip to "port it."
- Should the per-agent report size cap (rec. 3) be uniform across all 10 roles, or vary by artifact type (SRS vs. bug report vs. security scan)? ClaudeKit only caps *researcher* reports explicitly; other roles (planner, code-reviewer) have no stated numeric cap in the source.

Status: DONE
Summary: ClaudeKit-engineer carries zero orchestrator-style project registries — memory is native per-agent MEMORY.md (opt-in, ~200 lines, 5/12 agents) plus a global (not project) cross-session resume file; artifacts flow strictly by path with a ≤150-line report cap and a metadata-only pointer file for disambiguation.

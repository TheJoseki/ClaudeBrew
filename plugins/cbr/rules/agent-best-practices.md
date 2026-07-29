---
description: Universal agent best practices — ACI tool priority, Think Before Acting, subtask instructions, context management, escalation triggers. Always loaded alongside coding-standards.md and sdlc-conventions.md.
---

# Agent Best Practices — ClaudeKit

> Applies to ALL agents in every session. These rules operationalize Anthropic's ACI (Agent-Computer Interface) and multi-agent orchestration principles.

## 1. ACI Tool Priority (Universal)

When reading, searching, or modifying the codebase, use tools in this strict priority order:

| Priority | Tool | When to Use |
|----------|------|-------------|
| 0 | **Serena** (if available) | Symbol lookup, cross-reference, refactoring — semantic code navigation. Graceful degradation: if `find_symbol` tool unavailable, skip to Priority 1 |
| 1 | **Read** | Known file path — fastest, most precise |
| 2 | **Grep** | Search by content, pattern, or symbol across files |
| 3 | **Glob** | Discover files by name pattern when path is unknown |
| 4 | **Bash** | ONLY for build commands, test runners, or system operations |
| 5 | **Write / Edit** | Output artifacts and code modifications only |

**Never** use Bash to read files (`cat`, `head`, `tail`, `sed`) — use the **Read** tool.
**Never** use Bash to search (`grep`, `rg`, `find`) — use the **Grep** or **Glob** tool.

This prevents unnecessary permission escalation and makes agent actions auditable.

## 2. Think Before Acting (Mandatory Plan Block)

Before executing any non-trivial task, complete a **Plan Block** internally:

```
1. ANALYZE   — Read ALL input sources first. Do not start writing until all inputs are read.
2. HYPOTHESIZE — State your approach in 2-3 sentences (what + why).
3. IDENTIFY RISKS — Note 1-3 things that could go wrong or be ambiguous.
4. VERIFY SCOPE — Confirm boundaries: what is explicitly IN scope and what is NOT.
```

Only after completing the Plan Block → begin execution.

**Why this matters:** Agents that jump to output before reading all inputs produce misscoped artifacts that require expensive revisions. Forming an explicit hypothesis also makes scope drift detectable.

## 3. Subtask Instruction Template (For Orchestrators)

Every spawned subagent prompt MUST include all 4 components:

```
OBJECTIVE:       [Specific outcome expected — "produce X so that Y can proceed"]
OUTPUT FORMAT:   [Exact artifact path + key sections required]
TOOL HINTS:      [Which tools to use and in what order for this task]
TASK BOUNDARIES: [What is in scope | What is explicitly NOT in scope]
```

Missing any component → agent may duplicate work, miss scope, or produce wrong output format.

**Example (good spawn prompt):**
```
OBJECTIVE: Analyze requirements and write SRS so architect-agent can design the data schema.
OUTPUT FORMAT: docs/specs/requirements/SRS-[feature].md — must include Sections 1-9 per ba-agent template.
TOOL HINTS: Read PLAN file first, then Read any existing docs/REQUIREMENTS_ANALYSIS.md.
TASK BOUNDARIES: IN SCOPE — functional requirements, user stories, business rules.
                 NOT IN SCOPE — API endpoint details, ORM schema, UI wireframes.
```

## 4. Context Management Protocol

When executing a long task (reading many files, large codebase, complex feature):

- **After every 5 files read**: mentally note "Done: [...] | Remaining: [...]"
- **If context becomes heavy** (many large files loaded): write a checkpoint to the work log before continuing. Include: files read, decisions made, next step.
- **Do NOT re-read files already processed** — reference the work log checkpoint instead.
- **For handoff to a fresh agent**: summarize completed work in ≤5 bullet points at top of work log.

Context overflow is a silent failure mode — the agent continues but loses coherence. Proactive checkpointing prevents this.

## 5. Escalation Triggers (Stop and Ask User)

STOP the current task and ask the user before continuing if ANY of these occur:

| Trigger | Why It Matters |
|---------|---------------|
| Required input artifact is missing (SRS not found, no PROJECT.md) | Cannot produce correct output without it |
| Task scope is ambiguous after reading all available inputs | Wrong scope wastes entire agent run |
| A required decision has multiple valid paths with significant trade-offs | Wrong choice cascades through all downstream phases |
| Self-check fails after 2 attempts (tests broken, type errors unresolved) | Continuing compounds errors |
| Discovered information that contradicts the original task description | Plan may need revision before proceeding |

Do NOT silently approximate or skip. Raising an escalation is not failure — it prevents downstream waste.

## 6. Retroactive Gap Discovery (When a Critical Issue Is Found After Gates Passed)

If any agent discovers a critical infrastructure or design gap AFTER all gates are marked PASS:

**DO NOT silently continue. DO NOT assume another agent will handle it.**

Required actions (in this order):

1. Write `FLAG-[agent]-[timestamp]-[feature].md` to `docs/agent-comms/flags/` with `priority: HIGH`
2. Create a CONTESTED decision in `docs/plans/DECISION-LEDGER.md` documenting the gap (spec vs reality)
3. Create a DESIGN_DEBT or relevant type entry in `docs/plans/BACKLOG-REGISTRY.md`
4. In the original PLAN file, change the affected gate from ✅ to ⚠️ REOPENED:
   `⚠️ [Gate] REOPENED — [reason] discovered by [agent-name] on [YYYY-MM-DD]`
5. Report to orchestrator: gap description, which gates are now invalidated, required remediation steps
6. Do NOT proceed with new work until orchestrator acknowledges and provides a resolution path

**Orchestrator response**: Create a new sub-feature PLAN (or COUNCIL if complex), get user acknowledgment, then re-run the affected gates before re-declaring PASS.

**E2E infrastructure missing — specific trigger**: If a project declares a frontend framework in PROJECT.md but NO E2E config file exists (`playwright.config.*`, `cypress.config.*`, `wdio.conf.*`) when integration tests are about to run (Mode C):
→ STOP immediately. Write FLAG (priority: HIGH).
→ Do not run Mode C tests without E2E infrastructure.
→ Report: `E2E config missing — project has frontend ([framework]) but no E2E framework is configured. Escalating to orchestrator.`

## 7. Memory Accuracy Rule

When saving counts or metrics to a memory file (test case counts, endpoint counts, bug counts, screen counts):

- **Always count from the actual artifact file** — do not use your planning target number
- Write: `verified count: X (from [filename])` not `target: X` or `approximately X`
- If the file is too large to count precisely: write `unverified estimate: ~X — requires verification`

**Why**: Memory files are used for session resume. Inaccurate counts in memory cause re-work and missed quality gates when sessions are resumed.

## 8. Memory Write/Read Protocol (All Agents)

### Memory Write (at end of execution)

Agents use **two complementary memory targets** — each serves a different purpose:

**Native Memory** (auto-managed by Claude Code):
- `memory: project` in agent frontmatter → auto-manages `.claude/agent-memory/<agent-name>/MEMORY.md`
- First 200 lines auto-loaded every session — zero overhead, no manual injection needed
- Agent-specific patterns: codebase quirks, common pitfalls, spec interpretation notes
- Format: follow 3 sections from `docs/_templates/AGENT-MEMORY.md`

**Cross-Agent Knowledge** (manually appended by agent):
- `docs/memory/PROJECT-MEMORY.md` — insights ANY agent would benefit from (shared via git)
- `docs/plans/DECISION-LEDGER.md` — architectural decisions (append-only)
- `docs/plans/BACKLOG-REGISTRY.md` — carry-forward items

Before returning result, append cross-agent insights to `PROJECT-MEMORY.md`. Agent-specific patterns go to native memory automatically.

### Memory Location Rules

`.claude/agent-memory/<agent-name>/` is managed by native `memory: project` — do NOT manually create or delete files there.

**DO NOT** create per-feature status files at `.claude/agent-memory/` root level (e.g. `developer-[feature]-B1-status.md`, `ba-agent-[feature]-srs.md`). These duplicate formal artifacts already defined in sdlc-conventions.

### Memory Read (at start of execution)

Two independent read paths — both automatic:

1. **Native memory** — Claude Code auto-loads first 200 lines of `.claude/agent-memory/<agent-name>/MEMORY.md` into agent prompt at startup. No action needed.
2. **Context-injector** — SubagentStart hook (`.claude/hooks/subagent-context-inject.js`) auto-fires on every `*-agent` spawn, retrieving from registries (PLAN-REGISTRY, DECISION-LEDGER, BACKLOG-REGISTRY) and `PROJECT-MEMORY.md` using composite scoring:

```
score = (domain_match × 0.4) + (recency × 0.3) + (importance × 0.3)
```

Budget: injected context block ≤ 1500 tokens. Top-N entries by score (N=10 decisions, 5 backlog, 5 project memory).

### What to Save — Where

| Insight Type | Save To | Example |
|-------------|---------|---------|
| Role-specific codebase pattern | Native memory (auto) | "Service layer uses DI — never manual instantiation" |
| Common pitfall for YOUR role | Native memory (auto) | "Forgot DTO validation → 500 instead of 400" |
| Cross-role project learning | `PROJECT-MEMORY.md` | "MSW handlers must reset between tests" (affects dev + test agents) |
| Architectural decision | `DECISION-LEDGER.md` | "Chose JWT over session-based auth" |
| Deferred work item | `BACKLOG-REGISTRY.md` | "DESIGN_DEBT: API pagination not implemented" |

**DO NOT save:**
- General programming knowledge (how to use NestJS, how to write tests)
- Information already in CLAUDE.md, PROJECT.md, or your project's `docs/CODING_RULES.md`
- Ephemeral task details (current file being edited, temporary state)
- Git history or activity logs (use `git log` instead)

### Staleness Check

Before acting on a memory entry that references a specific file, function, or configuration:
- Verify the referenced artifact still exists (Glob/Grep check)
- If stale, update or remove the memory entry rather than acting on outdated information

## 9. Progressive Disclosure Rules (All Agents)

Agent definition files follow a 3-level progressive disclosure structure:

### Level 1: Frontmatter (always loaded, ≤20 lines)
- Agent role, capabilities, memory file path
- Read by orchestrator for spawn decisions

### Level 2: Body (loaded at spawn, ≤200 lines)
- Core execution protocol (numbered steps)
- Input/output format specifications
- Quality gate criteria
- Tool usage hints

### Level 3: Required Reading (loaded on-demand)
- Detailed templates (work-log, spec deviation, review checklist)
- Extended examples and edge cases
- Domain-specific rules

**Rules:**
1. Agents MUST NOT read Level 3 references at startup — only when reaching the relevant execution step
2. The `## Required Reading` section in agent body lists all available Level 3 files with timing instructions
3. Level 3 files live in `docs/_templates/` or skill `references/` directories
4. When an agent needs a template, it reads the file using the Read tool at the indicated step — not before
5. This saves context window space and allows agents to focus on the current task

## 10. Completion Status Protocol (All Agents)

Every agent MUST end execution with exactly ONE of these status codes in work-log footer:

| Status | When | Required Fields |
|--------|------|-----------------|
| **DONE** | All steps completed successfully | Evidence for each claim |
| **DONE_WITH_CONCERNS** | Completed but issues noted | List each concern + severity |
| **BLOCKED** | Cannot proceed | What blocks + what was tried + recommendation |
| **NEEDS_CONTEXT** | Missing required info | Exactly what info needed + from whom |

Work-log footer format:

```
STATUS: DONE_WITH_CONCERNS
CONCERNS:
- [MEDIUM] 2 unit tests skipped — missing test fixture for OAuth flow
- [LOW] API response time ~800ms on /users endpoint, consider caching
EVIDENCE: All 47/49 tests pass (2 skipped). Coverage: 87% statement.
```

Rules:
- Never declare DONE without evidence (test results, screenshots, or specific outputs)
- Never silently fail — use BLOCKED or NEEDS_CONTEXT with clear explanation
- DONE_WITH_CONCERNS must list severity per concern: [CRITICAL], [MEDIUM], [LOW]
- Orchestrator reads STATUS to decide next phase — ambiguous status = wasted rounds

## 11. 3-Strike Escalation Rule (Bug Fix & Debugging)

When fixing a bug or investigating a failure:

1. After each failed fix attempt, document in work-log:
   - What was tried (specific change, file:line)
   - Why it failed (error output, test result)
   - What was learned (narrowed scope, eliminated hypothesis)

2. After **3 consecutive failed attempts** → STOP immediately and choose ONE escalation path:
   - **Option A: Systematic Debugging** — invoke `systematic-debugging` skill (if Skill tool available) or report to orchestrator for skill invocation
   - **Option B: Bootstrap Reset** — scrap current approach entirely. Save lessons learned to work-log, reset to clean state (`git stash` or revert), re-read requirements fresh, form a completely NEW hypothesis, re-implement from scratch. Use when all 3 attempts were variations of the same flawed approach. See `systematic-debugging/references/bootstrap-strategy.md`
   - **Option C: Escalate BLOCKED** — report to orchestrator (if agent) or user (if standalone) with all 3 attempts documented. Use when the problem is genuinely outside your capability or requires external input

3. Failure report format:

```
ESCALATION: 3-Strike Rule Triggered
Attempt 1: [what] → [result] → [learned]
Attempt 2: [what] → [result] → [learned]
Attempt 3: [what] → [result] → [learned]
RECOMMENDATION: [next step — e.g., "invoke systematic-debugging" or "need user input on X"]
```

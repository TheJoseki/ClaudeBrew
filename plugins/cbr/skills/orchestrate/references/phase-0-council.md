# Phase 0 — Planning Council Protocol

> Reference for orchestrator-agent. Loaded on-demand when Phase 0 council is needed (Medium+ complexity).

## Planning Council — Agent Teams

If complexity = **Simple** → skip council → proceed to Step 0.3b then 0.4.
**Simple does NOT skip**: Step 0.2c (registry read), Step 0.3b (context injection), registry updates, or memory updates.

If complexity = **Medium | Large | Complex | Critical** → proceed with Agent Teams council.

### P1: Create Council Team

```
TeamCreate: name = "council-[feature]-[YYYYMMDD]"
```

### P2: Spawn Council Members Concurrently

Send both spawn prompts in the **same message**:

**Teammate 1 — ba-agent:**

```
Role instructions: Read `${CLAUDE_PLUGIN_ROOT}/agents/ba-agent.md` for your full role definition.
CONTEXT: AGENT_TEAMS
MODE: PLANNING
FEATURE ID: [feature-name]
OBJECTIVE: Assess domain risks and requirement clarity for feature: [feature description]
           so orchestrator can create a realistic PLAN with domain risks pre-identified.
INPUT: [paste feature description from user request]
OUTPUT ARTIFACT (MUST CREATE): docs/plans/COUNCIL-[feature]-BA.md
TEAMMATE NAME: "architect" (use SendMessage(to: "architect") for cross-agent questions)
TOOL HINTS: Read PROJECT.md or CLAUDE.md for domain context.
            Read docs/REQUIREMENTS_ANALYSIS.md if it exists.
TASK BOUNDARIES:
  IN SCOPE — domain risks, scope clarity, i18n/role complexity, hidden deliverables
  NOT IN SCOPE — writing full SRS, technical design, DB schema, API endpoints
```

**Teammate 2 — architect-agent:**

```
Role instructions: Read `${CLAUDE_PLUGIN_ROOT}/agents/architect-agent.md` for your full role definition.
CONTEXT: AGENT_TEAMS
MODE: PLANNING
FEATURE ID: [feature-name]
OBJECTIVE: Assess technical complexity and risks for feature: [feature description]
           so orchestrator can create a realistic PLAN with accurate sizing.
INPUT: [paste feature description from user request]
OUTPUT ARTIFACT (MUST CREATE): docs/plans/COUNCIL-[feature]-ARCH.md
TEAMMATE NAME: "ba" (check conversation for SendMessage from ba-agent; reply via SendMessage(to: "ba"))
TOOL HINTS: Read PROJECT.md or CLAUDE.md for tech stack context.
TASK BOUNDARIES:
  IN SCOPE — sizing estimate (components/routes/stores), technical risks, breaking change assessment
  NOT IN SCOPE — writing full TECH spec, SRS analysis, UI design
```

### P3: Wait for Both Teammates

Automatic TeammateIdle notification — do NOT proceed until both idle.

> **RESUME SAFETY**: If session interrupted during P2-P3, Agent Teams teammates cannot be restored.
> Recovery: check if both COUNCIL artifacts exist → if yes, skip to P4. If missing, re-run P1-P3 (idempotent).

> **RUNTIME NOTE**: If orchestrator runs as a subagent, TeamCreate may not be available.
> Fall back to spawning via Agent tool with `run_in_background: true`.

### P4: Read Artifacts and Synthesize

1. Read `docs/plans/COUNCIL-[feature]-BA.md`
2. Read `docs/plans/COUNCIL-[feature]-ARCH.md`
3. Check conversation for SendMessage exchanges
4. Write **Planning Council Synthesis** section into PLAN file:

```markdown
## Planning Council Synthesis
**Conducted**: [YYYY-MM-DD] | **Council**: ba-agent + architect-agent (Agent Teams)

### Sizing Decision
- Architect estimate: [Small | Medium | Large] — [n] modules, [n] endpoints, [n] tables
- BA estimate: [size tier from COUNCIL-BA.md §4]
- **Final sizing**: [reconciled] — [justification]

### Domain Risks Incorporated
| Risk ID | Description | Action in PLAN |
|---------|-------------|----------------|

### Technical Risks Incorporated
| Risk ID | Description | Action in PLAN |
|---------|-------------|----------------|

### Contradiction Resolutions
| Topic | BA Position | ARCH Position | Resolution | Rationale |
|-------|-------------|---------------|------------|-----------|

### Scope Clarifications Required Before Phase 1
[List UNCLEAR items — or "None"]

### Council Artifacts
- BA: `docs/plans/COUNCIL-[feature]-BA.md`
- Architect: `docs/plans/COUNCIL-[feature]-ARCH.md`
```

If scope clarity UNCLEAR → present to user, wait for resolution BEFORE creating PLAN.

### P5: Cleanup

```
TeamDelete: "council-[feature]-[YYYYMMDD]"
```

---

## Context Injection Pre-Spawn (automatic)

The `SubagentStart` hook auto-injects CAO context (≤1500 tokens) into every `*-agent` spawn. No manual action needed.

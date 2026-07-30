# Planning Council Protocol — Architect Agent

> Reference for architect-agent. Loaded on-demand when MODE: PLANNING is set.

## PLANNING Mode: What to Produce

Focus ONLY on **technical complexity and risk assessment** — NOT a full TECH spec.

**Output**: `docs/plans/COUNCIL-[feature]-ARCH.md`

### Step P1: Read Context

1. Read `CLAUDE.md` or `PROJECT.md` — detect tech stack, existing module structure
2. Read `docs/ARCHITECTURE.md` if exists
3. If `CONTEXT: AGENT_TEAMS`: check conversation for SendMessage from ba-agent
   If `CONTEXT: SUBAGENT`: Glob `docs/agent-comms/questions/Q-ba-architect-*-[feature].md`
4. Read feature description from spawn prompt

### Step 0.5: Read Decision Ledger (MANDATORY)

Read `docs/plans/DECISION-LEDGER.md`. Filter by feature domain. Note CONTESTED/NEEDS RESOLUTION decisions.

### Step P2: Assess Technical Complexity

**Sizing** — estimate new modules, DB tables, API endpoints, frontend components.
Cross-reference with existing codebase (Grep for similar modules).

**Risk lenses:**

| Lens | Questions |
|------|----------|
| Data model | Complex relations? Migration risk? |
| Integration | External APIs, auth providers, file storage? |
| Stack constraints | Unsupported tech? |
| Algorithm complexity | Non-trivial business logic? |
| Concurrency | Race conditions, idempotency? |

### Step P3: Answer BA Questions

**AGENT_TEAMS**: Reply via `SendMessage(to: "ba")`
**SUBAGENT**: Write answers to `docs/agent-comms/answers/A-architect-ba-*.md`
Section 5 MUST have answers or "No BA questions received" — never blank.

### Step P4: Write COUNCIL-[feature]-ARCH.md

```markdown
# Planning Council — Architect Perspective: [Feature Name]
**Feature ID**: [feature-name] | **Date**: [YYYY-MM-DD] | **Mode**: PLANNING

## 1. Sizing Estimate
| Metric | Estimate | Basis |
|--------|----------|-------|
| New modules/views | [n] | [reasoning] |
| New DB tables | [n] | [reasoning] |
| New API endpoints | [n] | [reasoning] |
| New components/stores/routes | [n] | [reasoning] |

**Sizing tier**: Small | Medium | Large — [justification]

## 2. Technical Risks (3–5 items)
| Risk ID | Description | Priority | Action |
|---------|------------|----------|--------|

## 2b. Cross-agent Awareness
What I expect ba-agent to cover: [scope clarity, domain risks, user story complexity]
Areas where ARCH/BA may differ: [list or "None"]

## 3. Technical Unknowns
[Numbered checklist for 5+, free-form for <5, or "None"]

## 4. Recommended Batch Split
[If Large: batch split suggestion. If Small/Medium: "Single batch"]

## 5. Answers to BA Questions
[Answers or "No BA questions received"]
```

**Self-check**: ≥3 specific risks, sizing justified, §2b filled, §5 not blank.

### Decision Ledger Append (MANDATORY)

After producing any design artifact:
1. Read `docs/plans/DECISION-LEDGER.md`
2. Append new decisions (check for duplicates first)
3. Mark superseded decisions if applicable
4. Update Domain Index

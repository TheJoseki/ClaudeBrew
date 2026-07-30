---
description: Agent communication protocol — file-based mailbox for inter-agent messaging.
             Read this when writing to or reading from docs/agent-comms/ in any project.
---

# Agent Communication Protocol — ClaudeBrew

## Purpose

Enables agents to communicate asynchronously through artifact files without routing
everything through the orchestrator. Used in Planning Council (Phase 0) and future
Design Validation phases.

## Directory Structure (auto-created at runtime)

```
docs/agent-comms/
  flags/          ← Urgent issues requiring orchestrator attention (blockers)
  questions/      ← Async questions from one agent to another
  answers/        ← Responses to questions
```

All directories: auto-create if missing (per auto-create rule in sdlc-conventions.md).

## Filename Convention

```
flags/:     FLAG-[from-agent]-[YYYYMMDDHHMMSS]-[feature].md
questions/: Q-[from]-[to]-[YYYYMMDDHHMMSS]-[feature].md
answers/:   A-[from]-[to]-[YYYYMMDDHHMMSS]-[feature].md
```

## Message Format (frontmatter + body)

```markdown
---
from: [agent-name]
to: [agent-name | orchestrator | broadcast]
type: FLAG | QUESTION | ANSWER
priority: HIGH | MEDIUM | LOW
feature: [feature-name]
timestamp: [YYYY-MM-DDTHH:MM:SSZ]
references: [optional — filename of message being answered]
---

## [Subject line]

### Context
[Why this message is being sent]

### Content
[The question, flag finding, or answer]

### Action Required
[What the receiver should do — be specific]
```

## When to Read Mailbox

| Agent | When to Read | What to Read |
|-------|-------------|-------------|
| orchestrator | Start of every phase | `docs/agent-comms/flags/` — check for blockers |
| ba-agent (PLANNING) | After writing COUNCIL artifact | `docs/agent-comms/answers/` — read architect answers (if any) |
| architect-agent (PLANNING) | Before finalizing COUNCIL artifact | `docs/agent-comms/questions/Q-ba-architect-*-[feature].md` |

## When to Write to Mailbox

- Write **BEFORE ending your task** (not after returning result)
- **FLAG**: only for genuine blockers — "cannot produce correct output without this info"
- **QUESTION**: when your output depends on another agent's specialized domain knowledge
- **ANSWER**: when you find questions addressed to you in `questions/`

## Constraints

- Mailbox is for **cross-agent communication only** — orchestrator-visible output belongs in artifact files (COUNCIL-BA.md, COUNCIL-ARCH.md, etc.)
- Do NOT write to mailbox if a direct artifact already conveys the information
- **HIGH priority** reserved for genuine blockers
- Mailbox messages are **permanent** — part of the feature's decision trail (never deleted)

## Planning Council Interaction Pattern

ba-agent and architect-agent run **sequentially** in Phase 0 Planning Council. BA writes first, Architect reads BA output before writing:

```
orchestrator (sequential spawn)
    │
    ├── P1: Agent(ba-agent)
    │       └── writes COUNCIL-BA.md (requirements, risks, sizing)
    │
    ├── P2: Agent(architect-agent)
    │       ├── reads COUNCIL-BA.md FIRST (alignment with BA)
    │       └── writes COUNCIL-ARCH.md (tech approach, aligned sizing)
    │
    ├── P3: [Complex/Critical only] Agent(architect-agent, critic)
    │       ├── reads BOTH COUNCIL artifacts
    │       └── writes COUNCIL-REVIEW.md (traceability check + challenges)
    │
    └── orchestrator reads all COUNCIL artifacts → synthesizes PLAN
```

Because architect reads BA output on disk, cross-agent Q/A is handled inline — no separate question/answer files needed for council. The `docs/agent-comms/` mailbox remains available for other inter-agent communication outside council.

**COUNCIL artifacts are always written to `docs/plans/`**:
- `COUNCIL-[feature]-BA.md`, `COUNCIL-[feature]-ARCH.md`, and optionally `COUNCIL-[feature]-REVIEW.md`
- These are permanent records and formal audit trail

**Note on COUNCIL file type**: COUNCIL files in `docs/plans/` use `type: COUNCIL` frontmatter.
This is distinct from the `FLAG | QUESTION | ANSWER` types used for `docs/agent-comms/` files.
COUNCIL files are plan artifacts, not comms messages — different lifecycle and purpose.

## Agent Teams Communication Patterns (Phase 4+)

When agents are spawned as Agent Teams teammates (via team-templates.md), these patterns apply:

| Pattern | Template | Protocol |
|---------|----------|----------|
| Developer ↔ Developer | T-IMPL-FULLSTACK | API contract exchange: response shape, enum values, error codes. Record in work-log `## Interface Contracts` |
| Developer → BA | T-IMPL-WITH-BA | Business rule clarification: dev asks specific question, BA answers from SRS context. Record in work-log `## Spec Clarifications` |
| Reviewer → Architect | T-REVIEW-ARCH | Architectural concern consultation: reviewer describes concern + file:line, architect explains design intent |
| UT ↔ IT | T-TEST-COORD | Shared test data dependency notification: UT finds bug affecting IT test data → notifies IT immediately |

**All patterns share**: Max 5 messages/teammate. Decisions in artifact files (source of truth). SendMessage is ephemeral — do not rely on it for audit trail.

## Lifecycle

Messages are NOT deleted after use. They are part of the feature's audit trail alongside other docs/ artifacts. Orchestrator may reference mailbox messages in the PLAN synthesis section.

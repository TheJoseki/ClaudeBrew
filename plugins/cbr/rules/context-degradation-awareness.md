---
description: Context window degradation awareness — 4-tier monitoring with checkpoint/stop thresholds. Prevents silent quality loss from context overflow.
---

# Context Degradation Awareness

> Agents MUST monitor their context usage and adjust behavior as the window fills. Context overflow is a silent failure — the agent continues but loses coherence. This rule makes degradation visible and actionable.

## 4-Tier Degradation Curve

| Tier | Window Used | Status | Agent Behavior |
|------|------------|--------|---------------|
| **PEAK** | 0–30% | Normal | Full operation — read freely, explore broadly |
| **GOOD** | 30–50% | Checkpoint | Write checkpoint to work-log every 5 files read. Note: files read, decisions made, remaining scope |
| **DEGRADING** | 50–70% | Reduce scope | Defer non-critical items to BACKLOG. Read only essential files. Skip optional docs (ARCHITECTURE.md, API_DESIGN.md if TECH spec is sufficient) |
| **POOR** | 70%+ | Stop or handoff | STOP current work. Save checkpoint with full state. Return STATUS: PARTIAL with remaining scope clearly listed |

## How to Estimate Context Usage

Agents cannot directly measure token count, but can estimate based on activity:

| Activity | Approximate Tokens |
|----------|-------------------|
| Session baseline (rules + skill body) | ~90K |
| Each file read (avg) | ~2-5K |
| Each file written/edited | ~1-3K |
| Spec document (TECH/BASIC) | ~5-15K |
| Tool call overhead (per call) | ~0.5K |

**Heuristic**: After reading 15+ files or processing 3+ large specs, assume you are in GOOD tier. After 25+ files or 5+ specs, assume DEGRADING.

## Checkpoint Format

```markdown
## Context Checkpoint [YYYY-MM-DD HH:MM]
- **Tier**: GOOD / DEGRADING / POOR
- **Files read**: [list with purpose]
- **Decisions made**: [key choices with rationale]
- **Files written**: [output artifacts so far]
- **Remaining scope**: [what still needs to be done]
- **Next step**: [exactly what to do next if resuming]
```

## Integration with Existing Protocols

| Protocol | How This Rule Applies |
|----------|----------------------|
| **PARTIAL return** | DEGRADING/POOR tier → return PARTIAL with remaining scope listed, instead of rushing to finish |
| **Incremental test writing** | GOOD tier → checkpoint after each layer (unit) or each workflow (integration) |
| **3-Strike Rule** (`coding-standards.md`) | If 2 strikes occurred in DEGRADING tier → likely context-related, not logic-related |

## Responsibility

- Monitor tier and write checkpoints per the thresholds above — in the main session and in any spawned subagent.
- A PARTIAL result with an accurate tier field is more useful than a complete-looking result produced past the POOR threshold.

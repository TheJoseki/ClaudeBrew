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
| Agent body + rules (baseline) | ~90K |
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
| **PARTIAL return** (developer-agent) | DEGRADING/POOR tier → return PARTIAL instead of rushing to finish |
| **Layer-by-layer writing** (unit-test-agent) | GOOD tier → mandatory checkpoint after each layer |
| **Workflow-by-workflow** (integration-test-agent) | GOOD tier → mandatory checkpoint after each workflow |
| **Input Pruning** (TIGHT batches) | DEGRADING tier → auto-apply pruning even for SAFE batches |
| **3-Strike Rule** | If 2 strikes occurred in DEGRADING tier → likely context-related, not logic-related |

## Agent Responsibility

- **All agents**: Monitor tier, write checkpoints per thresholds above
- **Orchestrator**: When reading PARTIAL work-logs, check tier field to understand why agent stopped
- **Developer-agent**: In TIGHT batches, start in GOOD tier (baseline already ~140K) — extra vigilance needed

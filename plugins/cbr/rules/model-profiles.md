---
description: Model profile selection — quality/balanced/budget tiers for agent spawning. Controls cost-quality trade-off per execution path.
---

# Model Profiles

> Controls which Claude model each agent uses based on task requirements and user preference. Set via `--quality` or `--budget` flags on `/orchestrate`, or `model_profile` in PROJECT.md.

## 3 Profiles

| Profile | Planning Agents | Execution Agents | Review Agents | Use Case |
|---------|----------------|-----------------|---------------|----------|
| **quality** | opus | opus | opus | Critical features, production releases, complex architecture |
| **balanced** | opus | sonnet | sonnet | Default — best cost/quality ratio for most features |
| **budget** | sonnet | sonnet | haiku | Prototyping, learning projects, non-critical features |

### Agent Role → Profile Mapping

| Agent | Role Category | quality | balanced | budget |
|-------|--------------|---------|----------|--------|
| orchestrator-agent | Planning | opus | opus | sonnet |
| ba-agent | Planning | opus | opus | sonnet |
| architect-agent | Planning | opus | opus | sonnet |
| ui-designer-agent | Planning | opus | opus | sonnet |
| developer-agent | Execution | opus | sonnet | sonnet |
| bug-fix-agent | Execution | opus | sonnet | sonnet |
| code-review-agent | Review | opus | sonnet | haiku |
| security-tester-agent | Review | opus | sonnet | haiku |
| unit-test-agent | Execution | opus | sonnet | sonnet |
| integration-test-agent | Execution | opus | sonnet | sonnet |

## Selection Logic

### Priority Order (highest wins)

1. **Flag on command**: `--quality` or `--budget` on `/orchestrate` → applies to entire pipeline
2. **PLAN file**: `model_profile: quality` in PLAN frontmatter → applies to that feature
3. **PROJECT.md**: `model_profile: balanced` in project config → project default
4. **System default**: `balanced` — if nothing specified

### How to Apply

When spawning an agent via Agent tool, include the `model` parameter:

```
Agent tool call:
  subagent_type: "developer-agent"
  model: "sonnet"                    ← from profile lookup
  description: "Implement [feature] Batch-1"
  prompt: |
    ...
```

### Override Rules

- Individual command runs (not via /orchestrate) use PROJECT.md profile or system default
- `/quick-fix` always uses `balanced` regardless of profile (optimized for speed)
- Security scan (Phase 5) minimum: `sonnet` even in budget profile (security cannot use haiku)

## Cost Estimation

Approximate token costs per profile for a Medium feature (~1M total tokens):

| Profile | Planning (~200K) | Execution (~600K) | Review (~200K) | Relative Cost |
|---------|-----------------|-------------------|----------------|--------------|
| quality | $$$ | $$$ | $$$ | ~3x |
| balanced | $$$ | $$ | $$ | ~1.5x (baseline) |
| budget | $$ | $$ | $ | ~1x |

## Auto-Route by Task Complexity

When spawning Phase 4 agents, auto-select model based on WBS Story Points if no explicit profile is set:

| WBS Task SP | Model Tier | Rationale |
|-------------|-----------|-----------|
| 1-2 (Trivial/Simple) | haiku | Config change, rename, simple CRUD |
| 3-5 (Typical/Complex) | sonnet | Standard implementation |
| 8+ (Very Complex) | opus | Multi-service, architecture change |

**Rules**:
- Per-batch: if batch has mixed SP tasks → use highest SP's model (e.g., SP-2 + SP-8 → opus)
- Override: `--quality` flag → opus for all. `--budget` flag → sonnet for all
- Explicit profile in PLAN frontmatter takes precedence over auto-route
- Security scan minimum: sonnet (even if SP suggests haiku)

## Integration

- Orchestrator reads profile at Step 0 → records in PLAN frontmatter
- All spawn templates in `references/spawn-templates.md` support `model` parameter
- `/sdlc-status` displays current profile in status output
- Auto-route applies at Phase 4 spawn time if no explicit profile specified

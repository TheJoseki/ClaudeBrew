---
name: parallel-agents
description: "Multi-agent orchestration patterns. Trigger: when task requires multiple specialists working concurrently, or when you need to parallelize independent work streams."
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
metadata:
  version: "3.1"
  category: core-sdlc
---

# Parallel Agents — Multi-Agent Orchestration

$ARGUMENTS

---

## When to Use Parallel Orchestration

**Good for:**
- Complex tasks requiring multiple expertise domains simultaneously
- Comprehensive analysis needing security + performance + quality perspectives
- Feature implementation requiring backend + frontend + database work in parallel
- Full system reviews where independent streams can run concurrently

**Not for:**
- Simple, single-domain tasks
- Quick fixes or small changes
- Tasks where one agent or one sequential pass suffices
- Tasks with strict ordering dependencies (Phase A must finish before Phase B starts)

---

## Claude Code: Parallel Agent Invocation

> In Claude Code, spawn parallel agents by making **multiple Agent tool calls in a SINGLE message response**. Each call runs concurrently. Do NOT chain them sequentially if they are independent.

### Single Agent (Sequential)
```
Invoke the developer-agent to implement the authentication module.
```

### Parallel Agents (Concurrent — preferred for independent streams)
```
[In a single message, make multiple Agent tool calls simultaneously:]

Agent 1: developer-agent → implement backend NestJS module
Agent 2: developer-agent → implement frontend Vue components
Agent 3: unit-test-agent → write unit tests for the service layer
```

### Sequential Chain (when ordering matters)
```
Step 1: architect-agent → produce TECH spec
Step 2 (after Step 1 completes): developer-agent → implement from spec
Step 3 (after Step 2 completes): unit-test-agent → test the implementation
```

### With Context Passing
```
Invoke the architect-agent to design the approval workflow.
Based on those findings, invoke the developer-agent to implement it.
```

---

## Available Agents in `.claude/agents/`

| Agent | Role | Trigger |
|-------|------|---------|
| `orchestrator-agent` | Coordination, SDLC flow | "plan", "multi-step", "comprehensive" |
| `ba-agent` | Requirements, user stories | "requirements", "user story", "scope" |
| `architect-agent` | TECH spec, data model, API design | "design", "architecture", "spec" |
| `developer-agent` | Full-stack implementation | "implement", "build", "create" |
| `ui-designer-agent` | Screen design, wireframes | "UI", "screen", "wireframe" |
| `code-review-agent` | Code quality review | "review", "audit", "check code" |
| `bug-fix-agent` | Bug fixes | "bug", "error", "broken" |
| `unit-test-agent` | Unit tests (detect runner from PROJECT.md) | "unit test", "UT", "coverage" |
| `integration-test-agent` | API + E2E integration tests | "integration test", "IT", "e2e" |

---

## Orchestration Patterns

### Pattern 1: Full-Stack Feature (Concurrent BE + FE)
```
Parallel streams:
  Stream A: developer-agent → backend implementation
  Stream B: developer-agent → frontend implementation

After both complete:
  Stream C: unit-test-agent → test both layers
```

### Pattern 2: Comprehensive Code Review
```
Parallel streams:
  Stream A: code-review-agent → backend review
  Stream B: code-review-agent → frontend review

After both:
  Synthesize findings into consolidated report
```

### Pattern 3: SDLC Feature Pipeline (Sequential)
```
1. ba-agent → analyze requirements → docs/specs/REQ-[feature].md
2. architect-agent → produce TECH spec → docs/specs/detail-design/TECH-[feature].md
3. developer-agent → implement → backend/ + frontend/
4. unit-test-agent → unit tests → docs/test-reports/UTR-[feature]-R1.md
5. integration-test-agent → integration tests → docs/test-reports/ITR-[feature]-R1.md
```

---

## Synthesis Protocol

After all parallel agents complete, synthesize into a single report:

```markdown
## Orchestration Synthesis

### Task Summary
[What was accomplished across all agents]

### Agent Contributions
| Agent | Output | Key Findings |
|-------|--------|--------------|
| developer-agent (BE) | backend/src/modules/[m]/ | [summary] |
| developer-agent (FE) | frontend/src/views/[m]/ | [summary] |
| unit-test-agent | docs/test-reports/UTR-[feature]-R1.md | Coverage: X% |

### Consolidated Action Items
- [ ] [Critical issue from Agent A]
- [ ] [Follow-up from Agent B]
- [ ] [Enhancement from Agent C]
```

---

## Best Practices

1. **Independent streams run in parallel** — make multiple Agent tool calls in a single message
2. **Dependent streams run sequentially** — wait for upstream output before invoking downstream agent
3. **Pass context explicitly** — include relevant findings when invoking downstream agents
4. **Single synthesis** — produce one unified report, not separate disconnected outputs
5. **Verify implementation** — always include unit-test-agent or integration-test-agent for code changes
6. **Logical order for sequential work**: Discovery → Spec → Implement → Test → Review

---

## Parallel vs Sequential Decision

| Condition | Pattern |
|-----------|---------|
| Tasks share no data dependencies | Parallel (single message, multiple Agent calls) |
| Task B needs Task A's output | Sequential (wait, then invoke) |
| Mixed (some parallel, some dependent) | Hybrid — batch independent tasks, then continue |
| Single specialist sufficient | No orchestration needed |

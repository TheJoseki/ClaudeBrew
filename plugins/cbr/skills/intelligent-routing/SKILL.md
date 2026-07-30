---
name: intelligent-routing
description: "Analyze user request and automatically route to the best skill or agent. Trigger: unclear requests, multi-domain tasks, or when user doesn't know which skill to use."
user-invocable: false
allowed-tools: Read, Grep, Glob
metadata:
  version: "3.1"
  category: meta
---

# Intelligent Routing — Automatic Skill and Agent Selection

$ARGUMENTS

---

## Skill Architecture — 4 Layers

Understanding this map helps route correctly. Each layer calls the layer below it; never skip layers.

| Layer | Skills | Role |
|-------|--------|------|
| **L1 Orchestrators** | `full-sdlc`, `orchestrate`, `parallel-agents` | End-to-end pipeline management — spawn and coordinate multiple skills/agents |
| **L2 Workflow Hubs** | `implement-feature`, `fix-bug`, `review-code`, `run-tests` | Core development work — each has explicit escalation/handoff to other skills |
| **L3 Utilities** | `systematic-debugging`, `lint-and-validate`, `vulnerability-scanner`, `create-pr` | Supporting tools — called BY L2 skills, rarely invoked directly |
| **L4 Domain** | `api-patterns`, `database-design`, `architecture`, `clean-code`, `tdd-workflow`, `testing-patterns`, `brainstorming`, `plan-writing`, `performance-profiling`, `deployment-procedures`, `documentation-templates`, `code-review-checklist` | Standalone reference/guidance — invoked directly by user for specific domain knowledge |

**Key connection paths:**
```
implement-feature → lint-and-validate → review-code → vulnerability-scanner → create-pr
fix-bug (×2 fail) → systematic-debugging → fix-bug → run-tests
unit-test (Mode A) ‖ implement-feature ‖ integration-test (Mode A)   [parallel]
```

---

## Core Principle

Act as an intelligent Project Manager: analyze each request, detect its domain(s) and complexity, then automatically route to the most appropriate skill or agent — without requiring the user to know the system architecture.

---

## Step 1: Request Analysis

Before responding to any request, silently perform:

1. **Classify request type**: implementation, bug fix, review, test, design, question, vague
2. **Detect domains**: backend, frontend, database, testing, DevOps, architecture, requirements
3. **Assess complexity**: SIMPLE (1 domain, 1 file) / MODERATE (2 domains) / COMPLEX (3+ domains or unclear)
4. **Select skill/agent** using the matrix below

---

## Step 2: Routing Matrix

### Single-Domain Tasks — Route to Skill Directly

| User Intent | Keywords | Route To |
|-------------|----------|----------|
| Requirements analysis | "requirements", "user story", "scope", "backlog" | `analyze-requirement` skill or `ba-agent` |
| Tech/Screen design | "design", "spec", "architecture", "TECH spec" | `design-function` / `design-screen` skill or `architect-agent` |
| Feature implementation | "implement", "build", "create feature", "code" | `implement-feature` skill or `developer-agent` |
| Bug fix | "bug", "error", "not working", "broken", "fix" | `fix-bug` skill or `bug-fix-agent` |
| Code review | "review", "audit", "check code", "PR review" | `review-code` skill or `code-review-agent` |
| Unit tests | "unit test", "UT", "coverage" | `run-tests` / `unit-test` skill or `unit-test-agent` |
| Integration tests | "integration test", "IT", "e2e", "API test" | `integration-test` skill or `integration-test-agent` |
| Security testing | "security", "vulnerability", "OWASP", "pen test", "scan" | `vulnerability-scanner` skill or `security-tester-agent` |
| Pull request | "PR", "pull request", "merge", "create PR" | `create-pr` skill |
| Full SDLC | "full feature", "end-to-end", "from scratch" | `full-sdlc` skill or `orchestrator` |

### Multi-Domain Tasks — Route to Orchestrator

If request spans 2+ domains from different categories:

```
Example: "Implement the document approval workflow with tests"
→ Detected: Implementation + Testing
→ Route: orchestrator → parallel developer-agent + unit-test-agent
```

### Domain Detection (adapt to PROJECT.md tech stack)

| Domain | Patterns | Agent |
|--------|----------|-------|
| **Backend** | controller, service, model, route, API, guard, middleware | `developer-agent` (BE focus) |
| **Frontend** | component, store, composable, i18n, router, view, page | `developer-agent` (FE focus) |
| **Database** | schema, migration, ORM model, relation, index | `developer-agent` + schema work |
| **Auth/Security** | JWT, session, guard, roles, permissions, RBAC | `developer-agent` + security review |
| **External Integration** | API client, webhook, third-party service, OAuth | `developer-agent` (integration) |
| **Business Workflow** | status, state machine, approval, pipeline, lifecycle | `developer-agent` + `architect-agent` |

---

## Step 3: Complexity Assessment

### SIMPLE — Direct skill invocation
- Single file or small change
- Clear, specific task
- One domain only
- Example: "Fix the soft delete filter in folder.service.ts"

**Action**: Invoke the matching skill directly.

### MODERATE — 2-3 skills/agents
- 2-3 files affected
- Clear requirements, 2 domains max
- Example: "Add a new API endpoint and update the Vue store"

**Action**: Invoke relevant skills sequentially or in parallel.

### COMPLEX — Orchestrate
- Multiple files/domains
- Architectural decisions needed
- Unclear or vague requirements
- Example: "Build the document management module"

**Action**: Invoke `orchestrator` or `full-sdlc` skill → decompose → delegate.

---

## Step 4: Response Format

When routing is determined, inform the user concisely (no verbose meta-commentary):

```
Routing to: `implement-feature` skill (detected: NestJS backend + Vue frontend implementation)

[Proceed with execution]
```

For vague requests, ask one focused clarifying question before routing:

```
To route this correctly: are you looking to (A) implement a new feature, (B) fix a bug,
or (C) review existing code?
```

---

## Available Skills in `.claude/skills/`

| Skill | Purpose |
|-------|---------|
| `analyze-requirement` | BA work: requirements, user stories, acceptance criteria |
| `design-function` | TECH spec: backend architecture, API design, data model |
| `design-screen` | SCREEN spec: UI wireframes, Vuetify component specs |
| `implement-feature` | Full-stack implementation (tech stack from PROJECT.md) |
| `fix-bug` | Bug diagnosis and fix with report |
| `review-code` | Code quality, security, convention review |
| `unit-test` | Unit test writing (test runner from PROJECT.md) |
| `run-tests` | Execute test suites, generate UTR/ITR reports |
| `integration-test` | Integration and API testing |
| `create-pr` | Git branch, commit, PR creation |
| `full-sdlc` | End-to-end SDLC pipeline orchestration |
| `orchestrate` | Multi-agent coordination for complex tasks |
| `parallel-agents` | Concurrent agent spawning patterns |
| `systematic-debugging` | 4-phase deep debugging methodology |
| `behavioral-modes` | Switch AI operational mode |
| `intelligent-routing` | This skill — request analysis and routing |

---

## Edge Cases

### Generic Question
```
User: "How does JWT refresh work?"
→ Type: QUESTION, no routing needed
→ Respond directly with explanation
```

### Vague Request
```
User: "Make it better"
→ Complexity: UNCLEAR
→ Action: Ask one clarifying question, then route
```

### Explicit Override
```
User: "Use the fix-bug skill for this"
→ Override auto-routing
→ Invoke fix-bug skill directly regardless of analysis
```

### Contradictory Signals
```
User: "Add mobile support"
→ Unclear: responsive web vs native mobile
→ Ask: "Do you mean responsive web design or a separate mobile app?"
```

---

## Routing Rules

1. **Analyze silently** — do not announce "I am analyzing your request"
2. **Inform the routing** — briefly state which skill/agent is being applied and why
3. **Explicit overrides win** — if user names a skill/agent explicitly, use it
4. **Ask before complex orchestration** — for COMPLEX tasks, confirm scope before spawning multiple agents
5. **Docs first** — for any implementation routing, remind developer-agent to read `docs/CODING_RULES.md` and the relevant TECH spec

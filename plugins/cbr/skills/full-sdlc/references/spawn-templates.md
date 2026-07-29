## MANDATORY: Context Injection Before Every Spawn

BEFORE every Agent tool call below, orchestrator MUST:
1. Invoke context-inject skill with: AGENT_ROLE, FEATURE, PHASE, DOMAIN_TAGS
2. Prepend returned context block to the agent's spawn prompt
3. If context-inject returns empty → note "First execution, no accumulated context"

FAILURE TO INJECT CONTEXT = agent runs blind. This is the #1 cause of context loss.

---

# Full SDLC Spawn Templates
> Referenced by full-sdlc/SKILL.md. Each section contains the complete prompt for the corresponding agent spawn call.

---

## Phase 0 Council

### ba-agent council spawn

```
Role instructions: Read `.claude/agents/ba-agent.md` for your full role definition.
CONTEXT: AGENT_TEAMS
MODE: PLANNING
FEATURE ID: [feature-name]
OBJECTIVE: Assess domain risks and requirement clarity for feature: [description]
INPUT: [paste feature description from $ARGUMENTS]
OUTPUT ARTIFACT (MUST CREATE): docs/plans/COUNCIL-[feature]-BA.md
TEAMMATE NAME: "architect" (use SendMessage(to: "architect") for cross-agent questions)
TOOL HINTS: Read PROJECT.md or CLAUDE.md for domain context.
TASK BOUNDARIES:
  IN SCOPE — domain risks, scope clarity, i18n/role complexity, hidden deliverables
  NOT IN SCOPE — writing full SRS, technical design, DB schema, API endpoints
```

### architect-agent council spawn

```
Role instructions: Read `.claude/agents/architect-agent.md` for your full role definition.
CONTEXT: AGENT_TEAMS
MODE: PLANNING
FEATURE ID: [feature-name]
OBJECTIVE: Assess technical complexity and risks for feature: [description]
INPUT: [paste feature description from $ARGUMENTS]
OUTPUT ARTIFACT (MUST CREATE): docs/plans/COUNCIL-[feature]-ARCH.md
TEAMMATE NAME: "ba" (check conversation for messages from ba-agent)
TOOL HINTS: Read PROJECT.md or CLAUDE.md for tech stack context.
TASK BOUNDARIES:
  IN SCOPE — sizing estimate (components/routes/stores), technical risks, breaking changes
  NOT IN SCOPE — writing full TECH spec, SRS analysis, UI design
```

---

## Phase 1 — ba-agent

```
Agent tool:
  subagent_type: "ba-agent"
  description: "Analyze requirements for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    OBJECTIVE: Produce a complete SRS so architect-agent can design the system without
               needing to ask clarifying questions about requirements.
    Feature description: [paste description from $ARGUMENTS]
    INPUT (read in this order):
      1. docs/plans/PLAN-[feature]-[date].md
      2. docs/REQUIREMENTS_ANALYSIS.md (if exists)
      3. PROJECT.md/CLAUDE.md for domain context
    OUTPUT FORMAT (MUST CREATE): docs/specs/requirements/SRS-[feature].md
      Required: Sections 1-12 per ba-agent template including Business Process Flow.
    TOOL HINTS: Read PLAN file first → Read existing REQUIREMENTS_ANALYSIS.md → Grep codebase
                for related existing modules before defining scope.
    TASK BOUNDARIES:
      IN SCOPE — user stories, business rules, acceptance criteria, business process flow
      NOT IN SCOPE — API endpoint details, ORM schema, UI wireframes (those belong in later phases)
```

---

## Phase 2 — ui-designer-agent

```
Agent tool:
  subagent_type: "ui-designer-agent"
  description: "Design screens for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    OBJECTIVE: Produce screen spec with all UI states defined so developer-agent can implement
               frontend without needing to make UI decisions independently.
    INPUT (read in this order):
      1. docs/specs/requirements/SRS-[feature].md (user stories drive the screens)
      2. PROJECT.md/CLAUDE.md (UI library and framework)
      3. docs/SCREEN_DESIGN.md (existing screen patterns to follow)
    OUTPUT FORMAT (MUST CREATE): docs/specs/requirements/SCREEN-[feature].md
      Required: all screens with default/loading/empty/error states, component hierarchy,
      design tokens, Figma frames table (if Figma MCP available).
    TOOL HINTS: Read SRS first → check Figma MCP availability → design screens.
    TASK BOUNDARIES:
      IN SCOPE — screen layouts, component specs, navigation flow, all UI states
      NOT IN SCOPE — API endpoint details, backend schema, business logic implementation
```

---

## Phase 3a — architect-agent (BASIC_DESIGN standard)

```
Agent tool:
  subagent_type: "architect-agent"
  description: "Basic design (基本設計) for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: BASIC_DESIGN
    OBJECTIVE: Produce high-level system design (module structure, DB table list, API endpoint list)
               for PM/customer review and approval before detail design begins.
    INPUT (read in this order):
      1. docs/specs/requirements/SRS-[feature].md
      2. docs/specs/requirements/SCREEN-[feature].md
      3. docs/CODING_RULES.md, docs/ARCHITECTURE.md (if exist)
    OUTPUT FORMAT (MUST CREATE): docs/specs/basic-design/BASIC-[feature].md
      Required sections: System Architecture (Mermaid), Module Breakdown, DB Design (ER + table list),
      API Endpoint List, Screen-to-API Mapping.
    TOOL HINTS: Read SRS first → Read SCREEN → Grep for existing similar modules in codebase.
    TASK BOUNDARIES:
      IN SCOPE — module list, table names + key columns + relations, endpoint list (method/URL/auth/description)
      NOT IN SCOPE — ORM decorators, DTO field details, service method signatures, class diagrams
```

---

## Phase 3a Enhanced — Voting Design

> Apply INSTEAD of standard Phase 3a when the feature has **8+ API endpoints OR 5+ new tables** (Large scope), OR when explicitly marked Critical by the orchestrator plan.

### V1 architect-agent (System / Data Model perspective)

```
Agent call 1 (background) → subagent_type: architect-agent
  FEATURE ID: [feature-name]
  MODE: BASIC_DESIGN
  PERSPECTIVE: System / Data Model
  OBJECTIVE: Design the BASIC spec from a data-model-first perspective.
    Focus on table relationships, domain entities, data flow between modules.
    Produce a complete BASIC design but save to docs/specs/basic-design/BASIC-[feature]-V1.md (NOT the final path).
  INPUT (read in this order):
    1. docs/specs/requirements/SRS-[feature].md
    2. docs/specs/requirements/SCREEN-[feature].md
    3. docs/ARCHITECTURE.md, docs/CODING_RULES.md
  OUTPUT FORMAT (MUST CREATE): docs/specs/basic-design/BASIC-[feature]-V1.md
    Required: same sections as standard BASIC template.
  TOOL HINTS: Read SRS → Grep for existing data models → design entity-first.
  TASK BOUNDARIES:
    IN SCOPE — module structure, entity model, DB table list, ER diagram, derived API endpoints
    NOT IN SCOPE — ORM decorators, DTO details, UI components
```

### V2 architect-agent (API / Integration perspective)

```
Agent call 2 (background) → subagent_type: architect-agent
  FEATURE ID: [feature-name]
  MODE: BASIC_DESIGN
  PERSPECTIVE: API / Integration
  OBJECTIVE: Design the BASIC spec from an API-contract-first perspective.
    Focus on endpoint contracts, request/response shapes, auth roles, and cross-module integration.
    Produce a complete BASIC design but save to docs/specs/basic-design/BASIC-[feature]-V2.md (NOT the final path).
  INPUT (read in this order):
    1. docs/specs/requirements/SRS-[feature].md
    2. docs/specs/requirements/SCREEN-[feature].md
    3. docs/API_DESIGN.md, docs/CODING_RULES.md
  OUTPUT FORMAT (MUST CREATE): docs/specs/basic-design/BASIC-[feature]-V2.md
    Required: same sections as standard BASIC template.
  TOOL HINTS: Read SRS → Read SCREEN → Grep for existing API patterns → design endpoint-first.
  TASK BOUNDARIES:
    IN SCOPE — API endpoint list, auth/role mapping, integration flow, derived table structure
    NOT IN SCOPE — ORM decorators, DTO details, UI implementation
```

### Voting Design — Synthesis instructions (orchestrator)

After both V1 and V2 agents return:

1. Read both V1 and V2 artifacts
2. Compare the two designs on these dimensions:
   - Table count and naming (prefer fewer, well-named tables)
   - API endpoint count and grouping (prefer REST-consistent grouping)
   - Conflicts between the two approaches (if any table/endpoint is present in one but not the other → include it)
   - Any design decision where V1 and V2 agree → adopt without discussion
   - Any design decision where they disagree → pick the approach with better justification, or flag for user
3. Write the final merged design to `docs/specs/basic-design/BASIC-[feature].md`
4. Present the synthesis to the user: highlight where the two perspectives differed and which approach was chosen
5. Pause for approval (G3a) → update PLAN T-03a → ✅ DONE

---

## Phase 3b — architect-agent (DETAIL_DESIGN)

```
Agent tool:
  subagent_type: "architect-agent"
  description: "Detail design (詳細設計) for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: DETAIL_DESIGN
    OBJECTIVE: Produce implementation-ready technical design so developer-agent can code
               directly from this document without making architectural decisions.
    INPUT (read in this order):
      1. docs/specs/basic-design/BASIC-[feature].md  ← READ FIRST — TECH must be consistent with BASIC
      2. docs/specs/requirements/SRS-[feature].md
      3. docs/specs/requirements/SCREEN-[feature].md
      4. docs/CODING_RULES.md, docs/API_DESIGN.md (if exist)
    OUTPUT FORMAT (MUST CREATE): docs/specs/detail-design/TECH-[feature].md
      Required sections: Full ORM schema, Module structure, Controller endpoints with DTOs,
      Service method signatures, Class diagram (Mermaid), Error handling table.
    TOOL HINTS: Read BASIC spec first → Read SRS → Grep codebase for ORM/DTO patterns.
    TASK BOUNDARIES:
      IN SCOPE — full ORM schema with decorators, service signatures, DTO validation, error codes
      NOT IN SCOPE — actual code implementation, UI wireframes (already in SCREEN spec)
```

---

## Phase 4 Pre — UTC (background)

```
Agent call 1 (background) → subagent_type: unit-test-agent
  MODE: CREATE (do not execute yet)
  COMPLEXITY: [Small | Medium | Large — from PLAN file sizing]
  OBJECTIVE: Create Unit Test Cases document so unit-test-agent (Mode B) can execute
             tests in Phase 6 without needing to ask clarifying questions.
  INPUT (read in this order — stop when you have enough context):
    1. docs/specs/detail-design/TECH-[feature].md  ← PRIMARY — read this first, always
    2. docs/TEST_VIEWPOINT.md        ← ISTQB technique requirements
    3. docs/CODING_RULES.md          ← only if TECH spec mentions auth guards or soft delete
    4. docs/API_DESIGN.md            ← only if endpoints are not fully described in TECH spec
    5. docs/ARCHITECTURE.md          ← only if cross-module RBAC flows are involved
  Output: docs/test-cases/UTC-[feature].md
  TOOL HINTS: Read TECH spec first. Only read further docs if TECH spec leaves gaps.
              For Large complexity: write layer by layer using Edit (append).
  TASK BOUNDARIES:
    IN SCOPE — test cases, ISTQB distribution, coverage matrix
    NOT IN SCOPE — executing tests, writing .spec files, modifying source code
```

---

## Phase 4 Pre — ITC (background)

```
Agent call 2 (background) → subagent_type: integration-test-agent
  MODE: CREATE (do not execute yet)
  COMPLEXITY: [Small | Medium | Large — from PLAN file sizing]
  OBJECTIVE: Create Integration Test Cases document so integration-test-agent (Mode B)
             can execute automation scripts in Phase 7 without clarifying questions.
  INPUT (read in this order — stop when you have enough context):
    1. docs/specs/detail-design/TECH-[feature].md  ← PRIMARY — read this first, always
    2. docs/specs/requirements/SRS-[feature].md   ← acceptance criteria for workflow coverage
    3. docs/TEST_VIEWPOINT.md        ← integration test strategy
    4. docs/specs/requirements/SCREEN-[feature].md ← only if feature has browser E2E flows
    5. docs/ARCHITECTURE.md          ← only if RBAC/multi-role flows are involved
  Output: docs/test-cases/ITC-[feature].md
  TOOL HINTS: Read TECH + SRS first. Only read SCREEN spec if E2E flows are needed.
              For Large complexity: write workflow by workflow using Edit (append).
  TASK BOUNDARIES:
    IN SCOPE — workflow scenarios, RBAC isolation, cross-module API chains
    NOT IN SCOPE — executing tests, writing Playwright/Cypress scripts, modifying source code
```

---

## Phase 4 Dev — developer-agent

### Standard spawn (SAFE batches, ≤150K estimated)

```
Agent tool → subagent_type: developer-agent
  CONTEXT BUDGET: SAFE (~[N]K estimated)
  OBJECTIVE: Implement all code deliverables in Batch-N so that code-review-agent can review
    without needing to ask clarifying questions. Work log must list every file created/modified
    with file path, change summary, and self-check results — this is the input for Step 4b.
  INPUT (read in this order):
    1. docs/specs/detail-design/TECH-[feature].md  ← primary spec — read THIS BATCH scope section first
    2. docs/specs/requirements/SCREEN-[feature].md  ← frontend component specs and UI states
    3. Existing source files for modules being modified (read before editing)
  OUTPUT FORMAT (MUST CREATE):
    - Code files: implement Batch-N scope only — no extra scope creep
    - docs/work-logs/DEV-[feature]-BN.md
      Required sections: Batch scope, Files created, Files modified, Self-review result,
      Self-check result (type check + tests), Context checkpoint.
  TOOL HINTS: Read TECH spec scope first → Grep codebase for existing patterns before writing
    new files → Read existing source before editing → Write/Edit code → Bash for tests/type-check.
  MANDATORY SELF-REVIEW: Before creating work-log, run self-review against docs/CODING-CHECKLIST.md.
    Record results in work-log § Self-Review Results. If checklist missing → report BLOCKED.
  TASK BOUNDARIES:
    IN SCOPE — implement files listed in Batch-N WBS row; run type check + affected tests
    NOT IN SCOPE — files from other batches; refactoring code outside batch scope;
      changing test configuration; modifying docs other than work log
```

### Pruned spawn (TIGHT batches, 150–200K estimated)

```
Agent tool → subagent_type: developer-agent
  CONTEXT BUDGET: TIGHT (~[N]K estimated)
  OBJECTIVE: [same as standard]
  INPUT (PRUNED — read ONLY what is listed, nothing else):
    1. docs/specs/detail-design/TECH-[feature].md — Sections: [list ONLY sections relevant to Batch-N modules]
    2. Source files to MODIFY: [explicit file list from WBS]
    3. Shared interfaces ONLY (not full source): [file path + export name for each shared dependency]
  DO NOT READ: docs/ARCHITECTURE.md, docs/API_DESIGN.md, docs/CODING_CONVENTION.md
    (already encoded in TECH spec — reading these wastes context budget)
  OUTPUT FORMAT: [same as standard]
  CHECKPOINT: MANDATORY after every sub-step (3 sub-steps for TIGHT: data → service → controller/FE).
    If remaining scope ≥ 4 files after completing a sub-step, return STATUS: PARTIAL.
  TOOL HINTS: [same as standard]
  TASK BOUNDARIES: [same as standard]
```

### Continuation spawn (after PARTIAL return from Batch-N)

```
Agent tool → subagent_type: developer-agent
  CONTEXT BUDGET: SAFE (~[N]K estimated, continuation — reduced scope)
  OBJECTIVE: Continue Batch-N implementation. Complete remaining scope from partial work log.
  CONTINUATION OF: docs/work-logs/DEV-[feature]-BN.md (read "Remaining scope" + "Key decisions")
  INPUT (PRUNED):
    1. docs/specs/detail-design/TECH-[feature].md — Sections: [only sections for remaining modules]
    2. Source files to MODIFY: [remaining file list from partial work log]
  OUTPUT FORMAT:
    - Code files: implement remaining scope only
    - docs/work-logs/DEV-[feature]-BN.1.md (continuation work log)
  TASK BOUNDARIES:
    IN SCOPE — remaining files from Batch-N partial; run type check + affected tests
    NOT IN SCOPE — files already completed in Batch-N original
```

---

## Phase 4 Review — code-review-agent

```
Agent tool → subagent_type: code-review-agent
  OBJECTIVE: Review Batch-N implementation against the TECH spec and coding rules.
    Produce a REVIEW report with clear PASS or FAIL verdict and actionable findings so that
    developer-agent can fix issues in the next round without ambiguity.
  INPUT (read in this order):
    1. docs/work-logs/DEV-[feature]-BN.md  ← scope list of files for THIS batch
    2. docs/specs/detail-design/TECH-[feature].md  ← spec to verify against
    3. docs/CODING_RULES.md, docs/CODING_CONVENTION.md  ← standards to enforce
    4. Source files listed in work log  ← actual code to review
  OUTPUT FORMAT (MUST CREATE): docs/reviews/REVIEW-[feature]-BN.md
    Required sections: Score Summary table (5 dimensions × weighted score),
    Findings by severity (Critical/Major/Minor), Verdict (PASS / FAIL / CONDITIONAL PASS).
  TOOL HINTS: Read work log first to get file list → Read each source file → Grep for
    patterns (soft delete, auth guards, pagination) → do NOT run Bash during review.
  PRECONDITION CHECK: Verify docs/CODING-CHECKLIST.md exists. If missing → report BLOCKED.
  AUDIT AGAINST: docs/CODING-CHECKLIST.md (primary) + docs/_templates/CODE-REVIEW-CHECKLIST.md (methodology)
  TASK BOUNDARIES:
    IN SCOPE — files listed in Batch-N work log; verify spec compliance, security, performance
    NOT IN SCOPE — files from other batches; test execution; architecture changes;
      implementing fixes (review only — fixes are done by developer-agent in next round)
```

---

## Phase 4 Fix — developer-agent (fix round)

```
Agent tool → subagent_type: developer-agent
  TASK: Fix review findings for Batch-N
  INPUT: docs/reviews/REVIEW-[feature]-BN.md (Critical + Major sections)
  Fix all Critical (mandatory) + Major findings (should fix).
  Update docs/work-logs/DEV-[feature]-BN.md with fixes applied.
```

---

## Phase 4 UTC Fallback (foreground re-spawn)

```
Agent tool → subagent_type: unit-test-agent
  MODE: CREATE (background spawn did not complete — foreground re-spawn)
  COMPLEXITY: [Small | Medium | Large]
  INPUT: 1. docs/specs/detail-design/TECH-[feature].md  2. docs/TEST_VIEWPOINT.md
  OUTPUT ARTIFACT (MUST CREATE): docs/test-cases/UTC-[feature].md
  For Large: write layer by layer using Edit (append).
```

---

## Phase 4 ITC Fallback (foreground re-spawn)

```
Agent tool → subagent_type: integration-test-agent
  MODE: CREATE (background spawn did not complete — foreground re-spawn)
  COMPLEXITY: [Small | Medium | Large]
  INPUT: 1. docs/specs/detail-design/TECH-[feature].md  2. docs/specs/requirements/SRS-[feature].md
  OUTPUT ARTIFACT (MUST CREATE): docs/test-cases/ITC-[feature].md
  For Large: write workflow by workflow using Edit (append).
```

---

## Phase 5 — security-tester-agent

```
Agent tool:
  subagent_type: "security-tester-agent"
  description: "Security scan for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: Mode A (Feature Scan)
    INPUT:
      - docs/reviews/REVIEW-[feature]-[date].md (reviewed files list)
      - docs/specs/detail-design/TECH-[feature].md
    OUTPUT ARTIFACT (MUST CREATE): docs/security/SEC-[feature]-[YYYYMMDD].md
    Scan: source code, API endpoints, database models, config files.
```

---

## Phase 6 — unit-test-agent (EXECUTE)

```
Agent tool:
  subagent_type: "unit-test-agent"
  description: "Execute unit tests R[n] for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: EXECUTE
    ROUND: R[n]
    INPUT: docs/test-cases/UTC-[feature].md
    OUTPUT ARTIFACT (MUST CREATE): docs/test-reports/UTR-[feature]-R[n].md
    Run test commands from PROJECT.md Build Commands section.
    Log bug reports in UTR document (section "Bug Reports").
```

---

## Phase 6 Bug Fix — bug-fix-agent

```
Agent tool (when UTR FAIL):
  subagent_type: "bug-fix-agent"
  description: "Fix unit test failures R[n]"
  prompt: |
    INPUT: docs/test-reports/UTR-[feature]-R[n].md (section "Bug Reports")
    Fix all bugs in the list.
    Create docs/bug-reports/BUG-[YYYYMMDD]-[nn].md for each bug.
    After fixing: run tests locally to verify before reporting done.
```

---

## Phase 7 — integration-test-agent (EXECUTE)

```
Agent tool:
  subagent_type: "integration-test-agent"
  description: "Execute integration tests R[n] for [feature]"
  prompt: |
    FEATURE ID: [feature-name]
    MODE: EXECUTE
    ROUND: R[n]
    INPUT: docs/test-cases/ITC-[feature].md
    OUTPUT ARTIFACT (MUST CREATE): docs/test-reports/ITR-[feature]-R[n].md
    Run integration test commands from PROJECT.md Build Commands section.
```

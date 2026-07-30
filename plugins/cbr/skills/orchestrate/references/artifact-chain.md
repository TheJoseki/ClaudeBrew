# Artifact Chain, Protocols & Templates

> Reference for orchestrator-agent. Loaded on-demand for artifact tracking, interrupts, and protocols.

## Artifact Chain

| Phase | Agent | Output Artifact |
|-------|-------|-----------------|
| 0 | orchestrator (self) | `docs/plans/PLAN-[f]-[YYYYMMDD].md` |
| 0-council | ba-agent (PLANNING) | `docs/plans/COUNCIL-[f]-BA.md` |
| 0-council | architect-agent (PLANNING) | `docs/plans/COUNCIL-[f]-ARCH.md` |
| 1 | ba-agent | `docs/specs/requirements/SRS-[f].md` |
| 2 | ui-designer-agent | `docs/specs/requirements/SCREEN-[f].md` |
| 3a | architect-agent (BASIC) | `docs/specs/basic-design/BASIC-[f].md` |
| 3b | architect-agent (DETAIL) | `docs/specs/detail-design/TECH-[f].md` |
| 4-dev | developer-agent | code + `docs/work-logs/DEV-[f]-B[n].md` |
| 4-rev | code-review-agent | `docs/reviews/REVIEW-[f]-B[n].md` |
| 4b | unit-test-agent | `docs/test-cases/UTC-[f].md` (background) |
| 4c | integration-test-agent | `docs/test-cases/ITC-[f].md` (background) |
| 5 | security-tester-agent | `docs/security/SEC-[f]-[date].md` |
| 6 | unit-test-agent | `docs/test-reports/UTR-[f]-R[n].md` |
| 7 | integration-test-agent | `docs/test-reports/ITR-[f]-R[n].md` |
| BUG | bug-fix-agent | `docs/bug-reports/BUG-[id].md` + fixed code |

---

## Interrupt Protocol

When unplanned task arrives during active execution:

**I-1: Checkpoint** — Write `## Checkpoint` to active PLAN:
```markdown
## Checkpoint — [YYYY-MM-DDTHH:MM:SSZ]
- Phase: [current], Batch: [if in Phase 4]
- Completed: [list]
- In Progress: [current work + % complete]
- Context files loaded: [list]
- Pending decisions: [list]
```

**I-2: Suspend** — Update PLAN-REGISTRY: Status → ⏸️ SUSPENDED

**I-3: Create interrupt plan** — `plan_type: HOTFIX/INTERRUPT`, `parent: [suspended-plan]`

**I-4: Execute** — Context-inject → spawn agents. Write `## Impact Notes` to parent PLAN if scope affected.

**I-5: Resume** — Mark interrupt COMPLETED → read parent checkpoint + impact → update specs → resume.

---

## Scope Change Protocol

1. Update PLAN Summary section
2. Update sizing tier if changed
3. Append Scope Change Log entry
4. Re-estimate batch assignments if ≥3 new items
5. Update memory

---

## Shared Context File

After PLAN creation, create and maintain `docs/agent-comms/SHARED-CONTEXT.md`:

```markdown
# Shared Context — [feature-name]
## Project
- Tech stack: [from PROJECT.md]
- PLAN file: docs/plans/PLAN-[feature]-[date].md
## SDLC Status
- Current phase: [phase]
- Last gate: [gate] ✅ [date]
## Open Issues
- HIGH/CRITICAL bugs: [count or IDs]
## Key Decisions
- [list]
```

---

## Bug Severity Flag Protocol

When HIGH/CRITICAL bug filed:
1. Update PLAN: `⚠️ Open HIGH bug: [BUG-ID]`
2. Update SHARED-CONTEXT open issues
3. If G8 approaching: note `G8 blocked until [BUG-ID] resolved`

---

## Post-Phase Diagnostic (optional)

After each gate, append diagnostic to PLAN:

```markdown
### Diagnostic: Phase [N] — [Phase Name]
| Question | Answer | Action? |
|----------|--------|---------|
| Agent prompt clear enough? | Y/N | |
| Scope mismatch? | Y/N | |
| Round count? | R[n] | R3+ = trouble |
```

---

## Deliverable Inventory Auto-Update

After each batch PASS: update PENDING deliverables → DONE in PLAN Deliverable Inventory.

---

## Step 1–3 Spawn Templates

### Step 1: ba-agent
```
subagent_type: "ba-agent"
prompt: FEATURE ID: [f] | TASK: Write SRS
  INPUT: docs/plans/PLAN-[f]-[date].md
  OUTPUT: docs/specs/requirements/SRS-[f].md
```
After: Read SRS → present → user approval → enumerate deliverables → fill Inventory → G1 ✅

### Step 2: ui-designer-agent
```
subagent_type: "ui-designer-agent"
prompt: FEATURE ID: [f] | TASK: Design deliverables
  INPUT: docs/specs/requirements/SRS-[f].md
  OUTPUT: docs/specs/requirements/SCREEN-[f].md
```
After: Read → present → approval → G2 ✅

### Step 3a: architect-agent (BASIC_DESIGN)
```
subagent_type: "architect-agent"
prompt: MODE: BASIC_DESIGN
  INPUT: SRS + SCREEN + CODING_RULES + ARCHITECTURE
  OUTPUT: docs/specs/basic-design/BASIC-[f].md
  IN SCOPE: module structure, table names, endpoint list
  NOT IN SCOPE: ORM decorators, DTOs, service signatures
```
After: Read → present → G3a ✅

### Step 3b: architect-agent (DETAIL_DESIGN)
```
subagent_type: "architect-agent"
prompt: MODE: DETAIL_DESIGN
  INPUT: BASIC (read FIRST) + SRS + SCREEN + CODING_RULES + API_DESIGN
  OUTPUT: docs/specs/detail-design/TECH-[f].md
  IN SCOPE: full ORM schema, service methods, DTOs, error codes
  NOT IN SCOPE: actual code, UI wireframes
```
After: Read → present → G3b ✅ → enumerate modules → fill Dev Batches → sizing

### Step 3c: G3c Gate — TEST_VIEWPOINT
1. Read `docs/TEST_VIEWPOINT.md` § Section 0
2. Verify: exists + APPROVED + production-equivalent DB + no placeholders
3. Present to user → approval → update status to ✅ APPROVED

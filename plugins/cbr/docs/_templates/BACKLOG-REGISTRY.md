---
type: BACKLOG
last_updated: YYYY-MM-DDTHH:MM:SSZ
---

# Backlog Registry

> Tracks tất cả carry-forward items across waves/features: NF code review findings, deferred items, retro action items, security findings.

## Open Items

| ID | Source | Type | Description | Priority | Target | Status |
|----|--------|------|-------------|----------|--------|--------|
| <!-- BL-001 | REVIEW-[feature]-R[n] NF-XX | CODE_QUALITY | Description | LOW/MEDIUM/HIGH | Wave N+1 | ⏳ OPEN / ✅ RESOLVED / ❌ WONTFIX --> |

## Source Type Legend

| Type | Auto-Created By | Description |
|------|----------------|-------------|
| CODE_QUALITY | code-review-agent | Non-functional findings (Minor/Info) deferred from review |
| SECURITY | security-tester-agent | Low/Info findings deferred from SEC report |
| PROCESS | retro skill output | Action items from retrospectives |
| DESIGN_DEBT | developer-agent | Spec deviations documented in work-log |
| BUG_DEFERRED | bug-fix-agent | Bugs deprioritized within current wave |
| RISK | orchestrator-agent / any | Materialized risks from risk register (CAR created) |
| CHECKLIST_UPDATE | any agent | New patterns discovered that need checklist addition |

## Rules

1. code-review-agent: Auto-append NF findings as CODE_QUALITY items
2. security-tester-agent: Auto-append Low/Info findings as SECURITY items
3. retro skill: Auto-append action items as PROCESS items
4. developer-agent: Auto-append spec deviations as DESIGN_DEBT items
5. Orchestrator: When creating new PLAN, MUST read this backlog and incorporate relevant items into WBS
6. Dedup: Before appending, check if similar item already exists — UPDATE if refinement, skip if duplicate
7. Any agent: Append materialized risks as RISK items (source: CAR-[ref])
8. Any agent: Append new checklist patterns as CHECKLIST_UPDATE items

---
type: REGISTRY
last_updated: YYYY-MM-DDTHH:MM:SSZ
---

# Plan Registry

> Single source of truth cho tất cả plan trong dự án. Orchestrator MUST update file này khi tạo, suspend, complete, hoặc resume bất kỳ plan nào.

## Active Plans

| Plan ID | Feature | Type | Parent | Status | Phase | Priority | Created |
|---------|---------|------|--------|--------|-------|----------|---------|
| <!-- PLAN-[feature]-[YYYYMMDD] | Feature Name | EPIC/WAVE/FEATURE/HOTFIX/INTERRUPT | parent-id or — | ACTIVE/SUSPENDED/COMPLETED | P0-P8 | CRITICAL/HIGH/MEDIUM/LOW | YYYY-MM-DD --> |

## Suspended Plans (need resume)

| Plan ID | Suspended At | Reason | Resume Prereq |
|---------|-------------|--------|---------------|
| <!-- Populated when a plan is suspended via Interrupt Protocol --> |

## Plan Type Definitions

| Type | Description | Typical Lifetime |
|------|-------------|-----------------|
| EPIC | Multi-wave master plan | Weeks–months |
| WAVE | Deliverable batch within EPIC | Days–1 week |
| FEATURE | Standalone feature | Days |
| HOTFIX | Urgent fix, interrupts current work | Hours–1 day |
| INTERRUPT | Unplanned work (demo, assessment) | Hours–1 day |

## Rules

1. Orchestrator MUST update this file when creating, suspending, completing, or resuming any plan
2. New plan MUST declare `parent` if it relates to an existing EPIC/WAVE
3. HOTFIX/INTERRUPT type MUST trigger Interrupt Protocol (suspend parent plan)
4. Context injector reads this file FIRST — agents know full plan landscape before starting work

---
type: LEDGER
last_updated: YYYY-MM-DDTHH:MM:SSZ
---

# Decision Ledger

> Append-only log của tất cả architectural & business decisions across all features. Mỗi council session, mỗi developer deviation MUST append vào đây.

## Decisions

| ID | Date | Source | Domain | Decision | Rationale | Supersedes | Status |
|----|------|--------|--------|----------|-----------|------------|--------|
| <!-- D-001 | YYYY-MM-DD | COUNCIL-[feature]-ARCH | domain-tag | Decision text | Why | — or D-XXX | ✅ ACTIVE / ❌ SUPERSEDED / ⚠️ CONTESTED / 🔄 NEEDS RESOLUTION --> |

## Domain Index (for RAG retrieval)

| Domain Tag | Active Decisions | Key Decision |
|------------|-----------------|--------------|
| <!-- domain-tag | D-001, D-002 | Summary of key decision --> |

## Status Definitions

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| ✅ ACTIVE | Current, valid decision | None — follow this |
| ❌ SUPERSEDED | Replaced by newer decision | Follow the superseding decision |
| ⚠️ CONTESTED | Spec says X, implementation says Y | Orchestrator must triage |
| 🔄 NEEDS RESOLUTION | Multiple valid options, no consensus | User decision required |

## Rules

1. Every council MUST append decisions after writing COUNCIL artifact
2. Every developer deviation from spec MUST create a CONTESTED decision
3. Before starting a new council, ba-agent and architect-agent MUST read this ledger (filter by relevant domain tags)
4. Superseded decisions MUST reference what replaces them (traceable chain)
5. Domain Index is maintained by the agent that appends — add/update domain tag grouping

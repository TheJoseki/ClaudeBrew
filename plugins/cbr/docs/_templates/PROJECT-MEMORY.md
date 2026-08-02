---
type: PROJECT_MEMORY
last_updated: YYYY-MM-DDTHH:MM:SSZ
---

# Project Memory

> Learned patterns mà agents phát hiện trong quá trình thực thi — những điều không hiển nhiên mà agent tương lai nên biết. Không phải decisions (→ DECISION-LEDGER) hay backlog (→ BACKLOG-REGISTRY).

## Tech Stack Learnings

| ID | Date | Agent | Learning | Confidence |
|----|------|-------|----------|------------|
| <!-- TL-001 | YYYY-MM-DD | agent-name | Non-obvious learning about tech stack | HIGH/MEDIUM/LOW --> |

## Testing Patterns

| ID | Date | Agent | Pattern | Applies To |
|----|------|-------|---------|-----------|
| <!-- TP-001 | YYYY-MM-DD | agent-name | Testing pattern discovered | Scope (FE/BE/E2E) --> |

## Domain Model Insights

| ID | Date | Agent | Insight |
|----|------|-------|---------|
| <!-- DM-001 | YYYY-MM-DD | agent-name | Non-obvious domain knowledge --> |

## Confidence Levels

| Level | Meaning |
|-------|---------|
| HIGH | Verified in production or confirmed by multiple agents |
| MEDIUM | Worked in dev/test environment |
| LOW | Theoretical or unverified — use with caution |

## Rules

1. Only save NON-OBVIOUS, REUSABLE patterns — not trivial facts or general programming knowledge
2. Mem0-style dedup: EXTRACT → SEARCH existing entries → CLASSIFY (NOOP/UPDATE/ADD/SUPERSEDE) → WRITE
3. Context injector filters by `Applies To` and agent role when retrieving
4. Staleness check: If entry references a file/function, verify it still exists before trusting

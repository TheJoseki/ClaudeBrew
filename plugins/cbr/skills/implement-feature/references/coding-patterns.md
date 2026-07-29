# Coding Patterns Reference — Developer Agent

> Reference for developer-agent. Loaded on-demand for framework-specific implementation patterns.

## Backend Coding Standards

Apply the backend framework's module/layer pattern from PROJECT.md. General principles:

- **Thin controllers**: only route mapping + delegation, no business logic
- **Services**: all business logic + data queries + error handling
- **DTOs**: input validation decorators on all input fields
- **API documentation**: decorators on all endpoints
- **Guards**: authentication + authorization guards on all protected endpoints
- **Soft delete**: apply soft delete filter in all data queries (per PROJECT.md convention)
- **Audit columns**: populate create/update tracking columns on mutations

### Controller Pattern (adapt to detected framework)

```
- Route handler receives validated input (via DTO/schema)
- Delegates to service immediately
- Returns service result
- All endpoints decorated with API docs and guards
```

### Service Pattern (adapt to detected framework)

```
- Query with soft delete filter
- Pagination: skip/take with page + pageSize
- Return { data, total, page, pageSize } for list endpoints
- Throw appropriate HTTP exceptions for error cases
```

---

## Frontend Coding Standards

Apply the frontend framework's component pattern from PROJECT.md. General principles:

- **Composition pattern**: use the framework's composition/hooks API (not class/options API where avoidable)
- **TypeScript strict**: no `any` type
- **All user-facing text via i18n**: no hardcoded strings
- **UI library components**: use the project's UI library (detect from PROJECT.md)
- **State management**: use the project's state management library

### Component Pattern (adapt to detected framework)

```
- Import i18n, state store, and utilities at top
- Define reactive state variables
- Load data on mount
- Template uses UI library components
- All text via $t('key') or equivalent i18n call
```

---

## Effort Scaling by Batch Size

| Batch Size | File Count | Approach |
|------------|-----------|----------|
| Small | 1–3 files | Implement all at once → single self-check at end |
| Medium | 4–6 files | Implement in 2 sub-steps (data/service layer first, then controller/frontend) → check between sub-steps |
| Large | 7+ files | Implement in 3 sub-steps → write a Context Checkpoint to work log after each sub-step |

If batch is **Large AND feature is Complex**: note in Implementation Notes section recommending the orchestrator split this into 2 batches for future features of this scale.

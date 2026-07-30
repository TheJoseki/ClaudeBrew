# ITC Document Template

Use this template when creating `docs/test-cases/ITC-[feature].md`.

```markdown
# Integration Test Cases: [Feature]
Date: [YYYY-MM-DD] | Author: integration-test-agent
Integration test framework: [detected from PROJECT.md]
E2E test framework: [detected from PROJECT.md — e.g. Playwright, Cypress, Selenium]

## Test Scope
| Workflow | Actors | Endpoints/Actions |
|----------|--------|------------------|

## Test Cases
### TC-IT-[feature]-001: [Name]
- Workflow: | Priority: High | Actors: [roles]
- Precondition: | Steps: | Expected:
- Category: Happy path / Negative / Permission

## Workflow Test Matrix
| Workflow | TC IDs | AC IDs |
|----------|--------|--------|
```

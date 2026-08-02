# Project Walkthrough — [PROJECT_NAME]

> **Phase**: [Prototype / MVP / Production]
> **Start Date**: [YYYY-MM-DD]
> **Target Completion**: [YYYY-MM-DD]

---

## Sprint Status

| Sprint | Goal | Status | Notes |
|--------|------|--------|-------|
| Sprint 0 | Foundation Setup | PENDING | |
| Sprint 1 | [MODULE_1] | PENDING | |
| Sprint 2 | [MODULE_2] | PENDING | |
| Sprint 3 | [WORKFLOW] | PENDING | |
| Sprint 4 | [ADMIN_MODULE] | PENDING | |
| Sprint 5 | Profile & Settings | PENDING | |
| Sprint 6 | Polish & Testing | PENDING | |
| Sprint 7 | Final Delivery | PENDING | |

Status legend: `PENDING` | `IN_PROGRESS` | `COMPLETED` | `BLOCKED`

---

## Per-Sprint Checkpoints

### Sprint 0: Foundation Setup

- [ ] [BACKEND_FRAMEWORK] project scaffold created
- [ ] [FRONTEND_FRAMEWORK] project scaffold created
- [ ] Database connection verified
- [ ] Auth endpoint returns JWT tokens
- [ ] Test runner configured and executing
- [ ] ESLint configured
- [ ] `.env.example` created

### Sprint 1: [MODULE_1]

**Backend**:
- [ ] ORM schema defined and migrated
- [ ] DTOs created with validation decorators
- [ ] Service: list, create, update, soft delete working
- [ ] Controller: all endpoints with auth guards
- [ ] Soft delete filter (`DeleteFlag: '0'`) in all queries
- [ ] Audit columns set on create/update

**Frontend**:
- [ ] TypeScript types defined
- [ ] API service created
- [ ] Pinia store created
- [ ] List view displays data with pagination
- [ ] Create/edit form working
- [ ] Delete with confirmation dialog
- [ ] Empty state on no data
- [ ] i18n keys added ([LANG_1] + [LANG_2])

**Tests**:
- [ ] Service unit tests pass
- [ ] Store unit tests pass

### Sprint 2: [MODULE_2]

- [ ] [CHECKLIST_ITEM_1]
- [ ] [CHECKLIST_ITEM_2]
- [ ] [CHECKLIST_ITEM_N]

### Sprint 3: [WORKFLOW]

- [ ] [WORKFLOW_STEP_1] works end-to-end
- [ ] [WORKFLOW_STEP_2] works end-to-end
- [ ] Status transitions enforced
- [ ] Invalid transitions return errors

### Sprint 4: [ADMIN_MODULE]

- [ ] Admin-only endpoints return 403 for non-admin
- [ ] Admin can list, create, update, delete
- [ ] Activity logging records actions

### Sprint 5: Profile & Settings

- [ ] User can view profile
- [ ] User can update editable fields
- [ ] Password change validation enforced
- [ ] Avatar upload working (if applicable)

### Sprint 6: Polish & Testing

- [ ] All views have empty states
- [ ] All async operations have loading indicators
- [ ] Error toasts appear on API failures
- [ ] Form validation shows inline errors
- [ ] Layout responsive on tablet
- [ ] Language switcher works (if applicable)
- [ ] `npx tsc --noEmit` passes
- [ ] `npx vue-tsc --noEmit` passes
- [ ] Backend coverage >= 80%
- [ ] Frontend coverage >= 80%
- [ ] ESLint: 0 errors

### Sprint 7: Final Delivery

- [ ] All user stories from requirements pass walkthrough
- [ ] No P1 bugs outstanding
- [ ] Work logs created for all features
- [ ] Release tagged

---

## User Story Coverage

[CUSTOMIZE: list your user stories]

| ID | User Story | Module | Status |
|----|-----------|--------|--------|
| US-01 | As [ROLE], I want to [ACTION] so that [BENEFIT] | [MODULE] | PENDING |
| US-02 | As [ROLE], I want to [ACTION] so that [BENEFIT] | [MODULE] | PENDING |
| US-N | As [ROLE], I want to [ACTION] so that [BENEFIT] | [MODULE] | PENDING |

---

## Inventory Summary

| Category | Planned | Actual | Status |
|----------|---------|--------|--------|
| Screens | [N] | 0 | 0% |
| API Endpoints | [N] | 0 | 0% |
| ORM Models | [N] | 0 | 0% |
| Backend Unit Tests | [N] | 0 | 0% |
| Frontend Unit Tests | [N] | 0 | 0% |
| Integration Tests | [N] | 0 | 0% |
| i18n Keys ([LANG_1]) | [N] | 0 | 0% |
| i18n Keys ([LANG_2]) | [N] | 0 | 0% |

---

## Bug Tracker

| Bug ID | Sprint | Severity | Description | Status |
|--------|--------|----------|-------------|--------|
| — | — | — | No bugs yet | — |

---

## Blockers & Decisions

| Date | Item | Decision | Resolved |
|------|------|----------|---------|
| [DATE] | [BLOCKER_DESCRIPTION] | [DECISION_MADE] | Yes/No |

---

## Known Limitations (Prototype Phase)

- Mock data used — no real backend calls (if prototype)
- [LIMITATION_1]
- [LIMITATION_2]
- [LIMITATION_N]

---

## Demo Script

### Pre-conditions
- Application running at `[APP_URL]`
- Test users seeded: [LIST_TEST_USERS]

### Demo Flow

1. **Login** as [ROLE_1]
   - Navigate to `/login`
   - Enter credentials
   - Verify redirect to dashboard

2. **[MODULE_1] Walkthrough**
   - Navigate to `/[module1]`
   - [STEP_1]
   - [STEP_2]
   - Verify [EXPECTED_RESULT]

3. **[MODULE_2] Walkthrough**
   - [DEMO_STEPS]

4. **[WORKFLOW] Demo**
   - [STEP_1]
   - Switch to [ROLE_2] account
   - [STEP_2]
   - Verify final state

5. **Admin Features**
   - Login as [ADMIN_ROLE]
   - Navigate to `/admin/[module]`
   - [ADMIN_DEMO_STEPS]

6. **Logout**
   - Verify session cleared
   - Verify protected routes redirect to login

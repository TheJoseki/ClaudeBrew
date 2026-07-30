# Integration Test Script Templates

> Reference for integration-test-agent Mode B. Loaded on-demand when creating test scripts.

## Playwright E2E Script Template

File: `tests/e2e/[feature].spec.ts`

```typescript
import { test, expect, Page } from '@playwright/test';

// Test data factory — isolate per test
const createTestData = async () => ({
  user: { email: `test-${Date.now()}@example.com`, password: 'Test@1234' },
  // ... other seed data
});

test.describe('[Feature] — E2E workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and authenticate
    await page.goto('/login');
    // seed data via API before each test
  });

  test.afterEach(async ({ request }) => {
    // cleanup: delete test data via API
  });

  test('should complete [workflow] happy path', async ({ page }) => {
    // 1. Navigate to feature screen
    await page.goto('/[feature-route]');
    await expect(page).toHaveTitle(/[expected title]/);

    // 2. Interact with UI
    await page.getByRole('button', { name: /create/i }).click();
    await page.getByLabel('Field Name').fill('value');

    // 3. Submit
    await page.getByRole('button', { name: /submit/i }).click();

    // 4. Verify success state
    await expect(page.getByText('Success message')).toBeVisible();

    // 5. Verify data in list
    await expect(page.getByRole('row', { name: /created item/ })).toBeVisible();
  });

  test('should show 403 when wrong role accesses [feature]', async ({ page }) => {
    // login as wrong role
    // attempt to access protected route
    // assert redirect or 403 response
  });
});
```

## Supertest/API Integration Script Template

File: `tests/integration/[feature].test.ts`

```typescript
describe('[Feature] Integration — API workflows', () => {
  let app: any;
  let tokens: Record<string, string> = {};

  beforeAll(async () => {
    // Start test server / connect to test DB
    // Seed: create users for each role
    // Authenticate each role and store tokens
  });

  afterAll(async () => {
    // cleanup: delete all test data
    // disconnect DB / stop server
  });

  afterEach(async () => {
    // reset feature-specific data between tests
  });

  describe('Happy path', () => {
    it('should [workflow] end-to-end', async () => {
      // Step 1: Create resource
      const createRes = await request(app)
        .post('/api/[endpoint]')
        .set('Authorization', `Bearer ${tokens.admin}`)
        .send({ /* payload */ });
      expect(createRes.status).toBe(201);
      const id = createRes.body.id;

      // Step 2: Advance workflow
      const advanceRes = await request(app)
        .patch(`/api/[endpoint]/${id}/[action]`)
        .set('Authorization', `Bearer ${tokens.manager}`)
        .send({ /* payload */ });
      expect(advanceRes.status).toBe(200);
      expect(advanceRes.body.status).toBe('[expected status]');

      // Step 3: Verify final state
      const getRes = await request(app)
        .get(`/api/[endpoint]/${id}`)
        .set('Authorization', `Bearer ${tokens.admin}`);
      expect(getRes.body.status).toBe('[final status]');
    });
  });

  describe('RBAC isolation', () => {
    it('should return 403 when wrong role calls [endpoint]', async () => {
      const res = await request(app)
        .post('/api/[admin-endpoint]')
        .set('Authorization', `Bearer ${tokens.viewer}`);
      expect(res.status).toBe(403);
    });

    it('should return 401 without token', async () => {
      const res = await request(app).get('/api/[protected-endpoint]');
      expect(res.status).toBe(401);
    });
  });

  describe('Soft delete', () => {
    it('should not return deleted record in list', async () => {
      // create → delete → list → assert absent
    });
  });
});
```

## Execution Commands

```bash
# Playwright E2E
npx playwright test tests/e2e/[feature].spec.ts --reporter=html

# Cypress E2E
npx cypress run --spec "cypress/e2e/[feature].cy.ts"

# Supertest/API integration
[backend test command from PROJECT.md] --testPathPattern=tests/integration/[feature]
```

**IMPORTANT**: You MUST run actual test commands and capture real output.
- Do NOT fabricate pass results
- If tests fail: capture the actual error messages
- Playwright: save screenshots/videos on failure (auto with `--reporter=html`)
- Report actual pass rate in ITR document

## Execution Process (R1→R5)

| Round | Trigger | Expected Pass Rate |
|-------|---------|-------------------|
| R1 | First run after Code Review PASS | Baseline |
| R2 | After bug-fix-agent fixes R1 failures | ≥70% |
| R3 | After bug-fix-agent fixes R2 failures | ≥90% |
| R4 | Full regression | ≥95% |
| R5 | Final verification | 100% — GATE |

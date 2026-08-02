---
feature: claudekit-portal
type: TEST_VIEWPOINT
version: 1.0
status: ACTIVE
date: 2026-03-22
author: qa-architect
gate: G3c
---

# Test Viewpoint — ClaudeKit Portal

> **Methodology**: ISTQB CTFL 4.0 · ISO/IEC 25010:2023
> **Reference SRS**: `docs/specs/requirements/SRS-claudekit-portal.md` (FR-01..FR-27, NFR-P01..NFR-S10, BR-01..BR-10)
> **Reference Design**: `docs/specs/detail-design/TECH-claudekit-portal.md` (module contracts, TypeScript interfaces, security guards)
> **Package**: d9-claude-kit v3.1.0 → v3.2.0

---

## 1. Test Strategy Overview

### 1.1 Test Pyramid

```
                    ╔═══════════════════════════╗
                    ║    E2E / Browser Tests     ║  <- 10–15 critical user journeys
                    ║      Playwright            ║     Real server + real browser
                    ╠═══════════════════════════╣
                ╔═══╩═══════════════════════════╩═══╗
                ║   API Integration Tests            ║  <- All 12 endpoints + SSE
                ║   Vitest + Fastify inject()        ║     Mocked PTY; real filesystem
                ╠═══════════════════════════════════╣
            ╔═══╩═══════════════════════════════════╩═══╗
            ║       Unit Tests                          ║  <- Server modules + FE hooks/stores
            ║   Vitest (BE: Node env) + Vitest+RTL (FE) ║     All I/O mocked
            ╚═══════════════════════════════════════════╝
```

### 1.2 Shift-Left Approach

Test cases (UTC / ITC) are created **in parallel** with implementation (Phase 4), not after. Per ClaudeKit SDLC:

- unit-test-agent runs in **Mode A** (create UTC document) concurrently with developer-agent during BE-B1 and BE-B2 spawns.
- integration-test-agent runs in **Mode A** (create ITC document) concurrently with developer-agent.
- Test execution (Mode B) follows after code review (G4 gate passes).

Security test inputs defined in Section 4 are mandatory additions to both UTC and ITC — they must not be deferred to a manual security review alone.

### 1.3 Quality Gates Mapping

| Gate | Test Layer | Trigger | Pass Criteria |
|------|-----------|---------|---------------|
| G6 | Unit Tests (UTC → UTR) | After G4 code review passes all 4 batches | BE ≥ 85% statement coverage; FE ≥ 75% statement coverage; 100% test pass rate ≤ R5 rounds |
| G7a | API Integration (ITC → ITR) | After G6 passes | 100% endpoint coverage (all 12 endpoints including SSE); 100% pass rate ≤ R5 |
| G7b | E2E Browser Tests (Playwright) | After G7a passes | All mandatory journeys (Section 2.3) pass; 100% pass rate ≤ R5 |
| G5a | Security scan | After G4 passes | 0 Critical, 0 High OWASP findings; path traversal variants confirmed blocked |
| G5b | Pre-delivery re-scan | After G7b passes | 0 Critical, 0 High confirmed clean |

### 1.4 Test Round Process (ISTQB R1 → R5)

| Round | Scope | Pass Rate Target | Focus |
|-------|-------|-----------------|-------|
| R1 | Execute all TCs | Baseline | Identify initial failures; environment setup issues |
| R2 | Re-run after fixes | ≥ 70% | Bug fixes from R1; targeted regression |
| R3 | Re-run remaining failures | ≥ 90% | Edge case resolution; regression check |
| R4 | Full regression | ≥ 95% | Stability; no new regressions introduced |
| R5 | Final verification | 100% | Release readiness; G6/G7a/G7b gate sign-off |

Maximum R5 rounds per phase. If R5 is exceeded, escalate to user with specific failure details — do not silently lower the pass bar.

---

## 2. Test Layers

### 2.1 Unit Tests (G6)

**Tool**: Vitest (matches ESM/CJS module system used by portal Node.js server and Vite-based frontend)
**Runner (BE)**: `npx vitest run --coverage --config vitest.config.ts`
**Runner (FE)**: `npx vitest run --coverage --config portal-src/vitest.config.ts`
**Coverage gate**: BE ≥ 85% statement coverage; FE ≥ 75% statement coverage
**Isolation strategy**: All file I/O mocked via `vi.mock('node:fs')` and `vi.mock('node:fs/promises')`; node-pty mocked via `vi.mock('node-pty')`; chokidar mocked via `vi.mock('chokidar')`; Fastify instance created in test mode with `fastify({ logger: false })`

---

#### 2.1.1 Backend Unit Test Scope (Modules M1–M6)

| Module | Source File | Key Behaviors to Test | High-Risk Scenarios |
|--------|-------------|----------------------|---------------------|
| M5 — PLAN Parser | `lib/portal/parser.js` | WBS table extraction from markdown; Quality Gates table extraction; status emoji → WBSStatus enum mapping; GateStatus enum mapping; header-name column mapping (column order agnostic); mtime-based cache (hit, miss, invalidation); `parseError` field on malformed input | Multi-line cell values; missing WBS header; missing Gates header; columns in non-standard order; Unicode emoji in status; file with frontmatter only; PLAN with 300+ task rows; concurrent parse calls |
| M6 — API Path Guard | `lib/portal/api.js` (`guardArtifactPath`) | Path resolves inside `docs/`; path traversal raises 403 error object | `../../../etc/passwd`; `%2e%2e%2f` URL-encoded traversal; absolute path `/etc/passwd`; `docs/../.env`; `docs/plans/../../package.json`; null byte injection `docs/plans/\x00evil`; Windows-style `docs\plans\..\..\.env` |
| M6 — API Handlers | `lib/portal/api.js` | `GET /api/agent-status` returns parsed JSON or empty default; `GET /api/plan` globs and sorts by mtime desc; `GET /api/plan/:feature` calls parsePlan and returns result; `GET /api/artifacts` builds flat sorted list; `GET /api/artifacts/*path` reads file after guard; `GET /api/skills` reads SKILL.md frontmatter; `POST /api/run-skill` validates command prefix and calls injectCommand; `GET /api/log` returns last 200 lines | Missing `docs/plans/` dir; missing `agent-status.json`; invalid JSON in `agent-status.json`; skill without `argument-hint` field; command that does not start with `/`; PTY not ready (503); file > 2MB (413) |
| M2 — PTY Bridge | `lib/portal/pty-bridge.js` | Focus token assigned to first WS client; subsequent clients marked read-only; focus transfers on primary disconnect; `injectCommand` validates `/` prefix; `injectCommand` throws 400 on invalid command; `injectCommand` throws 503 when PTY not ready; scrollback buffer replay to new client; `resize` passes WINCH signal; `destroy` is idempotent; auto-respawn after natural exit (3s delay); auto-respawn halts after 5 consecutive failures | Zero WS clients; 5 simultaneous WS clients connecting; rapid connect/disconnect cycle; non-text WS frame type; message > 4096 bytes; PTY spawn throws (node-pty unavailable); destroy called twice |
| M3 — SSE Manager | `lib/portal/sse.js` | `addClient` sends `connected` event with sessionId; `addClient` sends snapshot when agentStatusSnapshot is provided; `broadcast` writes SSE frame to all clients; `broadcast` removes failed clients silently; `removeClient` is idempotent; `clientCount` reflects live count | 0 clients; 100 clients; client write error mid-broadcast; client removed during broadcast iteration |
| M4 — File Watcher | `lib/portal/watcher.js` | Agent-status change triggers `agent-status` SSE (debounce 200ms); PLAN file change triggers `plan-updated` SSE (debounce 500ms); docs file change triggers `artifact-changed` SSE (debounce 300ms); `--no-watch` flag disables all watchers; `close()` stops chokidar | Rapid 10 writes within debounce window (only 1 SSE expected); file rename event; file delete (unlink) event; watched path does not exist at startup |
| M1 — Server Entry | `lib/portal.js` (`resolvePortalDir`) | `__dirname`-relative path resolves to `template/portal/`; throws with clear message if directory missing | Global npm install path; local `node_modules` install path; `template/portal/` deleted (error message) |
| M7 — CLI Handler | `lib/portal-cmd.js` | `--expose` prints security warning; `--expose --yes` skips countdown; orphan PID file read and SIGTERM sent; PID file written on startup; PID file removed on shutdown; `openBrowser` called with correct URL | Missing orphan PID file; orphan process already dead (ESRCH); port already in use (EADDRINUSE); QR code generation failure (fallback to raw URL) |

---

#### 2.1.2 Frontend Unit Test Scope (Module M8 — React SPA)

All frontend unit tests run in `jsdom` environment using Vitest + React Testing Library (RTL).

| Hook / Store / Component | Key Behaviors to Test | Mock Strategy |
|--------------------------|----------------------|---------------|
| `useSSE` hook | Connects to `/events` SSE endpoint; parses `agent-status` / `plan-updated` / `artifact-changed` events; emits parsed payload to subscribers; auto-reconnects when EventSource fires `onerror`; handles malformed JSON without crashing | Mock `EventSource` class with manual event dispatch |
| `useWS` hook | Connects to `/terminal` WS; receives `focus` message and stores token state; sends `input` messages only when focus state is `active`; drops messages when `readonly`; implements exponential backoff reconnect (1s, 2s, 4s, 8s, max 15s); displays "Connection lost" after 60s | Mock `WebSocket` class with `readyState` control |
| `agentStore` (Zustand) | `setAgents` replaces agent list; `elapsedSeconds` calculated from `startedAt`; empty state when agents array is empty; reactive to SSE events via store dispatch | No mocks; pure state test with `createPinia` equivalent |
| `planStore` (Zustand) | Feature selection updates `selectedFeature`; fetch triggered on feature change; WBS parse result stored; gate list stored; `isLoading` flag lifecycle; error state on fetch failure | Mock `fetch` via `vi.fn()` |
| `parsePlan` util (FE) | WBS status emoji → badge color mapping; gate status → Kanban column mapping; UNKNOWN status displays raw text with warning icon; FAST-TRACK gate maps to PASS column with badge | Pure function; no mocks needed |
| `WBSTable` component | Renders all task rows with correct status badges; DONE row has green badge; FAIL row has red badge; REOPENED row has amber badge; unknown status renders grey badge + warning icon; clicking row with artifact path navigates to `/artifacts?path=...` | Mock React Router `useNavigate` |
| `QualityGatesKanban` component | All gates render in correct Kanban columns per status; clicking gate card opens detail panel; detail panel shows gate ID, criteria, status, owner; Escape key closes panel; FAIL gate shows failure note | RTL render with test gate data |
| `SkillsLauncher` component | Skill cards render with argument input; [Run] disabled when required argument is empty; [Run] calls POST `/api/run-skill`; `sensitive: true` skill stores `[REDACTED]` in history; history persists in localStorage; [Re-run] re-sends same command | Mock `fetch`; mock `localStorage` |
| `ArtifactPreview` component | Markdown renders as HTML; GFM tables render as `<table>`; code blocks have syntax highlighting; `<script>` tag stripped by rehype-sanitize; `javascript:` href stripped; legitimate `https:` href preserved; non-markdown file shows "Preview not available" | RTL render with content strings |
| `ArtifactExplorer` component | Directory tree renders with correct hierarchy; clicking file calls GET `/api/artifacts/*path`; SSE `artifact-changed` event triggers tree re-fetch | Mock `fetch`; mock SSE via `useSSE` mock |
| `ConnectionIndicator` | Shows "SSE Connected" badge when `sseConnected: true`; shows "Disconnected" when false | RTL render with props |

---

### 2.2 API Integration Tests (G7a)

**Tool**: Vitest + Fastify `inject()` (in-process HTTP; no real TCP socket; no real node-pty)
**Config**: `vitest.integration.config.ts` with `include: ['test/integration/**/*.test.ts']`
**Runner**: `npx vitest run --config vitest.integration.config.ts`
**Coverage gate**: 100% endpoint coverage — all 12 endpoints must have at least one passing test
**Filesystem**: Real temp directory created in `beforeAll` via `fs.mkdtempSync()`; populated with fixture files; torn down in `afterAll`
**PTY**: `PtyBridge` instantiated with `shell: 'echo'` override (no real claude process)
**SSE**: Real `SseManager` instance; events verified by collecting broadcast calls via `vi.spyOn`

#### 2.2.1 Endpoint Coverage Matrix

| # | Endpoint | Happy Path | Error Cases |
|---|----------|-----------|-------------|
| E1 | `GET /` | Returns 200 with HTML content; `Content-Type: text/html` | — |
| E2 | `GET /assets/main.js` | Returns 200 with JS content when file exists | Non-existent asset → 404 |
| E3 | `GET /events` (SSE) | Connection established; `Content-Type: text/event-stream`; `connected` event received with sessionId; agent-status snapshot sent on connect | Client disconnect removes from registry (verify `clientCount` decrements) |
| E4 | `GET /health` | `{"status":"ok","pty":"active","version":"3.2.0"}`; uptime > 0 | node-pty disabled → `{"status":"degraded","pty":"disabled"}` |
| E5 | `GET /api/agent-status` | Returns parsed `agent-status.json` content; `agents` array populated | File missing → `{"agents":[],"timestamp":"..."}`; invalid JSON → HTTP 500 |
| E6 | `GET /api/plan` | Returns array of PlanMeta sorted by mtime desc; each entry has `feature`, `filename`, `path`, `mtime` | Empty `docs/plans/` dir → `[]`; `docs/plans/` missing → `[]` |
| E7 | `GET /api/plan/:feature` | Returns ParsedPlan with `wbs` array and `gates` array; `feature` and `date` populated | Unknown feature → 404; malformed PLAN → 200 with `parseError` field set |
| E8 | `GET /api/artifacts` | Returns flat array of docs entries sorted by mtime desc; each entry has `path`, `type`, `size`, `mtime`; paths use forward slashes | `docs/` missing → `[]`; empty `docs/` → `[]` |
| E9 | `GET /api/artifacts/*path` | Returns file content with `Content-Type: text/plain; charset=utf-8` | Path traversal `../../../etc/passwd` → 403; non-existent valid path → 404; file > 2MB → 413 |
| E10 | `GET /api/skills` | Returns SkillEntry array sorted by category then name; `argumentHint` is null when field absent; `sensitive` field present | Empty `.claude/skills/` → `[]`; SKILL.md with no frontmatter → entry with empty description |
| E11 | `POST /api/run-skill` | `{"command":"/orchestrate user auth"}` → 200 `{"injected":true,"command":"/orchestrate user auth"}`; command appears in PTY stdin spy | Command missing `/` prefix → 400; command > 1000 chars → 400; PTY not ready → 503 |
| E12 | `GET /api/log` | Returns `{"lines":[...],"totalLinesRead":N}` with last 200 lines | Log file missing → `{"lines":[],"totalLinesRead":0}` |

**Note**: WebSocket endpoint `WS /terminal` (E4 in API inventory) is tested for security (focus token behavior) in unit tests and for full-stack behavior in E2E tests only. In-process inject() does not support WS upgrade; Fastify inject() is HTTP-only.

#### 2.2.2 SSE Integration Scenarios

| Scenario | Setup | Trigger | Expected |
|----------|-------|---------|---------|
| Agent status update | Connect SSE client; write `agent-status.json` | Call watcher event handler manually | `agent-status` SSE event broadcast within debounce window |
| Plan update | Connect SSE client; `PLAN-sample-20260322.md` exists | Simulate chokidar `change` event on PLAN file | `plan-updated` SSE event broadcast with wbsTaskCount, pendingCount, doneCount |
| Artifact changed | Connect SSE client | Simulate chokidar `add` event on `docs/specs/requirements/SRS-foo.md` | `artifact-changed` SSE event with `changeType: 'add'` and correct `type: 'SRS'` |
| Multi-client broadcast | 3 SSE clients connected | Broadcast one event | All 3 clients receive the event |
| Failed client removed | 2 SSE clients; one has broken write stream | Broadcast | Healthy client receives event; broken client removed from registry; no crash |

---

### 2.3 E2E Browser Tests (G7b)

**Tool**: Playwright
**Config**: `playwright.config.ts` in `d9-claude-kit/` root
**Runner**: `npx playwright test`
**Scope**: Critical user journeys only — does not duplicate every unit-test assertion

The server is started by `test/e2e/start-server.js` which creates a temp `projectDir`, seeds fixture files, and starts `startPortal()` on port 3333. node-pty availability is detected in `globalSetup.ts`; terminal-dependent tests are skipped automatically when node-pty is not installed.

#### 2.3.1 Mandatory E2E Scenarios

| Journey ID | Journey Name | Steps | Pass Criteria |
|-----------|-------------|-------|---------------|
| E2E-01 | Portal startup and dashboard load | Start portal server; navigate to `http://localhost:3333`; wait for `GET /api/status` | Dashboard page renders; SSE "Connected" badge visible in sidebar; Agent Status panel visible |
| E2E-02 | Agent status live update (SSE) | Open Dashboard; write updated `agent-status.json` to temp projectDir | Agent name appears in status panel within 500ms; no page reload |
| E2E-03 | WBS table renders from PLAN file | Navigate to `/wbs`; select feature from dropdown | WBS table renders; task count matches fixture; ✅ DONE rows show green badge; ⏳ PENDING rows show grey badge |
| E2E-04 | Quality Gates Kanban board | Navigate to `/wbs` with PLAN selected | Gates appear in correct Kanban columns (PENDING, PASS, FAIL); FAST-TRACK gate appears in PASS column |
| E2E-05 | WBS live update on file change | WBS page open with PLAN selected; overwrite PLAN file with status change | WBS table re-renders with updated status within 500ms |
| E2E-06 | Terminal panel — PTY active | Navigate to `/terminal` (when node-pty available); wait for xterm.js mount | Terminal renders; xterm.js canvas visible; type `echo hello` | `hello` appears in terminal output |
| E2E-07 | Terminal panel — PTY absent | Navigate to `/terminal` when node-pty not installed | "Terminal unavailable — node-pty not installed" message visible; link to setup guide present |
| E2E-08 | Skill injection via Skills Launcher | Navigate to `/skills`; find `orchestrate` card; enter "user auth" in argument; click [Run] | POST to `/api/run-skill` succeeds (200); terminal tab shows injected command (if PTY active) |
| E2E-09 | Skill [Run] disabled on empty argument | Navigate to `/skills`; find skill requiring argument; leave argument empty | [Run] button is disabled (aria-disabled or disabled attribute) |
| E2E-10 | Artifact tree browse and preview | Navigate to `/artifacts`; expand `plans/` folder; click `PLAN-sample-20260322.md` | Markdown preview renders with table content; frontmatter displayed as key-value table |
| E2E-11 | Path traversal blocked at API level | Make direct `GET /api/artifacts/../.env` request via `page.evaluate(() => fetch(...))` | Response status is 403; no `.env` content returned |
| E2E-12 | XSS in artifact content blocked | Place markdown with `<script>alert(1)</script>` as artifact; open preview | No alert dialog fires; `<script>` tag absent from rendered DOM |
| E2E-13 | Mobile viewport — bottom tab navigation | Resize browser to 375px width; navigate to Dashboard | Bottom tab bar visible; no horizontal scroll overflow; all tabs accessible by tap |
| E2E-14 | Health endpoint responds | `GET /health` | HTTP 200; `status: "ok"` or `"degraded"`; `version: "3.2.0"` |
| E2E-15 | WS focus token — read-only secondary tab | Open two browser pages on `/terminal`; type in second page | Character not sent to PTY; second page shows "Read-only" badge |

#### 2.3.2 E2E Test Data Setup

```typescript
// test/e2e/globalSetup.ts
import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';

let tempProjectDir: string;

export async function setup() {
  tempProjectDir = mkdtempSync(path.join(os.tmpdir(), 'ck-portal-e2e-'));

  // Seed agent-status.json
  mkdirSync(path.join(tempProjectDir, '.claude'), { recursive: true });
  writeFileSync(
    path.join(tempProjectDir, '.claude', 'agent-status.json'),
    JSON.stringify({
      agents: [{ name: 'developer-agent', zone: 'BE-B1', task: 'Building Fastify server', startedAt: new Date().toISOString(), elapsedSeconds: 120, status: 'active' }],
      timestamp: new Date().toISOString(),
    })
  );

  // Seed PLAN fixture
  mkdirSync(path.join(tempProjectDir, 'docs', 'plans'), { recursive: true });
  // fixture content written from test/fixtures/plans/PLAN-sample.md

  // Seed skills fixture
  mkdirSync(path.join(tempProjectDir, '.claude', 'skills', 'orchestrate'), { recursive: true });
  writeFileSync(
    path.join(tempProjectDir, '.claude', 'skills', 'orchestrate', 'SKILL.md'),
    '---\nname: orchestrate\ndescription: Full SDLC pipeline\ncategory: Core SDLC\nargument-hint: "Feature description"\n---\n'
  );

  process.env.CK_PORTAL_TEST_DIR = tempProjectDir;
}

export async function teardown() {
  // Cleanup temp dir
}
```

---

## 3. Test Data Strategy

### 3.1 Server-Side Fixtures (`test/fixtures/`)

| Fixture File | Purpose | Content Description |
|-------------|---------|---------------------|
| `test/fixtures/plans/PLAN-sample-20260322.md` | Parser happy path; WBS + gates integration tests | 5 WBS rows covering all status variants (PENDING, IN_PROGRESS, DONE, FAIL, FAST_TRACK); 3 quality gates (G1: PASS, G3a: PENDING, G6: FAIL); valid frontmatter with feature and date |
| `test/fixtures/plans/PLAN-malformed.md` | Parser resilience test | Markdown with WBS header present but missing separator row; Gates table with no data rows; confirms `parseError` is set without throwing |
| `test/fixtures/plans/PLAN-columns-shuffled.md` | Column-order-agnostic parser test | Valid PLAN with WBS columns in non-standard order (Status before ID before Phase); confirms correct mapping |
| `test/fixtures/plans/PLAN-large-300.md` | Parser performance test (NFR-P09: ≤ 200ms) | 300-task WBS table; 12 gate rows; used to verify parse time under load |
| `test/fixtures/skills/orchestrate/SKILL.md` | Skills catalog test | Valid frontmatter with `argument-hint: "Feature description"` |
| `test/fixtures/skills/unit-test/SKILL.md` | Skills catalog test — no argument-hint | Valid frontmatter without `argument-hint` field; confirms `argumentHint: null` in response |
| `test/fixtures/skills/deploy/SKILL.md` | Skills catalog test — sensitive flag | Frontmatter with `sensitive: true`; confirms redaction behavior |
| `test/fixtures/agent-status.json` | Agent status API + SSE tests | 2 active agents (developer-agent, unit-test-agent); 1 idle agent |
| `test/fixtures/agent-status-empty.json` | Empty state test | `{"agents":[],"timestamp":"..."}` |
| `test/fixtures/artifacts/docs/specs/requirements/SRS-safe.md` | Artifact preview safe content | Valid markdown with GFM table and code block |
| `test/fixtures/artifacts/docs/specs/requirements/SRS-xss.md` | XSS sanitization test | Markdown containing `<script>alert(1)</script>`; `<img src=x onerror=alert(1)>`; `[click](javascript:alert(1))`; `[safe](https://example.com)` |

### 3.2 Frontend Test Mocks (`portal-src/src/test/`)

| Mock File | Purpose |
|-----------|---------|
| `mocks/handlers.ts` | MSW (Mock Service Worker) request handlers for all 12 API endpoints; used in frontend unit tests that trigger real fetch calls |
| `mocks/EventSource.ts` | Mock EventSource class with `dispatchEvent` helper; allows test code to fire SSE events manually to test `useSSE` hook |
| `mocks/WebSocket.ts` | Mock WebSocket class with `readyState` control, `send` spy, and `triggerMessage` helper; tests `useWS` hook in isolation |
| `setup.ts` | Vitest global setup: installs MSW; mocks `localStorage`; mocks `ResizeObserver`; sets up React Testing Library cleanup |

### 3.3 E2E Test Data

Playwright tests use real temp directory created in `globalSetup.ts` (see Section 2.3.2). Fixture content is seeded programmatically. Tests that verify live SSE updates write new fixture content mid-test using `fs.writeFileSync` and then assert DOM changes within 700ms (500ms SSE latency + 200ms React render budget).

---

## 4. Security Test Approach

### 4.1 Path Traversal Prevention (FR-25, BR-02, NFR-S03, NFR-S09)

The following exact inputs MUST be present in BOTH unit tests (`guardArtifactPath` function) AND API integration tests (`GET /api/artifacts/*path` endpoint). All must return HTTP 403 at the integration layer and throw the 403 error object at the unit layer.

| Input | Attack Vector | Expected Response |
|-------|-------------|-----------------|
| `../../../etc/passwd` | Simple parent traversal | 403 FORBIDDEN |
| `..%2f..%2fpackage.json` | URL-encoded dots (Fastify decodes before handler) | 403 FORBIDDEN |
| `/etc/passwd` | Absolute path injection | 403 FORBIDDEN |
| `docs/../.env` | Traversal out of docs/ via sibling | 403 FORBIDDEN |
| `docs/plans/../../package.json` | Multi-hop traversal | 403 FORBIDDEN |
| `docs/plans/PLAN-foo.md` (valid) | Legitimate request | 200 OK (file content) |
| `docs/specs/requirements/SRS-foo.md` (non-existent) | Valid path, missing file | 404 NOT_FOUND |

**Windows-specific variant**: On Windows test runners, also verify `docs\plans\..\..\.env` (backslash) resolves correctly after `path.normalize()`.

### 4.2 PTY stdin Injection Prevention (FR-09, BR-04, NFR-S04, NFR-S05)

The following scenarios must be tested at the unit level (PtyBridge) and API integration level (POST `/api/run-skill`):

| Scenario | Input | Expected Behavior |
|----------|-------|-----------------|
| Valid skill command | `{"command":"/orchestrate user auth"}` | Injected successfully; appears in PTY stdin |
| Missing `/` prefix | `{"command":"orchestrate user auth"}` | HTTP 400; BAD_REQUEST; PTY stdin NOT written |
| Shell metacharacters in skill name | `{"command":"/orchestrate; rm -rf /"}` | Command passed as-is to PTY stdin (PTY is the execution boundary; portal does NOT shell-interpret). Verify no `exec()` or `spawn()` called. |
| Command exceeds 1000 chars | `{"command":"/" + "a".repeat(1001)}` | HTTP 400; BAD_REQUEST |
| PTY not initialized | POST when `ptyBridge.isAlive === false` | HTTP 503; PTY_UNAVAILABLE |
| WS message > 4096 bytes | Send oversized binary frame to `/terminal` | Message dropped; no write to PTY stdin |
| Non-text WS frame | Send binary frame of type `Buffer` | Dropped silently; PTY stdin unchanged |
| Read-only client keystroke | Second WS client sends `{type:"input",data:"x"}` | Dropped; PTY stdin unchanged; no error sent to client |

**Critical clarification (BR-04)**: The portal does NOT need to sanitize shell metacharacters from skill commands because the command is written to PTY stdin, not to a shell `exec()`. The security control is that `POST /api/run-skill` MUST ONLY call `ptyBridge.injectCommand()` and MUST NOT call `child_process.exec()`, `child_process.spawn()`, or `eval()`. Unit tests must verify this with a spy confirming no shell execution occurs.

### 4.3 XSS via Artifact Content (FR-24, NFR-S06)

Frontend unit tests using RTL + `ArtifactPreview` component must verify the following inputs are safely rendered:

| Malicious Input | Expected Render Behavior | Test Method |
|----------------|--------------------------|------------|
| `<script>alert(1)</script>` in markdown | `<script>` tag stripped; no alert fires | RTL render; assert no `<script>` in DOM |
| `<img src=x onerror=alert(1)>` | `onerror` attribute stripped; img may or may not render | Assert no `onerror` attribute in DOM |
| `[click](javascript:alert(1))` | href stripped; link text rendered as plain text or `href=""` | Assert no `javascript:` in DOM links |
| `<iframe src="https://attacker.com">` | `<iframe>` tag stripped entirely | Assert no `<iframe>` in DOM |
| `[safe](https://example.com)` | Link renders correctly with `https:` href | Assert `href="https://example.com"` present |
| **Markdown table** (legitimate) | Renders as HTML `<table>` | Assert `<table>` element in DOM |
| **Code block** with TypeScript tag | Renders with syntax highlight CSS classes | Assert `language-typescript` class on code block |

E2E counterpart: E2E-12 verifies no `alert()` dialog fires when XSS artifact is previewed in real browser.

---

## 5. Performance Test Approach

### 5.1 SSE Update Latency (NFR-P01: ≤ 500ms end-to-end)

**Layer**: API Integration test (Vitest)
**Method**:
1. Connect a test SSE client (record `Date.now()` as `t0`).
2. Simulate chokidar `change` event on `agent-status.json` (call watcher event handler directly).
3. Measure elapsed time from chokidar event dispatch to SSE client receiving the broadcast event (`t1`).
4. Assert `(t1 - t0) ≤ 500ms`.

**Breakdown**: chokidar emit → 200ms debounce → SSE broadcast → client receipt. In integration tests, debounce is verified by confirming only 1 SSE event per rapid-fire sequence.

**Debounce correctness test**: Fire 5 chokidar events within 100ms; advance fake timers by 210ms; verify exactly 1 SSE broadcast occurred (not 5).

### 5.2 Skill Inject Latency (NFR-P04: ≤ 200ms)

**Layer**: API Integration test (Vitest)
**Method**:
1. Record `Date.now()` as `t0`.
2. Call `fastify.inject({ method: 'POST', url: '/api/run-skill', payload: { command: '/orchestrate user auth' } })`.
3. Record `Date.now()` as `t1` after response received.
4. Verify PTY stdin spy was called (inject occurred).
5. Assert `(t1 - t0) ≤ 200ms`.

**Note**: In-process inject() has near-zero network overhead, so the 200ms budget should be easily met. Any failure indicates synchronous blocking in the handler.

### 5.3 Portal Startup Time (NFR-P08: ≤ 2s)

**Layer**: E2E test (Playwright)
**Method**: The Playwright `webServer` config has `timeout: 2000ms` — if `GET /health` does not return 200 within 2 seconds of starting the server process, the test suite fails. This acts as a mandatory startup performance gate.

### 5.4 PLAN Parse Time (NFR-P09: ≤ 200ms for 300-task file)

**Layer**: Unit test (Vitest)
**Method**:
1. Read `test/fixtures/plans/PLAN-large-300.md` (300-task file, pre-generated).
2. Record `performance.now()` as `t0`.
3. Call `parsePlan(content, 'PLAN-large-300-20260322.md')`.
4. Record `performance.now()` as `t1`.
5. Assert `(t1 - t0) < 200`.

---

## 6. Test Infrastructure Requirements

### 6.1 Vitest Config — Backend Unit Tests

```typescript
// d9-claude-kit/vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/unit/**/*.test.ts'],
    environment: 'node',
    globals: true,
    coverage: {
      provider: 'v8',
      include: ['lib/portal/**/*.js', 'lib/portal.js', 'lib/portal-cmd.js'],
      exclude: ['lib/portal/static.js'],  // resolvePortalDir tested via integration
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        statements: 85,
        branches: 80,
        functions: 85,
        lines: 85,
      },
    },
    fakeTimers: {
      // Enable fake timers for debounce tests
      // Individual tests opt-in via vi.useFakeTimers()
    },
  },
});
```

### 6.2 Vitest Config — API Integration Tests

```typescript
// d9-claude-kit/vitest.integration.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/integration/**/*.test.ts'],
    environment: 'node',
    globals: true,
    // No coverage threshold here — 100% endpoint coverage is enforced
    // by test structure (each endpoint has a dedicated describe block)
    testTimeout: 10000,  // 10s timeout for SSE timing tests
    hookTimeout: 15000,  // 15s for beforeAll temp dir + server setup
    sequence: {
      concurrent: false,  // Integration tests run sequentially to avoid port conflicts
    },
  },
});
```

### 6.3 Vitest Config — Frontend Unit Tests

```typescript
// d9-claude-kit/portal-src/vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  test: {
    include: ['src/**/*.test.{ts,tsx}', 'src/**/*.spec.{ts,tsx}'],
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/types/**',
        'src/test/**',
        '**/*.d.ts',
      ],
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        statements: 75,
        branches: 70,
        functions: 75,
        lines: 75,
      },
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
});
```

### 6.4 Playwright Config

```typescript
// d9-claude-kit/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'test/e2e',
  globalSetup: 'test/e2e/globalSetup.ts',
  globalTeardown: 'test/e2e/globalTeardown.ts',
  webServer: {
    command: 'node test/e2e/start-server.js',
    port: 3333,
    reuseExistingServer: false,
    timeout: 2000,  // NFR-P08: portal must be ready within 2s
  },
  use: {
    baseURL: 'http://localhost:3333',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
  },
  timeout: 15000,
  retries: 1,
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],
});
```

### 6.5 Package.json Scripts

The following scripts must be added to `d9-claude-kit/package.json` under `"scripts"`:

```json
{
  "scripts": {
    "test:unit": "vitest run --coverage --config vitest.config.ts",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:fe": "cd portal-src && vitest run --coverage",
    "test:e2e": "playwright test",
    "test:all": "npm run test:unit && npm run test:integration && npm run test:fe && npm run test:e2e",
    "test:ci": "npm run test:unit && npm run test:integration && npm run test:fe && npm run test:e2e -- --reporter=junit",
    "build:portal": "cd portal-src && vite build --outDir ../template/portal",
    "dev:portal": "cd portal-src && vite"
  }
}
```

### 6.6 Test Directory Structure

```
d9-claude-kit/
├── vitest.config.ts                     ← BE unit test config
├── vitest.integration.config.ts         ← BE integration test config
├── playwright.config.ts                 ← E2E config
├── test/
│   ├── unit/                            ← Backend unit tests (G6 BE)
│   │   ├── parser.test.ts               ← M5: parsePlan(), invalidate()
│   │   ├── api.guard.test.ts            ← M6: guardArtifactPath()
│   │   ├── api.handlers.test.ts         ← M6: all route handlers
│   │   ├── pty-bridge.test.ts           ← M2: PtyBridge class
│   │   ├── sse.test.ts                  ← M3: SseManager class
│   │   ├── watcher.test.ts              ← M4: startWatcher()
│   │   └── static.test.ts              ← M1: resolvePortalDir()
│   ├── integration/                     ← API integration tests (G7a)
│   │   ├── endpoints.test.ts            ← All 12 endpoints via inject()
│   │   └── sse.integration.test.ts     ← SSE broadcast scenarios
│   ├── e2e/                             ← Playwright E2E tests (G7b)
│   │   ├── globalSetup.ts
│   │   ├── globalTeardown.ts
│   │   ├── start-server.js
│   │   ├── dashboard.spec.ts            ← E2E-01, E2E-02, E2E-13, E2E-14
│   │   ├── wbs.spec.ts                  ← E2E-03, E2E-04, E2E-05
│   │   ├── terminal.spec.ts             ← E2E-06, E2E-07, E2E-15
│   │   ├── skills.spec.ts               ← E2E-08, E2E-09
│   │   └── artifacts.spec.ts            ← E2E-10, E2E-11, E2E-12
│   └── fixtures/                        ← Shared test data (Section 3.1)
│       ├── plans/
│       │   ├── PLAN-sample-20260322.md
│       │   ├── PLAN-malformed.md
│       │   ├── PLAN-columns-shuffled.md
│       │   └── PLAN-large-300.md
│       ├── skills/
│       │   ├── orchestrate/SKILL.md
│       │   ├── unit-test/SKILL.md
│       │   └── deploy/SKILL.md
│       ├── agent-status.json
│       └── agent-status-empty.json
├── portal-src/
│   ├── vitest.config.ts                 ← FE unit test config
│   └── src/
│       ├── test/
│       │   ├── setup.ts
│       │   └── mocks/
│       │       ├── handlers.ts          ← MSW handlers
│       │       ├── EventSource.ts       ← Mock SSE
│       │       └── WebSocket.ts         ← Mock WS
│       ├── hooks/__tests__/
│       │   ├── useSSE.test.ts
│       │   └── useWS.test.ts
│       ├── store/__tests__/
│       │   ├── agentStore.test.ts
│       │   └── planStore.test.ts
│       ├── utils/__tests__/
│       │   └── parsePlan.test.ts
│       └── components/__tests__/
│           ├── WBSTable.test.tsx
│           ├── QualityGatesKanban.test.tsx
│           ├── SkillsLauncher.test.tsx
│           ├── ArtifactPreview.test.tsx
│           ├── ArtifactExplorer.test.tsx
│           └── ConnectionIndicator.test.tsx
```

---

## 7. ISTQB Technique Application

### 7.1 Equivalence Partitioning — Path Guard

| Partition | Representative Input | Class |
|-----------|---------------------|-------|
| Valid docs path, file exists | `docs/specs/requirements/SRS-foo.md` | Valid |
| Valid docs path, file absent | `docs/specs/requirements/SRS-missing.md` | Valid (→ 404) |
| Simple traversal (`../`) | `../package.json` | Invalid (→ 403) |
| URL-encoded traversal | `..%2fpackage.json` | Invalid (→ 403) |
| Absolute path | `/etc/passwd` | Invalid (→ 403) |
| Same-dir traversal that stays in docs | `docs/plans/../specs/SRS-foo.md` | Valid (resolves to docs/specs/) |

### 7.2 Boundary Value Analysis — WS Message Size

| Value | Expected |
|-------|---------|
| 1 byte | Accepted; forwarded to PTY |
| 4095 bytes | Accepted; forwarded to PTY |
| 4096 bytes | Accepted (boundary inclusive) |
| 4097 bytes | Dropped; PTY stdin unchanged |
| 10,000 bytes | Dropped; PTY stdin unchanged |

### 7.3 Decision Table — Focus Token Assignment

| Clients Connected | Action | Expected Focus State |
|-----------------|--------|---------------------|
| 0 → first client connects | handleConnection() | First client: `active` |
| 1 active → second client connects | handleConnection() | Second client: `readonly` |
| Active client disconnects (2 total) | WS close | Remaining client promoted to `active`; receives `{type:"focus",state:"active"}` |
| Active client disconnects (1 total) | WS close | No clients; focusClientId = null |
| Read-only client disconnects | WS close | Active client unchanged; focus preserved |
| 5 clients; active disconnects | WS close | Next oldest client promoted to `active` |

### 7.4 Error Guessing — Parser Resilience

| Malformed Input | Expected Parser Behavior |
|----------------|------------------------|
| Empty file | `parseError` set; `wbs: []`; `gates: []`; no throw |
| Valid frontmatter, no WBS table | `parseError` set with message "WBS table not found" |
| WBS table exists, no Gates table | `gates: []`; `wbs` populated; `parseError` set for missing gates |
| Row with empty status cell | Status maps to `UNKNOWN`; `rawStatus: ""` |
| Row with novel emoji not in status map | Status maps to `UNKNOWN`; `rawStatus` contains the raw cell text |
| WBS header present but no data rows | `wbs: []`; no throw |
| PLAN file with Windows CRLF line endings | Parsed correctly (regex handles `\r\n`) |

---

## 8. G3c Pass Criteria Checklist

This checklist must be fully checked before G3c is approved. All items must be confirmed by the QA architect or unit-test-agent lead.

- [x] All 3 test layers defined (unit — BE + FE, API integration, E2E browser)
- [x] Tool selection justified for each layer (Vitest for BE/FE; Vitest + Fastify inject() for integration; Playwright for E2E)
- [x] Coverage thresholds specified with no placeholders (BE ≥ 85% statement; FE ≥ 75% statement; 100% endpoint coverage for API integration)
- [x] All high-risk server modules have named test scenarios (M1–M7 in Section 2.1.1)
- [x] All high-risk frontend components have named test scenarios (Section 2.1.2)
- [x] Security test inputs listed for path traversal (Section 4.1 — 7 exact inputs including URL-encoded and absolute path variants)
- [x] Security test inputs listed for PTY stdin injection (Section 4.2 — 8 scenarios including shell metacharacters and oversized messages)
- [x] Security test inputs listed for XSS via artifact content (Section 4.3 — 7 inputs including script tag, onerror, and javascript: href)
- [x] E2E critical journeys listed with ≥ 8 scenarios (Section 2.3.1 — 15 mandatory journeys defined)
- [x] Test data and fixture strategy defined (Section 3 — 10 server fixture files, 4 frontend mock files, E2E globalSetup seeding)
- [x] Performance test approach mapped to NFR targets (NFR-P01 ≤ 500ms SSE; NFR-P04 ≤ 200ms skill inject; NFR-P08 ≤ 2s startup; NFR-P09 ≤ 200ms parse)
- [x] Test infrastructure config specified (Sections 6.1–6.4 — all 4 configs written with real thresholds)
- [x] package.json test scripts defined (Section 6.5 — test:unit, test:integration, test:fe, test:e2e, test:all, test:ci)
- [x] Test directory structure defined (Section 6.6)
- [x] ISTQB techniques applied (Section 7 — EP, BVA, Decision Table, Error Guessing)
- [x] node-pty optional dependency handling tested (E2E-07 for absent PTY; Unit PtyBridge for graceful degradation)
- [x] Windows ConPTY and Windows path normalization addressed (path traversal variant; forward-slash normalization in API responses)
- [x] Zero placeholders, TODO items, or TBD markers remaining in this document

---

*End of TEST_VIEWPOINT — ClaudeKit Portal — v1.0 — 2026-03-22*
*Gate G3c artifact — ready for user approval*
*Next: T-13 G3c Gate Review → T-14 Phase 4 Implementation (BE-B1 parallel spawn)*

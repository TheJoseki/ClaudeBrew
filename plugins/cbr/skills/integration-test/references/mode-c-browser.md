# Mode C — Browser Live Testing (Chrome DevTools MCP)

> Reference for integration-test. Loaded on-demand when executing Mode C.

## When to Use

UI features where SCREEN spec defines user flows AND Chrome DevTools MCP is running.

**Priority**: MUST use Mode C for all UI features when Playwright MCP is available.
Fall back to Mode B ONLY when: (1) MCP connection fails, or (2) feature is API-only with no SCREEN spec.
Document fallback reason in ITR header.

## Step 0 — Check Availability

```
list_pages()  → if error/no response, fall back to Mode B
```

## Execution Flow Per Test Scenario (MCP Tool Calls)

Use these exact MCP tool calls — invoke directly, do NOT write Playwright test scripts:

| Step | MCP Tool Call | Purpose |
|------|-------------|---------|
| Navigate | `mcp__playwright__browser_navigate(url)` | Open page |
| Snapshot | `mcp__playwright__browser_snapshot()` | Get accessibility tree with stable UIDs |
| Click | `mcp__playwright__browser_click(element, ref)` | Click by UID from snapshot |
| Fill | `mcp__playwright__browser_fill_form(data)` | Fill form fields by UID |
| Screenshot | `mcp__playwright__browser_take_screenshot()` | Visual evidence |
| Console | `mcp__playwright__browser_console_messages()` | Capture JS console errors |
| Wait | `mcp__playwright__browser_wait_for(selector)` | Wait for element/network |

**Per scenario:**
1. `mcp__playwright__browser_navigate(url="[app base url]")` — opens page
2. For each step in SCREEN spec user flow:
   a. `mcp__playwright__browser_navigate(url="[page url]")`
   b. `mcp__playwright__browser_snapshot()` — get accessibility tree with stable UIDs
   c. `mcp__playwright__browser_click(element, ref)` or `mcp__playwright__browser_fill_form(data)` — interact by UID
   d. `mcp__playwright__browser_take_screenshot()` — capture evidence
   e. Verify expected state, check for errors
3. Log result to ITR report with screenshot file paths

**RBAC testing**: Run each scenario as each role. Navigate to logout then login to re-authenticate as different role.

## On Test Failure

If any scenario FAIL → capture diagnostic info:
- `mcp__playwright__browser_snapshot()` — check alert roles for error messages
- `mcp__playwright__browser_console_messages()` — capture console errors
- `mcp__playwright__browser_take_screenshot()` — visual evidence
- Append finding to ITR report Bug Reports section

## Mode C Test Report Template

File: `docs/test-reports/ITR-[feature]-browser-R[n].md`

```markdown
# Integration Test Report: [Feature Name] — Browser Live R[n]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Round**: R[n]
**Author**: integration-test
**Tool**: Playwright MCP (mcp__playwright__*)
**Mode**: C — Browser Live (interactive MCP tool calls)
**App URL**: [base url]

## Summary
| Metric | Value |
|--------|-------|
| Total scenarios | X |
| Passed | X |
| Failed | X |
| Pass Rate | X% |

## Scenario Results
| TC-ID | Scenario | Steps | Result | Screenshot | Notes |
|-------|----------|-------|--------|-----------|-------|

## Failed Scenarios
| TC-ID | Failure Step | Browser State | Screenshot | Action |
|-------|-------------|---------------|-----------|--------|

## Bug Reports (for fix-bug)
| Bug ID | TC ID | Description | Steps to Reproduce | Expected | Actual | Severity |
|--------|-------|-------------|-------------------|---------|--------|---------|

## Next Action
- FAIL → fix-bug fixes bugs → re-run R[n+1]
- R5 PASS → report to the user with the verdict artifact: Integration Tests 100% PASS
```

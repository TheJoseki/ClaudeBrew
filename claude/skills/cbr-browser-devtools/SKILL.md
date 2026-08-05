---
name: cbr-browser-devtools
description: "DOM inspection + browser debugging skill. Uses chrome-devtools-mcp tools to analyze page structure, capture console errors, and produce a structured debug report. Connects to fix-bug for root cause analysis. TRIGGER: user says \"debug UI\", \"why is this failing in browser\", \"inspect the page\", \"DOM issue\", \"check what the browser shows\", \"browser error\". NOT FOR: server-side bugs, non-browser errors."
allowed-tools: Read, Grep, Glob, Write, Edit
metadata:
  version: "3.1"
  category: quality
---

# Browser DevTools Skill

$ARGUMENTS

> **MCP Server**: `browser-agent` key in `.mcp.json` → powered by `chrome-devtools-mcp` (Puppeteer/CDP).
> Tools use stable UIDs from accessibility tree — no numbered badge overlays.

## Step 0: Check Browser Connection

Before any DOM analysis, verify a page is open:
```
list_pages()
```

If no pages → open one first:
```
new_page(url="http://localhost:8000")
```

## Content Map

| Section | When to read |
| --- | --- |
| Step 1: Page State | Always — identify what page you are on |
| Step 2: Error Capture | Always — find console errors and DOM alerts |
| Step 3: Element Inspection | When specific element failing or form issue |
| Step 4: Diagnosis | Always — produce structured finding |
| Skill Connections | Routing to next agent/skill after diagnosis |

## Step 1: Capture Page State (low token)

Use accessibility snapshot first — compact and structured:

```
list_pages()              → confirm which page is active
take_snapshot()           → accessibility tree: roles, names, UIDs
```

Record:
- Current page title and URL (from `list_pages()`)
- Any alert/error roles in the snapshot (role: "alert", "status")
- Form structure (missing fields? correct action?)
- Navigation structure (are we on the right page?)

## Step 2: Capture Console Errors + Auth State

Get console messages from the MCP server directly:
```
list_console_messages(types=["error", "warning"])
```

Inject error collector for runtime JS errors not yet logged:
```javascript
evaluate_script(function: "() => { if(!window.__agentErrors){window.__agentErrors=[];window.onerror=(m,s,l,c,e)=>{window.__agentErrors.push({message:m,source:s,line:l,time:new Date().toISOString()});return false;};} return window.__agentErrors; }")
```

Check auth/session state:
```javascript
evaluate_script(function: "() => JSON.stringify({ localStorage_keys: Object.keys(localStorage), sessionStorage_keys: Object.keys(sessionStorage), cookies_count: document.cookie.split(';').length })")
```

## Step 3: Element Inspection (when specific element failing)

```
take_screenshot(filePath="debug-snapshot.png")   → visual snapshot for evidence
take_snapshot(verbose=true)                       → full accessibility tree with UIDs
```

Find error-state elements:
```javascript
evaluate_script(function: "() => JSON.stringify([...document.querySelectorAll('.error, .alert, [aria-invalid], .is-invalid')].map(e=>({tag:e.tagName,class:e.className,text:e.textContent.trim().slice(0,100)})))")
```

If form submission failing:
```javascript
evaluate_script(function: "() => JSON.stringify([...document.querySelectorAll('input,select,textarea')].map(i=>({name:i.name,value:i.value,valid:i.validity?.valid,message:i.validationMessage})))")
```

Check network for API failures:
```
list_network_requests(resourceTypes=["fetch", "xhr"])
```

## Step 4: Structured Diagnosis Report

Produce a diagnostic block:

```markdown
## Browser Diagnostic Report
**URL**: [current url]
**Page**: [page title]
**Time**: [timestamp]

### Findings

| # | Category | Finding | Severity |
|---|----------|---------|---------|
| 1 | Console Error | [error message] | High/Medium/Low |
| 2 | DOM Alert | [alert text] | High/Medium/Low |
| 3 | Form Validation | [field] is invalid: [message] | Medium |
| 4 | Network | [status code or failure] | High |

### Visual Evidence
- Screenshot: [path if saved]
- Accessibility UID: [uid] — [description of problematic element]

### Root Cause Hypothesis
[1-2 sentence hypothesis based on findings]

### Recommended Action
[Next step: fix code / check auth / check API / etc.]
```

## Skill Connections

| Direction | Skill/Agent | When |
|-----------|-------------|------|
| Calls → | `fix-bug` | Root cause unclear after DOM inspection |
| Calls → | `context7` MCP | Framework-specific JS/CSS error detected (React, Vue, etc.) |
| Calls → | `deepwiki` MCP | Custom library or project-specific error |
| Calls → | `fix-bug` | Root cause identified — needs code fix |
| Called from | `integration-test` | Test scenario fails visually — inspect actual browser state |
| Called from | `fix-bug` | Bug has UI component — need browser evidence first |

## Checklist Before Done

- [ ] `list_pages()` confirmed page is open
- [ ] `take_snapshot()` captured and alert roles reviewed
- [ ] `list_console_messages(types=["error","warning"])` checked
- [ ] `take_screenshot()` taken as evidence
- [ ] `list_network_requests()` checked for failed API calls
- [ ] Structured diagnosis report produced
- [ ] Next action recommended (routed to correct skill/agent)

## Verification

**Skill triggers correctly when:**
- User says: "The login button isn't working, debug it"
- User says: "Check what the browser is showing"
- User says: "Why is this failing in the browser?"
- User says: "Inspect the DOM of the dashboard page"

**Skill does NOT trigger for:**
- "Fix the bug in the API" (use fix-bug)
- "Why is the backend returning 500?" (use fix-bug)

# Browser Debug Checklist

> Reference for browser-devtools skill. Uses Chrome DevTools MCP tools (`chrome-devtools-mcp`).
> Check all areas before concluding diagnosis.

## Phase 1: Page State (always run first)

- [ ] `list_pages()` — confirm correct page is open (URL + title)
- [ ] `take_snapshot()` — review accessibility tree: look for `role="alert"` or `role="status"` nodes
- [ ] Check page title matches expected page
- [ ] Check scroll position in snapshot — important content may be below fold

## Phase 2: Console Errors

Get errors from MCP server directly (catches all errors since page load):

```javascript
list_console_messages(types: ["error", "warning"])
```

Inject runtime error collector for JS errors not yet logged:

```javascript
evaluate_script(function: "() => { if(!window.__agentErrors){window.__agentErrors=[];window.onerror=(m,s,l,c,e)=>{window.__agentErrors.push({message:m,source:s,line:l,time:new Date().toISOString()});return false;};} return window.__agentErrors; }")
```

Common error patterns:
- `TypeError: Cannot read property of undefined` → null/undefined data, check API response
- `401 Unauthorized` → auth token expired or missing, check localStorage/cookies
- `403 Forbidden` → RBAC issue, check user role vs required permission
- `404 Not Found` → wrong URL, route not registered, or deleted resource
- `CORS error` → backend CORS config, missing allowed origin
- `Network Error` → backend not running, or DNS issue
- `SyntaxError` → JSON parse failure, check API response format
- `ChunkLoadError` → JS bundle failed to load, try hard refresh

## Phase 3: DOM State Checks

```javascript
// Check form validation state
evaluate_script(function: "() => JSON.stringify([...document.querySelectorAll(':invalid')].map(i=>({name:i.name,message:i.validationMessage})))")

// Check hidden elements that might contain errors
evaluate_script(function: "() => JSON.stringify([...document.querySelectorAll('[aria-hidden=\"true\"]')].filter(e=>e.textContent.toLowerCase().includes('error')).map(e=>e.textContent.trim()))")

// Check auth tokens
evaluate_script(function: "() => JSON.stringify({token: !!localStorage.getItem('token') || !!localStorage.getItem('access_token'), keys: Object.keys(localStorage)})")
```

## Phase 4: Network State

Use MCP-native network inspection (no JS injection needed):

```
list_network_requests(resourceTypes: ["fetch", "xhr"])
```

For details on a specific failed request:

```
get_network_request(reqid: "[reqid from list_network_requests]")
```

Check framework initialization:

```javascript
evaluate_script(function: "() => JSON.stringify({vue: !!window.__vue_app__, react: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__, angular: !!window.ng})")
```

## Phase 5: Visual Inspection

1. `take_screenshot(filePath: "debug-snapshot.png")` — visual snapshot of current state
2. `take_snapshot(verbose: true)` — full accessibility tree with stable UIDs for all elements
3. Find error-state elements:

```javascript
evaluate_script(function: "() => JSON.stringify([...document.querySelectorAll('.error,.alert,[aria-invalid]')].map(e=>({tag:e.tagName,class:e.className,text:e.textContent.trim().slice(0,100)})))")
```

## Severity Guide

| Severity | Examples |
|----------|---------|
| Critical | Auth failure, page won't load, core feature broken |
| High | Form can't submit, button doesn't respond, API error |
| Medium | Wrong data displayed, validation message wrong |
| Low | Style issue, minor text error, cosmetic problem |

## Routing Decisions

| Finding | Route To |
|---------|---------|
| JS runtime error | `systematic-debugging` → `bug-fix-agent` |
| API 401/403 | Check auth config → `bug-fix-agent` |
| API 500 | `systematic-debugging` (backend) |
| Framework error | `context7` MCP for docs → `bug-fix-agent` |
| DOM structure wrong | `bug-fix-agent` (frontend template fix) |
| CSS/layout issue | `bug-fix-agent` (frontend style fix) |
| Root cause unknown | `systematic-debugging` |

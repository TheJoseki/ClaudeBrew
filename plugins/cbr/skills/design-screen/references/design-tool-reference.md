# Design Tool Reference

> Reference for design-screen. Loaded on-demand during Step 6 visual design output.
> Contains all 5 design tool paths: Figma (6B), SVG Fallback (6C), Pencil Dev (6D), Google Stitch (6E).

---

## 6A. Design Tool Selection (MANDATORY — ask user before proceeding)

Ask the user:

> "Which design tool should I use for visual output?"
> 1. **Figma** — push HTML prototype to Figma canvas via Figma MCP (requires Figma MCP configured + paid plan)
> 2. **Pencil Dev** — create `.pen` design file on canvas via Pencil MCP (requires Pencil Dev extension in VS Code/Cursor)
> 3. **Google Stitch** — generate screens from text prompts via Stitch MCP (free, requires Google account + stitch-mcp setup)
> 4. **SVG fallback** — generate SVG wireframe files (no external tool required)

| User Response | Next Step |
|---------------|-----------|
| Figma | → **Step 6B** |
| Pencil / Pencil Dev | → **Step 6D** |
| Stitch / Google Stitch | → **Step 6E** |
| SVG / Skip / unsure | → **Step 6C** (safe default) |

---

## 6B. Figma Path — HTML Prototype → Figma Canvas

> **First action**: Call `figma whoami` MCP tool to verify authentication.
> If returns error or auth failure → inform user and fall through to **Step 6C**.

> Uses Figma MCP `generate_figma_design` to push screens as editable layers into a new Figma file.
> **If ANY step in 6B fails → stop immediately and execute Step 6C.**

### Phase 1: Generate HTML Prototypes (Desktop + Mobile)

Create **two separate HTML files** — one per viewport:

- **Desktop**: `docs/specs/figma/SCREEN-[feature]-desktop.html` — 1920×1080
- **Mobile**: `docs/specs/figma/SCREEN-[feature]-mobile.html` — 390×844

> **Figma capture rules — CRITICAL for correct output:**
>
> 1. **NEVER use `display:none`** on screens/states — Figma's capture script skips hidden DOM. Every screen and state MUST be visible and stacked vertically.
> 2. **NO `position: fixed` or `position: sticky`** on content elements — fixed elements are captured at their fixed position, causing overlap artifacts. Use `position: relative` or `static` for all content. Only the `<proto-nav>` preview bar may use `position: sticky`.
> 3. **NO `overflow: hidden`** on the `<body>` or root containers — prevents full-page capture.
> 4. **Each screen = one `<section>` with explicit `width` and `min-height: 1080px` (desktop) or `min-height: 844px` (mobile)** — Figma creates one frame per visible section.
> 5. **Viewport meta must match file** — desktop file: `width=1920`, mobile file: `width=390`.

HTML structure (desktop example — apply same pattern for mobile with 390px widths):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, initial-scale=1.0">
  <title>[Feature] Desktop — ClaudeBrew Prototype</title>
  <style>
    :root {
      --color-primary: [hex from Step 5];
      --color-surface: [hex from Step 5];
      /* all tokens from Step 5 */
    }

    /* PROTO NAV — sticky preview only, not captured as content */
    .proto-nav {
      position: sticky; top: 0; z-index: 9999;
      background: #1a1a1a; color: #fff;
      display: flex; gap: 8px; padding: 8px 16px;
      font-family: monospace; font-size: 12px;
    }
    .proto-nav a { color: #7dd3fc; text-decoration: none; }

    /* SCREEN SECTIONS — all visible, stacked vertically */
    .screen {
      width: 1920px;          /* 390px for mobile file */
      min-height: 1080px;     /* 844px for mobile file */
      position: relative;     /* NEVER fixed/absolute */
      overflow: visible;      /* NEVER hidden */
      box-sizing: border-box;
      /* Section border for Figma frame detection */
      border-bottom: 4px solid #000;
    }

    /* AppBar — relative NOT fixed */
    .app-bar {
      position: relative;     /* NOT fixed */
      width: 100%; height: 64px;
      /* styles */
    }

    /* Sidebar — relative NOT fixed/sticky */
    .sidebar {
      position: relative;     /* NOT fixed */
      width: 240px; min-height: calc(1080px - 64px);
      float: left;
    }

    /* Main content */
    .main-content {
      margin-left: 240px;
      min-height: calc(1080px - 64px);
    }
  </style>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; overflow:visible;">

  <!-- Preview navigation (sticky, not captured as content frame) -->
  <nav class="proto-nav">
    <span>📐 [Feature] Desktop Prototype</span>
    <a href="#SCR-01-default">SCR-01 Default</a>
    <a href="#SCR-01-loading">SCR-01 Loading</a>
    <a href="#SCR-01-empty">SCR-01 Empty</a>
    <!-- ... more screens ... -->
  </nav>

  <!-- SCR-01: [Screen Name] — Default State -->
  <section id="SCR-01-default" class="screen">
    <div class="app-bar"><!-- AppBar content --></div>
    <div style="display:flex; height:calc(1080px - 64px);">
      <div class="sidebar"><!-- Sidebar nav --></div>
      <div class="main-content"><!-- Main content --></div>
    </div>
  </section>

  <!-- SCR-01: [Screen Name] — Loading State (VISIBLE, stacked below) -->
  <section id="SCR-01-loading" class="screen">
    <!-- Same layout with skeleton loaders replacing content -->
  </section>

  <!-- SCR-01: [Screen Name] — Empty State -->
  <section id="SCR-01-empty" class="screen">
    <!-- Empty state with CTA -->
  </section>

  <!-- More screens stacked below... -->

  <!-- NO display:none. NO visibility:hidden on any section. -->
</body>
</html>
```

Write complete HTML — no skeletons, realistic domain data, all sections filled.

### Phase 2: Serve + Two-Step Figma Capture

> **`generate_figma_design` is async — MUST use 2-step polling process. Run for BOTH desktop and mobile.**

```bash
# Start local HTTP server
python -m http.server 8765 --directory docs/specs/figma &
PROTO_SERVER_PID=$!
```

**Capture Desktop (1920×1080):**

Step 1 — Initial call with:
```
url:          http://localhost:8765/SCREEN-[feature]-desktop.html
outputMode:   "newFile"
fileName:     "[Project] [Feature] — Desktop 1920"
viewportWidth: 1920
viewportHeight: 1080
```
→ Returns `captureId`. Save as `desktopCaptureId`.

Step 2 — Poll every 5s with `desktopCaptureId`, up to 10 attempts:

| Response status | Action |
|----------------|--------|
| `"completed"` | Extract `desktopFileKey` + frame `nodeId`s → save |
| `"processing"` / `"pending"` | Wait 5s, retry |
| Error or 10 attempts exceeded | → Stop server, execute **Step 6C** |

**Capture Mobile (390×844):**

Step 1 — New initial call with:
```
url:          http://localhost:8765/SCREEN-[feature]-mobile.html
outputMode:   "existingFile"
fileKey:      [desktopFileKey]          ← same file, adds mobile page
fileName:     "[Project] [Feature] — Mobile 390"
viewportWidth: 390
viewportHeight: 844
```
→ Returns `mobileCaptureId`. Poll same way.

```bash
# Stop server after both captures complete or fail
kill $PROTO_SERVER_PID 2>/dev/null || true
```

### Phase 3: Record Figma Frame References

After successful capture, Figma returns a file URL. Extract `fileKey` and `nodeId` from each frame:
- URL format: `https://figma.com/design/{fileKey}/{fileName}?node-id={nodeId}`
- In `nodeId`: replace `-` with `:` (URL format `1-2` → API format `1:2`)

**Verify each frame** by calling `get_design_context(fileKey, nodeId)` — this confirms the frame is accessible and returns reference code.

Store all frame references in the SCREEN spec **Figma Frames** table (see output template).

**Ask user** to open the Figma file and confirm frames look correct before proceeding.

---

## 6C. SVG Fallback

> **MUST execute this step when:**
> - (a) User chose "SVG" in Step 6A, OR
> - (b) User chose "Figma" but `figma whoami` failed or any 6B step failed, OR
> - (c) User chose "Pencil" but `get_editor_state()` failed or any 6D step failed
>
> **DO NOT skip. DO NOT produce only design markdown. Always create artifact files.**

> Generates Figma-importable SVG wireframe files as fallback when Figma MCP is not connected.

**Output path**: `docs/specs/figma/SCREEN-[feature]-[SCR-XX]-desktop.svg`
**Mobile path**: `docs/specs/figma/SCREEN-[feature]-[SCR-XX]-mobile.svg` (375×812)

**SVG wireframe conventions:**

| Element | Color | Usage |
|---------|-------|-------|
| Page background | `#F5F5F5` | Root canvas |
| Panels / cards | `#FFFFFF` + `stroke="#E0E0E0"` | AppBar, sidebar, cards |
| Content placeholders | `#E0E0E0` fill | Text lines, image zones |
| Primary buttons | `#BDBDBD` fill + `#9E9E9E` stroke | CTA, submit buttons |
| Active/accent elements | `#B0C4A0` fill | Active nav, selected state |
| Annotation labels | `fill="#616161"` `font-size="11"` | Component name tags |
| Font | `font-family="Inter, sans-serif"` | All text |

**Desktop canvas**: 1440×900px — render these zones:
1. `AppBar` (y=0, h=64): logo rect + breadcrumb + action icons
2. `Sidebar` (x=0, y=64, w=240): nav items list with one active item highlighted
3. `PageHeader` (x=240, y=64, h=80): page title + primary action button
4. `ContentArea` (x=240, y=144): filters row + data table/cards with 3 skeleton rows
5. `Dialog` (if feature has create/edit): centered overlay with backdrop, form fields

**Rules:**
- Every zone MUST have a `<text>` label annotation (e.g. `AppBar`, `v-data-table`, `v-dialog`)
- Render actual `<rect>` shapes — NOT placeholder comments only
- Use `rx="4"` or `rx="8"` for cards and buttons to match modern UI
- Include skeleton rows (3 `<rect>` with `fill="#E0E0E0"`) in table/list zones

**Minimum SVG structure:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900">
  <!-- [SCR-XX] [Screen Name] — Desktop wireframe -->
  <rect width="1440" height="900" fill="#F5F5F5"/>
  <rect x="0" y="0" width="1440" height="64" fill="#FFFFFF" stroke="#E0E0E0" stroke-width="1"/>
  <text x="24" y="38" font-family="Inter,sans-serif" font-size="14" font-weight="600" fill="#333">Logo</text>
  <rect x="0" y="64" width="240" height="836" fill="#FFFFFF" stroke="#E0E0E0" stroke-width="1"/>
  <rect x="8" y="80" width="224" height="40" rx="6" fill="#B0C4A0"/>
  <text x="20" y="105" font-family="Inter,sans-serif" font-size="13" fill="#1A1A2E">[Nav Item]</text>
  <rect x="240" y="64" width="1200" height="836" fill="#F5F5F5"/>
  <rect x="256" y="80" width="400" height="32" rx="4" fill="#E0E0E0"/>
  <text x="256" y="130" font-family="Inter,sans-serif" font-size="11" fill="#616161">PageTitle</text>
  <!-- Add all remaining zones with <rect> and <text> labels -->
</svg>
```

Write each SVG file completely — render all zones with actual shapes, not placeholder comments.

---

## 6D. Pencil Dev Path — Create .pen Design on Canvas via Pencil MCP

> **Requires**: Pencil Dev extension installed in VS Code/Cursor (MCP auto-configured by extension).
> Agent calls Pencil MCP tools **programmatically** — NOT Pencil Studio's Cmd+K prompt.
> `batch_design` creates/modifies elements directly on canvas with structured operations.
> **If ANY step in 6D fails → stop immediately and execute Step 6C.**

### Phase 1: Initialize & Check Availability

1. Call `get_editor_state()` to verify Pencil MCP is available and get current context.
   - If error/not connected → inform user: "Pencil MCP not available. Falling back to SVG." → execute **Step 6C**
2. Call `get_guidelines(topic: "web-app")` (or `"mobile-app"` / `"landing-page"` based on product type from Step 1).
   - Extract layout rules, spacing conventions, component patterns.
3. Call `get_style_guide_tags()` → get available style tags.
4. Call `get_style_guide(tags: [5-10 tags matching product type + industry + style from Step 1])`.
   - Extract color palette, typography, visual direction — use alongside design-system output.
5. Create/open `.pen` file:
   `open_document(filePathOrNew: "docs/specs/pencil/SCREEN-[feature].pen")`
   - If `docs/specs/pencil/` does not exist → create it first.

### Phase 2: Set Up Design Tokens as Pencil Variables

Map the Design Tokens from Step 5 to Pencil variable format:

```
set_variables(variables: {
  "color-primary":      { type: "color", value: "#[hex from Step 5]" },
  "color-surface":      { type: "color", value: "#[hex]" },
  "color-text-primary": { type: "color", value: "#[hex]" },
  "color-text-muted":   { type: "color", value: "#[hex]" },
  "color-border":       { type: "color", value: "#[hex]" },
  "color-success":      { type: "color", value: "#[hex]" },
  "color-error":        { type: "color", value: "#[hex]" },
  "space-1":            { type: "number", value: 4 },
  "space-2":            { type: "number", value: 8 },
  "space-4":            { type: "number", value: 16 },
  "space-6":            { type: "number", value: 24 },
  "space-8":            { type: "number", value: 32 },
  "font-family":        { type: "string", value: "[font from Step 1]" }
})
```

If project supports dark mode → add theme axes:

```
set_variables(themes: { "mode": ["light", "dark"] }, variables: {
  "color-primary": { type: "color", value: [
    { theme: { mode: "light" }, value: "#[light-hex]" },
    { theme: { mode: "dark" },  value: "#[dark-hex]" }
  ]}
  // ... repeat for other color variables
})
```

### Phase 3: Build Screens with batch_design

For each screen (SCR-01, SCR-02, etc.), build in logical batches of **max 25 operations per call**.

**Batch strategy** — build in this order:

```
Batch 1 — Screen frame + top-level structure:
  SCR01=I("root", { type:"frame", width:1440, height:900, layout:"vertical", name:"SCR-01 [Name] Default" })
  appbar=I(SCR01, { type:"frame", height:64, layout:"horizontal", fill:"$color-surface", padding:[0,16,0,16], alignItems:"center" })
  body=I(SCR01, { type:"frame", layout:"horizontal", height:"fill_container" })
  sidebar=I("body", { type:"frame", width:240, layout:"vertical", fill:"$color-surface", padding:[16,8,16,8], gap:4 })
  main=I("body", { type:"frame", width:"fill_container", layout:"vertical", padding:[24,24,24,24], gap:16 })

Batch 2 — AppBar content:
  logo=I("appbar", { type:"text", content:"[ProjectName]", fontSize:18, fontWeight:700, fill:"$color-text-primary" })
  // breadcrumb, notification icons, avatar...

Batch 3 — Sidebar navigation items:
  navItem1=I("sidebar", { type:"frame", height:40, layout:"horizontal", fill:"$color-primary", rx:6, padding:[8,12,8,12], alignItems:"center" })
  navLabel1=I("navItem1", { type:"text", content:"[Active Item]", fill:"#FFFFFF", fontSize:14 })
  navItem2=I("sidebar", { type:"frame", height:40, layout:"horizontal", padding:[8,12,8,12], alignItems:"center" })
  navLabel2=I("navItem2", { type:"text", content:"[Other Item]", fill:"$color-text-primary", fontSize:14 })
  // ... more nav items

Batch 4 — Main content (page header + data area):
  pageHeader=I("main", { type:"frame", layout:"horizontal", justifyContent:"space_between", alignItems:"center" })
  title=I("pageHeader", { type:"text", content:"[Page Title]", fontSize:24, fontWeight:700, fill:"$color-text-primary" })
  ctaBtn=I("pageHeader", { type:"frame", rx:8, fill:"$color-primary", padding:[8,16,8,16], layout:"horizontal", alignItems:"center" })
  ctaText=I("ctaBtn", { type:"text", content:"+ Create New", fill:"#FFFFFF", fontSize:14, fontWeight:500 })
  // filters, data table rows, cards...
  // Use realistic domain data — not "Lorem ipsum"

Batch 5 — Screen states (loading, empty, error):
  // Call find_empty_space_on_canvas(direction:"right") for positioning
  SCR01_load=I("root", { type:"frame", width:1440, height:900, layout:"vertical", name:"SCR-01 [Name] Loading" })
  // ... same structure with skeleton rectangles (fill:"$color-border", rx:4) replacing content
  SCR01_empty=I("root", { type:"frame", width:1440, height:900, layout:"vertical", name:"SCR-01 [Name] Empty" })
  // ... empty state illustration + CTA

Batch 6 — Mobile viewport (390x844):
  SCR01_mob=I("root", { type:"frame", width:390, height:844, layout:"vertical", name:"SCR-01 [Name] Mobile" })
  // ... stacked layout, hamburger menu, bottom tab bar if applicable
```

**Rules for batch_design:**
- Use Pencil variables (`"$color-primary"`, `"$space-4"`) for all colors and spacing — enables token changes to cascade automatically
- Use realistic domain data matching the SRS feature context
- Render ALL mandatory states: default, loading, empty, error (minimum)
- Create mobile viewport (390x844) for each screen
- Label each frame with descriptive `name` property for developer reference

### Phase 4: Visual Validation (MANDATORY)

For each screen frame:

1. Call `get_screenshot(nodeId: "[screenFrameId]")` — visually inspect:
   - Alignment and spacing consistency (8pt grid)
   - Color contrast (body text 4.5:1 per WCAG)
   - Component hierarchy matches wireframe from Step 4
   - No overlapping or clipped elements

2. Call `snapshot_layout(parentId: "[screenFrameId]")` — check for layout problems:
   - Overlapping children, elements outside parent bounds
   - Unexpected sizing (0-width/height elements)

3. If issues found → call `batch_design` with Update/Replace operations to fix → re-screenshot.
   - **Max 3 fix iterations per screen** — if still broken after 3 rounds, note issues and proceed.

### Phase 5: Export and Record References

1. Export PNG screenshots for each screen frame:
   ```
   export_nodes(nodeIds: [all screen frame IDs], outputDir: "docs/specs/pencil/exports", format: "png")
   ```
   - If `docs/specs/pencil/exports/` does not exist → create it.

2. Record all frame references in the SCREEN spec **Pencil Frames** table (see output template).

3. Record the `.pen` file path in the SCREEN spec metadata header:
   ```
   **Design Tool**: Pencil Dev
   **Pencil File**: docs/specs/pencil/SCREEN-[feature].pen
   ```

4. **Ask user** to open the `.pen` file in Pencil and confirm designs look correct before proceeding.

---

---

## 6E. Google Stitch Path — AI Screen Generation via Stitch MCP

> **Requires**: Google Cloud CLI + GCP project + `GOOGLE_CLOUD_PROJECT` env var + `gcloud auth application-default login`. See `.mcp.json` `_setup` for full steps.
> Free tier: 350 AI generations/month — sufficient for most feature sprints.
> **If ANY step in 6E fails → inform user and execute Step 6C.**

### Phase 1: Initialize Stitch Project

1. Call `list_projects` to view existing Stitch projects.
   - If error/not connected → inform user: "Stitch MCP not available. Falling back to SVG." → **Step 6C**
2. If existing project fits this feature → use it (note project ID).
3. If new project needed → call `create_project` with a descriptive name: `[ProjectName]-[feature]`.
4. Call `list_screens` on the project to check existing screens (for Design DNA extraction).

### Phase 2: Extract Design DNA (MANDATORY for visual consistency)

> Design DNA = the extracted design system from an existing reference screen.
> **Always extract before generating new screens** — prevents visual inconsistency.

If project has existing screens:
1. Pick the most representative reference screen (e.g., dashboard default state).
2. Call `extract_design_context(projectId, screenId)`.
3. Design DNA returns: primary/accent colors, font families, border radius, spacing patterns, layout style.
4. **Preserve this Design DNA object** — pass it to every `generate_screen_from_text` call.

If project has NO existing screens (new project):
- Generate the first screen WITHOUT Design DNA.
- After first screen is generated → run `extract_design_context` on it.
- Use the extracted DNA for all subsequent screens.

### Phase 3: Generate Screens with Prompts

For each screen defined in the wireframe spec (Step 4):

1. **Build a detailed prompt** combining:
   - Screen name and purpose (from SRS user stories)
   - UI library and framework (from PROJECT.md — e.g., "Tailwind CSS + shadcn/ui components")
   - Key UI elements (data table, form fields, modal dialogs)
   - Target viewport (desktop 1440px / mobile 375px)
   - States to generate (default, loading, empty, error)
   - Tone/style from design-system Step 1 output

   Example prompt:
   ```
   "Create a [Screen Name] screen for a [product type] web app using [UI library].
   Layout: sidebar navigation (240px) + main content area. Header with page title
   and '+ Create' CTA button. Below: filter bar with search input + status dropdown.
   Data table with columns: [col1, col2, col3], status chip, row actions menu.
   Pagination bar at bottom. Primary color: [hex]. Font: [font family].
   Clean minimal enterprise style, 8pt spacing grid."
   ```

2. Call `generate_screen_from_text(projectId, prompt, designContext)` for Default state.
   - `designContext` = Design DNA from Phase 2 (null for first screen of new project)
   - Returns `screenId`. Save for asset retrieval.

3. For Loading/Empty/Error states — generate separately with state-specific prompts:
   - Loading: `"Same layout but replace data table with skeleton rows (3 rows of gray placeholder bars)"`
   - Empty: `"No data in table. Center: empty state illustration + message 'No [items] found' + '+ Create [item]' button"`
   - Error: `"API error banner at top of content area. Red alert with message 'Failed to load [items]' + Retry button"`

4. For mobile viewport — generate with: `"Same screen adapted for 375px mobile. Single column layout, hamburger menu, bottom tab bar."`

### Phase 4: Retrieve Assets (PNG + Code)

For each generated screen:

1. Call `get_screen_image(projectId, screenId)` → base64 PNG.
   - Decode and save to: `docs/specs/stitch/[feature]-[SCR-XX]-[state].png`
   - If `docs/specs/stitch/` does not exist → create it.

2. Call `get_screen_code(projectId, screenId)` → HTML/CSS/React reference code.
   - Save to: `docs/specs/stitch/[feature]-[SCR-XX]-[state].html`
   - Note: reference/prototype code — implement-feature adapts to actual project framework.

3. Call `get_screen_metadata(projectId, screenId)` → verify screen title, dimensions, creation date.

### Phase 5: Map Design DNA to ClaudeBrew Design Tokens

After all screens are generated, map Stitch's Design DNA to the ClaudeBrew 3-layer token format:

**Primitive layer** — from Design DNA raw values:
```
--color-brand-500: [primary hex from DNA]
--color-brand-600: [slightly darker variant]
--font-family-base: [font from DNA]
```

**Semantic layer** — purpose-mapped:
```
--color-primary:       var(--color-brand-500)
--color-text-primary:  [body text hex from DNA]
--color-surface:       [background hex from DNA]
--color-border:        [border hex from DNA]
```

Add this token mapping to the SCREEN spec Design Tokens section (from Step 5).

### Phase 6: Record Stitch References in SCREEN Spec

Add **Stitch Screens** table to the SCREEN spec. Record project ID, screen IDs, PNG export paths, reference code paths, and Design DNA summary.

**Ask user** to view the generated screen PNGs and confirm visual direction before proceeding.

---

## Step 7: DrawIO Navigation Map

For features with 2+ screens, include a **Screen Navigation Map** in DrawIO XML:

```markdown
## Screen Navigation Map (DrawIO)

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Add screen nodes and navigation arrows here -->
    <!-- Screen: [SCR-XX] Label, arrow: user action label -->
  </root>
</mxGraphModel>
```

Navigation flows to document:
- Entry points (login redirect, menu click, deep link)
- Screen-to-screen transitions with trigger label
- Modal/dialog flows (open/close/confirm)
- Error redirects
```

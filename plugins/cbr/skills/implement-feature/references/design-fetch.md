# Design Context Fetch — Figma & Pencil MCP

> Reference for implement-feature. Loaded on-demand when SCREEN spec has Figma or Pencil Frames.

## Figma Design Context Fetch

Before implementing any frontend component, check `docs/specs/requirements/SCREEN-[feature].md` for a **Figma Frames** table.

**If Figma Frames table exists AND Figma MCP is connected:**

For each screen to implement:

```bash
# 1. Verify Figma MCP connection
# Call: figma whoami → confirms authentication

# 2. Extract from SCREEN spec Figma Frames table:
#    fileKey = the Figma file key
#    nodeId  = the node ID for each screen (e.g. "1-2", "3-45")
```

Then call these tools in sequence:

| Tool | Purpose | Output used for |
|------|---------|----------------|
| `get_code(fileKey, nodeId)` | Frame → React/Tailwind component structure | Component hierarchy, props, layout |
| `get_variable_defs(fileKey, nodeId)` | Frame → design tokens (colors, spacing, typography) | CSS variables, Tailwind config values |
| `get_image(fileKey, nodeId)` | Frame → rendered screenshot | Visual reference while coding |
| `get_code_connect_suggestions(fileKey)` | Map Figma components → real codebase components | Replace generic elements with actual imports |

**Use the fetched context as PRIMARY source of truth** — it overrides ASCII wireframe descriptions in the SCREEN spec.

**If Figma Frames table does NOT exist** → check for Pencil Frames table (below).
**If Figma MCP is not connected but Figma Frames table exists:**
→ Ask user: "Figma MCP is not connected. Proceed with SCREEN spec markdown instead?"

---

## Pencil Design Context Fetch

Check `docs/specs/requirements/SCREEN-[feature].md` for a **Pencil Frames** table.

**If Pencil Frames table exists AND Pencil MCP is connected:**

For each screen to implement:

```
# 1. Read the .pen file path from SCREEN spec Pencil Frames section
# 2. Extract frameId for each screen from the Pencil Frames table
```

Then call these tools in sequence:

| Tool | Purpose | Output used for |
|------|---------|----------------|
| `batch_get(filePath, nodeIds:[frameId], readDepth:3)` | Frame → full node tree with layout, styles, component refs | Component hierarchy, layout structure, props |
| `get_variables(filePath)` | File → all design tokens with theme values | CSS variables, Tailwind config values |
| `get_screenshot(filePath, nodeId:frameId)` | Frame → visual screenshot | Visual reference while coding |
| `get_guidelines(topic:"code")` | Code generation guidelines for target framework | Best practices, component mapping |

**Use the fetched context as PRIMARY source of truth.** Map Pencil nodes to framework components:

| Pencil Node | Framework Output |
|-------------|-----------------|
| `frame` (layout:vertical) | `flex flex-col` / `<div class="flex flex-col">` |
| `frame` (layout:horizontal) | `flex flex-row` / `<div class="flex flex-row">` |
| `text` | `<p>`, `<h1-h6>`, `<span>` based on fontSize/fontWeight |
| `rectangle` | `<div>` with background/border styles |
| `ref` (component instance) | Mapped component from project's UI library |
| `icon_font` | Icon component from project's icon library |

**Pencil variable → CSS mapping:**
- Color: `color-primary: "#2563EB"` → `--color-primary: #2563EB`
- Number: `space-2: 8` → `--space-2: 8px`
- Themed: `{ light: "#fff", dark: "#1a1a2e" }` → `:root { --bg: #fff }` + `.dark { --bg: #1a1a2e }`

**If Pencil MCP is not connected but Pencil Frames table exists:**
→ Read the `.pen` file directly with Read tool (it is JSON). Parse node structure for component hierarchy.
→ Use exported PNG screenshots in `docs/specs/pencil/exports/` as visual reference.
→ Use Design Tokens from SCREEN spec markdown as fallback.

**If neither Figma Frames nor Pencil Frames exists** (SVG fallback was used):
→ Use the ASCII wireframes, component hierarchy, and design tokens directly from the SCREEN spec markdown.

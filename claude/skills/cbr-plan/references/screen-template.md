# SCREEN File Output Document Template

Use this template when creating `docs/streams/[feature]-[YYYYMMDD]/requirements/SCREEN.md`.

```markdown
# Screen Design: [Feature Name]
**Feature ID**: [feature] | **Date**: [YYYY-MM-DD] | **Author**: cbr-plan
**Input SRS**: docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md
**UI Library**: [detected from PROJECT.md]
**Design Style**: [selected from design-system output]
**Design Tool**: [Figma MCP / Pencil Dev / SVG fallback]
**Pencil File**: [docs/streams/[feature]-[YYYYMMDD]/assets/pencil/SCREEN.pen — or N/A]

## Design System Applied
- **Style**: [Minimal / Enterprise / Consumer / ...]
- **Primary Color**: #[hex] — [rationale, e.g. "trust signal for fintech"]
- **Typography**: [font family] — [rationale]
- **Key UX Rules Applied**: [e.g. "Hick's Law: nav capped at 6 items / Fitts': CTA 48px min"]

## Screen List
| Screen ID | Name | Route | Access Role |
|-----------|------|-------|-------------|

---
## [SCR-XX] [Screen Name]

### 1. Layout Wireframe — Default State (ASCII)
```
[ASCII art — realistic, labeled with component names from PROJECT.md UI library]
```

### 2. Layout Wireframe — Loading State
```
[Skeleton loaders in place of content, spinner if applicable]
```

### 3. Layout Wireframe — Empty State
```
[Empty illustration + "No [items] yet" + primary CTA button]
```

### 4. Layout Wireframe — Mobile (375px)
```
[Stacked layout, bottom tab bar if mobile-first project]
```

### 5. Component Hierarchy
```
ViewName.[ext]
└── [UI_LIBRARY_COMPONENT]
    └── [child components]
```

### 6. UI Components & Props
| Component | Key Props | Events | Notes |
|-----------|-----------|--------|-------|

### 7. Role-based Visibility
| Element | Visible to | Hidden from |
|---------|-----------|-------------|

### 8. States
| State | Description | Trigger |
|-------|-------------|---------|
| Default | Normal render, data loaded | — |
| Loading | Skeleton/spinner | API call in progress |
| Empty | No data, CTA to create | List returns 0 items |
| Error | Error message + retry button | API error / network fail |
| Success | Toast notification + redirect | Create/update/delete completes |
| Validation | Inline field errors | Form submit with invalid input |

### 9. i18n Keys
| Key | Default EN | Notes |
|-----|-----------|-------|

### 10. Responsive Breakpoints
| Breakpoint | Layout Change |
|-----------|---------------|
| 1440px | Full layout |
| 1024px | Collapsed sidebar/nav |
| 768px | Tablet stacked |
| 375px | Mobile stack, bottom nav |

## Figma Frames
<!-- Populated by Step 2.3B (Figma MCP path) — only if user chose Figma -->
<!-- Developer: use get_design_context(fileKey, nodeId) to fetch component structure -->

| Screen | Figma Frame URL | File Key | Node ID |
|--------|----------------|----------|---------|
| [SCR-XX] [Name] | https://figma.com/design/[fileKey]/[name]?node-id=[nodeId] | [fileKey] | [nodeId] |

<!-- Figma MCP tools for cbr-implement:
     get_design_context(fileKey, nodeId) → component structure + reference code + screenshot
     get_variable_defs(fileKey, nodeId)  → design tokens (colors, spacing, typography)
     get_screenshot(fileKey, nodeId)     → rendered screenshot for reference
     get_code_connect_suggestions()      → map Figma nodes to real codebase components -->

## Pencil Frames
<!-- Populated by Step 2.3D (Pencil Dev MCP path) — only if user chose Pencil Dev -->
<!-- Developer: use batch_get(filePath, nodeIds) to read component structure for implementation -->

**Pencil File**: `docs/streams/[feature]-[YYYYMMDD]/assets/pencil/SCREEN.pen`

| Screen | Frame ID | Name | Viewport | Exported PNG |
|--------|----------|------|----------|--------------|
| [SCR-XX] [Name] Default | [frameId] | [frame name] | 1440x900 | [exports/[frameId].png](../assets/pencil/exports/[frameId].png) |
| [SCR-XX] [Name] Loading | [frameId] | [frame name] | 1440x900 | [exports/[frameId].png](../assets/pencil/exports/[frameId].png) |
| [SCR-XX] [Name] Mobile  | [frameId] | [frame name] | 390x844  | [exports/[frameId].png](../assets/pencil/exports/[frameId].png) |

<!-- Pencil MCP tools for cbr-implement:
     batch_get(filePath, nodeIds, readDepth:3) → full node tree with layout/styles/component refs
     get_variables(filePath)                   → all design tokens with theme values
     get_screenshot(filePath, nodeId)          → visual reference screenshot
     get_guidelines(topic:"code")              → code generation guidelines for target framework -->

## SVG Wireframes
<!-- Populated by Step 2.3C (SVG fallback) — used when Figma/Pencil unavailable or user chose SVG -->

| Screen | Desktop SVG | Mobile SVG |
|--------|-------------|------------|
| [SCR-XX] [Name] | [[SCR-XX]-desktop.svg](../assets/figma/[SCR-XX]-desktop.svg) | [[SCR-XX]-mobile.svg](../assets/figma/[SCR-XX]-mobile.svg) |

<!-- SVG files: open in Figma via File → Import → select .svg, or open directly in browser -->

## Design Tokens
<!-- Token format depends on UI library:
     shadcn/ui + Tailwind → use HSL CSS variables (e.g. hsl(var(--primary)))
     Other libraries → use hex/rem values
     Reference: design-system skill for 3-layer token architecture -->

### Color Variables
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | #[hex] | Primary buttons, active states |
| `--color-surface` | #[hex] | Card backgrounds |
| `--color-text-primary` | #[hex] | Body text |
| `--color-text-muted` | #[hex] | Labels, hints |
| `--color-border` | #[hex] | Input borders, dividers |
| `--color-success` | #[hex] | Success states |
| `--color-error` | #[hex] | Error/destructive states |

### Spacing Scale (8pt grid)
| Token | Value |
|-------|-------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-4` | 16px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-12` | 48px |

### Typography Scale
| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `--text-4xl` | 36px | 700 | Page titles |
| `--text-xl` | 20px | 600 | Section headings |
| `--text-base` | 16px | 400 | Body text |
| `--text-sm` | 14px | 500 | Labels, chips |

## Screen Navigation Map (DrawIO)
<!-- Include for features with 2+ screens -->

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Screen nodes: id, label=[SCR-XX] Name -->
    <!-- Arrows: user action labels (click, submit, cancel) -->
  </root>
</mxGraphModel>
```
```

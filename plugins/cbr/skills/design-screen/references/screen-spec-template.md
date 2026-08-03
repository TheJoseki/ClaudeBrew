# SCREEN Spec Output Template

> Reference for design-screen. Loaded on-demand when creating SCREEN spec.

## Template

File: `docs/streams/[feature]-[YYYYMMDD]/requirements/SCREEN.md`

```markdown
# Screen Design: [Feature Name]
**Feature ID**: [feature-name]
**Date**: [YYYY-MM-DD]
**Author**: design-screen
**Input SRS**: docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md
**UI Library**: [detected from PROJECT.md]
**Design Style**: [selected style from Step 1]
**Design Tool**: [Figma MCP / Pencil Dev / Google Stitch / SVG fallback]
**Pencil File**: [docs/streams/[feature]-[YYYYMMDD]/assets/pencil/SCREEN.pen — or N/A]
**Related Screens**: [IDs from existing SCREEN specs]

## Design System Applied
- **Style**: [Minimal / Enterprise / Consumer / ...]
- **Primary Color**: #[hex] — [rationale]
- **Typography**: [font family] — [rationale]
- **Key Principles**: [Hick's Law applied as... / Fitts' Law applied as...]

## Screen List
| Screen ID | Name | Route | Access Role |
|-----------|------|-------|-------------|

---
## [SCR-XX] [Screen Name]

### 1. Layout Wireframe — Default State
[ASCII art — realistic, labeled with component names]

### 2. Layout Wireframe — Loading State
[Skeleton loaders in place of content]

### 3. Layout Wireframe — Empty State
[Empty illustration + "No [items] yet" + CTA button]

### 4. Layout Wireframe — Mobile (375px)
[Stacked layout, bottom tab bar if applicable]

### 5. Component Hierarchy
ViewName.[ext]
+-- [PageHeaderComponent]
+-- [FilterBarComponent]
+-- [DataTableComponent]
    +-- [StatusChipComponent]
    +-- [ActionMenuComponent]
+-- [CreateDialogComponent]
    +-- [FormComponent]
+-- [ConfirmDeleteDialogComponent]

### 6. UI Components & Props
| Component | Key Props | Events | Notes |
|-----------|-----------|--------|-------|

### 7. Data Binding
| Variable | Type | Source | Notes |
|----------|------|--------|-------|

### 8. User Interactions
| Trigger | Action | Result |
|---------|--------|--------|

### 9. Role-based Visibility
| Element | Visible to | Hidden from |
|---------|-----------|-------------|

### 10. State Definitions
- **Loading**: [skeleton/spinner description]
- **Empty**: [empty state message + CTA]
- **Error**: [error notification + retry]
- **Success**: [toast message + redirect]
- **Validation**: [inline errors per field]

### 11. i18n Keys Required
| Key | Default Text (EN) | Notes |
|-----|------------------|-------|

### 12. Responsive Breakpoints
| Breakpoint | Layout Change |
|-----------|---------------|
| 1440px | Full layout |
| 1024px | Collapsed nav |
| 768px | Tablet stacked |
| 375px | Mobile stack, bottom nav |

## Design Tokens
[Insert token table from Step 5 — colors, spacing, typography, frame specs]

## Figma Frames
<!-- Populated by Step 6B — only if user chose Figma -->
| Screen | Figma Frame URL | File Key | Node ID |
|--------|----------------|----------|---------|

### Developer Agent — Figma Consumption
get_design_context(fileKey, nodeId, clientFrameworks)
get_variable_defs(fileKey, nodeId)
get_screenshot(fileKey, nodeId)

## Pencil Frames
<!-- Populated by Step 6D — only if user chose Pencil Dev -->
**Pencil File**: `docs/streams/[feature]-[YYYYMMDD]/assets/pencil/SCREEN.pen`

| Screen | Frame ID | Name | Viewport | Exported PNG |
|--------|----------|------|----------|--------------|

### Developer Agent — Pencil Consumption
batch_get(filePath, nodeIds, readDepth:3)
get_variables(filePath)
get_screenshot(filePath, nodeId)
get_guidelines(topic:"code")

## Stitch Screens
<!-- Populated by Step 6E — only if user chose Google Stitch -->
**Stitch Project ID**: `[projectId]`

| Screen | State | Stitch Screen ID | PNG Export | Reference Code |
|--------|-------|-----------------|------------|----------------|

### Design DNA Summary
| Token | Value | Source |
|-------|-------|--------|

### Developer Agent — Stitch Consumption
View PNGs in docs/streams/[feature]-[YYYYMMDD]/assets/stitch/. Reference HTML as structural prototype. Map DNA tokens to CSS vars.

## SVG Wireframes
<!-- Populated by Step 6C — used when other tools unavailable -->
| Screen | Desktop SVG | Mobile SVG |
|--------|-------------|------------|

## Screen Navigation Map
[Insert DrawIO XML from Step 7]
```




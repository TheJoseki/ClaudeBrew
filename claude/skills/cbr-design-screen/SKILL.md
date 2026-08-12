---
name: cbr-design-screen
description: "UI/UX Designer designs screen layout, wireframes, and UI component spec for any project. UI library detected from PROJECT.md/CLAUDE.md. TRIGGER: user asks to design UI screens, create wireframes, specify components for a feature. NOT FOR: implementing frontend code (use implement-feature)."
allowed-tools: Read, Grep, Glob, Write, Edit, Task, Agent
argument-hint: "[feature name] [--parallel]"
metadata:
  version: "3.1"
  category: core-sdlc
---

# Screen Design

Feature to design UI for:

$ARGUMENTS

## Step 0: Context Detection

Read `CLAUDE.md` (auto-loaded) or `PROJECT.md` to detect tech stack before taking action.
Do NOT hardcode framework assumptions (UI library, component names, routing conventions).

## Content Map
| Section | When to read |
| --- | --- |
| Step 0 | Always — detect UI library and framework first |
| Step 1: Read Input | Always — mandatory before designing |
| Step 1b: Design Intelligence | Always — run before wireframing |
| Parallel mode | Only when invoked with `--parallel` |
| Step 2: Design | Always — core design work |
| Step 3: SCREEN File | Always — mandatory output artifact |
| Checklist | Before marking done |

## Step 1: Read Input (MANDATORY)

- `docs/SCREEN_DESIGN.md` — existing screens for reference (if exists)
- `docs/REQUIREMENTS_ANALYSIS.md` — User stories, acceptance criteria (if exists)
- `docs/CODING_RULES.md` — FE rules, i18n rules (if exists)
- `docs/CODING_CONVENTION.md` — Component templates (if exists)
- `PROJECT.md` or `CLAUDE.md` — detect UI library (Vuetify, shadcn/ui, Ant Design, MUI, Bootstrap, etc.)
- Input SRS: `docs/streams/[feature]-[YYYYMMDD]/requirements/SRS.md`

## Step 1b: Design Intelligence (MANDATORY — run before wireframing)

> **Invoke**: `design-system` — get style/color/typography recommendations before wireframing.

Extract from the SRS input:
- **Product type**: dashboard / admin / consumer app / landing / mobile app / ...
- **Industry/domain**: fintech / healthcare / HR / ecommerce / logistics / ...
- **Style keywords**: minimal / enterprise / modern / playful / dark / ...
- **Target audience**: internal B2B / end consumers B2C / mixed

Then apply `design-system` to get:
- Recommended style direction and color palette
- Typography pairing
- Anti-patterns to avoid for this product type
- UX priority rules (Priority 1–5: Accessibility, Touch, Performance, Style, Layout)

**Fallback** (no scripts available): Use the `design-system` skill's Product Type → Style Guide table in `references/ux-intelligence.md`.

> **Do NOT produce**: Bento grid, Aurora/mesh gradients, neon on dark, glassmorphism everywhere, emoji icons, inconsistent spacing.

Apply the design system output as the foundation for all wireframes in Step 2.

## Parallel mode (`--parallel`)

**Default is single-stream** — design every screen in this context.

When invoked with `--parallel` and the feature has several **independent**
screens, spawn N `cbr-developer` subagents in one message — one screen (or
screen group) per worker, each owning only its own wireframe/asset files — then
synthesize the slices into the single SCREEN spec here. The design-system
decisions from Step 1b are shared context passed to every worker, so the screens
stay visually consistent; a worker never re-picks the palette or typography.

> **Procedure**: `{{CBR_ROOT}}/docs/references/parallel-mode.md`
> — when to split, disjoint file ownership, the hard File Ownership Rules to
> restate in every spawn prompt, and how to synthesize.

Parallel or not, this skill **stops after Step 3**. It never spawns
`implement-feature` — the user starts the next stage.

## Step 2: Design

1. Identify screens to design
2. Sketch ASCII wireframe for each screen (format is universal — use for all frameworks)
3. Select [UI_LIBRARY] components matching PROJECT.md tech stack — do NOT use components from a different library
4. Define component hierarchy
5. Specify role-based visibility
6. Define loading / empty / error states
7. List i18n keys needed

**Component name reference by UI library:**
- Vuetify 3: `v-data-table`, `v-dialog`, `v-btn`, `v-text-field`, `v-card`, etc.
- shadcn/ui: `DataTable`, `Dialog`, `Button`, `Input`, `Card`, etc.
- Ant Design: `Table`, `Modal`, `Button`, `Input`, `Card`, etc.
- MUI (Material UI): `DataGrid`, `Dialog`, `Button`, `TextField`, `Card`, etc.
- Bootstrap Vue / Nuxt UI / other: use equivalent component names from that library

Always use the library identified in PROJECT.md, not these examples directly.

## Step 3: Create SCREEN File (MANDATORY — DO NOT SKIP)

File: `docs/streams/[feature]-[YYYYMMDD]/requirements/SCREEN.md`

> **Template**: See [`references/template.md`](references/template.md) for the full output document template.

## Checklist before Done
- [ ] Design Intelligence completed: product type, style, color, typography selected
- [ ] No AI anti-patterns (bento, aurora, neon, glassmorphism everywhere, emoji icons)
- [ ] Wireframes clear (ASCII format is framework-agnostic)
- [ ] Components use correct [UI_LIBRARY] API from PROJECT.md — no wrong-version or wrong-library components
- [ ] All text has i18n key
- [ ] Role-based visibility specified
- [ ] Loading / empty / error states defined (minimum: default, loading, empty, error)
- [ ] Responsive breakpoints noted (mobile 375px required)
- [ ] Status color mapping consistent
- [ ] Design tokens section included (colors, spacing, typography)
- [ ] Design output created via one of: Figma MCP (6B) / Pencil Dev MCP (6D) / SVG wireframes (6C)
- [ ] If Pencil path: `.pen` file at `docs/streams/[feature]-[YYYYMMDD]/assets/pencil/SCREEN.pen`, design tokens as variables, exported PNGs
- [ ] If Figma path: HTML prototype + Figma frames with file key and node IDs
- [ ] If SVG path: SVG wireframe files at `docs/streams/[feature]-[YYYYMMDD]/assets/figma/[SCR-XX]-desktop.svg` + `-mobile.svg`
- [ ] SCREEN spec has appropriate design references table (Figma Frames / Pencil Frames / SVG Wireframes)
- [ ] File `docs/streams/[feature]-[YYYYMMDD]/requirements/SCREEN.md` CREATED ✅

## Verification

**Skill triggers correctly when:**
- User says: "Design the UI screens for the order management feature"
- User says: "Create wireframes for the user profile page"
- User says: "Specify the component layout for the dashboard module"

**Skill does NOT trigger for:**
- "Implement the order management frontend" (use implement-feature)
- "Design the API for order management" (use design-function)
- "Review the dashboard components" (use review-code)

**Expected outputs:**
- Artifact: `docs/streams/[feature]-[YYYYMMDD]/requirements/SCREEN.md`
- Quality gate: All screens have wireframes, i18n keys, role-based visibility, and loading/empty/error states

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| Before this | `design-system` | Always — run design intelligence (style, color, typography) first (Step 1b) |
| Before this | `analyze-requirement` | SRS does not exist yet — analyze requirements first |
| After this | `design-system` | Token architecture from the selected colors/fonts, plus shadcn/ui + Tailwind implementation patterns |
| After this | `implement-feature` | Pass the SCREEN spec on for implementation |
| After this | `get_guidelines("code")` (Pencil MCP) | Pencil code-gen guidelines needed (if Pencil path) |
| Pairs with | `design-function` | Parallel: SCREEN spec + TECH spec created together |

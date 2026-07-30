---
name: design-system
description: "Design system authority for web and mobile — UX intelligence, design tokens, and shadcn/Tailwind implementation in one skill. Covers style, color-palette and font-pairing selection from a bundled searchable database (67+ styles, 161 palettes, 57 font pairings, 161 product types, 99 UX guidelines, 25 chart types), three-layer token architecture (Primitive → Semantic → Component), CSS variables, Tailwind theme configuration, component state specs, dark mode, and shadcn/ui component patterns. TRIGGER: user asks to design a UI, choose a style, color palette or font pairing, review UX or accessibility, plan interaction patterns, create design tokens, establish a design system, set up CSS variables, configure a Tailwind theme, define component variants, implement UI components, set up shadcn/ui, add dark mode, or build responsive layouts. NOT FOR: pure backend logic, API or database design, infrastructure or DevOps work. The shadcn/Tailwind implementation half is React-only — skip it for Vue, React Native, or Flutter stacks."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
metadata:
  version: "4.0"
  category: design
---

# Design System — UX Intelligence, Tokens, Implementation

The single authority for how a product **looks, feels, moves, and is interacted
with**. Three tracks, one skill:

1. **Decide** — what style, palette, and typography this product should have,
   and which UX rules govern it.
2. **Define** — encode those decisions as a layered token system so they are
   reusable and themeable.
3. **Build** — implement the tokens as accessible shadcn/ui + Tailwind components.

**Decision criteria:** if the task changes how a feature looks, feels, moves, or
is interacted with, this skill applies.

**Skip for** pure backend logic, API/database design, infrastructure, and DevOps
work. The *Build* track additionally assumes a React-based framework (Next.js,
Vite, Remix, Astro) — for Vue, React Native, or Flutter, the *Decide* track still
applies but the shadcn/Tailwind guidance does not.

---

## Pick your track

| You need to… | Go to | Contains |
|---|---|---|
| Choose a style, palette, or font pairing; review UX/accessibility; plan interactions, layout, navigation, charts | `references/ux-intelligence.md` | Full rule set per category, the searchable database + scripts, product-type style guide, AI anti-patterns, pre-delivery checklist |
| Create design tokens, set up CSS variables, define component states, wire a Tailwind theme, add dark-mode theming | `references/tokens.md` | Three-layer architecture, spacing/typography scales, dark-mode pattern, state specs, token file formats, SCREEN-spec token section |
| Install shadcn/ui, build components, forms, dialogs, tables; make layouts responsive; ship dark mode | `references/implementation.md` | Setup, component patterns, next-themes dark mode, breakpoints, theme customization, accessibility rules, component catalog |

**Normal order is Decide → Define → Build.** Style and palette choices feed the
primitive/semantic token layers; those tokens feed the Tailwind theme. Jumping
straight to Build with no tokens is how hardcoded hex values get shipped.

---

## Quick Reference — rule categories by priority

| Priority | Category | Impact | Key Checks (Must Have) | Anti-Patterns (Avoid) |
|----------|----------|--------|------------------------|------------------------|
| 1 | Accessibility | CRITICAL | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels | Removing focus rings, Icon-only buttons without labels |
| 2 | Touch & Interaction | CRITICAL | Min size 44×44px, 8px+ spacing, Loading feedback | Reliance on hover only, Instant state changes (0ms) |
| 3 | Performance | HIGH | WebP/AVIF, Lazy loading, Reserve space (CLS < 0.1) | Layout thrashing, Cumulative Layout Shift |
| 4 | Style Selection | HIGH | Match product type, Consistency, SVG icons (no emoji) | Mixing flat & skeuomorphic randomly, Emoji as icons |
| 5 | Layout & Responsive | HIGH | Mobile-first breakpoints, Viewport meta, No horizontal scroll | Horizontal scroll, Fixed px container widths |
| 6 | Typography & Color | MEDIUM | Base 16px, Line-height 1.5, Semantic color tokens | Text < 12px body, Gray-on-gray, Raw hex in components |
| 7 | Animation | MEDIUM | Duration 150–300ms, Motion conveys meaning | Decorative-only animation, Animating width/height |
| 8 | Forms & Feedback | MEDIUM | Visible labels, Error near field, Progressive disclosure | Placeholder-only label, Errors only at top |
| 9 | Navigation Patterns | HIGH | Predictable back, Bottom nav ≤5, Deep linking | Overloaded nav, Broken back behavior |
| 10 | Charts & Data | LOW | Legends, Tooltips, Accessible colors | Relying on color alone to convey meaning |

The individual rules under each category are in `references/ux-intelligence.md`.

---

## The design database

A BM25 search engine over the full corpus ships with this skill — no install
step. Scripts resolve `data/` relative to themselves, so they run from any
directory.

```bash
# Complete design-system recommendation (style + palette + fonts + effects)
python ${CLAUDE_PLUGIN_ROOT}/skills/design-system/scripts/search.py \
  "healthcare patient dashboard" --design-system -p "Project Name"

# Targeted lookup
python ${CLAUDE_PLUGIN_ROOT}/skills/design-system/scripts/search.py "saas dashboard" --domain product
```

Domains: `style` `color` `chart` `landing` `product` `ux` `typography` `icons`
`react` `web` `google-fonts`. Add `--stack react-native` for stack-specific
guidelines, `--persist` to write a MASTER.md design system, `--json` for
machine-readable output.

**If Python is unavailable**, the references carry the guidance inline — the
rule set, the product-type style guide, and the token patterns all work without
scripts.

---

## Non-negotiables

These hold across all three tracks. Everything else is a recommendation.

- **Contrast ≥ 4.5:1** for body text, verified independently in light *and* dark
  mode. Never convey meaning by color alone.
- **Touch targets ≥ 44×44pt** (iOS) / 48×48dp (Android), with ≥ 8px spacing.
- **Semantic tokens, never raw hex in components.** Primitive → Semantic →
  Component; never skip the semantic layer.
- **Never invert colors for dark mode** — use purpose-mapped dark values.
- **Never remove focus rings.** Icon-only buttons always carry an `aria-label`.
- **Spacing on the 4/8pt grid**, always.
- **No emoji as icons** — use SVG (Lucide, Heroicons).

---

## Reference map

**Track entry points** (start here):

| File | Content |
|------|---------|
| `references/ux-intelligence.md` | Design intelligence: full rule set, database usage, style selection, anti-patterns, checklist |
| `references/tokens.md` | Token architecture: three layers, scales, dark mode, state specs, SCREEN-spec section |
| `references/implementation.md` | shadcn/ui + Tailwind: setup, patterns, dark mode, responsive, accessibility |

**Deep dives** (loaded on demand from the entry points):

| File | Content |
|------|---------|
| `references/token-architecture.md` | Naming conventions, W3C DTCG format, migration guide |
| `references/primitive-tokens.md` | Full color scales, spacing, typography, shadows, motion, z-index |
| `references/semantic-tokens.md` | Color semantics, interactive states, dark mode overrides |
| `references/component-tokens.md` | Per-component tokens: Button, Input, Card, Badge, Alert, Dialog, Table |
| `references/states-and-variants.md` | State definitions, focus ring spec, ARIA state patterns |
| `references/tailwind-integration.md` | CSS variables in HSL, tailwind.config.ts, @layer components |
| `references/component-specs.md` | Variant/size/state tables + ASCII anatomy diagrams |
| `references/shadcn-components.md` | Component catalog with TSX examples (25+ components) |
| `references/shadcn-accessibility.md` | Radix ARIA foundation, keyboard nav, focus management, testing checklist |
| `references/shadcn-theming.md` | Dark mode, CSS variable system, HSL format, multiple themes, base presets |
| `references/tailwind-utilities.md` | Utility class reference: layout, spacing, typography, colors, borders, shadows |
| `references/tailwind-responsive.md` | Mobile-first breakpoints, container queries, max-width queries |
| `references/tailwind-customization.md` | @theme directive, custom utilities, @apply, plugins, full config example |
| `references/canvas-design-system.md` | Canvas/poster visual design philosophy (uses bundled `canvas-fonts/`) |

**Bundled assets:** `scripts/` (search engine, design-system generator, shadcn
installer, Tailwind config generator, token validators, slide tooling),
`data/` (the CSV corpus), `templates/design-tokens-starter.json`,
`canvas-fonts/` (open-licensed font files, see `LICENSE.txt`).

---

## Skill connections

| Direction | Skill | When |
|-----------|-------|------|
| Pairs with | `design-screen` | Run design intelligence before wireframing; include the token table in every SCREEN spec |
| Input to | `implement-feature` | Developer builds components against these tokens and patterns |
| On accessibility findings | `review-code` | Accessibility violations → flag in code review |

---
name: cbr-design-system
description: "Design system authority for web and mobile — authors a portable DESIGN.md (Google's open Apache-2.0 format: YAML tokens + rationale) as the single source of truth, then implements it in shadcn/Tailwind, in one skill. Grounds style, color-palette and font-pairing choices in a bundled searchable database (67+ styles, 161 palettes, 57 font pairings, 99 UX guidelines), encodes them as a three-layer token architecture (Primitive → Semantic → Component), and enforces WCAG contrast with a linter. TRIGGER: user asks to design a UI, author or update a DESIGN.md, choose a style, color palette or font pairing, review UX or accessibility, plan interaction patterns, create design tokens, establish a design system, set up CSS variables, configure a Tailwind theme, define component variants, implement UI components, set up shadcn/ui, add dark mode, or build responsive layouts. NOT FOR: pure backend logic, API or database design, infra/DevOps. shadcn/Tailwind implementation is React-only (skip for Vue, React Native, Flutter)."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
metadata:
  version: "5.0"
  category: design
---

# Design System — DESIGN.md authoring, UX intelligence, implementation

The single authority for how a product **looks, feels, moves, and is interacted
with**. Its durable output is **`docs/DESIGN.md`** — a portable design system in
Google's open [DESIGN.md format](references/designmd-spec.md): machine-readable
YAML tokens (the *what*) + `##` rationale (the *why* each token exists). The
bundled corpus is **grounding evidence**, not the authority — you reason from it,
you never retrieve a frozen answer as final.

**Decision criteria:** if the task changes how a feature looks, feels, moves, or
is interacted with, this skill applies.

## Input-contract (open-or-join)

Resolve the artifact first:

- **`docs/DESIGN.md` exists** → **UPDATE** it in place. It is a living document;
  extend/revise tokens and rationale, never fork a second copy.
- **None** → **AUTHOR** one: scaffold it, fill the rationale, validate, write it
  to `docs/DESIGN.md`.

## The four moves

1. **Decide** — reason about style, palette, typography, and UX rules for this
   product, *grounded* by the corpus (`references/ux-intelligence.md`) + fresh
   sources (Context7 for shadcn/Tailwind docs, WebSearch for current patterns —
   cite URLs). Never ship a frozen catalog pick as the final answer.
2. **Define** — encode the decisions as DESIGN.md YAML tokens + rationale
   (`references/tokens.md` maps the three token layers onto the schema). Every
   token states its intent; every surface color carries an `on-<X>`.
3. **Validate** — the linter is the gate; DESIGN.md must pass before you stop:
   ```bash
   python {{CBR_ROOT}}/skills/cbr-design-system/scripts/designmd_lint.py docs/DESIGN.md
   ```
4. **Build** — implement the tokens as accessible shadcn/ui + Tailwind components
   (`references/implementation.md`), reading them *from* `docs/DESIGN.md` — no
   raw hex.

**Skip for** pure backend logic, API/database design, infrastructure, DevOps. The
*Build* move assumes React (Next.js, Vite, Remix, Astro); for Vue, React Native,
or Flutter the Decide/Define/Validate moves still apply, the shadcn/Tailwind
guidance does not.

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

## The corpus — grounding evidence, not the answer

A BM25 search engine over the bundled corpus ships with this skill (no install
step; scripts resolve `data/` relative to themselves). It **grounds** your
reasoning with real palettes/styles/fonts and their trade-offs — it is not the
decision-maker, and its taste ages, so always cross-check fresh sources and the
contrast linter.

```bash
# Scaffold a spec-valid DESIGN.md (YAML tokens + rationale) for docs/DESIGN.md:
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py \
  "healthcare patient dashboard" --design-system --format designmd -p "Project Name"

# Grounding lookups (candidates + trade-offs, never a final answer):
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py "saas dashboard" --domain product
```

Domains: `style` `color` `chart` `landing` `product` `ux` `typography` `icons`
`react` `web` `google-fonts`. Add `--stack react-native` for stack-specific
guidelines, `--json` for machine-readable output.

**If Python is unavailable**, the references carry the guidance inline — the rule
set, the product-type style guide, the token patterns, and the manual lint
checklist (`references/designmd-spec.md` §6) all work without scripts.

---

## Non-negotiables

These hold across all three tracks. Everything else is a recommendation.

- **`docs/DESIGN.md` is the single source of truth** for tokens — author/update
  it there, components read *from* it, and it **must pass `designmd_lint.py`**
  before the stage stops.
- **Every token states its intent**, and **every surface color has an `on-<X>`**
  foreground — that pair is what makes contrast machine-checkable.
- **Contrast ≥ 4.5:1** for body text, verified independently in light *and* dark
  mode (author a `dark:` override map). Never convey meaning by color alone.
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
| `references/designmd-spec.md` | **The DESIGN.md format contract** (pinned): sections, YAML token subset, `{ref}`, the cbr strict-superset (`on-*`, `dark:`), lint rules, manual checklist |
| `references/ux-intelligence.md` | Design intelligence: full rule set, corpus grounding usage, style selection, anti-patterns, checklist |
| `references/tokens.md` | Token architecture: three layers mapped onto the DESIGN.md YAML schema, scales, dark mode, state specs, SCREEN-spec section |
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
| `references/stitch-interop.md` | Optional, detect-if-available Stitch round-trip for `docs/DESIGN.md` (import-from-URL / upload) — never a dependency |

**Bundled assets:** `scripts/` (search/grounding engine, DESIGN.md generator
[`design_system.py` → `format_designmd`], the **DESIGN.md linter**
[`designmd_lint.py` + `contrast.py`], shadcn installer, Tailwind config
generator, slide tooling), `data/` (the CSV grounding corpus), `canvas-fonts/`
(open-licensed font files, see `LICENSE.txt`).

---

## Skill connections

| Direction | Skill | When |
|-----------|-------|------|
| Pairs with | `cbr-plan` (Step 2: Screen) | Author/refresh `docs/DESIGN.md` before wireframing; SCREEN specs reference it (never re-derive tokens) |
| Input to | `cbr-implement` | Developer builds components reading tokens from `docs/DESIGN.md` — no raw hex |
| On accessibility findings | `cbr-verify` | Feed `designmd_lint.py` output as accessibility findings in code review |

# UX Intelligence — Rules, Database, and Style Selection

Design intelligence for web and mobile: the full UX rule set by priority
category, the searchable database (67+ styles, 161 color palettes, 57 font
pairings, 161 product types, 99 UX guidelines, 25 chart types across 10
technology stacks), the product-type style guide, AI anti-patterns, and the
pre-delivery checklist.

The 10 priority categories are summarized in `SKILL.md`; the rules for each are
below.

---

## When to apply

**Must use:**
- Designing new pages (Landing Page, Dashboard, Admin, SaaS, Mobile App)
- Creating or refactoring UI components (buttons, modals, forms, tables, charts)
- Choosing color schemes, typography systems, spacing standards, or layout systems
- Reviewing UI code for user experience, accessibility, or visual consistency
- Implementing navigation structures, animations, or responsive behavior
- Making product-level design decisions (style, information hierarchy, brand expression)

**Recommended:**
- UI looks "not professional enough" but the reason is unclear
- Receiving feedback on usability or experience
- Pre-launch UI quality optimization
- Aligning cross-platform design (Web / iOS / Android)
- Building design systems or reusable component libraries

**Skip:** pure backend logic, API/database design, infrastructure, DevOps work.

**Decision criteria:** if the task will change how a feature **looks, feels,
moves, or is interacted with**, these rules apply.

---

## The rules

### 1. Accessibility (CRITICAL)

- `color-contrast` — Minimum 4.5:1 ratio for normal text (large text 3:1)
- `focus-states` — Visible focus rings on interactive elements (2–4px)
- `alt-text` — Descriptive alt text for meaningful images
- `aria-labels` — aria-label for icon-only buttons
- `keyboard-nav` — Tab order matches visual order; full keyboard support
- `form-labels` — Use label with for attribute
- `skip-links` — Skip to main content for keyboard users
- `heading-hierarchy` — Sequential h1→h6, no level skip
- `color-not-only` — Don't convey info by color alone (add icon/text)
- `dynamic-type` — Support system text scaling; avoid truncation as text grows
- `reduced-motion` — Respect prefers-reduced-motion; reduce/disable animations
- `escape-routes` — Provide cancel/back in modals and multi-step flows

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` — Min 44×44pt (Apple) / 48×48dp (Material); extend hit area beyond visual bounds if needed
- `touch-spacing` — Minimum 8px gap between touch targets
- `hover-vs-tap` — Use click/tap for primary interactions; don't rely on hover alone
- `loading-buttons` — Disable button during async operations; show spinner or progress
- `error-feedback` — Clear error messages near problem
- `cursor-pointer` — Add cursor-pointer to clickable elements (Web)
- `gesture-conflicts` — Avoid horizontal swipe on main content; prefer vertical scroll
- `tap-delay` — Use touch-action: manipulation to reduce 300ms delay (Web)
- `press-feedback` — Visual feedback on press (ripple/highlight)
- `haptic-feedback` — Use haptic for confirmations; avoid overuse
- `safe-area-awareness` — Keep primary touch targets away from notch, Dynamic Island, gesture bar

### 3. Performance (HIGH)

- `image-optimization` — Use WebP/AVIF, responsive images (srcset/sizes), lazy load
- `image-dimension` — Declare width/height or use aspect-ratio to prevent layout shift
- `font-loading` — Use font-display: swap/optional to avoid invisible text (FOIT)
- `font-preload` — Preload only critical fonts; avoid over-preloading
- `critical-css` — Prioritize above-the-fold CSS
- `lazy-loading` — Lazy load non-hero components via dynamic import
- `bundle-splitting` — Split code by route/feature to reduce initial load and TTI
- `virtualize-lists` — Virtualize lists with 50+ items
- `progressive-loading` — Use skeleton screens instead of long blocking spinners for >1s
- `debounce-throttle` — Use debounce/throttle for high-frequency events (scroll, resize, input)

### 4. Style Selection (HIGH)

- `style-match` — Match style to product type (see Design System Generator below)
- `consistency` — Use same style across all pages
- `no-emoji-icons` — Use SVG icons (Heroicons, Lucide), not emojis
- `color-palette-from-product` — Choose palette from product/industry
- `effects-match-style` — Shadows, blur, radius aligned with chosen style
- `platform-adaptive` — Respect platform idioms (iOS HIG vs Material)
- `state-clarity` — Make hover/pressed/disabled states visually distinct
- `elevation-consistent` — Consistent elevation/shadow scale for cards, sheets, modals
- `dark-mode-pairing` — Design light/dark variants together
- `primary-action` — Each screen should have only one primary CTA

### 5. Layout & Responsive (HIGH)

- `viewport-meta` — width=device-width initial-scale=1 (never disable zoom)
- `mobile-first` — Design mobile-first, then scale up
- `breakpoint-consistency` — Use systematic breakpoints (375 / 768 / 1024 / 1440)
- `readable-font-size` — Minimum 16px body text on mobile (avoids iOS auto-zoom)
- `line-length-control` — Mobile 35–60 chars per line; desktop 60–75 chars
- `horizontal-scroll` — No horizontal scroll on mobile
- `spacing-scale` — Use 4pt/8dp incremental spacing system
- `container-width` — Consistent max-width on desktop (max-w-6xl / 7xl)
- `z-index-management` — Define layered z-index scale (0 / 10 / 20 / 40 / 100 / 1000)
- `content-priority` — Show core content first on mobile; fold secondary content
- `visual-hierarchy` — Establish hierarchy via size, spacing, contrast — not color alone

### 6. Typography & Color (MEDIUM)

- `line-height` — Use 1.5–1.75 for body text
- `line-length` — Limit to 65–75 characters per line
- `font-pairing` — Match heading/body font personalities
- `font-scale` — Consistent type scale (e.g. 12 14 16 18 24 32)
- `contrast-readability` — Darker text on light backgrounds
- `color-semantic` — Define semantic color tokens (primary, secondary, error, surface) not raw hex
- `color-dark-mode` — Dark mode uses desaturated/lighter tonal variants, not inverted colors
- `color-accessible-pairs` — Foreground/background pairs must meet 4.5:1 (AA) or 7:1 (AAA)
- `color-not-decorative-only` — Functional color must include icon/text; avoid color-only meaning
- `weight-hierarchy` — Bold headings (600–700), Regular body (400), Medium labels (500)
- `whitespace-balance` — Use whitespace intentionally to group related items

### 7. Animation (MEDIUM)

- `duration-timing` — Use 150–300ms for micro-interactions; complex transitions ≤400ms
- `transform-performance` — Use transform/opacity only; avoid animating width/height/top/left
- `loading-states` — Show skeleton or progress indicator when loading exceeds 300ms
- `excessive-motion` — Animate 1–2 key elements per view max
- `easing` — Use ease-out for entering, ease-in for exiting; avoid linear for UI transitions
- `motion-meaning` — Every animation must express a cause-effect relationship
- `spring-physics` — Prefer spring/physics-based curves for natural feel
- `exit-faster-than-enter` — Exit animations ~60–70% of enter duration
- `stagger-sequence` — Stagger list/grid item entrance by 30–50ms per item
- `interruptible` — Animations must be interruptible by user tap/gesture

### 8. Forms & Feedback (MEDIUM)

- `input-labels` — Visible label per input (not placeholder-only)
- `error-placement` — Show error below the related field
- `submit-feedback` — Loading then success/error state on submit
- `required-indicators` — Mark required fields (e.g. asterisk)
- `empty-states` — Helpful message and action when no content
- `toast-dismiss` — Auto-dismiss toasts in 3–5s
- `confirmation-dialogs` — Confirm before destructive actions
- `inline-validation` — Validate on blur (not keystroke); show error after user finishes
- `input-type-keyboard` — Use semantic input types (email, tel, number)
- `password-toggle` — Provide show/hide toggle for password fields
- `error-recovery` — Error messages must include a clear recovery path (retry, edit, help)
- `multi-step-progress` — Multi-step flows show step indicator; allow back navigation
- `error-clarity` — Error messages must state cause + how to fix (not just "Invalid input")
- `destructive-emphasis` — Destructive actions use red and are separated from primary actions

### 9. Navigation Patterns (HIGH)

- `bottom-nav-limit` — Bottom navigation max 5 items; use labels with icons
- `drawer-usage` — Use drawer/sidebar for secondary navigation, not primary actions
- `back-behavior` — Back navigation must be predictable; preserve scroll/state
- `deep-linking` — All key screens must be reachable via deep link / URL
- `nav-label-icon` — Navigation items must have both icon and text label
- `nav-state-active` — Current location must be visually highlighted in navigation
- `modal-escape` — Modals must offer a clear close/dismiss affordance
- `state-preservation` — Navigating back must restore previous scroll, filter state, and input
- `adaptive-navigation` — Large screens (≥1024px) prefer sidebar; small screens use bottom/top nav
- `navigation-consistency` — Navigation placement must stay the same across all pages
- `persistent-nav` — Core navigation must remain reachable from deep pages

### 10. Charts & Data (LOW)

- `chart-type` — Match chart type to data type (trend→line, comparison→bar, proportion→pie/donut)
- `color-guidance` — Use accessible color palettes; avoid red/green only pairs
- `data-table` — Provide table alternative for accessibility
- `legend-visible` — Always show legend near the chart
- `tooltip-on-interact` — Provide tooltips/data labels on hover (Web) or tap (mobile)
- `axis-labels` — Label axes with units and readable scale
- `responsive-chart` — Charts must reflow on small screens
- `empty-data-state` — Show meaningful empty state when no data exists
- `no-pie-overuse` — Avoid pie/donut for >5 categories; switch to bar chart

---

## Design System Generator (bundled Python scripts)

The database and its BM25 search engine ship with this skill — no install step.
Scripts resolve `data/` relative to themselves, so run them from any directory.

```bash
# Full design-system recommendation for a product
python {{CBR_ROOT}}/skills/design-system/scripts/search.py \
  "<product_type> <industry> <keywords>" --design-system -p "Project Name"
```

**What `--design-system` outputs:**
1. Pattern recommendation (Hero-Centric, Social Proof, etc.)
2. Style selection (from 67 styles)
3. Color palette (WCAG-compliant hex codes)
4. Typography pairing (Google Fonts)
5. Key effects (shadows, transitions, hover states)
6. Anti-patterns to avoid

**Domain searches:**
```bash
python {{CBR_ROOT}}/skills/design-system/scripts/search.py "<keyword>" --domain <domain>
# Domains: style | color | chart | landing | product | ux | typography | icons |
#          react | web | google-fonts
```

**Stack-specific guidelines:**
```bash
python {{CBR_ROOT}}/skills/design-system/scripts/search.py "<keyword>" --stack react-native
```

**Persisting a design system** (Master + Overrides pattern):
```bash
python {{CBR_ROOT}}/skills/design-system/scripts/search.py "<query>" \
  --design-system --persist -p "Project Name" [--page "dashboard"]
```
Writes `design-system/<project-slug>/MASTER.md` as the global source of truth,
plus optional per-page override files under `pages/`. When building a page,
check its override file first; it wins over MASTER.md.

Add `--json` for machine-readable output, `-n` to change the result count
(default 3).

**If Python is unavailable:** use the rule sections above and the fallback style
guide below — they contain the guidance inline and work without scripts.

### Database files

`data/` holds the CSV corpus the scripts search: `styles.csv`, `colors.csv`,
`typography.csv`, `google-fonts.csv`, `products.csv`, `landing.csv`,
`ux-guidelines.csv`, `charts.csv`, `icons.csv`, `react-performance.csv`,
`app-interface.csv`, `ui-reasoning.csv` (the reasoning rules behind
`--design-system`), and `stacks/react-native.csv`.

---

## Product Type → Style Guide (fallback reference)

| Product Type | Recommended Style | Color Mood | Typography Mood |
|-------------|------------------|------------|-----------------|
| SaaS / Admin | Clean minimal, data-dense | Primary blue/slate | Inter / Roboto |
| Enterprise B2B | Professional, structured | Navy + warm gray | Inter + Roboto Slab |
| Fintech / Banking | Trust, premium | Deep blue + green | Plus Jakarta Sans |
| Healthcare | Clean, accessible | Teal/blue + white | Lato / Source Sans |
| E-commerce | Visual, conversion | Brand primary + warm | Nunito / Poppins |
| Creative / Portfolio | Bold, expressive | Vibrant + dark mode | DM Sans / Sora |
| Consumer App | Friendly, immersive | Brand primary + warm accents | Nunito / Poppins |
| Gaming / Entertainment | Immersive, dark | Neon accents + dark bg | Rajdhani / Orbitron |
| Healthcare / Medical | Calm, accessible | Soft teal + white | Lato / Source Sans Pro |
| Real Estate | Premium, trust | Earth tones + gold | Playfair Display + Open Sans |

---

## AI Anti-Patterns (NEVER produce these)

| Anti-Pattern | Why to avoid |
|---|---|
| Bento grid layouts | Overused, predictable AI aesthetic |
| Hero: split left-text / right-image | Generic, seen everywhere |
| Mesh / Aurora gradients | Lazy AI default aesthetic |
| Glassmorphism on everything | Overused 2022 trend |
| Deep cyan + dark background | AI fintech look |
| Neon glow on dark background | AI cyberpunk look |
| Rounded-everything cards with no hierarchy | No visual tension |
| Emoji used as icons | Font-dependent, uncontrollable |
| Inconsistent spacing | Always use 8-point grid |
| Purple gradient hero | Overused AI startup look |

---

## Pre-Delivery Checklist

**Accessibility:**
- [ ] All meaningful images/icons have accessibility labels
- [ ] Color is not the only indicator for any state
- [ ] Contrast ratio ≥ 4.5:1 for body text in both light and dark mode
- [ ] All interactive elements keyboard-reachable and focusable

**Interaction:**
- [ ] All tappable elements have clear pressed feedback
- [ ] Touch targets ≥ 44×44pt (iOS) / 48×48dp (Android)
- [ ] Micro-interaction timing: 150–300ms with natural easing
- [ ] Disabled states are visually clear and non-interactive

**Layout:**
- [ ] Mobile-first verified at 375px
- [ ] Safe areas respected (notch, gesture bar)
- [ ] 8dp spacing rhythm maintained
- [ ] No horizontal scroll on any screen

**Typography & Color:**
- [ ] Semantic color tokens used (no hardcoded hex in components)
- [ ] Both light and dark modes tested
- [ ] Body text ≥ 16px on mobile

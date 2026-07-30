---
name: design-system
description: "Design token architecture — three-layer token system (Primitive → Semantic → Component), CSS variables, Tailwind theme configuration, and component state specs. TRIGGER: user asks to create design tokens, establish a design system, set up CSS variables, configure Tailwind theme, or define component variants. Pairs with ui-ux-pro-max (design intelligence) and ui-styling (implementation)."
allowed-tools: Read, Grep, Glob, Write, Edit
metadata:
  version: "3.1"
  category: design
---

# Design System — Token Architecture

Token architecture, component specifications, and CSS variable systems for consistent, themeable UIs.

## When to Use

- Creating or auditing design token systems
- Setting up CSS variable architecture for a project
- Configuring Tailwind theme with custom tokens
- Defining component state specs (hover, active, disabled, error)
- Design-to-code handoff documentation
- Establishing light/dark mode theming infrastructure

---

## Three-Layer Token Architecture

```
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

**Why 3 layers:**
- **Primitive** = raw values, changed rarely (brand palette)
- **Semantic** = purpose mapping, enables theme switching
- **Component** = component-specific overrides, enables per-component customization

### Example

```css
/* Layer 1: Primitive */
--color-blue-50:  #EFF6FF;
--color-blue-600: #2563EB;
--color-blue-700: #1D4ED8;

/* Layer 2: Semantic */
--color-primary:          var(--color-blue-600);
--color-primary-hover:    var(--color-blue-700);
--color-surface:          #FFFFFF;
--color-surface-muted:    var(--color-gray-50);
--color-text-primary:     var(--color-gray-900);
--color-text-muted:       var(--color-gray-500);
--color-error:            var(--color-red-600);
--color-success:          var(--color-green-600);
--color-border:           var(--color-gray-200);

/* Layer 3: Component */
--button-bg:              var(--color-primary);
--button-bg-hover:        var(--color-primary-hover);
--button-text:            #FFFFFF;
--input-border:           var(--color-border);
--input-border-focus:     var(--color-primary);
--card-bg:                var(--color-surface);
--card-border:            var(--color-border);
```

---

## Spacing Scale (8pt Grid)

```css
--space-1:  4px;    /* tight */
--space-2:  8px;    /* compact */
--space-3:  12px;
--space-4:  16px;   /* default */
--space-5:  20px;
--space-6:  24px;   /* section */
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;   /* large section */
--space-16: 64px;
--space-20: 80px;   /* page section */
```

---

## Typography Scale

```css
--text-xs:   12px;
--text-sm:   14px;
--text-base: 16px;   /* body default */
--text-lg:   18px;
--text-xl:   20px;
--text-2xl:  24px;
--text-3xl:  30px;
--text-4xl:  36px;
--text-5xl:  48px;

/* Line heights */
--leading-tight:   1.25;
--leading-normal:  1.5;   /* body */
--leading-relaxed: 1.75;

/* Font weights */
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
```

---

## Dark Mode Token Pattern

```css
:root {
  --color-surface:    #FFFFFF;
  --color-text:       #111827;
  --color-border:     #E5E7EB;
  --color-muted:      #F9FAFB;
}

[data-theme="dark"] {
  --color-surface:    #1F2937;
  --color-text:       #F9FAFB;
  --color-border:     #374151;
  --color-muted:      #111827;
}
```

**Rules:**
- Never invert colors for dark mode — use purpose-mapped dark values
- Test contrast independently for both modes (4.5:1 minimum)
- Semantic tokens enable theme switching with one attribute change

---

## Tailwind Theme Configuration

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          hover:   'var(--color-primary-hover)',
        },
        surface:  'var(--color-surface)',
        border:   'var(--color-border)',
        muted:    'var(--color-surface-muted)',
      },
      spacing: {
        // custom spacing tokens map here
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'sans-serif'],
      },
    },
  },
}
```

---

## Component State Specs

### Standard Component States

| State | Visual Signal | Token |
|-------|--------------|-------|
| Default | Normal render | `--button-bg` |
| Hover | Slightly darker/elevated | `--button-bg-hover` |
| Active/Pressed | Scale 0.98, deeper | `--button-bg-active` |
| Focus | 2–3px focus ring, primary color | `--color-focus-ring` |
| Disabled | 40–50% opacity, no pointer events | `opacity-50 cursor-not-allowed` |
| Loading | Spinner, disabled interaction | same as disabled |
| Error | Red border, error text below | `--color-error` |
| Success | Green border/check | `--color-success` |

### State Token Pattern (Per Component)

```css
/* Button */
--btn-primary-bg:        var(--color-primary);
--btn-primary-bg-hover:  var(--color-primary-hover);
--btn-primary-text:      #FFFFFF;
--btn-primary-disabled:  opacity 0.5;

/* Input */
--input-bg:              var(--color-surface);
--input-border:          var(--color-border);
--input-border-focus:    var(--color-primary);
--input-border-error:    var(--color-error);
--input-text:            var(--color-text-primary);
--input-placeholder:     var(--color-text-muted);
```

---

## Design Token File Formats

### JSON (Source of Truth)

```json
{
  "primitive": {
    "color": {
      "blue-600": { "value": "#2563EB" },
      "gray-900": { "value": "#111827" }
    }
  },
  "semantic": {
    "color": {
      "primary": { "value": "{primitive.color.blue-600}" },
      "text": { "value": "{primitive.color.gray-900}" }
    }
  }
}
```

### CSS Output

```css
:root {
  /* Primitive */
  --color-blue-600: #2563EB;
  --color-gray-900: #111827;
  /* Semantic */
  --color-primary: var(--color-blue-600);
  --color-text:    var(--color-gray-900);
}
```

---

## SCREEN Spec: Design Tokens Section

When creating a SCREEN spec, include this token section:

```markdown
## Design Tokens

### Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | #2563EB | Primary buttons, active states |
| `--color-surface` | #FFFFFF | Card backgrounds |
| `--color-text-primary` | #111827 | Body text |
| `--color-text-muted` | #6B7280 | Labels, hints |
| `--color-border` | #E5E7EB | Input borders, dividers |
| `--color-success` | #16A34A | Success states |
| `--color-error` | #DC2626 | Error/destructive states |

### Spacing Scale
| Token | Value |
|-------|-------|
| `--space-2` | 8px |
| `--space-4` | 16px |
| `--space-6` | 24px |
| `--space-8` | 32px |

### Typography Scale
| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `--text-4xl` | 36px | 700 | Page titles |
| `--text-xl` | 20px | 600 | Section headings |
| `--text-base` | 16px | 400 | Body text |
| `--text-sm` | 14px | 500 | Labels, chips |
```

---

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Raw hex in components (`color: #2563EB`) | Use semantic token (`color: var(--color-primary)`) |
| Same token for both light and dark | Use `[data-theme="dark"]` override |
| Skipping semantic layer | Map primitives → semantic → component; never skip |
| Inconsistent spacing (17px, 23px, 41px) | Always use 4/8dp grid values |
| One giant token file | Split: primitive.css + semantic.css + components.css |

---

## Reference Docs

Deep-dive references are in `references/`:

| File | Content |
|------|---------|
| `references/token-architecture.md` | Three-layer system, naming conventions, W3C DTCG format, migration guide |
| `references/primitive-tokens.md` | Full color scales, spacing (4px base), typography, shadows, motion, z-index |
| `references/semantic-tokens.md` | Color semantics, interactive states, dark mode overrides |
| `references/component-tokens.md` | Per-component token specs: Button, Input, Card, Badge, Alert, Dialog, Table |
| `references/states-and-variants.md` | State definitions, focus ring spec, ARIA state patterns |
| `references/tailwind-integration.md` | CSS variables in HSL, tailwind.config.ts, @layer components, dark mode toggle |
| `references/component-specs.md` | Variant/size/state tables + ASCII anatomy diagrams per component |

---

## Skill Connections

| Direction | Skill | When |
|-----------|-------|------|
| After | `ui-ux-pro-max` | Derive token colors/fonts from design system output |
| Before | `ui-styling` | Tokens defined here → configure Tailwind/shadcn theme |
| Pairs with | `design-screen` | Include token table in every SCREEN spec |
| Input to | `implement-feature` | Developer uses tokens when implementing components |
| Called by | `ui-designer-agent` | Step 5 — Figma-compatible token section |

# Design Intelligence Reference — UI Designer Agent

> Reference for ui-designer-agent. Loaded on-demand during Step 1 design intelligence.

## Extract from SRS Input

- **Product type**: dashboard / admin panel / consumer app / landing / mobile app
- **Industry/domain**: fintech / healthcare / HR / ecommerce / logistics
- **Style keywords** from project context: minimal / enterprise / modern / playful / dark
- **Target audience**: internal users (enterprise) / end consumers (B2C) / mixed

## Run ui-ux-pro-max Design System (MANDATORY)

```bash
# Try install locations in order:
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "[product_type] [industry] [style_keywords]" --design-system -p "[Project Name]"
# OR
python3 .agent/.shared/ui-ux-pro-max/scripts/search.py "[product_type] [industry] [style_keywords]" --design-system -p "[Project Name]"
```

Example: `python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "admin dashboard hr management minimal enterprise" --design-system -p "HRM Portal"`

Outputs: color palette, typography pairing, component library recommendations, spacing system, icon style.

**Additional domain searches** (if Python scripts available):
```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "[product_type]" --domain ux
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "[style_keywords]" --domain typography
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "[product_type]" --domain color
```

If Python unavailable → use `/ui-ux-pro-max` skill inline Quick Reference (Product Type → Style Guide table + 99 UX rules). Do NOT skip design intelligence.

## Design System Fallback Table

| Product Type | Recommended Style | Color Palette | Typography |
|-------------|------------------|---------------|------------|
| Admin / Dashboard | Clean minimal, data-dense | Primary blue/slate + accent | Inter / Roboto |
| Enterprise B2B | Professional, structured | Navy + warm gray | Inter + Roboto Slab |
| Consumer / B2C | Friendly, visual | Brand primary + warm accents | Nunito / Poppins |
| Fintech | Trust, premium | Deep blue + green success | Plus Jakarta Sans |
| Healthcare | Clean, accessible | Teal/blue + white space | Lato / Source Sans |
| Creative / SaaS | Modern, bold | Vibrant + dark mode capable | DM Sans / Sora |

## Anti-Pattern Checklist (AVOID these AI defaults)

- ❌ Bento grid layouts (overused, predictable)
- ❌ Hero section split left-text / right-image (generic)
- ❌ Mesh / Aurora gradients (lazy AI aesthetic)
- ❌ Glassmorphism on everything (overused)
- ❌ Deep cyan + dark background (AI fintech look)
- ❌ Neon glow on dark background (AI cyberpunk look)
- ❌ Rounded-everything cards with no hierarchy
- ❌ Emoji used as icons (use SVG icon libraries)
- ❌ Inconsistent spacing (use 8-point grid system)

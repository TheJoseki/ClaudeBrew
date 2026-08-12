# Design Intelligence Reference

> Reference for `cbr-plan`'s Screen internal phase. Loaded on-demand during Step 2.1 design intelligence.

## Extract from SRS Input

- **Product type**: dashboard / admin panel / consumer app / landing / mobile app
- **Industry/domain**: fintech / healthcare / HR / ecommerce / logistics
- **Style keywords** from project context: minimal / enterprise / modern / playful / dark
- **Target audience**: internal users (enterprise) / end consumers (B2C) / mixed

## Run the design-system search (MANDATORY)

```bash
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py \
  "[product_type] [industry] [style_keywords]" --design-system -p "[Project Name]"
```

Example: `python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py "admin dashboard hr management minimal enterprise" --design-system -p "HRM Portal"`

Outputs: color palette, typography pairing, component library recommendations, spacing system, icon style.

**Additional domain searches:**
```bash
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py "[product_type]" --domain ux
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py "[style_keywords]" --domain typography
python {{CBR_ROOT}}/skills/cbr-design-system/scripts/search.py "[product_type]" --domain color
```

If Python is unavailable → use the Design System Fallback Table below. Do NOT skip design
intelligence.

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

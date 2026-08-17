# DESIGN.md — vendored spec digest (pinned)

> **Pinned source.** This is a distilled, offline copy of the open DESIGN.md format — the parse + lint
> contract for this skill. It is a *rules digest*, not a mirror.
>
> - Upstream: `https://github.com/google-labs-code/design.md` (Apache-2.0)
> - Pinned commit: `9bf8eae67128b6cc55ad9bf86665767deb4c11cd`
> - Spec `version:` at pin: **`alpha`**
> - **Re-sync protocol (deliberate, not automatic):** re-fetch the pinned file → diff against this digest →
>   update → bump the commit SHA above. Never fetch upstream at runtime; this file is the contract.

DESIGN.md is a single markdown file at a project's `docs/` root (like `README.md`, but for the design
system). Two layers:

1. **YAML front-matter** — machine-readable tokens (deterministic → CSS vars / Tailwind).
2. **`##` Markdown body** — human rationale: *why* each decision exists (intent per token).

---

## 1. YAML front-matter schema (upstream `alpha`)

```yaml
version: <string>          # optional; current upstream value: "alpha"
name: <string>             # REQUIRED
description: <string>      # optional
omitted: <string[] | OmittedSection[]>   # sections intentionally left out
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string | token-reference>
```

**Token types (verbatim from upstream):**

- **Color** — any CSS color: hex, `rgb()`, `oklch()`, named. e.g. `"#1A1C1E"`, `"oklch(62% 0.18 250)"`.
- **Dimension** — number + unit (`px`, `em`, `rem`). e.g. `48px`, `-0.02em`.
- **Typography** — object with fields: `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`,
  `letterSpacing`, `fontFeature`, `fontVariation`.
- **Token reference** — `{path.to.token}` (e.g. `{colors.primary}`, `{rounded.sm}`).

**Component properties** (keys under a `components.<name>`): `backgroundColor`, `textColor`, `typography`,
`rounded`, `padding`, `size`, `height`, `width` — values are literals or token references.

## 2. Reference syntax

Curly-brace path: `{colors.primary}`, `{colors.tertiary-container}`, `{rounded.sm}`. Upstream lint rule
`broken-ref` flags any reference that does not resolve to a defined token.

## 3. Section structure (`##` headings)

Present sections must appear in this order (upstream rule `section-order`); any may be absent. List absent
ones in `omitted`. A **duplicate** section heading is an error; an **unknown** heading is preserved without
error.

| # | Section | Aliases |
|---|---------|---------|
| 1 | Overview | Brand & Style |
| 2 | Colors | — |
| 3 | Typography | — |
| 4 | Layout | Layout & Spacing |
| 5 | Elevation & Depth | Elevation |
| 6 | Shapes | — |
| 7 | Components | — |
| 8 | Do's and Don'ts | — |

## 4. Minimal example (upstream)

```markdown
---
name: Heritage
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
rounded:
  sm: 4px
spacing:
  sm: 8px
---

## Overview
Architectural Minimalism meets Journalistic Gravitas.

## Colors
The palette is rooted in high-contrast neutrals and a single accent color.
```

---

## 5. cbr extensions (a documented STRICT SUPERSET)

cbr authors and lints a **strict superset** of the alpha spec. Everything above stays valid and portable
(Stitch / Cursor / any consumer sees a clean spec-compliant file); cbr only *adds* rigor. Three additions:

### 5a. Constrained YAML subset (the parse contract)

The linter parses the front-matter with **stdlib only** (no `import yaml`, no pip dependency). To stay
parseable it constrains the token front-matter to this subset — **author within it, fail loud outside it**:

- Top-level keys limited to those in §1 (`version`, `name`, `description`, `omitted`, `colors`,
  `typography`, `rounded`, `spacing`, `components`) plus the cbr keys in §5c.
- `colors` / `rounded` / `spacing`: one level deep — `key: scalar` (a CSS color, a Dimension, or a
  `{ref}`).
- `typography.<name>`: one nested object of scalar fields only (the Typography fields in §1).
- `components.<name>`: one nested object of `key: (scalar | {ref})`. Component **variants** (hover, active,
  pressed, focus) are **separate entries** with related names, e.g. `button`, `button-hover` — not deeper
  nesting.
- **Quote color values** — an unquoted leading `#` is a YAML comment (the value would parse to null in a
  spec-compliant reader), so the linter rejects it as a Critical `parse` finding. A trailing ` # comment`
  after a quoted value is fine.
- No YAML anchors, tags, multi-doc streams, or flow-style maps/sequences. Out-of-subset input is a
  Critical parse finding naming the offending key.

### 5b. `on-<X>` requirement (makes contrast machine-checkable)

Every semantic color token `X` that is used as a background/surface MUST have an `on-<X>` counterpart
naming its foreground text/icon color. A semantic color with no resolvable `on-*` counterpart is a
**Critical** finding — without the pair, contrast is uncheckable. (This is stricter than the alpha spec,
which mandates no naming convention.)

### 5c. `dark:` map for dark-mode tokens (the alpha spec defines no light/dark)

Upstream expresses a single mode. cbr requires contrast verified in **light and dark**, so dark overrides
live in a sibling top-level map that mirrors `colors` token names:

```yaml
colors:            # the light set
  surface: "#FFFFFF"
  on-surface: "#0F172A"
dark:              # cbr extension — dark overrides, same token names
  surface: "#0F172A"
  on-surface: "#F8FAFC"
```

Tokens absent from `dark:` inherit their `colors` value. Vanilla DESIGN.md consumers ignore the unknown
`dark:` key (per the unknown-key tolerance in §1's parse subset); cbr's linter contrast-checks both sets.

### 5d. Lint rules cbr enforces (see `designmd_lint.py`, Phase 2)

`section-order` · `duplicate-heading` · `broken-ref` (upstream) + `missing-on-color` (§5b) +
`contrast` (every `on-<X>`↔`<X>` pair ≥ 4.5:1, or ≥ 3:1 for large/UI, in **both** `colors` and `dark`) +
`uncheckable-color` (**Critical, fail-closed** — a surface / `on-*` pair whose color is not hex or `rgb()`,
e.g. `oklch()` or a named color, so contrast cannot be verified: use hex/`rgb()` on surfaces) +
`missing-intent` (a color with no rationale line in the Colors body → Major/warn).

---

## 6. If Python is unavailable — manual lint checklist

- [ ] `name:` present; `version:` set (echo the pinned upstream `version:` — `alpha`).
- [ ] `##` sections in the §3 order; absent ones listed in `omitted`; no duplicate heading.
- [ ] Every `{ref}` resolves to a defined token.
- [ ] Every background/surface color has an `on-<X>`; each `on-<X>`↔`<X>` pair ≥ 4.5:1 (≥ 3:1 large/UI).
- [ ] `dark:` overrides present for any surface whose light contrast pairing differs; re-check contrast there.
- [ ] Front-matter stays within the §5a subset (no nesting/anchors beyond what is listed).

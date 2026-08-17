# Stitch interop (optional, detect-if-available)

Because `docs/DESIGN.md` uses the **open** DESIGN.md format, it round-trips with
Google Stitch and any other DESIGN.md-aware tool. This interop is a **convenience,
never a dependency** — the skill authors and lints `docs/DESIGN.md` fully offline;
Stitch only adds import/round-trip when its MCP happens to be connected.

## The rule

- **Detect first.** Only use Stitch tools if the Stitch MCP is present in the
  session (its tools appear under an `mcp__stitch__*` namespace / via ToolSearch).
  If absent, skip silently and proceed with local authoring + `designmd_lint.py`.
- **Never require it.** ClaudeBrew installs into environments with no Stitch. A
  DESIGN.md that only lint-passes locally is complete on its own.
- **Local validators stay authoritative.** Whatever Stitch returns, re-run
  `designmd_lint.py` on the result — cbr's contrast + `on-*` rules are the gate,
  and Stitch's own `design-md` skill has no WCAG checks.

## Two supported flows (minimal this release)

1. **Import a design system from a URL** → seed a DESIGN.md.
   Use the Stitch import tool (e.g. `import-design-from-url`) to pull an existing
   system, then translate it into `docs/DESIGN.md` and lint it. Treat the import
   as *grounding*, not a finished artifact.

2. **Round-trip an authored DESIGN.md** into Stitch to generate/preview screens.
   `upload_design_md` (base64) → `create_design_system_from_design_md` renders the
   system in Stitch. Author locally, validate locally, then push — not the reverse.

Broader Stitch features (screen generation, variants, applying a system to
screens) are out of scope for this release; add them behind the same
detect-if-available guard when needed.

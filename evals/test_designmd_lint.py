#!/usr/bin/env python3
"""Unit tests for the DESIGN.md linter (claude/skills/cbr-design-system/scripts).

Standalone runner to match the sibling evals/test_*.py suite:
    python evals/test_designmd_lint.py
Exit 0 = all pass, 1 = a failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "claude", "skills", "cbr-design-system", "scripts")
sys.path.insert(0, SCRIPTS)

import contrast  # noqa: E402
from designmd_lint import lint_text  # noqa: E402


def criticals(text):
    return [f for f in lint_text(text) if f["severity"] == "CRITICAL"]


def rules(text):
    return {f["rule"] for f in lint_text(text)}


PASSING = """---
version: alpha
name: Test System
colors:
  background: "#FFFFFF"
  on-background: "#0F172A"
  primary: "#1E40AF"
  on-primary: "#FFFFFF"
dark:
  background: "#0F172A"
  on-background: "#F8FAFC"
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
---

## Overview
A test system.

## Colors
background is the surface; primary is the brand; on- tokens are foregrounds.

## Typography
Sans.
"""

CONTRAST_FAIL = """---
name: Bad
colors:
  primary: "#FDE68A"
  on-primary: "#FEF3C7"
---
## Colors
primary is pale.
"""

BROKEN_REF = """---
name: Ref
colors:
  primary: "#1E40AF"
  on-primary: "#FFFFFF"
components:
  button:
    backgroundColor: "{colors.nope}"
---
## Colors
primary brand.
"""

WRONG_ORDER = """---
name: Order
colors:
  primary: "#1E40AF"
  on-primary: "#FFFFFF"
---
## Colors
primary brand.

## Overview
out of order.
"""

MISSING_ON = """---
name: Missing
colors:
  surface: "#FFFFFF"
---
## Colors
surface only.
"""

OMITTED_OK = """---
name: Omit
omitted:
  - Shapes
  - Elevation & Depth
colors:
  primary: "#1E40AF"
  on-primary: "#FFFFFF"
---
## Overview
x

## Colors
primary brand.
"""

OUT_OF_SUBSET = """---
name: Deep
colors:
  primary: {a: 1}
---
## Colors
primary brand.
"""

DARK_FAIL = """---
name: DarkFail
colors:
  background: "#FFFFFF"
  on-background: "#0F172A"
dark:
  background: "#0F172A"
---
## Overview
x

## Colors
background surface.
"""

COMMENTED_FAIL = """---
name: Commented
colors:
  primary: "#FDE68A"  # brand yellow
  on-primary: "#FEF3C7"  # near-white text
---
## Colors
primary is pale.
"""

UNQUOTED_HASH = """---
name: Unquoted
colors:
  primary: #1E40AF
  on-primary: "#FFFFFF"
---
## Colors
primary brand.
"""


OKLCH_UNCHECKABLE = """---
name: Oklch
colors:
  primary: "oklch(62% 0.18 250)"
  on-primary: "oklch(98% 0 0)"
---
## Colors
primary brand.
"""


def _designmd_roundtrip_ok():
    from design_system import format_designmd
    ds = {
        "project_name": "Round Trip", "category": "SaaS",
        "colors": {"primary": "#1E40AF", "secondary": "#3B82F6", "cta": "#F97316",
                   "background": "#F8FAFC", "text": "#0F172A", "notes": "trust blue"},
        "typography": {"heading": "Inter", "body": "Inter", "mood": "clean"},
        "style": {"name": "Minimalism", "best_for": "dashboards"},
        "anti_patterns": "neon gradients",
    }
    return len(criticals(format_designmd(ds))) == 0


CASES = [
    ("contrast self-test", lambda: round(contrast.contrast_ratio("#000", "#FFF"), 1) == 21.0),
    ("passing has no criticals", lambda: len(criticals(PASSING)) == 0),
    ("contrast failure caught", lambda: "contrast" in rules(CONTRAST_FAIL)),
    ("broken ref caught", lambda: "broken-ref" in rules(BROKEN_REF)),
    ("section order caught", lambda: "section-order" in rules(WRONG_ORDER)),
    ("missing on-color caught", lambda: "missing-on-color" in rules(MISSING_ON)),
    ("omitted parses clean", lambda: len(criticals(OMITTED_OK)) == 0),
    ("out-of-subset -> parse critical", lambda: "parse" in rules(OUT_OF_SUBSET)),
    ("light-pass / dark-fail", lambda: any(
        f["rule"] == "contrast" and "[dark]" in f["message"] for f in lint_text(DARK_FAIL))),
    ("light-pass / dark-fail: light clean", lambda: not any(
        f["rule"] == "contrast" and "[light]" in f["message"] for f in lint_text(DARK_FAIL))),
    ("commented failing color stays CRITICAL (H1-A)", lambda: any(
        f["rule"] == "contrast" and f["severity"] == "CRITICAL" for f in lint_text(COMMENTED_FAIL))),
    ("unquoted '#' value -> parse critical (H1-B)", lambda: "parse" in rules(UNQUOTED_HASH)),
    ("uncheckable oklch surface -> CRITICAL (M1)", lambda: any(
        f["rule"] == "uncheckable-color" and f["severity"] == "CRITICAL"
        for f in lint_text(OKLCH_UNCHECKABLE))),
    ("format_designmd output lints clean", _designmd_roundtrip_ok),
]


def main():
    failed = []
    for name, fn in CASES:
        try:
            ok = fn()
        except Exception as e:  # noqa: BLE001
            ok, name = False, f"{name} (raised {e!r})"
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            failed.append(name)
    if failed:
        print(f"\n{len(failed)} FAILED")
        return 1
    print(f"\nOK - {len(CASES)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""WCAG contrast helpers for the DESIGN.md linter (`designmd_lint.py`).

Pure stdlib. The luminance/hex formulas are the same ones used by
`data/_sync_all.py` (color derivation); this module is the canonical home for
the *lint* path. `_sync_all.py` (a legacy one-shot maintainer script) keeps its
own copy on purpose — re-pointing it risks the corpus rebuild.

Only hex and rgb()/rgba() are contrast-checkable here. oklch(), named colors,
and gradients raise ValueError so the linter can warn "uncheckable" rather than
silently pass or crash.
"""
import re

_HEXCHARS = set("0123456789abcdefABCDEF")
_RGB_RE = re.compile(r"rgba?\(\s*([0-9.]+)[ ,]+([0-9.]+)[ ,]+([0-9.]+)", re.I)


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:  # #RRGGBBAA -> drop alpha for the contrast estimate
        h = h[:6]
    if len(h) != 6 or any(c not in _HEXCHARS for c in h):
        raise ValueError(f"not a hex color: {h!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parse_color(value):
    """(r, g, b) 0-255 for a hex or rgb()/rgba() string; ValueError otherwise."""
    v = value.strip().strip('"').strip("'")
    if v.startswith("#"):
        return hex_to_rgb(v)
    m = _RGB_RE.match(v)
    if m:
        return tuple(min(255, max(0, int(round(float(x))))) for x in m.groups())
    raise ValueError(f"unsupported color format: {value!r}")


def _linearize(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = (_linearize(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    """WCAG 2.x contrast ratio. fg/bg may be (r,g,b) tuples or CSS strings."""
    if isinstance(fg, str):
        fg = parse_color(fg)
    if isinstance(bg, str):
        bg = parse_color(bg)
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def passes(fg, bg, large=False):
    """AA threshold: 3:1 for large/UI text, 4.5:1 otherwise."""
    return contrast_ratio(fg, bg) >= (3.0 if large else 4.5)


if __name__ == "__main__":
    assert round(contrast_ratio("#000000", "#FFFFFF"), 1) == 21.0
    assert round(contrast_ratio("#FFFFFF", "#FFFFFF"), 1) == 1.0
    assert passes("#0F172A", "#FFFFFF")          # dark ink on white
    assert not passes("#AAAAAA", "#FFFFFF")      # low-contrast gray on white
    assert passes("rgb(15,23,42)", "#FFFFFF")
    print("contrast.py self-test OK")

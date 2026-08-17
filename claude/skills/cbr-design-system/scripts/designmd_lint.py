#!/usr/bin/env python3
"""Linter for DESIGN.md — the physics-to-enforcement gate for cbr-design-system.

Validates a DESIGN.md against the vendored spec digest
(`references/designmd-spec.md`): structural correctness, token-reference
integrity, and WCAG contrast — the last two being the anti-slop / accessibility
guarantees. Pure stdlib (no pip dependency); parses the *constrained YAML
subset* documented in the digest §5a and fails loud on anything outside it.

Usage:
    python designmd_lint.py <path/to/DESIGN.md> [--json]

Exit code 0 = no Critical findings; 1 = at least one Critical; 2 = usage error.
"""
import json
import os
import re
import sys

# ── vendored-digest constants (keep in sync with references/designmd-spec.md) ──
CANONICAL_SECTIONS = [
    ("Overview", {"brand & style"}),
    ("Colors", set()),
    ("Typography", set()),
    ("Layout", {"layout & spacing"}),
    ("Elevation & Depth", {"elevation"}),
    ("Shapes", set()),
    ("Components", set()),
    ("Do's and Don'ts", set()),
]
TOP_LEVEL_KEYS = {"version", "name", "description", "omitted",
                  "colors", "typography", "rounded", "spacing", "components", "dark"}
# cbr strict-superset: core surfaces that MUST carry an on-<name> foreground.
REQUIRED_ON = ["background", "surface", "card", "popover",
               "primary", "secondary", "accent", "muted", "destructive"]
REF_RE = re.compile(r"^\{[A-Za-z0-9_.\-]+\}$")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contrast import contrast_ratio, parse_color  # noqa: E402


class LintError(Exception):
    """Out-of-subset front-matter — a Critical parse failure."""


def _finding(sev, rule, msg):
    return {"severity": sev, "rule": rule, "message": msg}


# ── constrained-subset YAML parser (digest §5a) ───────────────────────────────
def _scalar(val, raw):
    v = val.strip()
    if not v:
        return v
    # Quoted scalar: read to the matching quote; allow a trailing ` # comment`.
    if v[0] in ('"', "'"):
        q = v[0]
        end = v.find(q, 1)
        if end == -1:
            raise LintError(f"unterminated quoted string: {raw!r}")
        rest = v[end + 1:].strip()
        if rest and not rest.startswith("#"):
            raise LintError(f"unexpected text after quoted value: {raw!r}")
        return v[1:end]
    # Unquoted leading '#' is a YAML comment (the value would be null) — fail loud
    # rather than store a hex string that spec-compliant parsers drop.
    if v.startswith("#"):
        raise LintError(f'unquoted "#" value — quote hex colors, e.g. "#1A1C1E": {raw!r}')
    # Strip an inline ` #` comment from an unquoted scalar, then re-check emptiness.
    hash_at = v.find(" #")
    if hash_at != -1:
        v = v[:hash_at].rstrip()
    if not v:
        return v
    if v[0] == "{":
        if REF_RE.match(v):
            return v
        raise LintError(f"flow-style maps not allowed (only {{ref}} tokens): {raw!r}")
    if v[0] in ("[", "&", "*", "|", ">"):
        raise LintError(f"unsupported YAML construct: {raw!r}")
    return v


def parse_front_matter(fm_text):
    root = {}
    # stack of (indent, container, key_in_parent, parent)
    stack = [(-1, root, None, None)]
    for raw in fm_text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise LintError(f"tab indentation not allowed: {raw!r}")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise LintError(f"indent must be a multiple of 2 spaces: {raw!r}")
        while stack[-1][0] >= indent:
            stack.pop()
        _, container, ckey, cparent = stack[-1]
        line = raw.strip()

        if line.startswith("- "):  # block sequence item (e.g. `omitted:`)
            if not isinstance(container, list):
                if container:
                    raise LintError(f"mixed map/sequence under a key: {raw!r}")
                container = []
                cparent[ckey] = container
                stack[-1] = (stack[-1][0], container, ckey, cparent)
            container.append(_scalar(line[2:], raw))
            continue

        if ":" not in line:
            raise LintError(f"expected 'key: value' or 'key:': {raw!r}")
        if isinstance(container, list):
            raise LintError(f"mixed sequence/map under a key: {raw!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            child = {}
            container[key] = child
            stack.append((indent, child, key, container))
        else:
            container[key] = _scalar(val, raw)
    return root


# ── structure + reference + contrast checks ───────────────────────────────────
def _flatten_paths(fm):
    """token path -> value, for {ref} resolution."""
    paths = {}
    for group in ("colors", "dark", "rounded", "spacing"):
        for k, v in (fm.get(group) or {}).items():
            paths[f"{group}.{k}"] = v
    for grp in ("typography", "components"):
        for name, obj in (fm.get(grp) or {}).items():
            paths[f"{grp}.{name}"] = obj
            if isinstance(obj, dict):
                for f, v in obj.items():
                    paths[f"{grp}.{name}.{f}"] = v
    return paths


def _check_shapes(fm, out):
    for grp in ("colors", "dark", "rounded", "spacing"):
        node = fm.get(grp)
        if node is None:
            continue
        if not isinstance(node, dict):
            out.append(_finding("CRITICAL", "schema", f"`{grp}` must be a map"))
            continue
        for k, v in node.items():
            if isinstance(v, (dict, list)):
                out.append(_finding("CRITICAL", "schema", f"`{grp}.{k}` must be a scalar, got a block"))
    for grp in ("typography", "components"):
        node = fm.get(grp)
        if node is None:
            continue
        if not isinstance(node, dict):
            out.append(_finding("CRITICAL", "schema", f"`{grp}` must be a map"))
            continue
        for name, obj in node.items():
            if not isinstance(obj, dict):
                out.append(_finding("CRITICAL", "schema", f"`{grp}.{name}` must be a map of fields"))
                continue
            for f, v in obj.items():
                if isinstance(v, (dict, list)):
                    out.append(_finding("CRITICAL", "schema", f"`{grp}.{name}.{f}` nested too deep"))


def _resolve(value, paths, _seen=None):
    """Resolve a value that may be a {ref} chain to a concrete scalar, or None."""
    _seen = _seen or set()
    if not isinstance(value, str) or not REF_RE.match(value):
        return value
    if value in _seen:
        return None
    _seen.add(value)
    target = paths.get(value[1:-1])
    return _resolve(target, paths, _seen) if target is not None else None


def check_front_matter(fm, out):
    if not fm.get("name"):
        out.append(_finding("CRITICAL", "schema", "`name` is required"))
    if not fm.get("version"):
        out.append(_finding("MAJOR", "version", "`version:` missing (echo the pinned upstream value)"))
    for k in fm:
        if k not in TOP_LEVEL_KEYS:
            out.append(_finding("MAJOR", "unknown-key", f"unknown top-level key `{k}` (ignored by consumers)"))
    _check_shapes(fm, out)

    paths = _flatten_paths(fm)
    # broken-ref: every {ref} value must resolve
    for path, val in paths.items():
        if isinstance(val, str) and REF_RE.match(val) and _resolve(val, paths) is None:
            out.append(_finding("CRITICAL", "broken-ref", f"`{path}` -> `{val}` does not resolve"))

    colors = fm.get("colors") or {}
    dark = fm.get("dark") or {}

    # missing-on-color: dangling on-* + required surfaces need an on-*
    for tok in colors:
        m = re.match(r"on-(.+)", tok)
        if m and m.group(1) not in colors:
            out.append(_finding("CRITICAL", "missing-on-color", f"`on-{m.group(1)}` has no base color `{m.group(1)}`"))
    for surface in REQUIRED_ON:
        if surface in colors and f"on-{surface}" not in colors:
            out.append(_finding("CRITICAL", "missing-on-color", f"surface `{surface}` has no `on-{surface}` foreground"))

    # contrast: each on-<X>/<X> pair in light and (effective) dark
    def _pair_contrast(mode, base_map):
        for tok in base_map:
            m = re.match(r"on-(.+)", tok)
            if not m or m.group(1) not in {**colors, **base_map}:
                continue
            base = m.group(1)
            fg = _resolve(base_map.get(tok, colors.get(tok)), paths)
            bg = _resolve(base_map.get(base, colors.get(base)), paths)
            if fg is None or bg is None:
                continue
            try:
                ratio = contrast_ratio(fg, bg)
            except ValueError as e:
                # Fail-closed: a surface pair we cannot verify does not pass the gate.
                out.append(_finding("CRITICAL", "uncheckable-color",
                                    f"[{mode}] on-{base}: {e} — use hex or rgb() so contrast is verifiable"))
                continue
            if ratio < 4.5:
                out.append(_finding("CRITICAL", "contrast",
                                    f"[{mode}] on-{base} vs {base} = {ratio:.2f}:1 (< 4.5:1)"))

    _pair_contrast("light", colors)
    if dark:
        effective_dark = {**colors, **dark}
        _pair_contrast("dark", effective_dark)

    # component backgroundColor vs textColor
    for name, obj in (fm.get("components") or {}).items():
        if not isinstance(obj, dict):
            continue
        bg = _resolve(obj.get("backgroundColor"), paths)
        fg = _resolve(obj.get("textColor"), paths)
        if bg and fg:
            try:
                ratio = contrast_ratio(fg, bg)
            except ValueError as e:
                out.append(_finding("CRITICAL", "uncheckable-color",
                                    f"component `{name}`: {e} — use hex or rgb() so contrast is verifiable"))
                continue
            if ratio < 4.5:
                out.append(_finding("CRITICAL", "contrast",
                                    f"component `{name}` text vs background = {ratio:.2f}:1 (< 4.5:1)"))


def check_sections(body, out):
    headings = [ln[3:].strip() for ln in body.splitlines() if ln.startswith("## ")]
    canon_index = {}
    for i, (name, aliases) in enumerate(CANONICAL_SECTIONS):
        canon_index[name.lower()] = i
        for a in aliases:
            canon_index[a] = i
    seen = set()
    last = -1
    for h in headings:
        idx = canon_index.get(h.lower())
        if idx is None:
            continue  # unknown headings are preserved without error
        if idx in seen:
            out.append(_finding("CRITICAL", "duplicate-heading", f"duplicate section `{h}`"))
        seen.add(idx)
        if idx < last:
            out.append(_finding("CRITICAL", "section-order", f"section `{h}` is out of canonical order"))
        last = max(last, idx)


def _colors_rationale(body, fm, out):
    """missing-intent: base colors should be explained in the Colors body (Major)."""
    lower = body.lower()
    for tok in (fm.get("colors") or {}):
        if tok.startswith("on-"):
            continue
        if tok.lower() not in lower:
            out.append(_finding("MAJOR", "missing-intent", f"color `{tok}` has no rationale in the body"))


def split_document(text):
    if not text.startswith("---"):
        raise LintError("missing YAML front-matter (file must start with '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise LintError("front-matter not closed with a second '---'")
    return parts[1], parts[2]


def lint_text(text):
    out = []
    try:
        fm_text, body = split_document(text)
        fm = parse_front_matter(fm_text)
    except LintError as e:
        return [_finding("CRITICAL", "parse", str(e))]
    check_front_matter(fm, out)
    check_sections(body, out)
    _colors_rationale(body, fm, out)
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    if len(args) != 1:
        print("usage: designmd_lint.py <DESIGN.md> [--json]", file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8") as f:
        findings = lint_text(f.read())
    criticals = [f for f in findings if f["severity"] == "CRITICAL"]
    if as_json:
        print(json.dumps({"findings": findings, "criticals": len(criticals)}, indent=2))
    else:
        for f in findings:
            print(f"{f['severity']:>8}  {f['rule']:<18}  {f['message']}")
        print(f"\n{len(criticals)} critical, {len(findings) - len(criticals)} other")
    return 1 if criticals else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

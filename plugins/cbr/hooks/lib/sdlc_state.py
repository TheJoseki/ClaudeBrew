#!/usr/bin/env python3
"""sdlc_state.py — reconstruct cbr SDLC state from committed docs/ artifacts.

Pure, zero-dependency helpers shared by the `session-init` and `subagent-context`
hooks. The canonical layout in `rules/sdlc-conventions.md` IS the addressing scheme:
every per-feature artifact lives under `docs/streams/<slug>-<YYYYMMDD>/<subdir>/`, the
**folder is the identity**, the sub-folder is the type, and the filename drops the slug.
These helpers glob the stream folders and read only cheap signals (folder names, verdict
`decision` fields, STREAM.md status, markdown headers) — never full spec bodies.

Design contract: functions tolerate a missing/empty `docs/` tree (return None / [] / {}),
but do NOT blanket-swallow errors — the calling hooks own fail-open (try/except -> exit 0).
Keeping the logic here (not in the hooks) makes it directly unit-testable and thin.
"""
import glob
import json
import os
import re

# --- Canonical locations (relative to project_dir) --------------------------
STREAMS_DIR = os.path.join("docs", "streams")

# Gate -> the stage skill that advances it (drives next_action).
GATE_SKILL = {
    "G1": "analyze-requirement",
    "G3": "design-function",
    "G4": "review-code",
    "G5a": "vulnerability-scanner",
    "G6": "unit-test",
    "G7": "integration-test",
}
GATE_ORDER = ["G1", "G3", "G4", "G5a", "G6", "G7"]

# Verdict gate -> the stream sub-folder its VERDICT-*.json lives in (beside its report).
VERDICT_SUBDIR = {"G4": "reviews", "G5a": "security", "G6": "test-reports", "G7": "test-reports"}

# Large specs get section-range pointers (H6-style); stream-relative locations.
_STREAM_SPECS = (
    ("SRS", os.path.join("requirements", "SRS.md")),
    ("BASIC", os.path.join("design", "BASIC.md")),
    ("TECH", os.path.join("design", "TECH.md")),
    ("SCREEN", os.path.join("requirements", "SCREEN.md")),
)
_LARGE_SPEC_TYPES = {"SRS", "BASIC", "TECH"}

_HEADER_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
_STREAM_DIR_RE = re.compile(r"^(.+)-\d{8}$")                       # <slug>-<YYYYMMDD>
_ARCHIVED_RE = re.compile(r"^status:\s*[\"']?(archived|abandoned)\b", re.MULTILINE)


def slug_from_stream_dir(name):
    """Extract the slug from a stream folder name `<slug>-<YYYYMMDD>`. None if undated."""
    base = os.path.basename(str(name).rstrip("/\\"))
    m = _STREAM_DIR_RE.match(base)
    return m.group(1) if m else None


def _read_head(path, n=60):
    """Read the first n lines of a file; '' on any read error."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return "".join(fh.readlines()[:n])
    except OSError:
        return ""


def _stream_dir(project_dir, slug):
    """Return the newest `docs/streams/<slug>-*/` directory for a slug, or None.

    A feature may have more than one stream over time; the most-recently-modified is
    the current one.
    """
    if not slug:
        return None
    # Exact-slug filter: glob `<slug>-*` also matches a different feature that shares the
    # prefix (e.g. `payment-*` matches `payment-export-...`), so re-check the parsed slug.
    hits = [p for p in glob.glob(os.path.join(project_dir, STREAMS_DIR, f"{slug}-*"))
            if os.path.isdir(p) and slug_from_stream_dir(p) == slug]
    if not hits:
        return None
    return max(hits, key=os.path.getmtime)


def _stream_archived(stream_dir):
    """True if the stream's STREAM.md frontmatter marks it archived/abandoned."""
    return bool(_ARCHIVED_RE.search(_read_head(os.path.join(stream_dir, "STREAM.md"))))


def _all_pass(gates):
    """True when every ordered gate is 'pass' (the stream's work is complete)."""
    return all(gates.get(g) == "pass" for g in GATE_ORDER)


def resolve_active_feature(project_dir):
    """Return (slug, ambiguity_list).

    A stream is 'in flight' when its gate line is not all-pass and its STREAM.md is not
    archived/abandoned. Exactly one in-flight stream -> (slug, []); several -> (None,
    [slugs]) so the caller emits a picker; none -> (None, []). Gate authority is the glob,
    not a hand-set flag — `status:` only *excludes* an archived/abandoned stream.
    """
    in_flight = []
    for stream in sorted(glob.glob(os.path.join(project_dir, STREAMS_DIR, "*"))):
        if not os.path.isdir(stream):
            continue
        slug = slug_from_stream_dir(stream)
        if not slug or _stream_archived(stream):
            continue
        if not _all_pass(infer_gate_progress(project_dir, slug)["gates"]):
            in_flight.append(slug)
    in_flight = list(dict.fromkeys(in_flight))  # de-dupe, preserve order
    if len(in_flight) == 1:
        return in_flight[0], []
    if len(in_flight) > 1:
        return None, in_flight
    return None, []


def _verdict_decision(path):
    """Return the lowercased `decision` from a verdict JSON, or None."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    d = data.get("decision") if isinstance(data, dict) else None
    return d.lower() if isinstance(d, str) else None


def _gate_verdict(project_dir, slug, gate):
    """Aggregate verdict status for a gate across its (possibly per-batch) files.

    fail/blocked on any -> 'fail'; all pass -> 'pass'; some pass -> 'partial';
    none found -> None. Verdicts live in the stream's `reviews/`, `security/`, or
    `test-reports/` sub-folder.
    """
    d = _stream_dir(project_dir, slug)
    if not d:
        return None
    subdir = VERDICT_SUBDIR[gate]
    hits = set(glob.glob(os.path.join(d, subdir, f"VERDICT-*{gate}.json")))
    hits.add(os.path.join(d, subdir, f"VERDICT-{gate}.json"))
    decisions = [x for x in (_verdict_decision(h) for h in hits) if x]
    if not decisions:
        return None
    if any(x in ("fail", "blocked") for x in decisions):
        return "fail"
    if all(x == "pass" for x in decisions):
        return "pass"
    return "partial"


def infer_gate_progress(project_dir, slug):
    """Return {'gates': {G: status}, 'next_action': str|None, 'gate_line': str}.

    Gate status is inferred from artifact existence (G1 `requirements/SRS.md`, G3
    `design/TECH.md`) and verdict decisions (G4/G5a/G6/G7), all within the stream folder.
    next_action is the first non-'pass' gate's skill (fix-bug when that gate is 'fail').
    """
    d = _stream_dir(project_dir, slug)
    gates = {
        "G1": "pass" if (d and os.path.isfile(os.path.join(d, "requirements", "SRS.md"))) else "pending",
        "G3": "pass" if (d and os.path.isfile(os.path.join(d, "design", "TECH.md"))) else "pending",
    }
    for gate in ("G4", "G5a", "G6", "G7"):
        gates[gate] = _gate_verdict(project_dir, slug, gate) or "pending"

    next_action = None
    for g in GATE_ORDER:
        if gates[g] != "pass":
            skill = "fix-bug" if gates[g] == "fail" else GATE_SKILL[g]
            next_action = f"/cbr:{skill} {slug}"
            break

    icon = {"pass": "PASS", "fail": "FAIL", "partial": "PARTIAL", "pending": "pending"}
    gate_line = "Feature {}: {}".format(
        slug, " | ".join(f"{g} {icon[gates[g]]}" for g in GATE_ORDER)
    )
    return {"gates": gates, "next_action": next_action, "gate_line": gate_line}


def extract_sections(path):
    """Parse `##`/`###` headers into [{'title', 'lines': 'start-end'}].

    Line ranges are 1-indexed and inclusive; a section runs to the line before the
    next header (or EOF). Empty list if the file has no such headers / is unreadable.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    heads = []
    for i, line in enumerate(lines, start=1):
        m = _HEADER_RE.match(line.rstrip("\n"))
        if m:
            heads.append((i, m.group(2).strip()))
    sections = []
    for idx, (lineno, title) in enumerate(heads):
        end = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
        sections.append({"title": title, "lines": f"{lineno}-{end}"})
    return sections


def find_latest_handoff(project_dir, slug):
    """Return the newest `<stream>/handoffs/HANDOFF-*.md` as a /-path, or None."""
    d = _stream_dir(project_dir, slug)
    if not d:
        return None
    hits = glob.glob(os.path.join(d, "handoffs", "HANDOFF-*.md"))
    if not hits:
        return None
    newest = max(hits, key=os.path.getmtime)
    return os.path.relpath(newest, project_dir).replace("\\", "/")


def find_stream_manifest(project_dir, slug):
    """Return the newest `docs/streams/<slug>-*/STREAM.md` as a /-path, or None."""
    if not slug:
        return None
    hits = [p for p in glob.glob(os.path.join(project_dir, STREAMS_DIR, f"{slug}-*", "STREAM.md"))
            if slug_from_stream_dir(os.path.dirname(p)) == slug]  # exclude prefix-collisions
    if not hits:
        return None
    newest = max(hits, key=os.path.getmtime)
    return os.path.relpath(newest, project_dir).replace("\\", "/")


def _feature_artifacts(project_dir, slug):
    """Collect the stream's artifacts with paths; section-range the large specs."""
    d = _stream_dir(project_dir, slug)
    if not d:
        return []
    arts = []
    for type_, rel in _STREAM_SPECS:
        full = os.path.join(d, rel)
        if os.path.isfile(full):
            rec = {"type": type_, "path": os.path.relpath(full, project_dir).replace("\\", "/")}
            if type_ in _LARGE_SPEC_TYPES:
                rec["sections"] = extract_sections(full)
            arts.append(rec)
    for gate in ("G4", "G5a", "G6", "G7"):
        subdir = VERDICT_SUBDIR[gate]
        for h in sorted(glob.glob(os.path.join(d, subdir, f"VERDICT-*{gate}.json"))):
            arts.append({
                "type": f"VERDICT-{gate}",
                "path": os.path.relpath(h, project_dir).replace("\\", "/"),
                "decision": _verdict_decision(h),
            })
    return arts


def build_index(project_dir, active_slug, now=None):
    """Build the .claude/sdlc-index.json cache payload.

    Convenience cache (NOT authority) — a caller reads it to avoid re-globbing;
    glob-on-canonical-path stays the fail-loud source of truth. `now` is stamped by
    the caller (hook passes an ISO timestamp; tests pass a fixed value or None).
    """
    idx = {"generatedAt": now, "activeFeature": active_slug, "features": {}}
    if active_slug:
        prog = infer_gate_progress(project_dir, active_slug)
        idx["features"][active_slug] = {
            "gates": prog["gates"],
            "nextAction": prog["next_action"],
            "artifacts": _feature_artifacts(project_dir, active_slug),
        }
    return idx

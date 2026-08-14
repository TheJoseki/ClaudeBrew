#!/usr/bin/env python3
"""sdlc_state.py — reconstruct cbr SDLC state from committed docs/ artifacts.

Pure, zero-dependency helpers shared by the `session-init` and `subagent-context`
hooks. The canonical layout in `{{CBR_ROOT}}/docs/references/sdlc-reference.md` IS the addressing
scheme: every per-feature artifact lives under `docs/streams/<slug>-<YYYYMMDD>/<subdir>/`, the
**folder is the identity**, the sub-folder is the type, and the filename drops the slug.
These helpers glob the stream folders and read only cheap signals (folder names, verdict
`decision` fields, STREAM.md `status:`, markdown headers) — never full spec bodies. Stream
completion is the sole exception to "inferred": it is authored (`status: done`), never
computed from checkpoint/verdict state — see `_stream_closed`.

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

# Checkpoint -> the stage skill that advances it (drives next_action). REQUIREMENT/DESIGN are
# artifact-existence checkpoints (no verdict); REVIEW/SECURITY/UNIT/INTEGRATION are verdict-backed.
# Values are BARE stage-name tokens, never "cbr-"-prefixed — next_action's f-string supplies the
# prefix. Mixing the two produces a nonexistent "/cbr-cbr-plan" invocation (R3 design doc D7).
GATE_SKILL = {
    "REQUIREMENT": "plan",
    "DESIGN": "plan",
    "REVIEW": "verify",
    "SECURITY": "verify",
    "UNIT": "verify",
    "INTEGRATION": "verify",
}
GATE_ORDER = ["REQUIREMENT", "DESIGN", "REVIEW", "SECURITY", "UNIT", "INTEGRATION"]

# Verdict checkpoint -> the stream sub-folder its VERDICT-*.json lives in (beside its report).
VERDICT_SUBDIR = {"REVIEW": "reviews", "SECURITY": "security", "UNIT": "test-reports", "INTEGRATION": "test-reports"}

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
# A stream is closed (excluded from "in flight") when the USER has authored one of these —
# completion is never inferred from gate/checkpoint state (R2 design doc §1). `done` = finished;
# `archived`/`abandoned` = finished-without-finishing. `blocked`/`pending`/`in-progress` stay in flight.
_CLOSED_RE = re.compile(r"^status:\s*[\"']?(done|archived|abandoned)\b", re.MULTILINE)


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


def _stream_closed(stream_dir):
    """True if the stream's STREAM.md frontmatter marks it done/archived/abandoned."""
    return bool(_CLOSED_RE.search(_read_head(os.path.join(stream_dir, "STREAM.md"))))


def resolve_active_feature(project_dir):
    """Return (slug, ambiguity_list).

    A stream is 'in flight' when its STREAM.md is not closed (done/archived/abandoned).
    Exactly one in-flight stream -> (slug, []); several -> (None, [slugs]) so the caller
    emits a picker; none -> (None, []). Completion is authored, never inferred from gate
    state — a stream-light stream that never writes an SRS/TECH could otherwise never
    close (R2 design doc §1: this was a real, reproducible bug under the old all-pass
    predicate). `status:` is the sole completion signal; gate/checkpoint state below drives
    only the progress display (gate_line, next_action), not in-flight membership.
    """
    in_flight = []
    for stream in sorted(glob.glob(os.path.join(project_dir, STREAMS_DIR, "*"))):
        if not os.path.isdir(stream):
            continue
        slug = slug_from_stream_dir(stream)
        if not slug or _stream_closed(stream):
            continue
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


def _verdict_files(project_dir, slug, gate):
    """Glob every verdict file for `gate` in its stream sub-folder — the exact
    `VERDICT-<gate>.json` plus any per-batch `VERDICT-*<gate>.json`.
    """
    d = _stream_dir(project_dir, slug)
    if not d:
        return []
    subdir = VERDICT_SUBDIR[gate]
    hits = set(glob.glob(os.path.join(d, subdir, f"VERDICT-*{gate}.json")))
    hits.add(os.path.join(d, subdir, f"VERDICT-{gate}.json"))
    return sorted(p for p in hits if os.path.isfile(p))


def _gate_verdict(project_dir, slug, gate):
    """Aggregate verdict status for a gate across its (possibly per-batch) files.
    fail/blocked on any -> 'fail'; all pass -> 'pass'; some pass -> 'partial';
    none found -> None.
    """
    hits = _verdict_files(project_dir, slug, gate)
    decisions = [x for x in (_verdict_decision(h) for h in hits) if x]
    if not decisions:
        return None
    if any(x in ("fail", "blocked") for x in decisions):
        return "fail"
    if all(x == "pass" for x in decisions):
        return "pass"
    return "partial"


def _security_stale(project_dir, slug):
    """True if the newest SECURITY verdict predates the newest DEV-log or bug-report entry
    in the stream — the code-enforced replacement for the deleted "re-scan after every
    fix" mandate (R2 design doc §6). Both work-logs/ and bug-reports/ are checked: a
    post-scan fix made via `fix-bug` alone never touches the DEV log.
    """
    hits = _verdict_files(project_dir, slug, "SECURITY")
    if not hits:
        return False
    d = _stream_dir(project_dir, slug)
    touches = (glob.glob(os.path.join(d, "work-logs", "DEV-*.md")) +
               glob.glob(os.path.join(d, "bug-reports", "BUG-*.md")))
    if not touches:
        return False
    return max(os.path.getmtime(p) for p in touches) > max(os.path.getmtime(p) for p in hits)


def infer_gate_progress(project_dir, slug):
    """Return {'gates': {G: status}, 'next_action': str|None, 'gate_line': str}.

    Checkpoint status is inferred from artifact existence (REQUIREMENT `requirements/SRS.md`,
    DESIGN `design/TECH.md`) and verdict decisions (REVIEW/SECURITY/UNIT/INTEGRATION), all
    within the stream folder — this drives the progress DISPLAY only; stream completion
    (resolve_active_feature) no longer reads any of it (R2 design doc §1). next_action is
    the first non-'pass' checkpoint's skill (`cbr-implement --phase fix` when that checkpoint
    is 'fail'); a 'stale' SECURITY verdict routes back to `cbr-verify --phase security` via
    the same fallthrough.
    """
    d = _stream_dir(project_dir, slug)
    gates = {
        "REQUIREMENT": "pass" if (d and os.path.isfile(os.path.join(d, "requirements", "SRS.md"))) else "pending",
        "DESIGN": "pass" if (d and os.path.isfile(os.path.join(d, "design", "TECH.md"))) else "pending",
    }
    for gate in ("REVIEW", "SECURITY", "UNIT", "INTEGRATION"):
        hits = _verdict_files(project_dir, slug, gate)
        decisions = [x for x in (_verdict_decision(h) for h in hits) if x]
        if not decisions:
            gates[gate] = "pending"
        elif any(x in ("fail", "blocked") for x in decisions):
            gates[gate] = "fail"
        elif all(x == "pass" for x in decisions):
            gates[gate] = "pass"
        else:
            gates[gate] = "partial"
    if gates["SECURITY"] == "pass" and _security_stale(project_dir, slug):
        gates["SECURITY"] = "stale"

    next_action = None
    for g in GATE_ORDER:
        if gates[g] != "pass":
            if gates[g] == "fail":
                skill, hint = "implement", "fix"
            else:
                skill, hint = GATE_SKILL[g], g.lower()
            next_action = f"/cbr-{skill} {slug} --phase {hint}"
            break

    icon = {"pass": "PASS", "fail": "FAIL", "partial": "PARTIAL", "pending": "pending", "stale": "STALE"}
    gate_line = "Feature {}: {}".format(
        slug,
        " | ".join(f"{g} {icon[gates[g]]}" for g in GATE_ORDER),
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
    for gate in ("REVIEW", "SECURITY", "UNIT", "INTEGRATION"):
        for h in _verdict_files(project_dir, slug, gate):
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

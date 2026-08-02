#!/usr/bin/env python3
"""sdlc_state.py — reconstruct cbr SDLC state from committed docs/ artifacts.

Pure, zero-dependency helpers shared by the `session-init` and `subagent-context`
hooks. The canonical artifact-path table in `rules/sdlc-conventions.md` IS the
addressing scheme; these helpers glob those paths and read only cheap signals
(filenames, PLAN frontmatter, verdict `decision` fields, markdown headers) —
never full spec bodies.

Design contract: functions tolerate a missing/empty `docs/` tree (return
None / [] / {}), but do NOT blanket-swallow errors — the calling hooks own
fail-open (try/except -> exit 0). Keeping the logic here (not in the hooks) makes
it directly unit-testable and keeps both hooks thin.
"""
import glob
import json
import os
import re

# --- Canonical artifact locations (relative to project_dir) -----------------
# Mirror rules/sdlc-conventions.md. If that table changes, change these.
SPEC_REQUIREMENTS = os.path.join("docs", "specs", "requirements")
SPEC_BASIC = os.path.join("docs", "specs", "basic-design")
SPEC_DETAIL = os.path.join("docs", "specs", "detail-design")
PLANS_DIR = os.path.join("docs", "plans")
WORKLOGS_DIR = os.path.join("docs", "work-logs")
REVIEWS_DIR = os.path.join("docs", "reviews")
SECURITY_DIR = os.path.join("docs", "security")
TESTREPORTS_DIR = os.path.join("docs", "test-reports")
HANDOFFS_DIR = os.path.join("docs", "handoffs")

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

# Verdict gate -> the docs/ subdir its VERDICT-*.json lives in.
VERDICT_DIR = {
    "G4": REVIEWS_DIR,
    "G5a": SECURITY_DIR,
    "G6": TESTREPORTS_DIR,
    "G7": TESTREPORTS_DIR,
}

# Large specs get section-range pointers (H6-style) for the active feature.
LARGE_SPECS = (
    ("SRS", SPEC_REQUIREMENTS),
    ("BASIC", SPEC_BASIC),
    ("TECH", SPEC_DETAIL),
)
_ALL_SPECS = LARGE_SPECS + (("SCREEN", SPEC_REQUIREMENTS),)

_DATE_RE = re.compile(r"-\d{8}$")          # -YYYYMMDD
_GATE_RE = re.compile(r"-G\d[a-z]?$")      # -G4, -G5a
_BATCH_RE = re.compile(r"-B\d+$")          # -B2
_ROUND_RE = re.compile(r"-R\d+$")          # -R3
_HEADER_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
_STATUS_ACTIVE_RE = re.compile(r"^status:\s*ACTIVE", re.MULTILINE)


def slug_from_filename(name):
    """Extract the feature slug from a canonical artifact filename.

    Slugs may contain hyphens; only the uppercase TYPE- prefix and the known
    trailing tokens (gate, batch, round, date) are stripped. Returns None when the
    name has no TYPE- prefix (not a recognized artifact).
    """
    stem = os.path.basename(name)
    for ext in (".md", ".json"):
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break
    parts = stem.split("-", 1)
    if len(parts) != 2 or not parts[0].isupper() or not parts[0].isalpha():
        return None
    stem = parts[1]
    # Strip trailing tokens in the order they nest: gate, then batch/round, then date.
    stem = _GATE_RE.sub("", stem)
    stem = _BATCH_RE.sub("", stem)
    stem = _ROUND_RE.sub("", stem)
    stem = _DATE_RE.sub("", stem)
    return stem or None


def _read_head(path, n=60):
    """Read the first n lines of a file; '' on any read error."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return "".join(fh.readlines()[:n])
    except OSError:
        return ""


def resolve_active_feature(project_dir):
    """Return (slug, ambiguity_list).

    Rule (see plan phase-02):
      1. Exactly one docs/plans/PLAN-*.md with `status: ACTIVE` -> (its slug, []).
      2. Several ACTIVE plans -> (None, [slugs]) so the caller emits a picker.
      3. No ACTIVE plan -> most-recently-modified artifact under specs/work-logs/
         reviews -> (its slug, []).
      4. Nothing at all -> (None, []).
    """
    active = []
    for p in sorted(glob.glob(os.path.join(project_dir, PLANS_DIR, "PLAN-*.md"))):
        if _STATUS_ACTIVE_RE.search(_read_head(p)):
            s = slug_from_filename(p)
            if s:
                active.append(s)
    active = list(dict.fromkeys(active))  # de-dupe, preserve order
    if len(active) == 1:
        return active[0], []
    if len(active) > 1:
        return None, active

    candidates = []
    for d in (SPEC_REQUIREMENTS, SPEC_BASIC, SPEC_DETAIL, WORKLOGS_DIR, REVIEWS_DIR):
        candidates.extend(glob.glob(os.path.join(project_dir, d, "*.md")))
    if not candidates:
        return None, []
    newest = max(candidates, key=os.path.getmtime)
    return slug_from_filename(newest), []


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
    none found -> None.
    """
    subdir = VERDICT_DIR[gate]
    hits = set(glob.glob(os.path.join(project_dir, subdir, f"VERDICT-{slug}-*{gate}.json")))
    hits.add(os.path.join(project_dir, subdir, f"VERDICT-{slug}-{gate}.json"))
    decisions = [d for d in (_verdict_decision(h) for h in hits) if d]
    if not decisions:
        return None
    if any(d in ("fail", "blocked") for d in decisions):
        return "fail"
    if all(d == "pass" for d in decisions):
        return "pass"
    return "partial"


def _exists(project_dir, *relparts):
    return os.path.isfile(os.path.join(project_dir, *relparts))


def infer_gate_progress(project_dir, slug):
    """Return {'gates': {G: status}, 'next_action': str|None, 'gate_line': str}.

    Gate status is inferred from artifact existence (G1 SRS, G3 TECH) and verdict
    decisions (G4/G5a/G6/G7). next_action is the first non-'pass' gate's skill
    (fix-bug when that gate is 'fail').
    """
    gates = {
        "G1": "pass" if _exists(project_dir, SPEC_REQUIREMENTS, f"SRS-{slug}.md") else "pending",
        "G3": "pass" if _exists(project_dir, SPEC_DETAIL, f"TECH-{slug}.md") else "pending",
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
    """Return the newest docs/handoffs/HANDOFF-[slug]-*.md as a /-path, or None."""
    hits = glob.glob(os.path.join(project_dir, HANDOFFS_DIR, f"HANDOFF-{slug}-*.md"))
    if not hits:
        return None
    newest = max(hits, key=os.path.getmtime)
    return os.path.relpath(newest, project_dir).replace("\\", "/")


def _feature_artifacts(project_dir, slug):
    """Collect the feature's artifacts with paths; section-range the large specs."""
    arts = []
    for type_, subdir in _ALL_SPECS:
        rel = os.path.join(subdir, f"{type_}-{slug}.md")
        full = os.path.join(project_dir, rel)
        if os.path.isfile(full):
            rec = {"type": type_, "path": rel.replace("\\", "/")}
            if type_ in dict(LARGE_SPECS):
                rec["sections"] = extract_sections(full)
            arts.append(rec)
    for gate in ("G4", "G5a", "G6", "G7"):
        for h in sorted(glob.glob(
            os.path.join(project_dir, VERDICT_DIR[gate], f"VERDICT-{slug}*{gate}.json")
        )):
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

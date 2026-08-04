#!/usr/bin/env python3
"""SubagentStart hook (no matcher — fires for every spawn) — inject subagent context.

Gives every spawned subagent the active feature + where to read inputs / write outputs.
Reads the .claude/sdlc-index.json cache built at SessionStart (O(1), no docs/ glob);
falls back to the glob authority if the cache is missing/stale. Gate agents
(reviewer/tester/developer) also get the gate's verdict path + schema and section
pointers into large specs; unrelated agents get only the active-feature line
(relevance, not token-thrift).

Contract: SubagentStart injects via
  {"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "..."}}
Fail-open: any error -> emit empty context, exit 0.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import sdlc_state  # noqa: E402

# Agent types that act on SDLC artifacts and get the full gate section.
GATE_AGENTS = {
    "reviewer", "tester", "developer",
    "cbr:reviewer", "cbr:tester", "cbr:developer",
}


def load_cache(project_dir):
    """Read .claude/sdlc-index.json; None if absent/unreadable."""
    path = os.path.join(project_dir, ".claude", "sdlc-index.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def feature_state(project_dir):
    """(slug, feature_record) from the cache, else rebuilt via the glob authority."""
    cache = load_cache(project_dir)
    if cache and cache.get("activeFeature"):
        slug = cache["activeFeature"]
        return slug, (cache.get("features") or {}).get(slug)
    slug, _ = sdlc_state.resolve_active_feature(project_dir)
    if not slug:
        return None, None
    return slug, sdlc_state.build_index(project_dir, slug)["features"].get(slug)


def render(agent_type, slug, feature):
    """Compose the additionalContext string (relevance-based)."""
    lines = [f"cbr active feature: {slug or 'none'}",
             "Artifacts under docs/streams/<slug>-<YYYYMMDD>/ "
             "(requirements/ design/ plan/ reviews/ security/ test-reports/ retro/ …)"]
    if agent_type in GATE_AGENTS and feature:
        if feature.get("nextAction"):
            lines.append(f"Next gate action: {feature['nextAction']}")
        lines.append(
            f"Gate verdict -> docs/streams/{slug}-<YYYYMMDD>/{{reviews,security,test-reports}}/VERDICT-G<n>.json "
            "per {{CBR_ROOT}}/schemas/verdict-artifact.schema.json; validate before writing."
        )
        for art in feature.get("artifacts", []):
            secs = art.get("sections") or []
            if secs:
                ptrs = "; ".join(f"{s['title']} (lines {s['lines']})" for s in secs[:6])
                lines.append(f"{art['type']} {art['path']} sections: {ptrs}")
    return "\n".join(lines)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    agent_type = data.get("agent_type", "unknown")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    try:
        slug, feature = feature_state(project_dir)
        text = render(agent_type, slug, feature)
    except Exception as exc:  # fail-open
        sys.stderr.write(f"[subagent-context] {exc}\n")
        text = ""
    out = {"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": text}}
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()

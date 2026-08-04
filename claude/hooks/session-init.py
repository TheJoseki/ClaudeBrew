#!/usr/bin/env python3
"""SessionStart hook (startup|resume|clear|compact) — inject cbr SDLC state + cache.

At session start this reconstructs a cheap, gate-aware SDLC summary from committed
docs/ artifacts (the automatic version of what /cbr:handoff does by hand) and injects
it as plain stdout text. It also writes .claude/sdlc-index.json — a per-session CACHE
(not an authority) that subagent-context.py reads to avoid re-globbing docs/.

On `source == "compact"` it additionally reinjects the richer post-compaction context —
the PreCompact checkpoint (`.claude/compact-checkpoint.md`), PROJECT.md key sections, and
an approval-gate reminder — because SessionStart is the injection-capable compaction event
(PostCompact stdout is log-only and never reaches the model). This replaces the removed
`re-inject-context.sh` + `post-compact-reinject.sh` scripts.

Contract: SessionStart injects via PLAIN STDOUT text. Fail-open: any error -> exit 0.
"""
import json
import os
import sys
from datetime import datetime, timezone

# Make the sibling lib importable (hyphen-free module name).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import sdlc_state  # noqa: E402

# PROJECT.md sections worth reinjecting after a compaction (from the old re-inject script).
_PROJECT_SECTIONS = ("## Tech Stack", "## Build Commands", "## Domain Model")


def render(slug, ambiguity, progress, handoff, stream=None):
    """Compose the plain-stdout injection text. '' when there is nothing to say."""
    if ambiguity:
        return (
            f"cbr SDLC: {len(ambiguity)} features in flight: "
            f"{', '.join(ambiguity)} — pass a slug to stage skills."
        )
    if not slug:
        return ""
    lines = [f"cbr SDLC state — {progress['gate_line']}"]
    if progress["next_action"]:
        lines.append(f"Next: {progress['next_action']}")
    if stream:
        lines.append(f"Stream board: {stream}")
    if handoff:
        lines.append(f"Full state: {handoff}")
    return "\n".join(lines)


def read_checkpoint(project_dir):
    """Return the PreCompact checkpoint text (.claude/compact-checkpoint.md), or ''."""
    path = os.path.join(project_dir, ".claude", "compact-checkpoint.md")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def read_project_sections(project_dir):
    """Return PROJECT.md's Tech Stack / Build Commands / Domain Model sections, or ''."""
    try:
        with open(os.path.join(project_dir, "PROJECT.md"), "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return ""
    out, capture = [], False
    for raw in lines:
        line = raw.rstrip("\n")
        if line.startswith("## "):
            capture = line in _PROJECT_SECTIONS
        if capture:
            out.append(line)
    return "\n".join(out).strip()


def render_compact(project_dir, slug, ambiguity, progress, handoff, stream=None):
    """Rich post-compaction reinjection (SessionStart:compact is injection-capable)."""
    parts = []
    summary = render(slug, ambiguity, progress, handoff, stream)
    if summary:
        parts.append(summary)
    checkpoint = read_checkpoint(project_dir)
    if checkpoint:
        parts.append("--- Pre-compact checkpoint (what you were doing) ---\n" + checkpoint)
    project = read_project_sections(project_dir)
    if project:
        parts.append("--- PROJECT.md ---\n" + project)
    parts.append(
        "Context was compacted. If you were awaiting an AskUserQuestion approval (e.g. a gate), "
        "re-confirm with the user before proceeding — do NOT assume approval was given. "
        "Re-read the active plan / work-log and do not redo completed work."
    )
    return "\n\n".join(parts)


def write_cache(project_dir, index):
    """Atomically write the .claude/sdlc-index.json cache. Best-effort (glob is authority)."""
    cache_dir = os.path.join(project_dir, ".claude")
    try:
        os.makedirs(cache_dir, exist_ok=True)
        path = os.path.join(cache_dir, "sdlc-index.json")
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(index, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return path
    except OSError:
        return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    source = data.get("source", "")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    try:
        slug, ambiguity = sdlc_state.resolve_active_feature(project_dir)
        progress = sdlc_state.infer_gate_progress(project_dir, slug) if slug else None
        handoff = sdlc_state.find_latest_handoff(project_dir, slug) if slug else None
        stream = sdlc_state.find_stream_manifest(project_dir, slug) if slug else None
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_cache(project_dir, sdlc_state.build_index(project_dir, slug, now=now))
        if source == "compact":
            text = render_compact(project_dir, slug, ambiguity, progress, handoff, stream)
        else:
            text = render(slug, ambiguity, progress, handoff, stream)
        if text:
            print(text)
    except Exception as exc:  # fail-open: never break a session
        sys.stderr.write(f"[session-init] {exc}\n")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()

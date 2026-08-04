#!/usr/bin/env python3
"""PreCompact hook — checkpoints working context before compaction.

Ported from bash: drops the `jq` dependency and reads the PreCompact payload from
stdin JSON. Writes a small markdown checkpoint that the post-compact reinject hook
reads to restore state. PreCompact cannot block compaction — this is
observability/checkpoint only. Always exits 0.
"""
import sys
import os
import re
import json
import glob
import datetime


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or "."
    checkpoint = os.path.join(project_dir, ".claude", "compact-checkpoint.md")

    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    trigger = data.get("trigger") or "unknown"
    transcript = data.get("transcript_path") or ""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    tool_count = 0
    recent_files = []
    recent_tasks = []
    if transcript and os.path.isfile(transcript):
        try:
            with open(transcript, "r", encoding="utf-8", errors="ignore") as fh:
                text = "".join(fh.readlines()[-300:])
            tool_count = text.count('"tool_use"')
            recent_files = sorted(set(re.findall(r'"file_path"\s*:\s*"([^"]*)"', text)))[-20:]
            recent_tasks = re.findall(r'"description"\s*:\s*"([^"]*)"', text)[-5:]
        except Exception:
            pass

    # Active plan: the newest docs/streams/<slug>-<date>/plan/PLAN.md (report its stream folder).
    active_plan_name = ""
    current_phase = "N/A"
    plans = glob.glob(os.path.join(project_dir, "docs", "streams", "*", "plan", "PLAN.md"))
    if plans:
        newest_plan = max(plans, key=os.path.getmtime)
        active_plan_name = os.path.basename(os.path.dirname(os.path.dirname(newest_plan)))
        try:
            content = open(newest_plan, encoding="utf-8", errors="ignore").read()
            for line in content.splitlines():
                if "⏳" in line:  # ⏳ current-phase marker
                    current_phase = line.strip()
                    break
        except Exception:
            pass

    # Most recent work-log across streams.
    log_name = ""
    log_status = "N/A"
    logs = glob.glob(os.path.join(project_dir, "docs", "streams", "*", "work-logs", "*.md"))
    if logs:
        newest = max(logs, key=os.path.getmtime)
        log_name = os.path.basename(newest)
        try:
            for line in open(newest, encoding="utf-8", errors="ignore"):
                if line.startswith("STATUS:"):
                    log_status = line.strip()
        except Exception:
            pass

    files_block = "\n".join(f"- {f}" for f in recent_files) or "- (none detected)"
    tasks_block = "\n".join(f"- {t}" for t in recent_tasks) or "- (none detected)"

    os.makedirs(os.path.dirname(checkpoint), exist_ok=True)
    with open(checkpoint, "w", encoding="utf-8") as fh:
        fh.write(
            f"---\n"
            f"trigger: {trigger}\n"
            f"timestamp: {timestamp}\n"
            f"tool_calls_in_window: {tool_count}\n"
            f"---\n"
            f"## Pre-Compact Checkpoint\n\n"
            f"Context saved before compaction. Read by post-compact reinject to restore state.\n\n"
            f"### Active Plan\n"
            f"- Plan file: {active_plan_name or 'none'}\n"
            f"- Current phase: {current_phase}\n\n"
            f"### Recent Work Log\n"
            f"- Log file: {log_name or 'none'}\n"
            f"- Status: {log_status}\n\n"
            f"### Recently Touched Files\n{files_block}\n\n"
            f"### Recent Agent Tasks\n{tasks_block}\n\n"
            f"### Work Volume\n"
            f"- Tool calls in recent context window: {tool_count}\n"
        )

    print(f"[compact-context-saver] Checkpoint saved: {checkpoint}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()

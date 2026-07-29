#!/usr/bin/env bash
# compact-context-saver.sh — PreCompact hook
# Saves critical working context before compaction destroys conversation history.
# This checkpoint is read by post-compact-reinject.sh (PostCompact) to restore context.
#
# Event: PreCompact (matcher: auto|manual)
# Cannot block compaction — observability + checkpoint only.
# Exit codes: always 0 (PreCompact ignores exit code)

set -eo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CHECKPOINT="$PROJECT_DIR/.claude/compact-checkpoint.md"

# Read stdin JSON
INPUT=$(cat)
TRIGGER=$(echo "$INPUT" | jq -r '.trigger // "unknown"' 2>/dev/null || echo "unknown")
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)

echo "[compact-context-saver] Trigger: $TRIGGER — saving checkpoint..." >&2

# ─── Collect context from transcript ──────────────────────────────────────────
TOOL_COUNT=0
RECENT_FILES=""
RECENT_TASKS=""

if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  # Count tool calls in recent window (proxy for work volume)
  TOOL_COUNT=$(tail -300 "$TRANSCRIPT" | grep -c '"tool_use"' 2>/dev/null || echo "0")

  # Extract recently touched files (from Edit/Write/Read tool calls)
  RECENT_FILES=$(tail -300 "$TRANSCRIPT" \
    | grep -oE '"file_path"\s*:\s*"[^"]*"' 2>/dev/null \
    | sed 's/"file_path"\s*:\s*"//;s/"$//' \
    | sort -u \
    | tail -20 \
    || true)

  # Extract recent task/description context from Agent tool calls
  RECENT_TASKS=$(tail -300 "$TRANSCRIPT" \
    | grep -oE '"description"\s*:\s*"[^"]*"' 2>/dev/null \
    | sed 's/"description"\s*:\s*"//;s/"$//' \
    | tail -5 \
    || true)
fi

# ─── Find active PLAN file ───────────────────────────────────────────────────
ACTIVE_PLAN=""
ACTIVE_PLAN_NAME=""
CURRENT_PHASE=""
if [ -d "$PROJECT_DIR/docs/plans" ]; then
  ACTIVE_PLAN=$(grep -rl "status: ACTIVE" "$PROJECT_DIR/docs/plans/PLAN-"*.md 2>/dev/null | head -1 || true)
  if [ -n "$ACTIVE_PLAN" ]; then
    ACTIVE_PLAN_NAME=$(basename "$ACTIVE_PLAN")
    CURRENT_PHASE=$(grep -n "⏳" "$ACTIVE_PLAN" 2>/dev/null | head -1 || echo "N/A")
  fi
fi

# ─── Find most recent work-log ───────────────────────────────────────────────
RECENT_LOG=""
RECENT_LOG_NAME=""
RECENT_LOG_STATUS=""
if [ -d "$PROJECT_DIR/docs/work-logs" ]; then
  RECENT_LOG=$(ls -t "$PROJECT_DIR/docs/work-logs/"*.md 2>/dev/null | head -1 || true)
  if [ -n "$RECENT_LOG" ]; then
    RECENT_LOG_NAME=$(basename "$RECENT_LOG")
    RECENT_LOG_STATUS=$(grep -E "^STATUS:" "$RECENT_LOG" 2>/dev/null | tail -1 || echo "N/A")
  fi
fi

# ─── Write checkpoint ────────────────────────────────────────────────────────
mkdir -p "$(dirname "$CHECKPOINT")"
cat > "$CHECKPOINT" <<EOF
---
trigger: $TRIGGER
timestamp: $TIMESTAMP
tool_calls_in_window: $TOOL_COUNT
---
## Pre-Compact Checkpoint

Context saved before compaction. Read by post-compact-reinject.sh to restore working state.

### Active Plan
- Plan file: ${ACTIVE_PLAN_NAME:-none}
- Current phase: ${CURRENT_PHASE:-N/A}

### Recent Work Log
- Log file: ${RECENT_LOG_NAME:-none}
- Status: ${RECENT_LOG_STATUS:-N/A}

### Recently Touched Files
$(if [ -n "$RECENT_FILES" ]; then echo "$RECENT_FILES" | while read -r f; do echo "- $f"; done; else echo "- (none detected)"; fi)

### Recent Agent Tasks
$(if [ -n "$RECENT_TASKS" ]; then echo "$RECENT_TASKS" | while read -r t; do echo "- $t"; done; else echo "- (none detected)"; fi)

### Work Volume
- Tool calls in recent context window: $TOOL_COUNT
EOF

echo "[compact-context-saver] Checkpoint saved: $CHECKPOINT" >&2
exit 0

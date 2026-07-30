#!/usr/bin/env bash
# post-compact-reinject.sh — PostCompact hook
# Reinjects working context after compaction: checkpoint + active PLAN + work-log.
# Replaces re-inject-context.sh (SessionStart:compact) with richer context.
#
# Event: PostCompact (matcher: auto|manual)
# Cannot block — stdout text is added to Claude's context.
# Exit codes: always 0 (PostCompact ignores exit code)

set -eo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CHECKPOINT="$PROJECT_DIR/.claude/compact-checkpoint.md"

# ─── 1. Inject pre-compact checkpoint ────────────────────────────────────────
if [ -f "$CHECKPOINT" ]; then
  echo "=== PRE-COMPACT CHECKPOINT (saved before compaction) ==="
  cat "$CHECKPOINT"
  echo ""
  echo "=== END CHECKPOINT ==="
  echo ""
fi

# ─── 2. Inject PROJECT.md key sections (same as old re-inject-context.sh) ────
if [ -f "$PROJECT_DIR/PROJECT.md" ]; then
  echo "=== PROJECT CONTEXT ==="
  grep -A 20 "^## Tech Stack\|^## Build Commands\|^## Domain Model" \
    "$PROJECT_DIR/PROJECT.md" 2>/dev/null | head -60 || true
  echo "=== END PROJECT CONTEXT ==="
  echo ""
fi

# ─── 3. Inject active PLAN status ────────────────────────────────────────────
if [ -d "$PROJECT_DIR/docs/plans" ]; then
  ACTIVE_PLAN=$(grep -rl "status: ACTIVE" "$PROJECT_DIR/docs/plans/PLAN-"*.md 2>/dev/null | head -1 || true)
  if [ -n "$ACTIVE_PLAN" ]; then
    echo "=== ACTIVE PLAN: $(basename "$ACTIVE_PLAN") ==="
    # Extract frontmatter + phase status lines
    head -30 "$ACTIVE_PLAN" 2>/dev/null || true
    echo "..."
    # Show all phase status markers
    grep -nE "(✅|⏳|❌|⚠️).*(Phase|Step|Gate)" "$ACTIVE_PLAN" 2>/dev/null | head -15 || true
    echo "=== END PLAN ==="
    echo ""
  fi
fi

# ─── 4. Inject most recent work-log tail ─────────────────────────────────────
if [ -d "$PROJECT_DIR/docs/work-logs" ]; then
  RECENT_LOG=$(ls -t "$PROJECT_DIR/docs/work-logs/"*.md 2>/dev/null | head -1 || true)
  if [ -n "$RECENT_LOG" ]; then
    echo "=== RECENT WORK LOG: $(basename "$RECENT_LOG") ==="
    # Show last 20 lines (most recent activity)
    tail -20 "$RECENT_LOG" 2>/dev/null || true
    echo "=== END WORK LOG ==="
    echo ""
  fi
fi

# ─── 5. Inject recent decisions (last 5 from DECISION-LEDGER) ────────────────
LEDGER="$PROJECT_DIR/docs/plans/DECISION-LEDGER.md"
if [ -f "$LEDGER" ]; then
  # Count total decisions
  DECISION_COUNT=$(grep -c "^### D-" "$LEDGER" 2>/dev/null || echo "0")
  if [ "$DECISION_COUNT" -gt 0 ]; then
    echo "=== RECENT DECISIONS ($DECISION_COUNT total) ==="
    # Show last 3 decision headers + status
    grep -E "^### D-|^status:|^domain:" "$LEDGER" 2>/dev/null | tail -9 || true
    echo "=== END DECISIONS ==="
    echo ""
  fi
fi

echo "[post-compact-reinject] Context restored after compaction." >&2
exit 0

#!/usr/bin/env bash
# re-inject-context.sh — SessionStart hook (matcher: compact)
# Re-injects critical project context after conversation compaction

set -eo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Check for PROJECT.md and output key sections
if [ -f "$PROJECT_DIR/PROJECT.md" ]; then
  echo "=== PROJECT CONTEXT (re-injected after compaction) ==="
  echo ""
  echo "Project config: PROJECT.md"
  grep -A 20 "^## Tech Stack\|^## Build Commands\|^## Domain Model" "$PROJECT_DIR/PROJECT.md" 2>/dev/null | head -60 || true
  echo ""
  echo "=== END PROJECT CONTEXT ==="
fi

#!/usr/bin/env bash
# guard-webfetch.sh — PreToolUse hook for WebFetch tool
# Blocks known malicious URL patterns and logs all outbound fetches for audit.
#
# Exit codes: 0 = allow | 2 = block tool call

set -eo pipefail

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
if [ -z "$TOOL_INPUT" ]; then exit 0; fi

# Extract URL from JSON input
URL=$(echo "$TOOL_INPUT" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
if [ -z "$URL" ]; then exit 0; fi

# ─── BLOCK: URL shorteners ──────────────────────────────────────────────────
# Shorteners hide actual destination — indirect injection via redirect
SHORTENER_PATTERN='bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|short\.io|rebrand\.ly|cutt\.ly|is\.gd|v\.gd|tiny\.cc'
if echo "$URL" | grep -qE "($SHORTENER_PATTERN)"; then
  echo "SECURITY BLOCKED [guard-webfetch]: URL shortener detected."
  echo "URL: $URL"
  echo "Risk: Shorteners can redirect to pages containing prompt injection payloads."
  echo "Use the full destination URL instead."
  exit 2
fi

# ─── BLOCK: Non-HTTPS in production-style URLs ──────────────────────────────
# Allow http://localhost and http://127.0.0.1 for local dev — block others
if echo "$URL" | grep -qE '^http://'; then
  if ! echo "$URL" | grep -qE '^http://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:|/)'; then
    echo "SECURITY WARNING [guard-webfetch]: Non-HTTPS URL detected."
    echo "URL: $URL"
    echo "Risk: Unencrypted traffic can be intercepted and injected."
    echo "Proceeding — but prefer HTTPS for all external URLs."
    # Warn only, do not block — may be legitimate internal HTTP endpoint
  fi
fi

# ─── AUDIT LOG: Record all WebFetch calls ───────────────────────────────────
# Provides traceability for security review
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
  mkdir -p "$LOG_DIR"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WebFetch: $URL" \
    >> "$LOG_DIR/network-audit.log" 2>/dev/null || true
fi

exit 0

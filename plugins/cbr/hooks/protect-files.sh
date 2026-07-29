#!/usr/bin/env bash
# protect-files.sh — PreToolUse hook for Edit | Write | Read tools
#
# WRITE mode (default): blocks modifications to sensitive files and lock files
# READ mode ($1=read):  blocks reading credential/secret files only
#                       (lock files are safe to read — not blocked in read mode)
#
# Exit codes: 0 = allow | 2 = block tool call

set -eo pipefail

MODE="${1:-write}"

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
if [ -z "$TOOL_INPUT" ]; then
  exit 0
fi

# Parse file path from tool input (portable sed, no -P flag)
FILE_PATH=$(echo "$TOOL_INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# ─── BOTH MODES: Block sensitive credential files ───────────────────────────
BLOCKED_CREDS=".env .env.local .env.production .env.staging .env.test credentials.json secrets.json service-account.json id_rsa id_ed25519"
for BLOCKED in $BLOCKED_CREDS; do
  if [ "$BASENAME" = "$BLOCKED" ]; then
    if [ "$MODE" = "read" ]; then
      echo "SECURITY BLOCKED [protect-files]: Cannot read sensitive credential file: $BASENAME"
      echo "Risk: Agents reading secrets/credentials may leak them via outputs or logs."
    else
      echo "SECURITY BLOCKED [protect-files]: Cannot modify sensitive file: $BASENAME"
    fi
    exit 2
  fi
done

# Block .env* pattern (any variant)
if [[ "$BASENAME" == .env* ]]; then
  if [ "$MODE" = "read" ]; then
    echo "SECURITY BLOCKED [protect-files]: Cannot read env file: $BASENAME"
    echo "Risk: Env files contain secrets — agent outputs are not sandboxed."
  else
    echo "SECURITY BLOCKED [protect-files]: Cannot modify env file: $BASENAME"
  fi
  exit 2
fi

# Block PEM / private key files
if echo "$BASENAME" | grep -qE '\.(pem|key|p12|pfx|crt|cer)$'; then
  if [ "$MODE" = "read" ]; then
    echo "SECURITY BLOCKED [protect-files]: Cannot read key/certificate file: $BASENAME"
  else
    echo "SECURITY BLOCKED [protect-files]: Cannot modify key/certificate file: $BASENAME"
  fi
  exit 2
fi

# ─── WRITE MODE ONLY: Block lock files ──────────────────────────────────────
# Lock files are safe to read but must never be manually modified
if [ "$MODE" != "read" ]; then
  LOCK_FILES="package-lock.json yarn.lock pnpm-lock.yaml Pipfile.lock poetry.lock Gemfile.lock composer.lock"
  for LOCK in $LOCK_FILES; do
    if [ "$BASENAME" = "$LOCK" ]; then
      echo "SECURITY BLOCKED [protect-files]: Cannot modify lock file: $BASENAME"
      echo "Reason: Lock files must only be updated by package managers, not manually."
      exit 2
    fi
  done
fi

exit 0

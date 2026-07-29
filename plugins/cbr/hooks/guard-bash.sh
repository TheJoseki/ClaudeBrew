#!/usr/bin/env bash
# guard-bash.sh — PreToolUse hook for Bash tool
# Blocks dangerous shell command patterns: code injection, data exfiltration,
# credential access, URL shorteners, and command substitution with remote fetch.
#
# Exit codes: 0 = allow | 2 = block tool call

set -eo pipefail

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
if [ -z "$TOOL_INPUT" ]; then exit 0; fi

# Strategy: scan raw TOOL_INPUT (JSON) directly.
# The command value is embedded as-is — dangerous patterns are not JSON-escaped
# in ways that would hide them (e.g. "| bash" stays "| bash" in JSON).

# ─── BLOCK: Pipe to shell interpreter ───────────────────────────────────────
# Catches: echo payload | bash  /  curl url | sh  /  cat file | zsh
if echo "$TOOL_INPUT" | grep -qE '\|\s*(bash|sh|zsh|ksh|csh|dash)([[:space:]"\\]|\\\\n|$)'; then
  echo "SECURITY BLOCKED [guard-bash]: Pipe to shell interpreter detected."
  echo "Risk: '| bash/sh/zsh' is the primary prompt-injection execution vector."
  echo "If this is intentional, ask the user to run the command manually."
  exit 2
fi

# ─── BLOCK: eval execution ──────────────────────────────────────────────────
# Catches: eval "$cmd"  /  eval "$(curl ...)"  /  ; eval ...
if echo "$TOOL_INPUT" | grep -qE '(^|[[:space:];\`]|\\n)eval[[:space:]]'; then
  echo "SECURITY BLOCKED [guard-bash]: eval detected in command."
  echo "Risk: eval executes arbitrary string as code — top injection vector."
  exit 2
fi

# ─── BLOCK: Env var exfiltration to network ─────────────────────────────────
# Catches: echo $SECRET | curl ...  /  curl ... $API_KEY
if echo "$TOOL_INPUT" | grep -qE '\$[A-Z_]{3,}[^"]{0,80}\|\s*(curl|wget|nc\s|netcat)'; then
  echo "SECURITY BLOCKED [guard-bash]: Env var piped to network tool."
  echo "Risk: '\$SECRET | curl/wget' is a credential exfiltration pattern."
  exit 2
fi
if echo "$TOOL_INPUT" | grep -qE '(curl|wget)[^"]{0,120}\$[A-Z_]{4,}'; then
  echo "SECURITY BLOCKED [guard-bash]: Env var embedded in network request."
  echo "Risk: Passing credentials directly to external network calls."
  exit 2
fi

# ─── BLOCK: base64 decode piped to shell ────────────────────────────────────
# Catches: echo b64 | base64 -d | bash  /  base64 --decode payload | sh
if echo "$TOOL_INPUT" | grep -qE 'base64[^"]{0,40}(-d|--decode)[^"]{0,40}\|\s*(bash|sh|eval)'; then
  echo "SECURITY BLOCKED [guard-bash]: base64 decode piped to shell."
  echo "Risk: Classic obfuscated payload delivery technique."
  exit 2
fi

# ─── BLOCK: Command substitution fetching remote content ────────────────────
# Catches: $(curl url)  /  `wget url`  used inline in commands
if echo "$TOOL_INPUT" | grep -qE '\$\(\s*(curl|wget)\s'; then
  echo "SECURITY BLOCKED [guard-bash]: Command substitution with network fetch."
  echo "Risk: '\$(curl...)' injects remote content directly into shell execution."
  exit 2
fi

# ─── BLOCK: URL shorteners in network commands ──────────────────────────────
# Shorteners obscure destination — cannot audit or allowlist safely
SHORTENER_PATTERN='bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|short\.io|rebrand\.ly|cutt\.ly|is\.gd|v\.gd|tiny\.cc'
if echo "$TOOL_INPUT" | grep -qE "(curl|wget)[^\"]{0,200}($SHORTENER_PATTERN)"; then
  echo "SECURITY BLOCKED [guard-bash]: URL shortener in network request."
  echo "Risk: Shorteners can redirect to malicious payloads — destination unauditable."
  exit 2
fi

# ─── BLOCK: Reading sensitive credential files via shell ────────────────────
# Catches: cat .env  /  head .env.production  /  type credentials.json
CRED_FILE_PATTERN='\.env\b|\.env\.|credentials\.json|secrets\.json|service-account\.json|\.pem\b|\.key\b|\.p12\b|\.pfx\b|id_rsa|id_ed25519'
if echo "$TOOL_INPUT" | grep -qE "(cat|type|more|less|head|tail|bat|Get-Content)[[:space:]][^\"]{0,200}($CRED_FILE_PATTERN)"; then
  echo "SECURITY BLOCKED [guard-bash]: Attempt to read sensitive credential file via shell."
  echo "Risk: Direct shell access to .env / key files may expose secrets."
  exit 2
fi

# ─── WARN: Outbound POST to external host (log, do not block) ───────────────
# Blocking would break legitimate deploy/API workflows — log for audit instead
if echo "$TOOL_INPUT" | grep -qE '(curl|wget)[^"]{0,200}(-X POST|--request POST|--post-data|--post-file)'; then
  echo "SECURITY NOTICE [guard-bash]: Outbound POST request detected."
  echo "This is allowed but logged. Verify the destination is intentional."
  # Write to audit log if project dir is known
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    mkdir -p "$CLAUDE_PROJECT_DIR/.claude/logs"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OUTBOUND POST detected in Bash command" \
      >> "$CLAUDE_PROJECT_DIR/.claude/logs/security-audit.log" 2>/dev/null || true
  fi
fi

exit 0

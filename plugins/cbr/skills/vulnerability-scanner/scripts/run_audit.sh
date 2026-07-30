#!/usr/bin/env bash
# ClaudeBrew — Auto-detect package manager and run security audit
# Sprint 3: deterministic stack detection avoids Claude guessing wrong audit tool.
#
# Usage:
#   bash run_audit.sh          # human-readable output
#   bash run_audit.sh --json   # JSON output (for CI/machine parsing)
#
# Exit codes:
#   0  — audit ran, no vulnerabilities found
#   1  — audit ran, vulnerabilities found (details in output)
#   2  — no supported package manager detected
#   3  — audit tool not available (needs installation)

set -euo pipefail

JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

DETECTED=""
AUDIT_CMD=""
INSTALL_HINT=""

# ── Detection priority: most specific first ──────────────────────────────────

if [[ -f "package-lock.json" ]] || [[ -f "package.json" ]]; then
    DETECTED="Node.js (npm)"
    AUDIT_CMD="npm audit --audit-level=high"
    INSTALL_HINT="Node.js and npm must be installed"

elif [[ -f "yarn.lock" ]]; then
    DETECTED="Node.js (yarn)"
    AUDIT_CMD="yarn audit --level high"
    INSTALL_HINT="Yarn must be installed: npm install -g yarn"

elif [[ -f "pnpm-lock.yaml" ]]; then
    DETECTED="Node.js (pnpm)"
    AUDIT_CMD="pnpm audit --audit-level high"
    INSTALL_HINT="pnpm must be installed: npm install -g pnpm"

elif [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]]; then
    DETECTED="Python"
    AUDIT_CMD="pip-audit"
    INSTALL_HINT="Install pip-audit: pip install pip-audit"

elif [[ -f "Gemfile.lock" ]] || [[ -f "Gemfile" ]]; then
    DETECTED="Ruby"
    AUDIT_CMD="bundle audit check --update"
    INSTALL_HINT="Install bundler-audit: gem install bundler-audit"

elif [[ -f "go.mod" ]]; then
    DETECTED="Go"
    AUDIT_CMD="govulncheck ./..."
    INSTALL_HINT="Install govulncheck: go install golang.org/x/vuln/cmd/govulncheck@latest"

elif [[ -f "Cargo.toml" ]]; then
    DETECTED="Rust"
    AUDIT_CMD="cargo audit"
    INSTALL_HINT="Install cargo-audit: cargo install cargo-audit"

else
    if $JSON_MODE; then
        echo '{"status":"error","message":"No supported package manager detected","supported":["npm","yarn","pnpm","pip","bundler","go","cargo"]}'
    else
        echo "❌  No supported package manager detected in current directory."
        echo "    Supported: npm / yarn / pnpm / pip / bundler / go / cargo"
    fi
    exit 2
fi

# ── Verify tool availability ──────────────────────────────────────────────────

TOOL_BIN="${AUDIT_CMD%% *}"
if ! command -v "$TOOL_BIN" &>/dev/null; then
    if $JSON_MODE; then
        echo "{\"status\":\"error\",\"message\":\"Tool not found: $TOOL_BIN\",\"hint\":\"$INSTALL_HINT\"}"
    else
        echo "❌  Audit tool not found: $TOOL_BIN"
        echo "    $INSTALL_HINT"
    fi
    exit 3
fi

# ── Run audit ─────────────────────────────────────────────────────────────────

if $JSON_MODE; then
    echo "{\"status\":\"running\",\"stack\":\"$DETECTED\",\"command\":\"$AUDIT_CMD\"}"
else
    echo "🔍  Stack detected: $DETECTED"
    echo "🔧  Running: $AUDIT_CMD"
    echo "────────────────────────────────────────────────────────"
fi

set +e
eval "$AUDIT_CMD"
EXIT_CODE=$?
set -e

if [[ $EXIT_CODE -eq 0 ]]; then
    $JSON_MODE || echo "────────────────────────────────────────────────────────"
    $JSON_MODE || echo "✅  Audit complete — no vulnerabilities found"
else
    $JSON_MODE || echo "────────────────────────────────────────────────────────"
    $JSON_MODE || echo "⚠️   Audit complete — vulnerabilities found (exit code: $EXIT_CODE)"
    $JSON_MODE || echo "    Review output above. Fix Critical and High findings before delivery."
fi

exit $EXIT_CODE

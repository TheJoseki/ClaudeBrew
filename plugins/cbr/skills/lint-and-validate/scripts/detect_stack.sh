#!/usr/bin/env bash
# ClaudeKit — Detect project tech stack and output lint + type-check commands
# Sprint 3: eliminates Claude guessing wrong linting commands from file extensions.
#
# Usage:
#   bash detect_stack.sh            # human-readable: prints commands to run
#   bash detect_stack.sh --export   # machine-readable: exports LANG, LINT_CMD, TYPE_CMD
#   source detect_stack.sh --export # source to use vars in calling script
#
# Output (--export mode):
#   LANG=typescript|javascript|python|ruby|go|rust
#   LINT_CMD=<command to run linter>
#   TYPE_CMD=<command to run type checker (empty string if N/A)>

set -euo pipefail

EXPORT_MODE=false
[[ "${1:-}" == "--export" ]] && EXPORT_MODE=true

LANG=""
LINT_CMD=""
TYPE_CMD=""
PACKAGE_MANAGER=""

# ── Detect package manager for JS/TS projects ────────────────────────────────

if [[ -f "pnpm-lock.yaml" ]]; then
    PACKAGE_MANAGER="pnpm"
elif [[ -f "yarn.lock" ]]; then
    PACKAGE_MANAGER="yarn"
elif [[ -f "package-lock.json" ]] || [[ -f "package.json" ]]; then
    PACKAGE_MANAGER="npm"
fi

# ── Primary stack detection ───────────────────────────────────────────────────

if [[ -f "tsconfig.json" ]] || [[ -f "tsconfig.base.json" ]]; then
    LANG="typescript"
    # Prefer project lint script over direct eslint call
    if [[ -n "$PACKAGE_MANAGER" ]] && grep -q '"lint"' package.json 2>/dev/null; then
        LINT_CMD="$PACKAGE_MANAGER run lint"
    elif [[ -n "$PACKAGE_MANAGER" ]]; then
        LINT_CMD="${PACKAGE_MANAGER} exec eslint . --ext .ts,.tsx --fix"
    else
        LINT_CMD="npx eslint . --ext .ts,.tsx --fix"
    fi
    TYPE_CMD="npx tsc --noEmit"

elif [[ -n "$PACKAGE_MANAGER" ]] && [[ -f "package.json" ]]; then
    LANG="javascript"
    if grep -q '"lint"' package.json 2>/dev/null; then
        LINT_CMD="$PACKAGE_MANAGER run lint"
    else
        LINT_CMD="${PACKAGE_MANAGER} exec eslint . --ext .js,.jsx --fix"
    fi
    TYPE_CMD=""  # No type checking for plain JS

elif [[ -f "pyproject.toml" ]] || [[ -f "setup.cfg" ]] || [[ -f ".flake8" ]]; then
    LANG="python"
    if command -v ruff &>/dev/null; then
        LINT_CMD="ruff check . --fix"
        TYPE_CMD="mypy . --ignore-missing-imports"
    elif command -v flake8 &>/dev/null; then
        LINT_CMD="flake8 ."
        TYPE_CMD="mypy . --ignore-missing-imports"
    else
        LINT_CMD="python -m flake8 ."
        TYPE_CMD="python -m mypy . --ignore-missing-imports"
    fi

elif [[ -f "Gemfile" ]] || [[ -f ".rubocop.yml" ]]; then
    LANG="ruby"
    LINT_CMD="bundle exec rubocop --auto-correct"
    TYPE_CMD=""  # Sorbet/RBS optional

elif [[ -f "go.mod" ]]; then
    LANG="go"
    LINT_CMD="golangci-lint run ./..."
    TYPE_CMD="go vet ./..."

elif [[ -f "Cargo.toml" ]]; then
    LANG="rust"
    LINT_CMD="cargo clippy -- -D warnings"
    TYPE_CMD="cargo check"

else
    if $EXPORT_MODE; then
        echo "LANG=unknown"
        echo "LINT_CMD="
        echo "TYPE_CMD="
    else
        echo "❌  No recognizable tech stack found in current directory."
        echo "    Supported: TypeScript, JavaScript, Python, Ruby, Go, Rust"
    fi
    exit 1
fi

# ── Output ────────────────────────────────────────────────────────────────────

if $EXPORT_MODE; then
    echo "LANG=$LANG"
    echo "LINT_CMD=$LINT_CMD"
    echo "TYPE_CMD=$TYPE_CMD"
else
    echo "🔍  Stack detected: $LANG"
    echo ""
    echo "  Lint command:"
    echo "    $LINT_CMD"
    if [[ -n "$TYPE_CMD" ]]; then
        echo ""
        echo "  Type check command:"
        echo "    $TYPE_CMD"
    else
        echo ""
        echo "  Type check: N/A for $LANG"
    fi
    echo ""
    echo "  Run both to validate:"
    if [[ -n "$TYPE_CMD" ]]; then
        echo "    $TYPE_CMD && $LINT_CMD"
    else
        echo "    $LINT_CMD"
    fi
fi

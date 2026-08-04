#!/usr/bin/env bash
# post-edit-reminder.sh — Stop hook
# Reminds to run tests if code files were modified during the session

set -eo pipefail

echo ""
echo "=== Session Complete ==="
echo "If code was modified, remember to:"
echo "  - Run tests (unit + integration)"
echo "  - Check linting / type errors"
echo "  - Review changes before committing"
echo "========================"

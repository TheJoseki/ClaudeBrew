#!/usr/bin/env bash
# subagent-quality-gate.sh — SubagentStop hook
# Enforces STATUS declaration for ClaudeKit SDLC agents before they can stop.
# Agents MUST end with: STATUS: DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT
#
# Event: SubagentStop (matcher: .*-agent)
# Policy: Strict block for 9 ClaudeKit agents, skip all others.
# Exit codes: 0 = allow stop | 2 = block stop (agent forced to continue)
#
# CRITICAL: Check stop_hook_active to prevent infinite loops!

set -eo pipefail

# Read stdin JSON
INPUT=$(cat)

# ─── INFINITE LOOP GUARD ─────────────────────────────────────────────────────
# When this hook blocks (exit 2), agent continues and eventually stops again.
# On second stop, stop_hook_active=true — we MUST allow it through.
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "unknown"' 2>/dev/null || echo "unknown")
LAST_MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // ""' 2>/dev/null || echo "")

# ─── SKIP non-SDLC agents ────────────────────────────────────────────────────
# Only enforce for the 9 ClaudeKit SDLC agents
SDLC_AGENTS="orchestrator-agent ba-agent architect-agent ui-designer-agent developer-agent code-review-agent unit-test-agent integration-test-agent bug-fix-agent security-tester-agent"

IS_SDLC=false
for AGENT in $SDLC_AGENTS; do
  if [ "$AGENT_TYPE" = "$AGENT" ]; then
    IS_SDLC=true
    break
  fi
done

if [ "$IS_SDLC" = "false" ]; then
  exit 0
fi

# ─── CHECK: STATUS declaration present ────────────────────────────────────────
STATUS_PATTERN='STATUS:\s*(DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT)'

if echo "$LAST_MSG" | grep -qE "$STATUS_PATTERN"; then
  # STATUS found — check for evidence on DONE claims
  if echo "$LAST_MSG" | grep -qE 'STATUS:\s*DONE\b'; then
    # DONE requires some evidence (file paths, test results, counts)
    if echo "$LAST_MSG" | grep -qE '(EVIDENCE:|test.*pass|created|modified|verified|file|coverage)'; then
      exit 0  # DONE with evidence — allow
    else
      echo "Quality gate [$AGENT_TYPE]: STATUS: DONE declared but no EVIDENCE found." >&2
      echo "Add EVIDENCE line with specific outputs (test results, file paths, counts)." >&2
      echo "Example: EVIDENCE: 15/15 tests pass. Coverage: 87%. Created: src/auth/service.ts" >&2
      exit 2
    fi
  fi
  # DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT — allow (they carry their own context)
  exit 0
fi

# ─── STATUS missing — block and instruct ──────────────────────────────────────
echo "Quality gate [$AGENT_TYPE]: Missing STATUS declaration." >&2
echo "" >&2
echo "You MUST end your response with one of:" >&2
echo "  STATUS: DONE              — all steps completed (requires EVIDENCE line)" >&2
echo "  STATUS: DONE_WITH_CONCERNS — completed with issues (list each concern + severity)" >&2
echo "  STATUS: BLOCKED           — cannot proceed (explain what blocks + what was tried)" >&2
echo "  STATUS: NEEDS_CONTEXT     — missing required info (specify exactly what + from whom)" >&2
echo "" >&2
echo "Example:" >&2
echo "  STATUS: DONE" >&2
echo "  EVIDENCE: All 47/49 tests pass (2 skipped). Coverage: 87% statement." >&2
exit 2

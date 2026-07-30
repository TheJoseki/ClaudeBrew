#!/usr/bin/env python3
"""SubagentStop hook — enforces a STATUS declaration for cbr SDLC role agents.

Ported from bash: drops the `jq` dependency (absent on stock Windows/macOS, which
made the gate fail-open to a no-op) and reads the SubagentStop payload from stdin
JSON. Blocks (exit 2) an SDLC role agent that stops without a STATUS line so it is
forced to continue; allows every non-SDLC agent through untouched.

Loop guard: when this hook blocks, the agent continues and stops again; on that
second stop `stop_hook_active` is true and we MUST allow it, or the agent loops
forever.

Exit codes: 0 = allow stop | 2 = block stop (agent forced to continue).
"""
import sys
import re
import json

# The cbr SDLC role agents this gate enforces (matcher .*-agent already narrows
# to agents; this narrows further to the pipeline roles that must report STATUS).
SDLC_AGENTS = {
    "orchestrator-agent", "ba-agent", "architect-agent", "ui-designer-agent",
    "developer-agent", "code-review-agent", "unit-test-agent",
    "integration-test-agent", "bug-fix-agent", "security-tester-agent",
}


def block(lines):
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unreadable payload -> allow stop (fail open)

    if data.get("stop_hook_active"):
        sys.exit(0)  # loop guard — already continuing from a prior block

    # Plugin agents may arrive namespaced (e.g. "cbr:developer-agent"); match bare name.
    agent_type = (data.get("agent_type") or "unknown").split(":")[-1]
    if agent_type not in SDLC_AGENTS:
        sys.exit(0)  # only gate cbr SDLC role agents

    last_msg = data.get("last_assistant_message") or ""

    if re.search(r"STATUS:\s*(DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT)", last_msg):
        # A bare DONE must carry evidence; the other statuses carry their own context.
        if re.search(r"STATUS:\s*DONE\b", last_msg):
            if re.search(r"(EVIDENCE:|\btests?\b.{0,20}\bpass|\bcreated\b|\bmodified\b|\bverified\b|\bcoverage\b)",
                         last_msg, re.IGNORECASE):
                sys.exit(0)
            block([
                f"Quality gate [{agent_type}]: STATUS: DONE declared but no EVIDENCE found.",
                "Add an EVIDENCE line with specific outputs (test results, file paths, counts).",
                "Example: EVIDENCE: 15/15 tests pass. Coverage: 87%. Created: src/auth/service.ts",
            ])
        sys.exit(0)

    block([
        f"Quality gate [{agent_type}]: Missing STATUS declaration.",
        "",
        "You MUST end your response with one of:",
        "  STATUS: DONE               — all steps completed (requires an EVIDENCE line)",
        "  STATUS: DONE_WITH_CONCERNS — completed with issues (list each concern + severity)",
        "  STATUS: BLOCKED            — cannot proceed (explain the blocker + what was tried)",
        "  STATUS: NEEDS_CONTEXT      — missing required info (specify what + from whom)",
    ])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tests for the ported SubagentStop / PreCompact hooks.

- subagent-quality-gate.py: exit 2 = block stop, exit 0 = allow.
- compact-context-saver.py: smoke test — writes a checkpoint and exits 0.

Run: python evals/test_subagent_gate.py
"""
import json
import os
import subprocess
import sys
import tempfile

HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "cbr", "hooks",
)
GATE = os.path.join(HOOKS, "subagent-quality-gate.py")
SAVER = os.path.join(HOOKS, "compact-context-saver.py")


def run(hook, payload, env=None):
    return subprocess.run(
        [sys.executable, hook], input=json.dumps(payload),
        capture_output=True, text=True, env=env,
    )


# (payload, expected returncode)
GATE_CASES = [
    ({"agent_type": "general-purpose", "last_assistant_message": "all done"}, 0),           # non-SDLC -> allow
    ({"agent_type": "developer-agent", "last_assistant_message": "finished the work"}, 2),   # SDLC, no STATUS -> block
    ({"agent_type": "developer-agent", "last_assistant_message": "STATUS: DONE\nEVIDENCE: 3/3 tests pass"}, 0),
    ({"agent_type": "developer-agent", "last_assistant_message": "STATUS: DONE"}, 2),         # DONE, no evidence -> block
    ({"agent_type": "developer-agent", "last_assistant_message": "STATUS: BLOCKED - missing creds"}, 0),
    ({"agent_type": "developer-agent", "last_assistant_message": "x", "stop_hook_active": True}, 0),  # loop guard
]


def main():
    failures = 0

    for payload, expect in GATE_CASES:
        rc = run(GATE, payload).returncode
        ok = rc == expect
        failures += not ok
        msg = (payload.get("last_assistant_message") or "")[:34]
        print(f"{'OK  ' if ok else 'FAIL'} gate rc={rc} expect={expect}  {payload.get('agent_type'):18} {msg!r}")

    # compact-context-saver smoke test — checkpoint written, exit 0.
    with tempfile.TemporaryDirectory() as proj:
        env = dict(os.environ, CLAUDE_PROJECT_DIR=proj)
        res = run(SAVER, {"trigger": "manual", "transcript_path": ""}, env=env)
        checkpoint = os.path.join(proj, ".claude", "compact-checkpoint.md")
        ok = res.returncode == 0 and os.path.isfile(checkpoint) and "Pre-Compact Checkpoint" in open(checkpoint, encoding="utf-8").read()
        failures += not ok
        print(f"{'OK  ' if ok else 'FAIL'} saver rc={res.returncode} checkpoint_written={os.path.isfile(checkpoint)}")

    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

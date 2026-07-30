#!/usr/bin/env python3
"""PreToolUse hook for the WebFetch tool — blocks URL shorteners.

Shorteners hide the real destination and are an indirect prompt-injection vector
(redirect to a payload page). Reads tool_input.url from stdin JSON (the real hook
contract); the previous bash version read a non-existent env var and never fired.

A block is signalled with a permissionDecision:deny JSON object + exit 0.
(The old script also logged every fetch and warned on non-HTTPS, but that code sat
after the dead early-exit and never ran; those non-blocking side effects are
intentionally not carried over — the guard's job is to block.)
"""
import sys
import re
import json

SHORTENERS = r"bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|short\.io|rebrand\.ly|cutt\.ly|is\.gd|v\.gd|tiny\.cc"


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unreadable payload -> fail open

    url = (data.get("tool_input") or {}).get("url") or ""
    if not url:
        sys.exit(0)

    if re.search(r"(?<![\w.])(" + SHORTENERS + r")(?![\w])", url):
        deny(f"guard-webfetch: URL shortener detected ({url}) — destination is unauditable; use the full URL.")

    sys.exit(0)


if __name__ == "__main__":
    main()

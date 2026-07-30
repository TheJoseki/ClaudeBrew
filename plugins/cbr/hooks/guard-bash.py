#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool — blocks dangerous shell patterns.

Best-effort heuristic guard (NOT a sandbox — determined injection can evade it):
pipe-to-shell, eval, env-var exfiltration to network, base64|shell, command
substitution with remote fetch, URL shorteners, and reading credential files via
shell. Reads tool_input.command from stdin JSON (the real hook contract); the
previous bash version read a non-existent env var and never fired.

A block is signalled with a permissionDecision:deny JSON object + exit 0.
"""
import sys
import re
import json

SHORTENERS = r"bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|short\.io|rebrand\.ly|cutt\.ly|is\.gd|v\.gd|tiny\.cc"
CRED_FILES = r"\.env\b|\.env\.|credentials\.json|secrets\.json|service-account\.json|\.pem\b|\.key\b|\.p12\b|\.pfx\b|id_rsa|id_ed25519"

# (regex, reason) — first match blocks. Ordered most-specific-first.
RULES = [
    (r"\|\s*(bash|sh|zsh|ksh|csh|dash)(\s|$|\"|')", "pipe to a shell interpreter (| bash/sh) — the primary injection execution vector"),
    (r"(^|[\s;`])eval\s", "eval executes an arbitrary string as code"),
    (r"\$[A-Z_]{3,}[^\"']{0,80}\|\s*(curl|wget|nc\s|netcat)", "environment variable piped to a network tool (credential exfiltration)"),
    (r"(curl|wget)[^\"']{0,120}\$[A-Z_]{4,}", "credential environment variable embedded in a network request"),
    (r"base64[^\"']{0,40}(-d|--decode)[^\"']{0,40}\|\s*(bash|sh|eval)", "base64 decode piped to a shell (obfuscated payload delivery)"),
    (r"\$\(\s*(curl|wget)\s", "command substitution fetching remote content ($(curl ...))"),
    (r"(curl|wget)[^\"']{0,200}(?<![\w.])(" + SHORTENERS + r")(?![\w])", "URL shortener in a network request — destination is unauditable"),
    (r"(cat|type|more|less|head|tail|bat|Get-Content)\s[^\"']{0,200}(" + CRED_FILES + ")", "reading a credential/secret file via shell"),
]


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

    command = (data.get("tool_input") or {}).get("command") or ""
    if not command:
        sys.exit(0)

    for pattern, reason in RULES:
        if re.search(pattern, command):
            deny(f"guard-bash: {reason}. If this is intentional, ask the user to run it manually.")

    sys.exit(0)


if __name__ == "__main__":
    main()

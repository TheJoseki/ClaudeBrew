#!/usr/bin/env python3
"""PreToolUse hook for Edit | Write | Read — blocks secrets & lock files.

WRITE mode (default): blocks modification of credential/secret files and lock files.
READ mode  (argv[1] == "read"): blocks reading credential/secret files only
           (lock files are safe to read, so they are not blocked in read mode).

Contract (https://code.claude.com/docs/en/hooks.md): the tool payload arrives as
JSON on **stdin** (tool_input.file_path / notebook_path). A block is signalled with
a permissionDecision:deny JSON object on stdout and exit 0 — the decision rides in
the JSON, not the exit code. The previous bash version read a non-existent env var
($CLAUDE_TOOL_INPUT) and therefore never fired.

Design stance: fail OPEN. An unreadable payload or missing path allows the edit —
a guard that bricks unrelated work is worse than one with a narrow, known bypass.
Matching is case-insensitive because the primary target (win32) has a
case-insensitive filesystem, so `.ENV` must be caught like `.env`.
"""
import sys
import os
import json

# Exact credential basenames (compared casefolded).
CRED_BASENAMES = {
    ".env", ".env.local", ".env.production", ".env.staging", ".env.test",
    "credentials.json", "secrets.json", "service-account.json",
    "id_rsa", "id_ed25519",
    ".npmrc", ".pgpass",          # commonly carry auth tokens
}
# Credential/secret file extensions (casefolded).
CRED_EXTS = (".pem", ".key", ".p12", ".pfx", ".crt", ".cer", ".tfvars")
# Lock files: safe to read, must never be hand-edited.
LOCK_BASENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "pipfile.lock",
    "poetry.lock", "gemfile.lock", "composer.lock",
}


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "write"
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unreadable payload -> fail open

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    norm = file_path.replace("\\", "/").casefold()
    base = os.path.basename(norm)
    verb = "read" if mode == "read" else "modify"

    # AWS shared credentials — path-aware so a bare "credentials" basename elsewhere
    # is not a false positive.
    if norm.endswith("/.aws/credentials"):
        deny(f"protect-files: cannot {verb} AWS credentials file.")

    if base in CRED_BASENAMES or base.startswith(".env") or base.endswith(CRED_EXTS):
        deny(f"protect-files: cannot {verb} sensitive/credential file: {base}")

    if mode != "read" and base in LOCK_BASENAMES:
        deny(f"protect-files: cannot modify lock file {base} — only package managers should update it.")

    sys.exit(0)


if __name__ == "__main__":
    main()

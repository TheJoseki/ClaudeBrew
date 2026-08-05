#!/usr/bin/env python3
"""Stop hook — reminds to run tests / lint / review after a session that may have
touched code.

Ported from the former post-edit-reminder.sh so that Python is the *sole* runtime
prerequisite for CBR's hooks (D-1): no Git Bash dependency on Windows. Behaviour is
unchanged — it prints a plain-text reminder to stdout. A Stop hook receives a JSON
payload on stdin, but this reminder needs no field from it, so stdin is drained and
ignored (never parsed).
"""
import sys

REMINDER = """
=== Session Complete ===
If code was modified, remember to:
  - Run tests (unit + integration)
  - Check linting / type errors
  - Review changes before committing
========================"""


def main():
    try:
        sys.stdin.read()  # drain the payload if the harness sent one; no field is needed
    except Exception:
        pass
    print(REMINDER)


if __name__ == "__main__":
    main()

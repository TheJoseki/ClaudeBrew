#!/usr/bin/env python3
"""Fresh-eyes mechanism gate — the R3 3-skill split's actual security control, checked directly.

Run: python evals/test_fresh_eyes_mechanism.py

The R3 merge split the old 2-skill draft into 3 (`cbr-plan`, `cbr-implement`, `cbr-verify`)
specifically because a merged implement+verify skill could never mechanically deny itself
`Write` during a review/security/test-execution phase — Claude Code skills have no
per-internal-phase tool scoping. `cbr-verify`'s `allowed-tools` grant omitting `Write`/`Edit` IS
the control; it is not a design detail to re-derive by reading prose, it is the single fact this
gate exists to protect against silent regression (e.g. a future edit widening the grant "just to
let it also update the work log").

Checks the mechanism, not just that a verdict-artifact shape exists:
1. cbr-verify/SKILL.md's frontmatter `allowed-tools` contains no `Write` or `Edit`.
2. cbr-implement/SKILL.md's body contains no *affirmative* spawn of `cbr-reviewer`/`cbr-tester`
   (an explicit prohibition sentence like "never spawn cbr-tester" is the correct, intended
   guardrail and must NOT trip this gate — only a line that reads as an instruction to actually
   spawn one, with no negation word nearby, is a real regression).
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VERIFY_SKILL = os.path.join(_ROOT, "claude", "skills", "cbr-verify", "SKILL.md")
_IMPLEMENT_SKILL = os.path.join(_ROOT, "claude", "skills", "cbr-implement", "SKILL.md")

_NEGATION_WORDS = ("never", "not ", "n't", "no ", "held no", "holds no", "do not")

_FAILURES = []


def _read(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def test_verify_holds_no_write_edit():
    if not os.path.isfile(_VERIFY_SKILL):
        _FAILURES.append(f"missing file: {_VERIFY_SKILL}")
        return
    text = _read(_VERIFY_SKILL)
    m = re.search(r"^allowed-tools:\s*(.+)$", text, re.MULTILINE)
    if not m:
        _FAILURES.append("cbr-verify/SKILL.md has no `allowed-tools:` frontmatter line at all")
        return
    tools = [t.strip() for t in m.group(1).split(",")]
    for bad in ("Write", "Edit"):
        if bad in tools:
            _FAILURES.append(
                f"cbr-verify/SKILL.md allowed-tools includes '{bad}' -- this is the exact "
                f"regression the R3 3-skill split exists to prevent: {m.group(0)!r}"
            )


def test_implement_never_spawns_verify_agents():
    if not os.path.isfile(_IMPLEMENT_SKILL):
        _FAILURES.append(f"missing file: {_IMPLEMENT_SKILL}")
        return
    text = _read(_IMPLEMENT_SKILL)
    for i, line in enumerate(text.splitlines(), 1):
        if "cbr-reviewer" not in line and "cbr-tester" not in line:
            continue
        low = line.lower()
        if any(neg in low for neg in _NEGATION_WORDS):
            continue  # an explicit prohibition -- the intended guardrail, not a regression
        # A mention with no negation nearby and language suggesting an actual spawn instruction.
        if re.search(r"spawn|Agent\(|subagent_type", line):
            _FAILURES.append(
                f"cbr-implement/SKILL.md:{i} affirmatively mentions spawning a verify-role "
                f"agent with no negation -- {ascii(line.strip()[:120])}"
            )


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)} fresh-eyes mechanism violations):")
        for f in _FAILURES:
            print("  -", f)
        sys.exit(1)
    print("OK - cbr-verify holds no Write/Edit; cbr-implement never spawns a verify-role agent")


if __name__ == "__main__":
    main()

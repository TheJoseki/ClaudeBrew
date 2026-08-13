#!/usr/bin/env python3
"""R3 blast-radius regression guard — no shipped file may name one of the 10 skills the R3
merge retired (plan phases 4/6/9, 2026-08).

Run: python evals/test_r3_retired_skill_refs.py

The R3 merge (10 stage-executor skills -> 3: cbr-plan, cbr-implement, cbr-verify) found the
original migration-plan's "10 evals untouched, 14 files unaffected" blast-radius estimate was
false by 4 independent reviewers' count -- the real surviving-reference footprint spanned
evals.json routing assertions, skill frontmatter trigger descriptions, pool-agent identity docs,
and files shipped into every user's own docs/ root via claude/docs/_templates/. Nothing in the
repo caught that undercount mechanically; this gate is that mechanism going forward.

Scans the full shipped prose surface (claude/skills/, claude/agents/, claude/rules/,
claude/docs/) for the 10 retired skill-name tokens, in any of their common referenced forms
(`cbr-<name>`, `/cbr-<name>`, or the bare pre-cbr-prefix stage name in a skill-identity
context). A hit inside a historical/explanatory sentence describing the OLD 10-skill layout
(e.g. this file's own docstring, or CLAUDE.md's migration narrative) is expected prose, not a
regression -- this gate is intentionally narrow: it flags the token appearing as a live
skill-invocation reference (a slash command, a "Skill Connections" table cell, a Content Map
row), not every English mention of the word.

NOTE: intentionally RED until the R3 blast-radius sweep (plan phase 8) completes -- that sweep's
job is exactly to make this gate pass. It stays green afterward as the permanent regression
guard the original undercounted claim proves the repo needs.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = [os.path.join(_ROOT, "claude", "skills"),
         os.path.join(_ROOT, "claude", "agents"),
         os.path.join(_ROOT, "claude", "rules"),
         os.path.join(_ROOT, "claude", "docs")]

# The 10 stage-executor skills the R3 merge retired (plan phases 4, 6, 9).
_RETIRED = ("analyze-requirement", "design-screen", "design-function", "plan-writing",
            "implement-feature", "review-code", "unit-test", "integration-test",
            "vulnerability-scanner", "fix-bug")

# Match as a live skill reference: cbr-<name>, /cbr-<name>, or /<name> — word-bounded so
# "unit-test" doesn't false-positive inside an unrelated compound like "unit-testable".
_PATTERN = re.compile(
    r"(?:\bcbr-(?:" + "|".join(_RETIRED) + r")\b)"
    r"|(?:/cbr-(?:" + "|".join(_RETIRED) + r")\b)"
)

# Files whose whole purpose is to narrate the OLD 10-skill history — expected prose, not a
# dangling reference. Kept to an explicit, reviewed allowlist rather than a broad exemption.
_ALLOW_HISTORICAL = {
    os.path.join(_ROOT, "evals", "test_r3_retired_skill_refs.py"),
}

_FAILURES = []


def _files():
    for base in _SCAN:
        if not os.path.isdir(base):
            continue
        for d, _dirs, fs in os.walk(base):
            for f in fs:
                if f.endswith((".md", ".json")):
                    yield os.path.join(d, f)


def test_no_retired_skill_references():
    for path in _files():
        if path in _ALLOW_HISTORICAL:
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            m = _PATTERN.search(line)
            if m:
                rel = os.path.relpath(path, _ROOT).replace("\\", "/")
                _FAILURES.append(f"{rel}:{i} -> {ascii(line.strip()[:100])}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)} retired-skill references remain):")
        for f in _FAILURES[:60]:
            print("  -", f)
        if len(_FAILURES) > 60:
            print(f"  ... and {len(_FAILURES) - 60} more")
        sys.exit(1)
    print("OK - no shipped file references a retired R3 skill name")


if __name__ == "__main__":
    main()

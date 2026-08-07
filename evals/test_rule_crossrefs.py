#!/usr/bin/env python3
"""Cross-reference integrity for the rules layer.

Every path-prefixed citation of a rule or reference file in claude/**/*.md must resolve to a
real file. This is the guard the repo lacked when the rules diet ran: deleting or renaming a
rule file could otherwise leave a dangling `rules/<x>.md` pointer or @-import (the class of bug
that shipped for real as work-log-template.md's "sdlc-conventions.md § Context Budget" citation).

Scope is the RULES LAYER only — the citations the rules diet could break:
  - `rules/<name>.md` / `rules/references/<name>.md` anywhere: claude-root-anchored cross-skill
    pointers into the rules layer. Always checked.
  - bare `references/<name>.md` inside a file that itself lives under claude/rules/: a rules-layer
    reference (e.g. the contract pointing at its own references/). Checked, citing-file-relative.
A bare `references/...` citation inside a SKILL file is that skill's own local convention (each
skill has its own references/ subdir) and is out of scope. Bare mentions with no prefix
(e.g. "the former coding-standards.md") are prose, not pointers, and are not checked.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "claude"
RULES = CLAUDE / "rules"

CITATION = re.compile(r"`((?:rules/|references/)[^`]+\.md)`")


def main() -> int:
    checked = 0
    failures = []
    for md in CLAUDE.rglob("*.md"):
        in_rules_layer = md.parent == RULES or RULES in md.parents
        for cit in CITATION.findall(md.read_text(encoding="utf-8")):
            if cit.startswith("rules/"):
                target = CLAUDE / cit
            elif in_rules_layer:
                target = md.parent / cit  # rules-layer reference, citing-file-relative
            else:
                continue  # skill-local references/ citation — out of scope
            checked += 1
            if not target.is_file():
                shown = target.relative_to(ROOT) if ROOT in target.parents else target
                failures.append(f"{md.relative_to(ROOT)} -> `{cit}` (not found at {shown})")

    if failures:
        print(f"FAIL - {len(failures)} dangling rule citation(s) of {checked} checked:")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"OK - all {checked} rule/reference citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())

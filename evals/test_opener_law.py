#!/usr/bin/env python3
"""Structural gate: every stream-opener skill resolves the stream by topic-slug
(open-if-none / join-if-exists) and NONE uses resolve_active_feature() as the join
mechanism (it is topic-blind + not callable from a prose skill).

Guards red-team findings F1/F2/F11 against prose drift: the no-double-open invariant is
behavioral, so it needs a mechanical gate the way test_canonical_paths.py guards paths.
Run: python evals/test_opener_law.py
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPENERS = [
    "claude/skills/cbr-brainstorming/SKILL.md",
    "claude/skills/cbr-explore/SKILL.md",
    "claude/skills/cbr-plan-writing/SKILL.md",
]

fail = []
for rel in OPENERS:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    low = text.lower()

    # 1. Must describe the topic-slug stream lookup (glob docs/streams/* + a slug).
    if "slug" not in low or ("glob" not in low and "docs/streams/*" not in text):
        fail.append(f"{rel}: no topic-slug stream lookup (glob docs/streams/* + slug) found")

    # 2. Must carry both an open and a join branch (open-if-none / join-if-exists).
    if "join" not in low or "open" not in low:
        fail.append(f"{rel}: missing open/join branch language")

    # 3. Must NOT prescribe resolve_active_feature() as the mechanism. Any mention is
    #    allowed only inside a negation ("not"/"never"/"do not use it").
    for m in re.finditer(r"[^\n]*resolve_active_feature[^\n]*", text):
        line = m.group(0).lower()
        if "not" not in line and "never" not in line:
            fail.append(
                f"{rel}: resolve_active_feature() referenced as the mechanism "
                f"(must be a topic-slug lookup): {m.group(0).strip()[:90]}"
            )

if fail:
    print("FAIL - stream-opener open-or-join law drift:")
    for f in fail:
        print("  -", f)
    sys.exit(1)

print(f"OK - {len(OPENERS)} openers resolve the stream by topic-slug (open-if-none / join-if-exists)")

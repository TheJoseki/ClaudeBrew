#!/usr/bin/env python3
"""English-only gate for shipped skill prose (ported from clawform's english-docs test).

Run: python evals/test_english_docs.py

The cbr suite was imported from a Japanese/Chinese-influenced codebase, and CJK terms
kept creeping into SKILL.md / references / rules / templates (e.g. `BD書`, `基本設計書`,
`包豪斯`). This asserts the shipped markdown prose stays English-only — CJK
(Han / Hiragana / Katakana / fullwidth forms) is treated as a language leak.

Scope is `*.md` under `plugins/cbr/` — the instructions the model actually reads. Data
corpora under `skills/*/data/*.csv` are intentionally out of scope: a design/font corpus
may legitimately name CJK typefaces or scripts, and flagging those would be a false alarm.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PLUGIN = os.path.join(_ROOT, "plugins", "cbr")
# Hiragana + Katakana + CJK ideographs + CJK fullwidth/halfwidth forms.
_CJK = re.compile("[぀-ヿ㐀-鿿＀-￯]")
_FAILURES = []


def _md_files():
    for base, _dirs, files in os.walk(_PLUGIN):
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(base, name)


def test_no_cjk_in_shipped_markdown():
    for path in _md_files():
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if _CJK.search(line):
                rel = os.path.relpath(path, _ROOT).replace("\\", "/")
                # ascii() escapes the CJK to \uXXXX so the report prints on any console
                # (Windows cp1252 stdout raises UnicodeEncodeError on raw CJK).
                _FAILURES.append(f"{rel}:{i} CJK -> {ascii(line.strip()[:80])}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)}):")
        for f in _FAILURES[:40]:
            print("  -", f)
        sys.exit(1)
    print("OK — shipped markdown is English-only (no CJK)")


if __name__ == "__main__":
    main()

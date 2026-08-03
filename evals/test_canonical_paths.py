#!/usr/bin/env python3
"""Canonical-paths gate — every SDLC artifact path a skill references must be stream-first.

Run: python evals/test_canonical_paths.py

Since the canonical layout (design-260803-1649), the home for every per-feature artifact is
`docs/streams/<slug>-<YYYYMMDD>/<subdir>/<TYPE>.<ext>`. The old type-first dirs (`docs/specs/`,
`docs/reviews/`, `docs/plans/`, `docs/work-logs/`, …) are retired. This gate FAILS if any shipped
skill/agent prose still references a retired type-first path — so the layout is enforced, not merely
documented (sibling of the `release-docs` / `english-docs` gates).

Allowed `docs/` roots: `docs/streams/` (canonical per-feature), `docs/decisions/` + `docs/risks/`
(project-wide), `docs/_templates/`, and bare project reference files (`docs/PROJECT.md`, …). Scoped to
`plugins/cbr/skills/` + `plugins/cbr/agents/` prose (SKILL.md, references/*.md, evals/*.json). Rules are
governance authored directly and are checked by hand during the migration.

NOTE: this gate is RED-by-design until the skill migration (plan phase 03) completes — that is its job:
its output IS the migration work-queue. It goes green only when the last skill drops the last type-first path.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = [os.path.join(_ROOT, "plugins", "cbr", "skills"),
         os.path.join(_ROOT, "plugins", "cbr", "agents")]

# Retired type-first per-feature artifact dirs (now under docs/streams/<id>/…).
_RETIRED = re.compile(
    r"docs/(?:specs|reviews|plans|work-logs|security|test-reports|test-cases|"
    r"bug-reports|retros|handoffs|estimates|dars|cars)/"
)
_FAILURES = []


def _files():
    for base in _SCAN:
        for d, _dirs, fs in os.walk(base):
            for f in fs:
                if f.endswith((".md", ".json")):
                    yield os.path.join(d, f)


def test_no_type_first_paths_in_skills():
    for path in _files():
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if _RETIRED.search(line):
                rel = os.path.relpath(path, _ROOT).replace("\\", "/")
                # ascii() escapes any non-ASCII (e.g. checkmarks) so the report prints on
                # Windows cp1252 stdout without UnicodeEncodeError.
                _FAILURES.append(f"{rel}:{i} -> {ascii(line.strip()[:90])}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)} type-first references remain):")
        for f in _FAILURES[:60]:
            print("  -", f)
        if len(_FAILURES) > 60:
            print(f"  ... and {len(_FAILURES) - 60} more")
        sys.exit(1)
    print("OK — all skill/agent artifact paths are stream-canonical")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Release-docs gate — fails when a version bump leaves the release docs stale.

Run: python evals/test_release_docs.py

Ported from clawform's tests/packaging/* (version-sync / english-docs): the lesson
is that CHANGELOG, CLAUDE.md and README drift silently across releases unless a
test forces the touch. This is a *touch-forcing* gate, not a semantic-freshness
one — it cannot prove the prose is current, but it makes bumping the version
without opening each doc mechanically impossible:

  - `plugin.json` version is plain semver;
  - CHANGELOG.md has a `## [<version>]` section (forces release notes on a bump);
  - CLAUDE.md and README each carry `<!-- release: <version> -->` equal to it
    (a version bump changes the required anchor -> forces opening both files);
  - README carries the install invariants and none of the statements a past
    release already made false;
  - the marketplace entry pins no version (cbr single-sources it in plugin.json).

Exit non-zero if any check fails.
"""
import json
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FAILURES = []


def check(cond, msg):
    if not cond:
        _FAILURES.append(msg)


def read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def version():
    return json.loads(read("plugins/cbr/.claude-plugin/plugin.json"))["version"]


def test_version_is_semver():
    v = version()
    check(re.match(r"^\d+\.\d+\.\d+$", v) is not None, f"version not plain semver: {v!r}")


def test_changelog_has_current_version():
    v = version()
    check(f"## [{v}]" in read("CHANGELOG.md"),
          f"CHANGELOG.md has no '## [{v}]' section — add release notes when bumping the version")


def test_release_anchor_in_claude_md():
    v = version()
    check(f"<!-- release: {v} -->" in read("CLAUDE.md"),
          f"CLAUDE.md missing '<!-- release: {v} -->' — review it for this release, then update the anchor")


def test_release_anchor_in_readme():
    v = version()
    check(f"<!-- release: {v} -->" in read("README.md"),
          f"README.md missing '<!-- release: {v} -->' — review it for this release, then update the anchor")


def test_readme_install_invariants():
    r = read("README.md")
    check("/plugin marketplace add" in r and "/plugin install cbr@" in r and "/cbr:setup" in r,
          "README lost an install step (marketplace add / plugin install / cbr:setup)")


def test_readme_no_stale_claims():
    r = read("README.md")
    check("remaining stages are in progress" not in r,
          "README still claims 'remaining stages are in progress' — the single-layer suite shipped")
    check("docs/specs/YYYY-MM-DD-" not in r,
          "README uses the old artifact-path scheme — see the canonical table in sdlc-conventions.md")


def test_marketplace_pins_no_version():
    mp = read(os.path.join(".claude-plugin", "marketplace.json"))
    check('"version"' not in mp,
          "marketplace.json must not pin a version — single-source it in plugins/cbr/.claude-plugin/plugin.json")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)}):")
        for f in _FAILURES:
            print("  -", f)
        sys.exit(1)
    print(f"OK — {len(tests)} release-docs checks passed")


if __name__ == "__main__":
    main()

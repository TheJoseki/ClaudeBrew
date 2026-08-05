#!/usr/bin/env python3
"""Release-docs gate — fails when a version bump leaves the release docs stale.

Run: python evals/test_release_docs.py

A *touch-forcing* gate (not a semantic-freshness one): it cannot prove the prose is
current, but it makes bumping the version without opening each doc mechanically
impossible.

  - package.json version is plain semver (the single source of truth since the
    re-platform retired plugin.json);
  - CHANGELOG.md has a `## [<version>]` section (forces release notes on a bump);
  - CLAUDE.md and README each carry `<!-- release: <version> -->` equal to it
    (a version bump changes the required anchor -> forces opening both files);
  - README describes the `npx claudebrew` install flow and none of the plugin-era
    statements a past release already made false.

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
    return json.loads(read("package.json"))["version"]


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
    check("npx claudebrew install" in r,
          "README lost the install command (`npx claudebrew install`)")
    check("claudebrew update" in r and "claudebrew uninstall" in r,
          "README must document `claudebrew update` and `claudebrew uninstall`")


def test_readme_no_plugin_era_claims():
    r = read("README.md")
    check("/plugin marketplace" not in r and "cbr@claudebrew" not in r,
          "README still describes the retired plugin/marketplace install flow")
    check("/cbr:setup" not in r,
          "README still references /cbr:setup — its job moved into the installer")
    check("remaining stages are in progress" not in r,
          "README still claims 'remaining stages are in progress' — the single-layer suite shipped")


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
    print(f"OK - {len(tests)} release-docs checks passed")


if __name__ == "__main__":
    main()

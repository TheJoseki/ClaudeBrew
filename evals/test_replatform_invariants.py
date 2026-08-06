#!/usr/bin/env python3
"""Re-platform structural gate — the invariants the plugin->npm-installer move must hold.

Run: python evals/test_replatform_invariants.py

Deterministic scans over the shipped payload (`claude/`). These encode decisions from
the re-platform so a later edit can't silently reintroduce a plugin-ism:

  - ZERO `${CLAUDE_PLUGIN_ROOT}` — the plugin path idiom is retired (two-tier resolution).
  - The residual manifest lives in-band: the payload CARRIES `{{CBR_ROOT}}` tokens on
    residual refs (a positive marker; the installed-tree 0-token check is behavioral).
  - ZERO `.sh` under `claude/hooks/` — every hook is Python (D-1, Python is the sole prereq).
  - ZERO `cbr:` (colon) namespace refs — skills/agents are authored `cbr-<name>`.
  - ZERO `*.cbrtmp` in the payload — that suffix is the installer's staging marker; a
    payload file using it would be clobbered mid-install.
  - ZERO bare `docs/_templates/` *source* refs — every source ref is `{{CBR_ROOT}}`-tokenized
    (the seeding gap fix). Destinations (`docs/<NAME>`) are fine.

Exit non-zero if any invariant is violated.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CLAUDE = os.path.join(_ROOT, "claude")
_HOOKS = os.path.join(_CLAUDE, "hooks")
_FAILURES = []


def _text_files():
    for d, _dirs, fs in os.walk(_CLAUDE):
        for f in fs:
            if f.endswith((".md", ".json", ".py", ".txt")):
                yield os.path.join(d, f)


def _grep(pattern):
    rx = re.compile(pattern)
    hits = []
    for path in _text_files():
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for i, line in enumerate(fh, 1):
                    if rx.search(line):
                        hits.append(f"{os.path.relpath(path, _ROOT)}:{i}")
        except OSError:
            continue
    return hits


def check(cond, msg):
    if not cond:
        _FAILURES.append(msg)


def test_no_plugin_root():
    hits = _grep(r"CLAUDE_PLUGIN_ROOT")
    check(not hits, f"{len(hits)} ${{CLAUDE_PLUGIN_ROOT}} refs remain (e.g. {hits[:3]})")


def test_payload_carries_tokens():
    hits = _grep(r"\{\{CBR_ROOT\}\}")
    check(len(hits) > 0, "payload carries NO {{CBR_ROOT}} tokens — residual refs would resolve nowhere")


def test_no_sh_hooks():
    sh = [f for f in os.listdir(_HOOKS) if f.endswith(".sh")]
    check(not sh, f".sh hooks remain under claude/hooks/: {sh} (D-1: Python-only)")


def test_no_colon_namespace():
    hits = _grep(r"cbr:")
    check(not hits, f"{len(hits)} cbr: (colon) namespace refs remain (e.g. {hits[:3]}) — author cbr-<name>")


def test_no_staging_suffix_in_payload():
    hits = [os.path.relpath(os.path.join(d, f), _ROOT)
            for d, _dirs, fs in os.walk(_CLAUDE) for f in fs if f.endswith(".cbrtmp")]
    check(not hits, f"payload contains staging-suffixed files: {hits}")


def test_no_bare_template_source():
    # A `docs/_templates/` occurrence is a bare source unless it is the tail of the
    # tokenized form `{{CBR_ROOT}}/docs/_templates/`. Count-difference avoids any
    # lookbehind-width pitfalls with the 13-char token.
    hits = []
    for path in _text_files():
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for i, line in enumerate(fh, 1):
                    bare = line.count("docs/_templates/") - line.count("{{CBR_ROOT}}/docs/_templates/")
                    if bare > 0:
                        hits.append(f"{os.path.relpath(path, _ROOT)}:{i}")
        except OSError:
            continue
    check(not hits, f"{len(hits)} bare docs/_templates/ source refs (e.g. {hits[:3]}) — tokenize the source")


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
    print(f"OK - {len(tests)} re-platform invariants hold")


if __name__ == "__main__":
    main()

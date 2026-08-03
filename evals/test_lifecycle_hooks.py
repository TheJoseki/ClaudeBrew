#!/usr/bin/env python3
"""Durable tests for session-init.py + subagent-context.py.

Run: python evals/test_lifecycle_hooks.py

Hooks have hyphenated filenames, so they're loaded IN-PROCESS via importlib (so
`coverage` instruments them). main() is exercised with patched stdin/env; render
helpers and cache I/O are called directly. Exit non-zero if any case fails.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

_HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "cbr", "hooks",
)
sys.path.insert(0, os.path.join(_HOOKS, "lib"))
import sdlc_state as S  # noqa: E402


def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HOOKS, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # __main__-guarded: does not run main()
    return mod


SI = _load("session_init_hook", "session-init.py")
SC = _load("subagent_context_hook", "subagent-context.py")

_FAILURES = []


def check(cond, msg):
    if not cond:
        _FAILURES.append(msg)


def write(root, relpath, content=""):
    full = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    return full


def run_main(mod, stdin_str="{}", project_dir=None, use_env=True):
    """Invoke mod.main() with patched stdin + CLAUDE_PROJECT_DIR; return stdout."""
    old_stdin = sys.stdin
    old_env = os.environ.get("CLAUDE_PROJECT_DIR")
    sys.stdin = io.StringIO(stdin_str)
    if project_dir and use_env:
        os.environ["CLAUDE_PROJECT_DIR"] = project_dir
    elif not use_env:
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            try:
                mod.main()
            except SystemExit:
                pass
    finally:
        sys.stdin = old_stdin
        if old_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = old_env
    return buf.getvalue()


def active_plan_tree(d, slug="payment", with_specs=True):
    # Canonical stream tree: an in-flight stream (gates not all-pass) is the active feature.
    write(d, f"docs/streams/{slug}-20260801/STREAM.md", "---\nstatus: in-progress\n---\n")
    write(d, f"docs/streams/{slug}-20260801/plan/PLAN.md", "# Plan\n")
    if with_specs:
        write(d, f"docs/streams/{slug}-20260801/requirements/SRS.md", "# S\n## Scope\nx\n")
        write(d, f"docs/streams/{slug}-20260801/design/TECH.md", "# T\n## Methods\na\n## DTO\nb\n")


# --- session-init render --------------------------------------------------- #
def test_si_render_ambiguity():
    out = SI.render(None, ["a", "b"], None, None)
    check("2 features in flight" in out and "a, b" in out, out)


def test_si_render_none():
    check(SI.render(None, [], None, None) == "", "no slug -> ''")


def test_si_render_full():
    out = SI.render("payment", [], {"gate_line": "GL", "next_action": "/cbr:review-code payment"},
                    "docs/handoffs/HANDOFF-payment-20260801.md")
    check("cbr SDLC state" in out and "Next:" in out and "Full state:" in out, out)


def test_si_render_no_next_no_handoff():
    out = SI.render("payment", [], {"gate_line": "GL", "next_action": None}, None)
    check("Next:" not in out and "Full state:" not in out, out)


def test_si_render_with_stream():
    out = SI.render("payment", [], {"gate_line": "GL", "next_action": None}, None,
                    stream="docs/streams/payment-20260801/STREAM.md")
    check("Stream board:" in out and "STREAM.md" in out, out)


def test_si_main_includes_stream():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d)
        write(d, "docs/streams/payment-20260801/STREAM.md", "# Stream\n")
        out = run_main(SI, "{}", d)
        check("Stream board:" in out and "STREAM.md" in out, f"stdout={out!r}")


# --- session-init main + cache --------------------------------------------- #
def test_si_main_writes_cache_and_prints():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d)
        out = run_main(SI, "{}", d)
        check("cbr SDLC state" in out, f"stdout={out!r}")
        cache = os.path.join(d, ".claude", "sdlc-index.json")
        check(os.path.isfile(cache), "cache written")
        idx = json.load(open(cache, encoding="utf-8"))
        check(idx["activeFeature"] == "payment", str(idx.get("activeFeature")))


def test_si_main_empty_docs_silent():
    with tempfile.TemporaryDirectory() as d:
        out = run_main(SI, "{}", d)
        check(out.strip() == "", f"expected silence, got {out!r}")
        idx = json.load(open(os.path.join(d, ".claude", "sdlc-index.json"), encoding="utf-8"))
        check(idx["activeFeature"] is None, str(idx))


def test_si_main_cwd_fallback():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d, with_specs=False)
        out = run_main(SI, json.dumps({"cwd": d}), project_dir=None, use_env=False)
        check("cbr SDLC state" in out, f"cwd-fallback stdout={out!r}")


def test_si_main_bad_stdin():
    with tempfile.TemporaryDirectory() as d:
        out = run_main(SI, "{not json", d)  # must not crash
        check(isinstance(out, str), "bad stdin handled")


def test_si_write_cache_oserror():
    with tempfile.TemporaryDirectory() as d:
        # .claude exists as a FILE -> makedirs raises -> write_cache returns None
        with open(os.path.join(d, ".claude"), "w") as fh:
            fh.write("x")
        check(SI.write_cache(d, {"a": 1}) is None, "OSError -> None")


def test_si_main_exception_failopen():
    saved = S.resolve_active_feature
    S.resolve_active_feature = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        with tempfile.TemporaryDirectory() as d:
            out = run_main(SI, "{}", d)  # exception caught -> exit 0
            check(out.strip() == "", "exception path prints nothing")
    finally:
        S.resolve_active_feature = saved


# --- session-init compaction path ------------------------------------------ #
def test_si_read_checkpoint():
    with tempfile.TemporaryDirectory() as d:
        check(SI.read_checkpoint(d) == "", "no checkpoint -> ''")
        write(d, ".claude/compact-checkpoint.md", "## Pre-Compact\n- plan: X\n")
        check("Pre-Compact" in SI.read_checkpoint(d), "reads checkpoint")


def test_si_read_project_sections():
    with tempfile.TemporaryDirectory() as d:
        check(SI.read_project_sections(d) == "", "no PROJECT.md -> ''")
        write(d, "PROJECT.md",
              "# P\n## Tech Stack\nPython\n## Other\nignored\n## Build Commands\nmake\n")
        out = SI.read_project_sections(d)
        check("Python" in out and "make" in out and "ignored" not in out, out)


def test_si_render_compact_full():
    with tempfile.TemporaryDirectory() as d:
        write(d, ".claude/compact-checkpoint.md", "checkpoint-body")
        write(d, "PROJECT.md", "## Tech Stack\nGo\n")
        out = SI.render_compact(d, "payment", [],
                                {"gate_line": "GL", "next_action": None}, None)
        check("checkpoint-body" in out and "Tech Stack" in out
              and "compacted" in out.lower(), out)


def test_si_render_compact_minimal():
    with tempfile.TemporaryDirectory() as d:
        out = SI.render_compact(d, None, [], None, None)
        check("compacted" in out.lower(), out)  # just the approval-gate warning


def test_si_main_compact_source():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d)
        write(d, ".claude/compact-checkpoint.md", "was-editing-payment")
        out = run_main(SI, json.dumps({"source": "compact"}), d)
        check("was-editing-payment" in out and "compacted" in out.lower(),
              f"compact stdout={out!r}")


# --- subagent-context render ----------------------------------------------- #
def _feature():
    return {
        "gates": {"G4": "pending"},
        "nextAction": "/cbr:review-code payment",
        "artifacts": [
            {"type": "TECH", "path": "docs/streams/payment-20260801/design/TECH.md",
             "sections": [{"title": "Methods", "lines": "3-5"}]},
        ],
    }


def test_sc_render_reviewer():
    out = SC.render("reviewer", "payment", _feature())
    check("Next gate action" in out and "VERDICT-G" in out and "sections:" in out, out)


def test_sc_render_explore_minimal():
    out = SC.render("Explore", "payment", _feature())
    check("VERDICT" not in out and "cbr active feature: payment" in out, out)


def test_sc_render_no_feature():
    out = SC.render("reviewer", "payment", None)
    check("VERDICT" not in out and "cbr active feature: payment" in out, out)


def test_sc_render_slug_none():
    check("cbr active feature: none" in SC.render("Explore", None, None), "none slug")


# --- subagent-context cache/glob ------------------------------------------- #
def test_sc_load_cache_edges():
    with tempfile.TemporaryDirectory() as d:
        check(SC.load_cache(d) is None, "missing -> None")
        write(d, ".claude/sdlc-index.json", "{bad")
        check(SC.load_cache(d) is None, "malformed -> None")
        write(d, ".claude/sdlc-index.json", '{"activeFeature":"x"}')
        check(SC.load_cache(d)["activeFeature"] == "x", "valid -> dict")


def test_sc_feature_state_from_cache():
    with tempfile.TemporaryDirectory() as d:
        write(d, ".claude/sdlc-index.json",
              json.dumps({"activeFeature": "payment", "features": {"payment": {"gates": {}}}}))
        slug, feat = SC.feature_state(d)
        check(slug == "payment" and feat == {"gates": {}}, f"{slug!r},{feat!r}")


def test_sc_feature_state_glob_fallback():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d)  # no cache present
        slug, feat = SC.feature_state(d)
        check(slug == "payment" and feat is not None, f"glob fallback {slug!r}")


def test_sc_feature_state_none():
    with tempfile.TemporaryDirectory() as d:
        check(SC.feature_state(d) == (None, None), "no cache no docs -> (None,None)")


def test_sc_main_emits_json_reviewer():
    with tempfile.TemporaryDirectory() as d:
        active_plan_tree(d)
        run_main(SI, "{}", d)  # build cache first
        out = run_main(SC, json.dumps({"agent_type": "reviewer"}), d)
        obj = json.loads(out)
        check(obj["hookSpecificOutput"]["hookEventName"] == "SubagentStart", out)
        check("cbr active feature: payment" in obj["hookSpecificOutput"]["additionalContext"], out)


def test_sc_main_bad_stdin_still_emits():
    with tempfile.TemporaryDirectory() as d:
        out = run_main(SC, "{not json", d)
        obj = json.loads(out)
        check(obj["hookSpecificOutput"]["hookEventName"] == "SubagentStart", out)


def test_sc_main_exception_failopen():
    saved = S.resolve_active_feature
    S.resolve_active_feature = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        with tempfile.TemporaryDirectory() as d:  # no cache -> hits glob authority -> raises
            out = run_main(SC, json.dumps({"agent_type": "reviewer"}), d)
            obj = json.loads(out)
            check(obj["hookSpecificOutput"]["additionalContext"] == "", "exception -> empty context")
    finally:
        S.resolve_active_feature = saved


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
    print(f"OK — {len(tests)} lifecycle-hook tests passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Durable tests for hooks/lib/sdlc_state.py — run: python evals/test_sdlc_state.py

Pure-function tests over throwaway canonical stream trees (docs/streams/<slug>-<date>/…)
in a tempdir. mtimes are set explicitly where "most-recently-modified" matters. Exit
non-zero if any case fails.
"""
import os
import sys
import tempfile

_LIB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins", "cbr", "hooks", "lib",
)
sys.path.insert(0, _LIB)
import sdlc_state as S  # noqa: E402

_FAILURES = []


def check(cond, msg):
    if not cond:
        _FAILURES.append(msg)


def write(root, relpath, content="", mtime=None):
    """Create root/relpath with content; optionally pin its mtime (epoch seconds)."""
    full = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    if mtime is not None:
        os.utime(full, (mtime, mtime))
    return full


def sd(slug, date="20260801"):
    """Return the canonical stream-relative prefix docs/streams/<slug>-<date>."""
    return f"docs/streams/{slug}-{date}"


# --- slug_from_filename (kept for the type-first migrator) ------------------- #
def test_slug_from_filename():
    cases = {
        "SRS-payment.md": "payment",
        "TECH-user-auth.md": "user-auth",
        "PLAN-user-auth-20260801.md": "user-auth",
        "VERDICT-payment-G4.json": "payment",
        "VERDICT-payment-B2-G4.json": "payment",
        "DEV-payment-B2.md": "payment",
        "UTR-payment-R3.md": "payment",
        "README.md": None,        # no hyphen
        "foo-bar.md": None,       # prefix not uppercase
    }
    for name, want in cases.items():
        got = S.slug_from_filename(name)
        check(got == want, f"slug_from_filename({name!r}) = {got!r}, want {want!r}")


def test_slug_from_stream_dir():
    check(S.slug_from_stream_dir("docs/streams/payment-20260801") == "payment", "simple slug")
    check(S.slug_from_stream_dir("user-auth-20260801") == "user-auth", "hyphenated slug")
    check(S.slug_from_stream_dir("no-date-here") is None, "no date -> None")


# --- resolve_active_feature (derived from streams) -------------------------- #
def test_resolve_active_single():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")  # G1 pass, rest pending -> in-flight
        slug, amb = S.resolve_active_feature(d)
        check(slug == "payment" and amb == [], f"single in-flight -> {slug!r},{amb!r}")


def test_resolve_active_multiple():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('search')}/requirements/SRS.md", "x")
        slug, amb = S.resolve_active_feature(d)
        check(slug is None and set(amb) == {"payment", "search"}, f"multi in-flight -> {slug!r},{amb!r}")


def test_resolve_skips_archived():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")            # in-flight
        write(d, f"{sd('old', '20260101')}/requirements/SRS.md", "x")   # also in-flight, but...
        write(d, f"{sd('old', '20260101')}/STREAM.md", "---\nstatus: archived\n---\n")
        slug, amb = S.resolve_active_feature(d)
        check(slug == "payment" and amb == [], f"archived excluded -> {slug!r},{amb!r}")


def test_resolve_skips_done():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('live')}/requirements/SRS.md", "x")              # in-flight
        done = sd("done")                                              # all gates pass -> excluded
        write(d, f"{done}/requirements/SRS.md", "x")
        write(d, f"{done}/design/TECH.md", "x")
        write(d, f"{done}/reviews/VERDICT-G4.json", '{"decision":"PASS"}')
        write(d, f"{done}/security/VERDICT-G5a.json", '{"decision":"PASS"}')
        write(d, f"{done}/test-reports/VERDICT-G6.json", '{"decision":"PASS"}')
        write(d, f"{done}/test-reports/VERDICT-G7.json", '{"decision":"PASS"}')
        slug, amb = S.resolve_active_feature(d)
        check(slug == "live" and amb == [], f"all-pass excluded -> {slug!r},{amb!r}")


def test_resolve_empty():
    with tempfile.TemporaryDirectory() as d:
        slug, amb = S.resolve_active_feature(d)
        check(slug is None and amb == [], f"empty -> {slug!r},{amb!r}")


# --- infer_gate_progress ---------------------------------------------------- #
def test_infer_gates_empty():
    with tempfile.TemporaryDirectory() as d:
        p = S.infer_gate_progress(d, "payment")  # no stream folder -> all pending
        check(all(v == "pending" for v in p["gates"].values()), f"all pending: {p['gates']}")
        check(p["next_action"] == "/cbr:analyze-requirement payment", p["next_action"])
        check("G1 pending" in p["gate_line"], p["gate_line"])


def test_infer_gates_srs_tech():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["G1"] == "pass" and p["gates"]["G3"] == "pass", str(p["gates"]))
        check(p["next_action"] == "/cbr:review-code payment", p["next_action"])


def test_infer_gates_verdict_pass():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        write(d, f"{sd('payment')}/reviews/VERDICT-G4.json", '{"decision":"PASS"}')
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["G4"] == "pass", str(p["gates"]))
        check(p["next_action"] == "/cbr:vulnerability-scanner payment", p["next_action"])


def test_infer_gates_verdict_fail_routes_fixbug():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        write(d, f"{sd('payment')}/reviews/VERDICT-G4.json", '{"decision":"FAIL"}')
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["G4"] == "fail", str(p["gates"]))
        check(p["next_action"] == "/cbr:fix-bug payment", p["next_action"])


def test_stream_dir_no_prefix_collision():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")             # payment: G1 pass, G3 pending
        exp = sd("payment-export", "20260803")                           # newer, shares the prefix
        write(d, f"{exp}/requirements/SRS.md", "x")
        write(d, f"{exp}/design/TECH.md", "x")                            # export HAS TECH -> would be G3 pass
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["G3"] == "pending",
              f"'payment' must NOT read payment-export's TECH (prefix collision): {p['gates']}")


def test_gate_verdict_partial_and_batch():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/reviews/VERDICT-B1-G4.json", '{"decision":"PASS"}')
        write(d, f"{sd('payment')}/reviews/VERDICT-B2-G4.json", '{"decision":"pending"}')
        got = S._gate_verdict(d, "payment", "G4")
        check(got == "partial", f"partial -> {got!r}")


def test_verdict_decision_edges():
    with tempfile.TemporaryDirectory() as d:
        bad = write(d, "vbad.json", "{not json")
        check(S._verdict_decision(bad) is None, "malformed json -> None")
        nodec = write(d, "vnodec.json", '{"foo":1}')
        check(S._verdict_decision(nodec) is None, "missing decision -> None")
        check(S._verdict_decision(os.path.join(d, "nope.json")) is None, "missing file -> None")


def test_read_head_oserror():
    with tempfile.TemporaryDirectory() as d:
        check(S._read_head(d) == "", "_read_head on a dir -> ''")


def test_extract_sections():
    body = "# Title\nintro\n## A\nline\nline\n### A.1\nx\n## B\ny\n"
    with tempfile.TemporaryDirectory() as d:
        p = write(d, f"{sd('payment')}/design/TECH.md", body)
        secs = S.extract_sections(p)
        titles = [s["title"] for s in secs]
        check(titles == ["A", "A.1", "B"], f"titles={titles}")
        check(secs[0]["lines"] == "3-5", f"A lines={secs[0]['lines']}")
        check(secs[-1]["lines"].endswith(str(body.count(chr(10)))), f"B lines={secs[-1]['lines']}")


def test_extract_sections_none():
    with tempfile.TemporaryDirectory() as d:
        p = write(d, "x.md", "no headers here\njust text\n")
        check(S.extract_sections(p) == [], "no headers -> []")
        check(S.extract_sections(os.path.join(d, "missing.md")) == [], "missing -> []")


# --- find_latest_handoff (stream-scoped) ------------------------------------ #
def test_find_latest_handoff():
    with tempfile.TemporaryDirectory() as d:
        check(S.find_latest_handoff(d, "payment") is None, "no handoff -> None")
        write(d, f"{sd('payment')}/handoffs/HANDOFF-20260801.md", "x", mtime=1_000_000)
        write(d, f"{sd('payment')}/handoffs/HANDOFF-20260802.md", "x", mtime=2_000_000)
        got = S.find_latest_handoff(d, "payment")
        check(got == f"{sd('payment')}/handoffs/HANDOFF-20260802.md", f"newest -> {got!r}")
        check("\\" not in got, "forward slashes only")


def test_find_stream_manifest():
    with tempfile.TemporaryDirectory() as d:
        check(S.find_stream_manifest(d, "payment") is None, "no manifest -> None")
        check(S.find_stream_manifest(d, None) is None, "no slug -> None")
        write(d, "docs/streams/payment-20260801/STREAM.md", "x", mtime=1_000_000)
        write(d, "docs/streams/payment-20260803/STREAM.md", "x", mtime=2_000_000)
        got = S.find_stream_manifest(d, "payment")
        check(got == "docs/streams/payment-20260803/STREAM.md", f"newest -> {got!r}")
        check("\\" not in got, "forward slashes only")


# --- build_index ------------------------------------------------------------ #
def test_build_index_no_slug():
    with tempfile.TemporaryDirectory() as d:
        idx = S.build_index(d, None)
        check(idx["activeFeature"] is None and idx["features"] == {}, str(idx))


def test_build_index_with_feature():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "# S\n## Scope\nx\n")
        write(d, f"{sd('payment')}/design/TECH.md", "# T\n## Methods\nx\n## DTO\ny\n")
        write(d, f"{sd('payment')}/reviews/VERDICT-G4.json", '{"decision":"pass"}')
        idx = S.build_index(d, "payment", now="2026-08-02T00:00:00Z")
        feat = idx["features"]["payment"]
        check(idx["generatedAt"] == "2026-08-02T00:00:00Z", "now stamped")
        check(feat["gates"]["G4"] == "pass", str(feat["gates"]))
        types = {a["type"] for a in feat["artifacts"]}
        check({"SRS", "TECH", "VERDICT-G4"} <= types, f"types={types}")
        tech = next(a for a in feat["artifacts"] if a["type"] == "TECH")
        check(len(tech["sections"]) == 2, f"TECH sections={tech['sections']}")
        verdict = next(a for a in feat["artifacts"] if a["type"] == "VERDICT-G4")
        check(verdict["decision"] == "pass", str(verdict))


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except Exception as exc:  # a test crashing is a failure
            _FAILURES.append(f"{t.__name__} raised {exc!r}")
    if _FAILURES:
        print(f"FAIL ({len(_FAILURES)}):")
        for f in _FAILURES:
            print("  -", f)
        sys.exit(1)
    print(f"OK — {len(tests)} sdlc_state tests passed")


if __name__ == "__main__":
    main()

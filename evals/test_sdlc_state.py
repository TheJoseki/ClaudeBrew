#!/usr/bin/env python3
"""Durable tests for hooks/lib/sdlc_state.py — run: python evals/test_sdlc_state.py

Pure-function tests over throwaway canonical stream trees (docs/streams/<slug>-<date>/…)
in a tempdir. mtimes are set explicitly where "most-recently-modified" matters. Exit
non-zero if any case fails.
"""
import os
import sys
import tempfile
import time

_LIB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "claude", "hooks", "lib",
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


def test_slug_from_stream_dir():
    check(S.slug_from_stream_dir("docs/streams/payment-20260801") == "payment", "simple slug")
    check(S.slug_from_stream_dir("user-auth-20260801") == "user-auth", "hyphenated slug")
    check(S.slug_from_stream_dir("no-date-here") is None, "no date -> None")


# --- resolve_active_feature (derived from STREAM.md status: only — R2) ------ #
def test_resolve_active_single():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")  # any un-closed stream -> in-flight
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


def test_resolve_skips_status_done():
    """The headline R2 fix: completion is authored, never inferred. A stream-light
    stream with ZERO artifacts (no SRS, no TECH, no verdicts -- the shape that could
    never satisfy the old all-pass predicate) closes the instant `status: done` is
    stamped. This reproduces the today-bug and proves it fixed.
    """
    with tempfile.TemporaryDirectory() as d:
        stream = sd("maint-fix")
        write(d, f"{stream}/STREAM.md", "---\nstatus: pending\nlane: brownfield\n---\n")
        slug, amb = S.resolve_active_feature(d)
        check(slug == "maint-fix" and amb == [], f"pending stream-light still in-flight -> {slug!r},{amb!r}")

        write(d, f"{stream}/STREAM.md", "---\nstatus: done\nlane: brownfield\n---\n")
        slug, amb = S.resolve_active_feature(d)
        check(slug is None and amb == [], f"status:done closes a stream-light stream with NO artifacts -> {slug!r},{amb!r}")


def test_resolve_allpass_without_status_stays_open():
    """R2 design doc dry-run shape A': a stream with every checkpoint verdict PASS
    but no authored `status:` stays in-flight -- the accepted migration trade-off
    (opt-in closure over inference). This is intentional, not a regression.
    """
    with tempfile.TemporaryDirectory() as d:
        s = sd("legacy-done")
        write(d, f"{s}/requirements/SRS.md", "x")
        write(d, f"{s}/design/TECH.md", "x")
        for gate, subdir in (("REVIEW", "reviews"), ("SECURITY", "security"),
                             ("UNIT", "test-reports"), ("INTEGRATION", "test-reports")):
            write(d, f"{s}/{subdir}/VERDICT-{gate}.json", '{"decision":"PASS"}')
        slug, amb = S.resolve_active_feature(d)
        check(slug == "legacy-done" and amb == [], f"all-pass with no status: stays in-flight -> {slug!r},{amb!r}")


def test_resolve_empty():
    with tempfile.TemporaryDirectory() as d:
        slug, amb = S.resolve_active_feature(d)
        check(slug is None and amb == [], f"empty -> {slug!r},{amb!r}")


# --- infer_gate_progress (progress display only -- does not drive closure) -- #
def test_infer_gates_empty():
    with tempfile.TemporaryDirectory() as d:
        p = S.infer_gate_progress(d, "payment")  # no stream folder -> all pending
        check(all(v == "pending" for v in p["gates"].values()), f"all pending: {p['gates']}")
        check(p["next_action"] == "/cbr-plan payment --phase requirement", p["next_action"])
        check("REQUIREMENT pending" in p["gate_line"], p["gate_line"])


def test_infer_gates_srs_tech():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["REQUIREMENT"] == "pass" and p["gates"]["DESIGN"] == "pass", str(p["gates"]))
        check(p["next_action"] == "/cbr-verify payment --phase review", p["next_action"])


def test_infer_gates_verdict_pass():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        write(d, f"{sd('payment')}/reviews/VERDICT-REVIEW.json", '{"decision":"PASS"}')
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["REVIEW"] == "pass", str(p["gates"]))
        check(p["next_action"] == "/cbr-verify payment --phase security", p["next_action"])


def test_infer_gates_verdict_fail_routes_fixbug():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        write(d, f"{sd('payment')}/reviews/VERDICT-REVIEW.json", '{"decision":"FAIL"}')
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["REVIEW"] == "fail", str(p["gates"]))
        check(p["next_action"] == "/cbr-implement payment --phase fix", p["next_action"])


def test_stream_dir_no_prefix_collision():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")             # payment: REQUIREMENT pass, DESIGN pending
        exp = sd("payment-export", "20260803")                           # newer, shares the prefix
        write(d, f"{exp}/requirements/SRS.md", "x")
        write(d, f"{exp}/design/TECH.md", "x")                            # export HAS TECH -> would be DESIGN pass
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["DESIGN"] == "pending",
              f"'payment' must NOT read payment-export's TECH (prefix collision): {p['gates']}")


def test_gate_verdict_partial_and_batch():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/reviews/VERDICT-B1-REVIEW.json", '{"decision":"PASS"}')
        write(d, f"{sd('payment')}/reviews/VERDICT-B2-REVIEW.json", '{"decision":"pending"}')
        got = S._gate_verdict(d, "payment", "REVIEW")
        check(got == "partial", f"partial -> {got!r}")


# --- legacy-verdict shim (R2 design doc §3) --------------------------------- #
def test_gate_verdict_legacy_shim():
    """A pre-0.11.0-named verdict (VERDICT-G4.json, no VERDICT-REVIEW.json present)
    is still recognized by the renamed lookup and flagged legacy in the display.
    """
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/reviews/VERDICT-G4.json", '{"decision":"PASS"}')
        got = S._gate_verdict(d, "payment", "REVIEW")
        check(got == "pass", f"legacy-named verdict still decides -> {got!r}")
        p = S.infer_gate_progress(d, "payment")
        check("REVIEW PASS (legacy)" in p["gate_line"], p["gate_line"])


def test_gate_verdict_mixed_era():
    """Mixed-era stream: an old-named REVIEW verdict alongside a new-named UNIT
    verdict in the same stream -- both read correctly, no contradiction, and only
    the legacy one is marked.
    """
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/reviews/VERDICT-G4.json", '{"decision":"PASS"}')          # legacy
        write(d, f"{sd('payment')}/test-reports/VERDICT-UNIT.json", '{"decision":"PASS"}')   # current
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["REVIEW"] == "pass" and p["gates"]["UNIT"] == "pass", str(p["gates"]))
        check("REVIEW PASS (legacy)" in p["gate_line"], p["gate_line"])
        check("UNIT PASS (legacy)" not in p["gate_line"], p["gate_line"])


# --- SECURITY staleness (R2 design doc §6 -- replaces the deleted G5b mandate) #
def test_infer_gates_security_stale():
    """A SECURITY verdict older than the stream's newest bug-report entry shows
    STALE and re-routes to cbr-verify's SECURITY phase -- the case a DEV-log-only
    check would miss, since `cbr-implement`'s fix loop writes bug-reports/, not
    work-logs/.
    """
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/requirements/SRS.md", "x")
        write(d, f"{sd('payment')}/design/TECH.md", "x")
        write(d, f"{sd('payment')}/reviews/VERDICT-REVIEW.json", '{"decision":"PASS"}')
        write(d, f"{sd('payment')}/security/VERDICT-SECURITY.json", '{"decision":"PASS"}', mtime=1_000_000)
        write(d, f"{sd('payment')}/bug-reports/BUG-20260801-01.md", "x", mtime=2_000_000)
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["SECURITY"] == "stale", str(p["gates"]))
        check(p["next_action"] == "/cbr-verify payment --phase security", p["next_action"])
        check("SECURITY STALE" in p["gate_line"], p["gate_line"])


def test_infer_gates_security_fresh_stays_pass():
    with tempfile.TemporaryDirectory() as d:
        write(d, f"{sd('payment')}/bug-reports/BUG-20260801-01.md", "x", mtime=1_000_000)
        write(d, f"{sd('payment')}/security/VERDICT-SECURITY.json", '{"decision":"PASS"}', mtime=2_000_000)
        p = S.infer_gate_progress(d, "payment")
        check(p["gates"]["SECURITY"] == "pass", f"verdict newer than the fix -> should stay pass: {p['gates']}")


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
        write(d, f"{sd('payment')}/reviews/VERDICT-REVIEW.json", '{"decision":"pass"}')
        idx = S.build_index(d, "payment", now="2026-08-02T00:00:00Z")
        feat = idx["features"]["payment"]
        check(idx["generatedAt"] == "2026-08-02T00:00:00Z", "now stamped")
        check(feat["gates"]["REVIEW"] == "pass", str(feat["gates"]))
        types = {a["type"] for a in feat["artifacts"]}
        check({"SRS", "TECH", "VERDICT-REVIEW"} <= types, f"types={types}")
        tech = next(a for a in feat["artifacts"] if a["type"] == "TECH")
        check(len(tech["sections"]) == 2, f"TECH sections={tech['sections']}")
        verdict = next(a for a in feat["artifacts"] if a["type"] == "VERDICT-REVIEW")
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

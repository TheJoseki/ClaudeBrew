#!/usr/bin/env python3
"""Skill-invoked verdict gate for cbr SDLC quality gates (G4/G5a/G6/G7).

A gate-owning skill (review-code, vulnerability-scanner, unit-test,
integration-test) spawns a fresh reviewer/tester agent, which writes a verdict
artifact (schema: schemas/verdict-artifact.schema.json). The skill
then runs this validator BEFORE its user-facing AskUserQuestion:

    python verdict-gate.py --gate <G4|G5a|G6|G7> --artifact <path>

exit 0 = PASS  — gate criteria objectively met; skill may present the verdict.
exit 2 = BLOCK — FAIL decision, unresolved Critical, missing test evidence,
                 leaked secret, or a malformed artifact. Reason on stderr.

Unlike the ambient guards (protect-files.py fails OPEN so it never bricks
unrelated work), a gate fails CLOSED: exit 0 must mean "definitively passed".
A missing / malformed / underspecified artifact therefore BLOCKS.

Per-gate policy:
  G4 (code review) / G5a (security): decision==PASS and no unresolved Critical.
      A reviewer runs no commands, so no verification entry is required.
  G6 (unit) / G7 (integration): decision==PASS, no unresolved Critical, and at
      least one verification entry with result=="pass" (the test run).
  All gates: the artifact text is scanned for leaked credentials — a match BLOCKS.

Invoked by skill instruction via Bash; never registered as an automatic hook, so
it needs no matcher and works regardless of who produced the artifact.
"""
import argparse
import json
import re
import sys

VALID_GATES = ("G4", "G5a", "G6", "G7")
TEST_GATES = ("G6", "G7")  # gates that require a passing verification entry

# Content secret patterns — a leaked credential must never ride into a committed
# artifact. Kept specific so the artifact's own keys are not false positives.
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),                       # AWS access key id
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),  # PEM private key
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                    # GitHub PAT
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),           # Slack token
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}"),      # bearer token
)


def block(reason):
    print(f"verdict-gate BLOCK: {reason}", file=sys.stderr)
    sys.exit(2)


def load_artifact(path):
    """Read + secret-scan + JSON-parse the artifact, or block()."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        block(f"cannot read artifact {path}: {e}")
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            block(f"leaked credential matching /{pat.pattern}/ in artifact")
    try:
        return json.loads(text)
    except ValueError as e:  # JSONDecodeError subclasses ValueError
        block(f"artifact is not valid JSON: {e}")


def validate_shape(a, gate):
    if not isinstance(a, dict):
        block("artifact is not a JSON object")
    if a.get("gate") != gate:
        block(f"artifact gate {a.get('gate')!r} != requested gate {gate!r}")
    if a.get("decision") not in ("PASS", "FAIL"):
        block(f"decision must be PASS|FAIL, got {a.get('decision')!r}")
    if not isinstance(a.get("findings"), list):
        block("findings must be an array")
    if not isinstance(a.get("verification"), list):
        block("verification must be an array")


def apply_policy(a, gate):
    if a["decision"] != "PASS":
        block(f"decision is {a['decision']} at {gate}")
    criticals = [f for f in a["findings"]
                 if str(f.get("severity", "")).casefold() == "critical"]
    if criticals:
        block(f"{len(criticals)} unresolved Critical finding(s) at {gate}")
    if gate in TEST_GATES:
        passed = [v for v in a["verification"]
                  if str(v.get("result", "")).casefold() == "pass"]
        if not passed:
            block(f"{gate} requires >=1 passing verification entry (test run)")


def main():
    p = argparse.ArgumentParser(description="cbr SDLC verdict gate")
    p.add_argument("--gate", required=True, choices=VALID_GATES)
    p.add_argument("--artifact", required=True)
    args = p.parse_args()
    try:
        a = load_artifact(args.artifact)
        validate_shape(a, args.gate)
        apply_policy(a, args.gate)
    except SystemExit:
        raise  # block()/argparse already chose the exit code
    except Exception as e:  # anything unexpected -> fail closed
        block(f"unexpected validator error: {e}")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Durable tests for verdict-gate.py — run: python evals/test_verdict_gate.py

The verdict gate is a skill-invoked validator (not an ambient hook): a skill
writes a verdict-artifact JSON, then runs this gate before the user-facing
AskUserQuestion. exit 0 = PASS (allow), exit 2 = BLOCK. It fails CLOSED — any
unreadable / malformed / policy-failing / secret-bearing artifact blocks.

Cases are driven IN-PROCESS (importlib) so `coverage` instruments the validator,
plus one real-subprocess smoke test proving the CLI entrypoint works end-to-end.
Exit non-zero if any case fails.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

GATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "claude", "hooks", "verdict-gate.py",
)
PASS, BLOCK = 0, 2

# Load the validator in-process so coverage sees its lines. A hyphenated filename
# can't be `import`ed by name, so go through importlib. The module is __main__-
# guarded, so exec_module does not run main().
_spec = importlib.util.spec_from_file_location("verdict_gate", GATE)
verdict_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verdict_gate)


def run_gate(gate, artifact_path):
    """Invoke the validator's main() in-process; return its exit code."""
    saved = sys.argv
    sys.argv = ["verdict-gate.py", "--gate", gate, "--artifact", artifact_path]
    try:
        verdict_gate.main()
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = saved


def run_gate_cli(gate, artifact_path):
    """Real subprocess invocation — proves the CLI wiring end-to-end."""
    return subprocess.run(
        [sys.executable, GATE, "--gate", gate, "--artifact", artifact_path],
        capture_output=True, text=True,
    ).returncode


def artifact(**overrides):
    """A well-formed PASS artifact; override fields per case."""
    a = {
        "gate": "REVIEW",
        "decision": "PASS",
        "findings": [],
        "verification": [],
        "secretsScanned": True,
        "producedBy": "cbr:reviewer",
        "timestamp": "2026-07-31T00:00:00Z",
    }
    a.update(overrides)
    return a


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        def write(obj_or_text):
            p = os.path.join(d, "verdict.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write(obj_or_text if isinstance(obj_or_text, str)
                        else json.dumps(obj_or_text))
            return p

        crit = [{"severity": "Critical", "file": "a.py", "line": 3, "note": "x"}]
        major = [{"severity": "Major", "file": "a.py", "line": 3, "note": "x"}]
        minor = [{"severity": "Minor", "file": "a.py", "line": 3, "note": "x"}]
        vpass = [{"cmd": "pytest", "result": "pass"}]
        vfail = [{"cmd": "pytest", "result": "fail"}]

        # (label, gate, artifact-or-text, expected-exit)
        cases = [
            # REVIEW — PASS + no Critical, no command needed; Major does NOT block (asymmetric with SECURITY)
            ("REVIEW pass clean",            "REVIEW",  artifact(gate="REVIEW"), PASS),
            ("REVIEW pass w/ minor finding", "REVIEW",  artifact(gate="REVIEW", findings=minor), PASS),
            ("REVIEW Major does not block",  "REVIEW",  artifact(gate="REVIEW", findings=major), PASS),
            ("REVIEW FAIL decision",         "REVIEW",  artifact(gate="REVIEW", decision="FAIL"), BLOCK),
            ("REVIEW pass but Critical",     "REVIEW",  artifact(gate="REVIEW", findings=crit), BLOCK),
            # SECURITY — PASS + no Critical/Major, requires >=1 passing verification entry (R2 §7)
            ("SECURITY pass w/ verification",   "SECURITY", artifact(gate="SECURITY", verification=vpass), PASS),
            ("SECURITY Critical blocks",        "SECURITY", artifact(gate="SECURITY", verification=vpass, findings=crit), BLOCK),
            ("SECURITY Major blocks",           "SECURITY", artifact(gate="SECURITY", verification=vpass, findings=major), BLOCK),
            ("SECURITY requires verification",  "SECURITY", artifact(gate="SECURITY", verification=[]), BLOCK),
            # UNIT / INTEGRATION — tests: PASS + >=1 passing verification entry
            ("UNIT pass w/ verification",  "UNIT",  artifact(gate="UNIT", verification=vpass), PASS),
            ("UNIT pass no verification",  "UNIT",  artifact(gate="UNIT", verification=[]), BLOCK),
            ("UNIT verification all fail", "UNIT",  artifact(gate="UNIT", verification=vfail), BLOCK),
            ("INTEGRATION pass w/ verification",  "INTEGRATION",  artifact(gate="INTEGRATION", verification=vpass), PASS),
            ("INTEGRATION Critical blocks",       "INTEGRATION",  artifact(gate="INTEGRATION", verification=vpass, findings=crit), BLOCK),
            ("INTEGRATION Major does not block",  "INTEGRATION",  artifact(gate="INTEGRATION", verification=vpass, findings=major), PASS),
            # secret scan — any gate blocks on a leaked credential in the artifact
            ("secret AWS key",           "REVIEW",  artifact(gate="REVIEW", producedBy="AKIA1234567890ABCDEF"), BLOCK),
            ("secret PEM block",         "REVIEW",  artifact(gate="REVIEW",
                                                         findings=[{"severity": "Minor", "file": "k", "line": 1,
                                                                    "note": "-----BEGIN RSA PRIVATE KEY-----"}]), BLOCK),
            # malformed / missing / invalid
            ("malformed json",           "REVIEW",  "{not json", BLOCK),
            ("missing decision field",   "REVIEW",  artifact(gate="REVIEW", decision=None), BLOCK),
            ("invalid decision value",   "REVIEW",  artifact(gate="REVIEW", decision="MAYBE"), BLOCK),
            ("finding not an object",    "REVIEW",  artifact(gate="REVIEW", findings=["oops"]), BLOCK),
            ("top-level non-dict json",  "REVIEW",  "[1, 2, 3]", BLOCK),
            ("findings not a list",      "REVIEW",  artifact(gate="REVIEW", findings="nope"), BLOCK),
            ("verification not a list",  "REVIEW",  artifact(gate="REVIEW", verification="nope"), BLOCK),
            ("gate mismatch artifact",   "REVIEW",  artifact(gate="INTEGRATION", verification=vpass), BLOCK),
            # R2 identity coupling — the pre-0.11.0 token is no longer a valid --gate value
            ("legacy G4 token rejected", "G4",      artifact(gate="G4"), BLOCK),
        ]
        for label, gate, body, expect in cases:
            p = write(body)
            got = run_gate(gate, p)
            ok = got == expect
            failures += not ok
            print(f"{'OK  ' if ok else 'FAIL'} exit={got} expect={expect}  {label}")

        # unknown gate value on the CLI -> block (argparse choices)
        p = write(artifact())
        got = run_gate("G99", p)
        failures += got != BLOCK
        print(f"{'OK  ' if got == BLOCK else 'FAIL'} exit={got} expect={BLOCK}  unknown gate arg")

        # missing artifact file -> block
        got = run_gate("REVIEW", os.path.join(d, "nope.json"))
        failures += got != BLOCK
        print(f"{'OK  ' if got == BLOCK else 'FAIL'} exit={got} expect={BLOCK}  missing artifact file")

        # CLI smoke — prove the real subprocess entrypoint works end-to-end
        p = write(artifact(gate="REVIEW"))
        got = run_gate_cli("REVIEW", p)
        failures += got != PASS
        print(f"{'OK  ' if got == PASS else 'FAIL'} exit={got} expect={PASS}  [cli smoke] REVIEW pass")

    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

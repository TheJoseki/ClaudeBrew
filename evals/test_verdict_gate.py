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
    "plugins", "cbr", "hooks", "verdict-gate.py",
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
        "gate": "G4",
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
        minor = [{"severity": "Minor", "file": "a.py", "line": 3, "note": "x"}]
        vpass = [{"cmd": "pytest", "result": "pass"}]
        vfail = [{"cmd": "pytest", "result": "fail"}]

        # (label, gate, artifact-or-text, expected-exit)
        cases = [
            # G4 / G5a — review & security: PASS + no Critical, no command needed
            ("G4 pass clean",            "G4",  artifact(gate="G4"), PASS),
            ("G4 pass w/ minor finding", "G4",  artifact(gate="G4", findings=minor), PASS),
            ("G4 FAIL decision",         "G4",  artifact(gate="G4", decision="FAIL"), BLOCK),
            ("G4 pass but Critical",     "G4",  artifact(gate="G4", findings=crit), BLOCK),
            ("G5a pass clean",           "G5a", artifact(gate="G5a"), PASS),
            ("G5a Critical blocks",      "G5a", artifact(gate="G5a", findings=crit), BLOCK),
            # G6 / G7 — tests: PASS + >=1 passing verification entry
            ("G6 pass w/ verification",  "G6",  artifact(gate="G6", verification=vpass), PASS),
            ("G6 pass no verification",  "G6",  artifact(gate="G6", verification=[]), BLOCK),
            ("G6 verification all fail", "G6",  artifact(gate="G6", verification=vfail), BLOCK),
            ("G7 pass w/ verification",  "G7",  artifact(gate="G7", verification=vpass), PASS),
            ("G7 Critical blocks",       "G7",  artifact(gate="G7", verification=vpass, findings=crit), BLOCK),
            # secret scan — any gate blocks on a leaked credential in the artifact
            ("secret AWS key",           "G4",  artifact(gate="G4", producedBy="AKIA1234567890ABCDEF"), BLOCK),
            ("secret PEM block",         "G4",  artifact(gate="G4",
                                                         findings=[{"severity": "Minor", "file": "k", "line": 1,
                                                                    "note": "-----BEGIN RSA PRIVATE KEY-----"}]), BLOCK),
            # malformed / missing / invalid
            ("malformed json",           "G4",  "{not json", BLOCK),
            ("missing decision field",   "G4",  artifact(gate="G4", decision=None), BLOCK),
            ("invalid decision value",   "G4",  artifact(gate="G4", decision="MAYBE"), BLOCK),
            ("finding not an object",    "G4",  artifact(gate="G4", findings=["oops"]), BLOCK),
            ("top-level non-dict json",  "G4",  "[1, 2, 3]", BLOCK),
            ("findings not a list",      "G4",  artifact(gate="G4", findings="nope"), BLOCK),
            ("verification not a list",  "G4",  artifact(gate="G4", verification="nope"), BLOCK),
            ("gate mismatch artifact",   "G4",  artifact(gate="G7", verification=vpass), BLOCK),
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
        got = run_gate("G4", os.path.join(d, "nope.json"))
        failures += got != BLOCK
        print(f"{'OK  ' if got == BLOCK else 'FAIL'} exit={got} expect={BLOCK}  missing artifact file")

        # CLI smoke — prove the real subprocess entrypoint works end-to-end
        p = write(artifact(gate="G4"))
        got = run_gate_cli("G4", p)
        failures += got != PASS
        print(f"{'OK  ' if got == PASS else 'FAIL'} exit={got} expect={PASS}  [cli smoke] G4 pass")

    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

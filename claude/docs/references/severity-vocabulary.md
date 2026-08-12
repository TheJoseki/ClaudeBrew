# Severity Vocabulary — ClaudeBrew Gates

> On-demand detail behind every gate-owning skill's verdict rubric. Load this when spawning a `cbr-reviewer`
> or `cbr-tester` verdict, or when authoring a new gate. One home for the Critical/Major/Minor/Info scale and
> the per-gate blocking rules — do not restate or re-derive these inline in a skill body; cite this file.

## Canonical Severity Scale

| Severity | Meaning |
|----------|---------|
| Critical | Blocks every gate. RCE, auth bypass, mass data exposure, broken build, data loss. |
| Major | Should fix before merge/ship. Feature broken with no workaround, privilege escalation, wrong data. |
| Minor | Fix if time permits. Degraded UX, workaround exists, style/consistency issues. |
| Info | Non-blocking. Cosmetic, verbose logging, improvement suggestions. |

## OWASP → Verdict Scale Mapping

The verdict artifact's `severity` field has no separate `High` value. When a `cbr-reviewer` runs the
SECURITY checkpoint against the OWASP Top 10:2025 Report Format's own `Critical/High/Medium/Low` scale
(`cbr-vulnerability-scanner/SKILL.md`'s Report Format table), map on write:

| OWASP label | Verdict artifact `severity` |
|-------------|-----------------------------|
| Critical | Critical |
| High | **Major** |
| Medium | Minor |
| Low | Info |

The validator (`hooks/verdict-gate.py`) blocks SECURITY verdicts on Critical *or* Major directly — mapping
High → Major is what makes that block actually fire on High-severity OWASP findings. No severity-inflation
trick is needed or intended.

## Per-Gate Blocking Rules

Asymmetric by design — do not assume every gate blocks the same way:

| Gate | Validator blocks on | Enforced by |
|------|---------------------|-------------|
| REVIEW | `decision != PASS`, or ≥1 Critical finding | `verdict-gate.py` (hard floor) |
| REVIEW | 3+ Major findings → FAIL | **Reviewer's judgment only** — the validator does not count Majors. This rule lives entirely in the spawn prompt handed to the fresh `cbr-reviewer`; if it's dropped from the prompt, the rule silently stops applying. |
| SECURITY | `decision != PASS`, ≥1 Critical, **or** ≥1 Major finding | `verdict-gate.py` (`MAJOR_BLOCKS = ("SECURITY",)`) |
| UNIT | `decision != PASS`, ≥1 Critical, or zero passing `verification` entries | `verdict-gate.py` (`TEST_GATES` requires ≥1 passing verification) |
| INTEGRATION | `decision != PASS`, ≥1 Critical, or zero passing `verification` entries | `verdict-gate.py` (`TEST_GATES` requires ≥1 passing verification) |

REVIEW and SECURITY differ on Major-blocking on purpose: a Major code-quality finding is a judgment call
best left to the reviewer; a Major *security* finding is not — the validator enforces it mechanically so a
rushed or lenient reviewer can't silently pass one through.

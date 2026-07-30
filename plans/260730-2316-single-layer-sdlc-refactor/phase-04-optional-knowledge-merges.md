# Phase 4 — OPTIONAL Knowledge Merges

**Depends on:** Phase 1 · **Status:** RECOMMENDATION from audit — **NOT a user-locked decision.** Execute only on explicit opt-in. Keep isolated so Phases 1–3 ship independently.

## Context
These are the audit's Tier-3 merges (report §5.1–5.4). Each consolidates *reference* skills feeding a surviving executor; executors are never merged.

## Candidate merges
| Merge | Sources (lines) | Target | Rationale |
|-------|-----------------|--------|-----------|
| Command-runner | `lint-and-validate` (87) + `run-tests` (99) | 1 skill `validate-and-test` | Both pure command-runners, no agent binding — cleanest merge in suite. |
| Testing strategy | `testing-patterns` (85) + `tdd-workflow` (109) | 1 skill `testing-strategy` | Both strategy/pattern guidance feeding `unit-test`/`integration-test`. |
| Code quality | `clean-code` (122) + `code-review-checklist` (92) | 1 skill `code-quality` | Both feed `review-code`. |
| Debugging methodology | `systematic-debugging` (215) | → `references/` of `fix-bug` | fix-bug already escalates to it. Trade-off: loses standalone invocation — confirm acceptable. |

## Per-merge steps (same pattern as Phase 2)
1. Pick target dir; write lean `SKILL.md` + move detail to `references/`.
2. Consolidate `evals/evals.json` (2 positive + 1 boundary).
3. Delete source dirs.
4. Repoint `NOT FOR:` / connection refs to the new name (re-grep).
5. `claude plugin validate ./plugins/cbr` → 0 errors.

## Net effect
~29 → ~25 skills.

## Risk
- `systematic-debugging` merge changes user-facing invocation (no longer standalone). If the user values `/cbr:systematic-debugging` as a direct entry, keep it standalone and skip that row.

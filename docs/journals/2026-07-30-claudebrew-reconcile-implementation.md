# ClaudeBrew Reconcile: Implementation — the Validator and the Reviewer Caught What Reading Didn't

**Date**: 2026-07-30 22:50
**Severity**: High
**Component**: `plugins/cbr/hooks/*`, `plugins/cbr/agents/*`, `plugins/cbr/skills/*`, worktree policy
**Status**: Resolved — merged as PR #1 (11 commits, `main` untouched at merge time), https://github.com/TheJoseki/ClaudeBrew/pull/1

## What Happened

Executed the red-teamed reconcile plan from the prior audit session via `/cook --tdd`: P0 (real security/quality-gate hooks), P1 (executable imported SDLC suite), P2 (consistency pass). Verified end-to-end with `claude plugin validate`, 56 test cases across 4 Python suites, and 40/40 skill evals. Shipped as a single PR, no direct commits to `main`.

## The Brutal Truth

The project's own hard-mandatory-worktree rule collided with its own uncommitted state on step one: the entire imported suite (50 files) sat untracked, so a worktree branched from HEAD would carry none of it. Had to snapshot a baseline commit first, then branch — the policy assumed a clean tree that didn't exist. And twice during implementation, tools I trusted less than "careful reading" found things careful reading missed: `claude plugin validate` surfaced 33 silently-broken frontmatter files that 4 earlier scout agents had eyeballed and rubber-stamped "40/40 valid," and a code-reviewer found 3 real behavior bugs in hooks that 56 passing unit tests said were fine. Tests passing is not correctness; it's "the cases I thought to write pass."

## Technical Details

- **Worktree collision**: resolved with feature-branch-in-place + baseline commit (`4898dbd chore: snapshot imported SDLC suite and reconcile docs as pre-rework baseline`) instead of a separate worktree — keeps `main` clean, keeps all files present for the branch.
- **P0 security**: 3 `PreToolUse` guards read nonexistent `$CLAUDE_TOOL_INPUT` and never fired — ported bash→Python reading stdin JSON (`951dac0`), verified against hooks docs in the prior audit session. Also ported `SubagentStop` quality-gate + `PreCompact` saver off `jq` (absent on stock Windows/macOS = silent fail-open). Worktree gate made opt-in via `/cbr:setup` + testable `settings_merge.py` (`9876cd1`). TDD throughout: failing test first, then fix.
- **The frontmatter discovery**: mid-cook, `claude plugin validate` returned 33 parse errors — unquoted `TRIGGER:`/`NOT FOR:` descriptions containing `: ` broke YAML, silently voiding role-agent `tools`/`permissionMode`. Fixed with one deterministic script (`c827941`), not 33 hand-edits.
- **P1 executability** (`8ad1a80`): 3 parallel subagents, strict disjoint file ownership — dead `orchestrator-agent` phase paths, `retro` missing `Agent`/`Write`/`Edit` tools, missing security phase, `.claude/` → `${CLAUDE_PLUGIN_ROOT}`, deprecated `context-inject` mandate removed.
- **Code review found 3 bugs unit tests didn't** (`dc69ae0`): quality gate no-op'd on namespaced `cbr:developer-agent` (matcher assumed unnamespaced agent names); URL-shortener regex hard-denied legit hosts (`airport.co.jp` substring-matched `t.co`); `protect-files` blocked committed `.env.example`. All three had passing tests before review — the tests just didn't cover these inputs.
- **P2** (`f77ebe7`, `895d9aa`, `ed05476`, `32df6d2`, `469867f`): unified artifact path to `docs/specs/<stage>/<TYPE>-<slug>.md`; authored `evals/evals.json` for all 40 skills (was 2, via 6 parallel agents); added `TRIGGER:`/`NOT FOR:` guards to 7 knowledge skills — same `: ` syntax that broke frontmatter, so every guard had to stay double-quoted (the fix for the bug was applying the exact pattern that caused it, carefully this time).
- Final state: `claude plugin validate ./plugins/cbr` passes; 56 tests green; 40/40 evals present; BACKLOG-tracked items emptied.

## What We Tried

Trusted 4 scout agents' frontmatter read ("40/40 valid") until the actual validator disagreed — validator wins, scouts were doing pattern-matching, not parsing. Trusted 56 passing unit tests until a code-reviewer read the hooks for behavior, not just contract — reviewer wins, tests only exercise what you thought to write. Both times the cheaper/faster signal (agent eyeballing, green test suite) was wrong in ways that would have shipped silently.

## Root Cause Analysis

Two independent instances of the same failure mode: confidence from inspection substituting for confidence from execution. Scouts read YAML visually and pattern-matched "looks like frontmatter" instead of running a parser. Unit tests covered the paths the implementer thought of, not the paths that break in practice (a namespace prefix, a substring collision, a committed example file). Neither failure was caused by carelessness — both authors were being reasonably thorough — the gap is structural: static review and unit tests both stop at the boundary of what the author imagined to check.

## Lessons Learned

Run the actual tool that will consume the artifact (validator, not eyeball) before trusting a "looks fine" scout verdict. Don't treat a green test suite as done — get an adversarial second pass (code review) specifically hunting for inputs the tests didn't cover, especially anywhere there's a naming convention (namespacing), a string-matching guard (substring collision), or a file-existence assumption (committed vs. generated). File-ownership partitioning (explicit disjoint file sets) is what made ~9 parallel subagents across this session safe — no merge conflicts, no silent overwrites, because ownership was decided before spawning, not discovered after.

## Next Steps

PR #1 merged; no open follow-ups from this pass — BACKLOG emptied at P2 close. Future skill/agent authors: run `claude plugin validate` after any frontmatter edit involving `TRIGGER:`/`NOT FOR:` (colon-space breaks YAML scalars unless quoted) — don't rely on visual review. Any new hook or gate should get both a unit test AND a review pass explicitly asked to hunt for namespace/substring/existence edge cases, not just "does it pass."

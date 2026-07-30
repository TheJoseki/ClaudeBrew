# ClaudeBrew Re-Audit: The Hard Gates Aren't Hard

**Date**: 2026-07-30 02:00
**Severity**: High
**Component**: `plugins/cbr/hooks/*`, `worktree` skill, imported SDLC suite (orchestrate/full-sdlc/agents)
**Status**: Resolved (plan accepted; implementation not yet started — no code touched this session)

## What Happened

Asked for a full re-audit of ClaudeBrew ("scout và review phân tích lại toàn bộ"). Ran ground-truth grep plus 4 parallel scout agents (committed core / orchestration / hooks / skills-breadth), then verified every hook-contract claim against the official docs (`code.claude.com/docs/en/hooks.md`) via a `claude-code-guide` agent instead of trusting repo inference. Produced two artifacts, no code changes: `plans/reports/review-260730-0113-claudebrew-audit.md` and a 3-phase reconcile plan at `plans/260730-0139-claudebrew-reconcile-hard-gates-python-hooks-executable-suite/`.

## The Brutal Truth

The project's entire pitch is "hard gates, not markdown promises" — and the audit found the shipped plugin doesn't have them. The worktree base-branch gate (`enforce-worktree.py`) is not registered in `hooks.json` at all; installed users get zero enforcement despite `enforcement.md` claiming it's live "whenever plugin enabled." Worse: the 3 PreToolUse security guards (`protect-files.sh`, `guard-bash.sh`, `guard-webfetch.sh`) are **complete no-ops** — they read `$CLAUDE_TOOL_INPUT`, an env var that doesn't exist. PreToolUse payload only ever arrives via stdin JSON. Docs confirmed it. So the secrets guard, bash guard, and webfetch guard have never blocked anything, ever, and nothing in the test suite would have caught it because `test_hook.py` tests the script directly, not the wiring.

## Technical Details

- `hooks.json:45-54` — worktree gate slot runs `protect-files.sh`, not `enforce-worktree.py`.
- `protect-files.sh:14`, `guard-bash.sh:10`, `guard-webfetch.sh:9` — all `[ -z "$TOOL_INPUT" ] && exit 0`, sourced from a nonexistent env var.
- `retro/SKILL.md` declares `allowed-tools: Read,Grep,Glob,Bash` (no Agent/Write) yet the workflow spawns 5 agents and writes a report — non-executable as written.
- `orchestrator-agent.md:27-28,145-148` points to `skills/orchestrate/references/phase-4-implementation.md`, which actually lives under `skills/full-sdlc/references/` — dead paths in Phase 4-8.
- 38/40 skills have no `evals/evals.json` — no way to check trigger reliability for almost the whole suite.

## What We Tried (and a correction mid-flight)

Verification against docs **retracted 2 of the scouts' own findings**: they'd claimed `SubagentStop` doesn't provide `agent_type`/`last_assistant_message`, and that `PostCompact` isn't a real event. Both wrong — docs confirm both are legitimate. The scouts had committed a category error: "repo doesn't set X ⇒ X doesn't exist," when the harness, not the repo, sets hook env/fields. Good thing this got checked instead of shipped as-is.

Then the reconcile plan itself got 3 hostile reviewers (Security Adversary, Assumption Destroyer, Failure Mode Analyst) — 14 evidence-backed findings, all applied. The sharpest one: the plan's own step to "fix 10 `.claude/` refs via grep" would have corrupted `sdlc-conventions.md:241`, a legitimate reference to the *user's own* project doc — i.e., the plan almost repeated the exact "infer, don't verify" mistake the audit had just diagnosed in the codebase. Also caught: the opt-in worktree gate design would've written `${CLAUDE_PROJECT_DIR}/...` into user settings, which doesn't resolve post-install — recreating the same silent no-op it was meant to fix.

## Root Cause Analysis

Markdown describes the intended system, not the shipped one, and nobody ran the suite end-to-end. Two disjoint hook contracts got merged (native stdin-reading vs. an imported harness's env-var convention) without anyone re-verifying the imported half against actual docs. No eval harness exists to catch drift for 38/40 skills, and the one hook test that does exist checks script correctness, not registration.

## Lessons Learned

When the "code" is markdown a model obeys, correctness needs adversarial + source verification at *every* layer — docs caught the scouts' wrong inferences, red-teaming caught the plan repeating the audit's own root cause. Reading carefully is not enough; a claim about harness behavior needs the harness's docs, not repo archaeology. And a plan's own repair steps need the same skepticism applied to the bugs it's fixing — "fix all N references matching this grep" is exactly how you turn a targeted fix into new damage.

## Next Steps

4 decisions locked with the user: reconcile the imported suite to actually ship; worktree gate becomes opt-in via `/cbr:setup` (not always-on); all hooks port to Python stdlib reading stdin (drop bash/jq/`$CLAUDE_TOOL_INPUT`); unify artifact paths to `docs/specs/<stage>/<TYPE>-<slug>.md`. Implementation is P0→P1→P2 per the plan, owner TBD, and per project policy must happen in a git worktree off `main` — not on it.

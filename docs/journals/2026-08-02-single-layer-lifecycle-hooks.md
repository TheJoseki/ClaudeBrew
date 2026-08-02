# Lifecycle Hooks: The Rich Reinject Had Been Shipping to /dev/null

**Date**: 2026-08-02 21:45
**Severity**: High
**Component**: `plugins/cbr/hooks/*` (`session-init.py`, `subagent-context.py`, `lib/sdlc_state.py`), `plugins/cbr/hooks/hooks.json`, `skills/setup`
**Status**: Resolved — implemented on `worktree-single-layer-refactor`; bundled into **PR #3** to `main` (this session), MERGEABLE/CLEAN

## What Happened

Gave the single-layer suite the three ClaudeKit lifecycle **behaviors** — rich session-init context, per-subagent context, cross-session continuity — using **single-layer-native mechanisms**: no orchestrator, no role agents, no `.*-agent` matcher reintroduced. Built TDD-first: `hooks/lib/sdlc_state.py` (shared state reconstruction, 263 lines) feeds two general hooks — `session-init.py` (`SessionStart: startup|resume|clear|compact`) and `subagent-context.py` (`SubagentStart`, no matcher — every spawn). **100% coverage, 44 cases** across `evals/test_sdlc_state.py` + `evals/test_lifecycle_hooks.py`; `claude plugin validate ./plugins/cbr` clean; P1 firing validated live in a `--plugin-dir` session. Then, this session, merged `origin/main` (one duplicate-`/plans/` gitignore conflict, resolved by keeping the branch's superset) and opened **PR #3** carrying both the v0.3.0 single-layer pivot and this hooks work to `main`.

## The Brutal Truth

The headline "fix" was a bug we shipped and never noticed: the rich post-compaction reinjection was wired to `PostCompact`, whose **stdout is log-only — it never reaches the model**. So after every compaction, the context we thought we were restoring went nowhere; the model resumed blind. This wasn't new breakage — it was a latent no-op carried in from the imported suite, sitting in `post-compact-reinject.sh` (75 lines) looking like it worked. Nothing caught it because "the script runs and prints" and "the model receives what it prints" are different claims, and only the first was ever checked. It took reading the harness docs — again — to find that the entire mechanism was aimed at the wrong event.

## Technical Details

- **Shared reconstruction** (`lib/sdlc_state.py`): globs `docs/specs/<stage>/` artifacts for the active feature, assesses gate progress G1–G8, finds the `⏳ IN_PROGRESS` stage + open items — the same logic `/cbr:handoff` Steps 1–3 specify by hand. The hook is the *cheap automatic* form; the skill stays the *rich manual* form. Cite, don't restate.
- **`session-init.py`** (135 lines): on `startup|resume|clear`, injects the gate-aware SDLC summary and writes a `.claude/sdlc-index.json` cache. On `compact`, reinjects the `PreCompact` checkpoint + SDLC gate-state + PROJECT.md sections + an `AskUserQuestion` approval-gate reminder (ClaudeKit's Issue-#277 mitigation) — one hook now handles new sessions *and* compaction.
- **`subagent-context.py`** (90 lines): on every `SubagentStart` (no matcher), injects active feature + gate + verdict path/schema + section pointers to the pool agent. Reads the cache with a **glob-on-canonical-path fallback** — the cache is convenience, the glob stays the fail-loud authority.
- **Removed** `post-compact-reinject.sh` (dead — wrong event) and the thin redundant `re-inject-context.sh` (17 lines, also still read the deleted `DECISION-LEDGER.md`).
- **`hooks.json`**: registers the two Python hooks; still no `.*-agent` matcher — `SubagentStart` fires with no name filter, so it does not re-couple to the removed role agents.
- **`/cbr:setup` step 7**: gitignore the ephemeral hook caches (`.claude/sdlc-index.json`, `compact-checkpoint.md`, `.smoke-*`) in user projects — derived artifacts, not source.

## What We Tried

Started from ClaudeKit's lifecycle model but deliberately **copied behavior, not mechanism**: text injection instead of ClaudeKit's `CK_*` env backbone, and cross-session memory that **self-reconstructs from committed `docs/`** rather than a durable state file — no new persistent state to drift. When the `PostCompact` path looked suspicious, the check was not "does the script output the right text" (it did) but "does this event deliver stdout to the model" — answered against `code.claude.com/docs/en/hooks.md`, which lists the injection-capable events (`SessionStart`/`Setup`/`SubagentStart` + `UserPromptSubmit`/tool events) and does **not** include `PostCompact`.

## Root Cause Analysis

Same failure mode this project keeps rediscovering: **confidence from inspection substituting for confidence from harness docs.** The reinject "worked" under every test that exercised the script in isolation; what none tested was the wiring assumption — that `PostCompact` is injection-capable. It isn't. The imported suite conflated two compaction-adjacent events (`PostCompact` runs after compaction; `SessionStart:compact` is the one that can *inject* on that transition), and the mistake survived because a markdown/script harness has no compiler to reject an output aimed at a channel the model never reads.

## Lessons Learned

A hook that prints is not a hook that reaches the model — verify the *delivery contract of the event*, not just the correctness of the script, against the harness docs before trusting any injection. This is the third session in a row where source/docs verification beat careful reading (audit: `$CLAUDE_TOOL_INPUT` doesn't exist; reconcile: 33 silently-broken frontmatter files; here: `PostCompact` stdout is log-only). Two design guardrails paid off: reconstructing state from `docs/` instead of a state file means there is nothing to keep in sync, and keeping the glob-on-canonical-path as authority (cache as convenience) means a stale/missing cache degrades to correct, not to silent-wrong.

## Next Steps

PR #3 (`worktree-single-layer-refactor` → `main`) is open and MERGEABLE/CLEAN, bundling the single-layer pivot + these hooks; awaiting merge. One question still open from the prior session: whether to invest in multi-run (3–5×) trigger-eval majority voting for a stable recall number, or accept **precision-only** as the shipped metric (current recommendation: accept, document the ceiling, move on). Owner: whoever merges PR #3.

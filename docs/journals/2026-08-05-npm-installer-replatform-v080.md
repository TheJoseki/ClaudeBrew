# CBR Re-Platform: Plugin to `npx claudebrew` — and the 3 Bugs Review Caught Before They Shipped

**Date**: 2026-08-05 14:20
**Severity**: High
**Component**: whole suite — packaging (`plugins/cbr/` → `claude/` payload), `scripts/lib/*.mjs` (new installer), `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `evals/*`
**Status**: Implemented on `feat/npm-installer-replatform` (off v0.7.0) — **not pushed, no PR yet**

## What Happened

ClaudeBrew stopped being a Claude Code plugin/marketplace and became a standalone `npx claudebrew` npm installer CLI, shipped as **0.8.0**. This is a one-way door across the whole suite, not a scoped patch. Executed via `/ak:cook --advise --tdd` against a plan validated the same day (`plans/260804-2315-cbr-re-platform-plugin-to-npm-installer-cli/`, 7 phases). Result: 8 commits, one per phase plus a deferred-items closeout — `4240c10` (P1 packaging skeleton) → `df6229b` (P2 path rework) → `859cd53` (P3 settings.json as hook SoT) → `e6a6530` (P4 installer file-side) → `ad230fb` (P5 installer config-side) → `5488b43` (P6 `cbr:` → `cbr-` namespace) → `44afa98` (P7, 0.8.0 release) → `eb53db6` (closeout: tarball test, user-scope test, CLAUDE.md refresh).

## The Brutal Truth

This is a full re-platform of a suite that's been shipping as a plugin since v0.1.0, done in one day, with no PR merged yet — the risk was real, not theoretical. The plugin model's `${CLAUDE_PLUGIN_ROOT}` gave every path resolution for free; dropping it meant hand-rolling install/update/uninstall as a small transactional filesystem+config engine, and that class of code is exactly where "looks done, ships a data-loss bug" lives. It did, twice, in the config-merge layer — the layer users trust least to be gentle with their own `settings.json`.

## Technical Details

**The load-bearing fix:** a two-tier path scheme. Intra-skill references stay skill-relative (`references/X.md`, free, scope/CWD-independent). Everything else — cross-skill, subagent-passed schemas, `Bash`-invoked scripts, `rules/`/`agents/`/`hooks/`, template sources — carries a `{{CBR_ROOT}}` token, baked to an absolute path at install (`grep -rn '{{CBR_ROOT}}' claude/` = **54 occurrences / 21 files**, exact-literal `split/join` bake, never a brace regex — the payload already has 111 unrelated `{{` from JSX `style={{}}` and Python f-strings). This invariant was re-asserted after every phase, including the P6 namespace sweep that rewrote ~90 `cbr:`→`cbr-` refs — the count never moved, which is the proof nothing silently ate or minted a token. It also dissolves the long-standing `docs/_templates/` seeding gap for free.

**3 bugs advisor review caught before ship:**
1. **P4 — `update`/`uninstall` asymmetry.** `update` skipped a user-edited file; `uninstall` deleted every tracked file regardless, destroying the edit `update` had just protected. Fix: `uninstall` is now hash-aware — removes a file only if its on-disk hash still equals the recorded (ours) hash; `--force` overrides.
2. **P5 — empty-container data loss.** `computeUnmerge` pruned any settings.json container left empty after removing CBR's leaf. But "empty after removal" ≠ "CBR created it" — a user's pre-existing `{"env": {}}` would get silently deleted on uninstall. Fix: provenance now tracks `createdContainers`; un-merge prunes only those.
3. **P5 — non-transactional `fullInstall`.** A malformed target `settings.json` correctly throws (fail-closed), but by then files + `metadata.json` were already on disk — a wedged half-install recoverable only via `install --force`. Fix: config stages wrapped, payload rolled back (`uninstallFiles --force`) on any failure.

A fourth, quieter one at P7: `hooks/settings_merge.py` (the old plugin-era merge script) was still shipping to users **with a passing test** (`evals/test_settings_merge.py`) — 63 + 66 lines of dead code the test suite was masking as live. Both deleted in `44afa98`.

**2 plan details overturned by primary-source evidence**, not assumption: the plan defaulted to *absolute* `@`-imports for the rules block because "relative resolves against the working directory." The `claude-code-guide` agent, citing the docs directly (`"Relative paths resolve relative to the file containing the import, not the working directory"`), showed the premise false — so the rules block uses plain relative imports, no token needed on that surface at all. Second: `CLAUDE.local.md` auto-loads alongside `CLAUDE.md` and is the documented gitignored per-machine file — so the project-scope rules block writes there, not into the tracked `CLAUDE.md`, avoiding 13 dangling `@`-imports for a teammate who clones but hasn't run the installer.

**Other decisions:** `settings.json` is deep-merged fail-closed (a malformed target file aborts byte-for-byte unchanged — never the old script's `{}`-clobber) and provenance-tracked for symmetric uninstall, never copied as a file (copy-then-bake would defeat the "0 tokens survive" check since the hook commands are baked at merge time, not copy time). `hooks.json` retired — `settings.json` is the single hook-registration source now. Python is a hard prerequisite with a fail-loud doctor (`python`/`python3`/`py -3`); the one bash hook (`post-edit-reminder.sh`) ported to Python so it's the *only* runtime prereq, literally. 24 skills + 5 agents renamed `cbr:` → `cbr-` (colon is plugin-only; personal skills invoke by folder name) — including the hardcoded `subagent-context.py` `GATE_AGENTS` set, which would otherwise silently fail to resolve a spawned `cbr-reviewer`. The worktree gate stays opt-in, now via an `install --gate` flag rather than an interactive prompt (a TTY prompt hangs a non-interactive `npx`/CI run).

## What We Tried

Advisor was consulted ~8 times across the cook (before-approach, P2 path classification, P3 rules-loading fork, P4/P5 done-reviews) — every one of the 3 real bugs above surfaced in a done-review, not during initial implementation. `claude-code-guide` was spawned twice specifically to verify Claude Code doc claims before trusting the plan's stated mechanism, and both checks reversed a plan detail. Verification: 21 Node installer tests (`node --test`), 11 retargeted/new Python gates (including a new `test_replatform_invariants.py` asserting 0 `${CLAUDE_PLUGIN_ROOT}`, 0 `.sh` under `claude/hooks/`, 0 `cbr:` colon refs, 0 `*.cbrtmp` stragglers), and an empirical install-from-tarball run (`npm pack` → extract → `node bin/claudebrew.mjs --help`, no `ERR_MODULE_NOT_FOUND`).

## Root Cause Analysis

The bugs cluster in one place: **inverse operations written after their forward operation, not alongside it.** `update` was built first and got its skip-on-edit protection; `uninstall` was written later against the same tracked-file list without re-deriving what "protected" meant for deletion, not skip. Same shape in P5 — `computeUnmerge` was built as the literal inverse of the merge's container-creation, without separately asking "empty" vs "we created it." A single happy-path spec for install never forces you to write the failure-path (uninstall, un-merge, rollback) with the same rigor — only a fresh reviewer re-deriving the inverse from scratch caught the asymmetry both times.

## Lessons Learned

When an operation ships with an explicit inverse (install/uninstall, merge/un-merge, update/rollback), write and adversarially review the inverse with the same scrutiny as the forward path — "symmetric by construction" is a claim to verify, not assume. Trust primary docs over a plan's stated rationale even mid-cook; two `claude-code-guide` checks reversed decisions that had already been "validated" the day before. And a residual-manifest invariant (the token count) earned its keep as a cheap, mechanical proof of "nothing silently changed" across five phases of heavy sed/regex sweeps — worth the discipline of re-asserting it every phase rather than once at the end.

## Next Steps

Push `feat/npm-installer-replatform` and open the PR — owner: next session. One honest leftover, not a blocker: `CLAUDE.md`'s deeper conceptual worktree/pivot narrative is only top-flagged with a migration note, not sentence-rewritten to the npm model (the user-shipped `enforcement.md` is already correct). Worth a follow-up pass before or shortly after merge so a new contributor reading CLAUDE.md end-to-end doesn't hit stale plugin-era prose deep in the doc.

## AgentWiki

AgentWiki publishing skipped (`agentwiki` CLI not found on PATH; no MCP publishing tool exposed in this session) — this file is the source of truth.

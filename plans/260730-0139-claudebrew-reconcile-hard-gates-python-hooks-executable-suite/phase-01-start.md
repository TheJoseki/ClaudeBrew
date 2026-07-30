---
phase: 1
title: "Real gates + Python hooks"
status: pending
priority: P1
effort: "1.5-2.5d"
dependencies: []
---

# Phase 1: Real gates + Python hooks (audit tier P0)

## Overview
Make the two "hard gates" the project advertises actually true: the PreToolUse security guards must enforce (they are currently no-ops), the SubagentStop quality gate must not be a jq no-op, and the worktree gate must match its docs (honest opt-in, not fake always-on). Correctness/security tier — ship first.

## Requirements
- Functional: guards block on real payloads; SubagentStop quality gate runs without jq; worktree gate installs via `/cbr:setup` and its docs describe opt-in; tests prove behavior at the level they claim to.
- Non-functional: no `bash`/`jq`/`$CLAUDE_TOOL_INPUT` dependency in any load-bearing hook; cross-platform (Windows + Unix).

## Architecture
Claude Code delivers hook payloads as **JSON on stdin** (`tool_name`, `tool_input`, `hook_event_name`, …) — NOT via env vars (`CLAUDE_TOOL_INPUT` does not exist; verified vs `code.claude.com/docs/en/hooks.md`). `enforce-worktree.py:63` already reads stdin correctly and is the reference to mirror. Guards + quality gate + compact-saver become Python stdlib scripts. **[RT-C1]** The worktree gate is registered into the *user's* `.claude/settings.json` by `/cbr:setup`, but a plugin installs to `~/.claude/plugins/cache/<marketplace>/cbr/...`, and neither `${CLAUDE_PROJECT_DIR}` nor `${CLAUDE_PLUGIN_ROOT}` resolves inside user `settings.json` (confirmed by `enforcement.md:117-118`). Setup MUST resolve the installed plugin's **absolute cache path** at install time and write that literal path.

## Related Code Files
- Rewrite bash→Python, read stdin: `plugins/cbr/hooks/protect-files.sh` → `protect-files.py`; `guard-bash.sh` → `guard-bash.py`; `guard-webfetch.sh` → `guard-webfetch.py` (evidence: `:14`/`:10`/`:9` read `$CLAUDE_TOOL_INPUT` → empty → `exit 0`).
- **[RT-H1]** Also port jq→Python (same phase, so "no jq" is true, not "true for guards only"): `subagent-quality-gate.sh` → `.py` (`:20,25,26` use jq; still wired at `hooks.json:30`) and `compact-context-saver.sh` → `.py` (`:17,18` use jq). If a script cannot be ported this phase, it stays `.sh` and Phase 3's rename note is corrected accordingly — no phantom `.py`.
- Modify: `plugins/cbr/hooks/hooks.json` — point matchers at the new `python` scripts; remove 4 dangling `pixel-status-update.js` calls (`:17,:38,:87,:100`); resolve `PostCompact` vs `SessionStart:compact` reinject redundancy (keep one). **[RT-M1]** Use a launcher that resolves on both OSes (e.g. `py -3` on Windows / `python3` on Unix via a tiny shim, or a documented single prereq) — a bare `python` string satisfies neither reliably.
- **[RT-C3]** Modify EVERY always-on assertion (grep-guarded): `worktree/SKILL.md:33-40,104-108`; `worktree/references/enforcement.md:80-82,95-113,132`; `worktree/references/artifact-template.md:34`; **`plugins/cbr/README.md:29`** ("gate active whenever this plugin is enabled"). Rewrite all to opt-in.
- **[RT-H2]** Modify `worktree/evals/evals.json:14,20,26` (currently assert gate-denies-on-main as default + "no stay-on-main opt-out") to reflect opt-in reality; add a "gate-not-installed → offer setup" branch to the worktree skill precondition.
- **[RT-H3]** Create `plugins/cbr/hooks/settings_merge.py` (pure-Python helper that merges the gate registration into a settings.json dict) so `/cbr:setup` calls it AND `test_hook.py` can invoke it directly. Modify `setup/SKILL.md` to call the helper + resolve the absolute cache path + run a `python`/`py -3` availability doctor check.
- Fix: `plugins/cbr/hooks/enforce-worktree.py:81` — cross-drive `os.path.relpath` ValueError fails-open (allow). **[RT]** Scope the `except` to "relpath escapes repo_root ⇒ allow", not a blanket `except Exception`, so a future exception type can't silently widen the bypass. (Cross-drive fail-open itself was red-team-cleared as coherent with the script's documented stance.)
- **[RT-M6]** Note (do not silently diverge): dev `.claude/settings.json:28-39` registers `enforce-worktree.py` always-on for contributors. Either reconcile it to the same opt-in mechanism or add an explicit comment that dev dogfoods always-on by choice — record the decision so dev and shipped stop drifting.
- Modify: `evals/test_hook.py` — add guard stdin tests + a `settings_merge.py` unit test (the runnable wiring proxy) + `master`/`develop`/`notebook_path`/cross-drive cases.

## Implementation Steps
1. Port `protect-files.sh` → `.py`: read `json.load(sys.stdin)`, pull `tool_name`/`tool_input`, block secrets + lock files. **[RT-M2]** Match basenames **case-insensitively** (`casefold()`) — win32 FS is case-insensitive, so `.ENV`/`ID_RSA`/`Credentials.json` must be caught. Expand scope: `.npmrc`, `*.tfvars`, `.pgpass`, `aws credentials`. Emit deny via documented `permissionDecision` JSON.
2. Port `guard-bash.sh`/`guard-webfetch.sh` → `.py` (stdin JSON); keep heuristics, mark in-code as best-effort.
3. **[RT-H1]** Port `subagent-quality-gate.sh` + `compact-context-saver.sh` → `.py` (drop jq). Preserve exit-2 blocking + loop-guard semantics.
4. Update `hooks.json`: swap to the launcher shim for all ported scripts; delete the 4 `pixel-status-update.js` blocks; keep one post-compact reinject hook.
5. **[RT-C1/H3]** Write `settings_merge.py`; in `/cbr:setup`: resolve the plugin's absolute cache path, run the python-availability doctor, then call `settings_merge.py` to register `enforce-worktree.py` on `Edit|Write|NotebookEdit`. **[RT-M3]** Merge must be idempotent (detect existing registration before append) and use ONE canonical hook shape.
6. **[RT-C3]** Rewrite all always-on assertions (SKILL.md, enforcement.md, artifact-template.md, README.md) to opt-in; remove the fabricated always-on hooks.json snippet in enforcement.md.
7. **[RT-H2]** Rewrite `worktree/evals/evals.json` for opt-in; make the doctor read user settings.json and REFUSE to claim enforcement when the registration is absent.
8. Fix `enforce-worktree.py:81` except scoping.
9. Extend `test_hook.py`: guard stdin block/allow (incl. case), `settings_merge.py` idempotent-merge test, master/develop/notebook/cross-drive.

## Success Criteria
- [ ] Each guard, given a real stdin JSON payload, blocks the intended target (incl. mixed-case names) and allows others — proven by `test_hook.py`.
- [ ] Zero `jq` and zero `bash` dependency across guards, quality-gate, and compact-saver; `hooks.json` has zero dead references.
- [ ] **[RT-H3]** `settings_merge.py` is unit-tested for correct + idempotent registration (the runnable wiring proxy). The plan makes NO claim that a subprocess test invokes the `/cbr:setup` skill.
- [ ] **[RT-C3]** `grep -rn "active whenever\|live whenever\|auto-register" plugins/cbr/{README.md,skills/worktree}` returns 0 always-on claims; all worktree docs describe opt-in.
- [ ] `/cbr:setup` writes an absolute, resolvable cache path (not `${CLAUDE_PROJECT_DIR}`) and the doctor refuses to claim enforcement when the gate is not installed.
- [ ] `enforce-worktree.py` no longer false-denies cross-drive.

## Risk Assessment
- **[RT-H2] Accepted posture change (explicit):** with opt-in, a user who never runs `/cbr:setup` — including all headless `claude -p`/CI runs, which cannot answer the confirm — gets **no base-branch gate by default**. This intentionally relaxes the audit's "hard-mandatory" framing to "opt-in enforced"; the doctor must never overstate it. Accepted per locked-decision #2.
- **Behavior change:** guards go inert→active; a too-broad secrets matcher could block legitimate writes. Mitigate: exact/glob basename + allow-case tests.
- **[RT-M1] Launcher:** wrong interpreter name → hook fails to spawn → silent no-op (the original bug). Resolve the shim before claiming cross-platform "block"; note it is not mechanically testable here (no Unix/CI).
- **Rollback:** keep old `.sh` one commit / git revert; hooks.json is the switch.

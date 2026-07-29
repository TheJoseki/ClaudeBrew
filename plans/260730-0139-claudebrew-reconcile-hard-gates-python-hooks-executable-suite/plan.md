---
title: "ClaudeBrew reconcile - hard gates, python hooks, executable suite"
description: "Wire the hard gates that don't ship, port PreToolUse hooks to Python, make the imported SDLC suite executable, unify conventions."
status: pending
priority: P1
effort: "3-5d"
tags: [reconcile, hooks, sdlc, plugin]
created: 2026-07-30
---

# ClaudeBrew reconcile - hard gates, python hooks, executable suite

## Overview

Reconcile ClaudeBrew from "documented ideal" → "shipping reality." Audit found the project's *hard gates are mostly soft or absent in the shipped plugin*: worktree gate not wired, 3 PreToolUse guards are no-ops (read a non-existent env var instead of stdin — confirmed vs `code.claude.com/docs/en/hooks.md`), and the imported SDLC suite is not executable as written. Fix in 3 priority tiers.

**Source (read first):** `../reports/review-260730-0113-claudebrew-audit.md` — findings (verified + retracted), root cause, P0/P1/P2 recommendations, locked decisions.

## Locked decisions (user-confirmed 2026-07-30 — DO NOT reverse)

1. **Reconcile** imported suite (orchestrate/full-sdlc/10 agents/16 rules) to **SHIP** — pipeline must execute end-to-end.
2. **Worktree gate = OPT-IN** via `/cbr:setup` (writes `enforce-worktree.py` into user `.claude/settings.json`); NOT always-on in plugin `hooks.json`. Docs must describe opt-in.
3. **Hook runtime = Python stdlib** — guards read stdin JSON (`tool_name`/`tool_input`); drop `bash`/`jq`/`$CLAUDE_TOOL_INPUT`.
4. **Artifact-path = authority scheme** `docs/specs/<stage>/<TYPE>-<slug>.md`; migrate the minority (brainstorming/worktree/clean-code).

## Goals

| # | Goal | Priority |
|---|------|----------|
| 1 | Make the "hard gates" real: security guards enforce; worktree gate honestly opt-in; docs match behavior | P1 |
| 2 | Make the imported SDLC pipeline actually executable (no dead tools/paths/refs) | P1 |
| 3 | One artifact-path convention; finish "ClaudeKit"→"ClaudeBrew"; ship-hygiene (version, cruft, evals) | P2 |

## Phases

| # | Phase | Tier | Status |
|---|-------|------|--------|
| 1 | [Phase 1: Real gates + Python hooks](./phase-01-start.md) | P0 | Pending |
| 2 | [Phase 2: Suite executable](./phase-02-suite-executable.md) | P1 | Pending |
| 3 | [Phase 3: Consistency and polish](./phase-03-consistency-and-polish.md) | P2 | Pending |

Tier = audit priority (P0 correctness/security → P1 executability → P2 consistency). Phases are sequential to keep shared-file edits (`hooks.json`, `sdlc-conventions.md`) conflict-free.

## Success Criteria

- [ ] The 3 PreToolUse guards block on a real stdin payload (proven by test, incl. mixed-case names); zero bash/jq dependency across guards + `subagent-quality-gate` + `compact-context-saver`. Cross-OS launcher resolved; real-harness firing is acknowledged as not mechanically testable here (Phase 1 [RT-M1]).
- [ ] worktree docs (SKILL.md, enforcement.md, artifact-template.md, **README.md**) describe the gate as opt-in; `/cbr:setup` writes a *resolvable absolute* cache path (not `${CLAUDE_PROJECT_DIR}`); `settings_merge.py` is unit-tested for idempotent registration (the runnable wiring proxy — no claim a subprocess invokes the skill). **Default-without-setup = no gate is an accepted, documented posture** (locked decision #2).
- [ ] Imported pipeline runs end-to-end: `retro` can spawn+write; no dead file references in `orchestrator-agent.md`; security phase executes and its "PASS" claim is real; `context-inject` no longer double-invoked.
- [ ] Single artifact-path scheme across all skills; zero "ClaudeKit" occurrences; `plugin.json` version bumped; no dev cruft (`.coverage`) shipped.
- [ ] `claude plugin validate ./plugins/cbr` and `claude plugin validate .` pass.

## Constraints / Environment

- Windows win32, repo root `C:\Works\Tool\AWSClaw\ClaudeBrew`. Plugin repo — no conventional build/test runner; "source" = markdown skills + Python helpers.
- **Implementation must run in a git worktree** (project policy; currently on `main`). Planning writes only markdown to `plans/` so it is gate-exempt, but `/cbr:cook`/implementation of this plan must first `/cbr:worktree`.

## Red Team Review

Adversarial review (2026-07-30, 3 hostile reviewers: Security Adversary + Assumption Destroyer + Failure Mode Analyst). **14 findings, all evidence-backed (passed the file:line evidence filter), all adjudicated Accept and applied.**

| Sev | Count | Applied to |
|-----|-------|-----------|
| Critical | 3 | Phase 1 (C1 path, C3 doc-coverage), Phase 2 (C2 don't-corrupt-legit-refs) |
| High | 4 | Phase 1 (H1 port quality-gate, H2 default-off posture+doctor, H3 runnable wiring proxy), Phase 2 (H4 verify fork) |
| Medium | 7 | Phase 1 (M1 launcher, M2 casefold, M3 idempotent merge, M6 dev divergence), Phase 2 (M4 rationale), Phase 3 (M5 edit-list, M6 CLAUDE.md:76, M7 backlog) |

**Key risks addressed:**
- **C1** — opt-in gate would have registered `${CLAUDE_PROJECT_DIR}/...`, which does not resolve for installed users → re-created the silent no-op. Now: setup resolves the absolute cache path.
- **C2** — a grep-derived "fix 10 `.claude/` refs" would have corrupted `sdlc-conventions.md:241` (the user's own memory-tier doc). Now: only the 8 genuine plugin-path bugs are touched.
- **C3** — three always-on doc claims (incl. `README.md:29`) survived the phase meant to kill them. Now: all in the rewrite list + grep-guarded.
- **H1** — `subagent-quality-gate.sh`/`compact-context-saver.sh` jq no-ops would have shipped while Phase 3 renamed a phantom `.py`. Now: ported in Phase 1.
- **H2/H3** — "hard-mandatory" default silently deleted + unverifiable "wiring test." Now: default-off recorded as accepted posture, doctor forbidden from lying, wiring proven via an extractable `settings_merge.py`.

### Whole-Plan Consistency Sweep

Re-read `plan.md` + all 3 phase files after applying findings. Reconciled:
- **Python-port scope** now consistently 5 scripts (3 guards + quality-gate + compact-saver) across Phase 1 (scope), Phase 3 (rename by content, any extension), and plan.md success criteria.
- **Opt-in doc set** consistent (SKILL.md, enforcement.md, artifact-template.md, README.md, worktree evals) between Phase 1 and plan.md; default-off posture stated in Phase 1 risk + plan.md success + locked decision #2.
- **`.claude/` refs**: "8 genuine + 2 preserved" consistent between Phase 2 Related-Files, Impl-step 5, and success criterion (no residual "fix 10 / grep to 0" language).
- **`worktree/*` double-touch** (Phase 1 opt-in docs vs Phase 3 artifact-path) explicitly scoped to avoid clobber.
- No stale "verify wiring via subprocess", no residual "context7 also cited by sdlc-conventions", no phantom `.py` claims remain.

**Unresolved contradictions: none.** Two items are deferred-by-design (not contradictions): retro fork behavior (H4) and cross-OS launcher (M1) require harness verification *at implementation time* — the plan now instructs verify-first rather than asserting an outcome.

<!-- slug: claudebrew-reconcile-hard-gates-python-hooks-executable-suite -->

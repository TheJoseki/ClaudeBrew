# Backlog Registry

Durable follow-up log. The reconcile plan that produced these lives under `plans/`
and archives with its reports, so items it surfaced are tracked here instead.

## Open

_None._

## Completed — reconcile (2026-07-30)

### ✅ 1. Unify the artifact-path convention
Converged every stage on `docs/specs/<stage>/<TYPE>-<slug>.md`. `brainstorming` → `docs/specs/brainstorms/BRAINSTORM-`; `worktree` → `docs/specs/worktrees/WORKTREE-`; the 5 `docs/decisions/` knowledge skills → `docs/specs/decisions/ADR-`; `parallel-agents` `REQ-` → `requirements/SRS-`. New stages added to `rules/sdlc-conventions.md`; the brainstorming/worktree evals migrated (the caveat asserted). 0 date-based paths remain; `claude plugin validate` passes.

### ✅ 2. Author `evals/evals.json` for skills that lacked them
All **40/40** skills now ship `evals/evals.json` (was 2) — each 2 positive triggers + 1 boundary/negative that routes to the right sibling. Runner: `evals/triggers/run_triggers.py` (Windows caveats in `CLAUDE.md`).

### ✅ 3. Add `TRIGGER:` / `NOT FOR:` guards to overlapping knowledge skills
Added to `tdd-workflow`, `clean-code`, `code-review-checklist`, `architecture`, `api-patterns`, `database-design`, `testing-patterns`. Every `description` scalar kept **double-quoted** (the load-bearing constraint), so `claude plugin validate` stays at 0 frontmatter errors.

# Backlog Registry

Durable follow-up log for deferred work. The reconcile plan that produced these
lives under `plans/` and will be archived with its reports, so the deferred items
it surfaced are tracked here instead of dying with the plan.

Each entry: what, why it matters, rough effort, affected files, and any caveat
that will bite whoever picks it up.

## Open

### 1. Unify the artifact-path convention

- **What:** Converge every stage on a single handoff-artifact path shape,
  `docs/specs/<stage>/<TYPE>-<slug>.md`.
- **Why:** Three conventions currently coexist, so a reader can't predict where a
  stage's artifact lands or which the next stage consumes. `brainstorming` writes
  `docs/specs/YYYY-MM-DD-<topic>-<stage>.md`, `clean-code` writes `docs/decisions/`,
  `worktree` assumes the brainstorming path, and the imported SDLC suite writes
  `docs/specs/requirements/SRS-<feature>.md`, `docs/specs/detail-design/TECH-*`, etc.
- **Effort:** Medium (touches multiple skills + their references, plus one eval).
- **Affected files:**
  - `plugins/cbr/skills/brainstorming/SKILL.md` and references (current `docs/specs/YYYY-MM-DD-*`)
  - `plugins/cbr/skills/clean-code/SKILL.md` (`docs/decisions/clean-code-[YYYYMMDD].md`)
  - `plugins/cbr/skills/worktree/` (consumes the brainstorming path)
  - `plugins/cbr/rules/sdlc-conventions.md` (the canonical artifact-path table for the imported suite)
  - the imported stage-executor skills that write `SRS-*` / `TECH-*`
- **CAVEAT:** `plugins/cbr/skills/brainstorming/evals/evals.json` asserts the OLD path
  (`docs/specs/<date>-...-brainstorm.md`). Migrate that assertion in the same change
  or the brainstorming eval will fail against the new convention.

### 2. Author `evals/evals.json` for the skills that lack them

- **What:** Add representative trigger/behavioral eval prompts to the skills that
  ship no `evals/evals.json`.
- **Why:** Only `brainstorming` and `worktree` currently ship evals; ~38 of the ~40
  skills have none, so their trigger reliability (does the description fire on the
  right request, stay quiet on the wrong one?) is entirely unverified.
- **Effort:** Large in aggregate, small per skill (one `evals.json` each); can be
  done incrementally, prioritizing overlapping/ambiguous skills first.
- **Affected files:** `plugins/cbr/skills/<name>/evals/evals.json` (new, per skill).
  Follow the shape in `plugins/cbr/skills/brainstorming/evals/evals.json`; runner is
  `evals/triggers/run_triggers.py` (see the Windows caveats in `CLAUDE.md`).

### 3. Add `TRIGGER:` / `NOT FOR:` guards to overlapping knowledge skills

- **What:** Add explicit `TRIGGER:` and `NOT FOR:` disambiguation lines to the
  knowledge/reference skills whose scopes overlap (e.g. `architecture`,
  `clean-code`, `database-design`, `testing-patterns`, `ui-ux-pro-max`,
  `vulnerability-scanner`), so the router picks one cleanly.
- **Why:** Overlapping descriptions cause mis-triggering between sibling knowledge
  skills; explicit guards sharpen the boundary.
- **Effort:** Small–medium (frontmatter edits across the overlapping set).
- **Affected files:** `plugins/cbr/skills/<name>/SKILL.md` frontmatter.
- **CAVEAT (load-bearing):** The `TRIGGER:`/`NOT FOR:` text contains `: `, which
  breaks YAML unless the `description` scalar stays **double-quoted**. Unquoting it
  is exactly what caused the 33 frontmatter parse failures the reconcile just fixed —
  keep every `description` double-quoted and re-run `claude plugin validate ./plugins/cbr`.

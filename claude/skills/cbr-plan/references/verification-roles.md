# Verification Roles

Language-agnostic roles for verifying a plan/design artifact against the *actual* codebase, shared
by both `cbr-plan` subcommands (`red-team` for evidence-backed adversarial review, `validate` for
the pre-interview verification pass). The principle: `user asks → cbr-plan writes → audit-verify →
report`, not `write → report done`. CBR's SRS/BASIC/TECH content is otherwise trusted as written;
these roles give it a fact-checked-against-the-repo guarantee it doesn't have by default.

**Where a role runs depends on the caller.** In `validate`'s Step 2.5 the verification pass is a
*standalone* step — spawn `cbr-reviewer` for it (grep/glob fact-checking, per D9; not a
creative-divergence task). In `red-team` the verification role instead **rides with each lens
reviewer** as a methodology it applies using its own grep/glob/Bash tools — and both pool agents
(`cbr-reviewer` and `cbr-strategist`) carry those tools, so a strategist-held lens (Assumption
Destroyer, Scope Critic) applies its paired role too. The role is a fact-checking *method*, not a
second agent.

## Tiering (auto-scale by size)

Count `PLAN.md`'s phases (fall back to `BASIC.md`'s module count for a phase-free stream-light plan):

| Phases | Tier | Active roles | Spot-check budget |
|--------|------|-------------|-------------------|
| 1-2 | Light | Fact Checker | 5 claims/phase |
| 3-4 | Standard | Fact Checker + Contract Verifier | 10 claims/phase |
| 5+ | Full | all 4 roles | 15+ claims/phase |

## Role: Fact Checker

**Purpose**: every file path, symbol, endpoint, and config key the artifact cites actually exists.
**Method**: sample N claims/phase (per budget); `grep -rn "{symbol}" .` for symbols, `Glob "{path}"`
for paths; grep route definitions for endpoints, env/config for config keys.
**Red flags**: wrapper/manager/handler names grep returns nothing for; a "centralized" module actually
scattered; paths renamed since the SRS/TECH was written.
**Output per claim**: `VERIFIED (file:line)` | `FAILED (not found)` | `UNVERIFIED (ambiguous)`.

## Role: Flow Tracer

**Purpose**: behavioral claims ("X triggers Y", "guard runs before handler", a BASIC §6.5 flow's step
order). **Method**: start at the claimed entry point, read the real path (entry → guards → branch →
target); list early returns / middleware / listeners; for async, check await/Promise ordering; verify
causality (A invokes B) vs mere correlation (both in one file).
**Red flags**: "X triggers Y" with no shared call path; missing intermediate hop; async assumed sync.
**Output**: the traced path with `file:line`, or `FAILED` with the actual flow.

## Role: Scope Auditor

**Purpose**: state additions (new fields, context values, singletons, env vars) respect lifetime
boundaries. **Method**: grep the target struct/class for ALL instantiation sites; classify lifetime
(request / session / process-global); check shared-state leaks across isolation boundaries; verify no
existing state already serves the purpose.
**Red flags**: "add a field to X" when X is a shared singleton; new state duplicating existing under a
different name; module-level vars in request-handling code.
**Output**: lifetime classification with instantiation sites, or `FAILED` with the leak.

## Role: Contract Verifier

**Purpose**: interface changes (endpoints, signatures, config schemas, exports) account for ALL
consumers. **Method**: `grep -rn "{name}" .` to enumerate every caller — **state the count, list them**,
never "update all callers"; if >10, list the first 10 + total; check tests, imports, re-exports
downstream, and config/env/CI/CLI-help upstream.
**Red flags**: plan says "3 callers", grep finds 7; missing test updates; re-exported types not updated
at barrels; CLI help referencing old names.
**Output**: caller list with `file:line`, compatibility assessment, or `FAILED` with the missing callers.

## Verification output format

Append to the artifact's `## Validation Log`, or fold into red-team findings:

```markdown
### Verification Results
- **Tier:** Light | Standard | Full
- **Claims checked:** N  ·  **Verified:** N  ·  **Failed:** N  ·  **Unverified:** N

#### Failures
1. [Fact Checker] `src/utils/auth.ts` — not found; actual: `src/lib/auth.ts`
2. [Contract Verifier] `parseConfig()` — plan says 3 callers, found 7
```

## Whole-Plan Consistency Sweep

**Purpose**: stop an iterative validate/red-team edit from fixing one artifact while leaving a stale
claim elsewhere in the SRS → BASIC §6.5 → TECH §4.3 → PLAN chain. Run after **any** edit either
subcommand makes.

**Inputs**: `plan/PLAN.md`, every design artifact present in the stream, and the current session's
new decisions / accepted findings.

**Method**:
1. Re-read all artifacts after applying edits.
2. Build a decision-delta list: renamed fields/APIs/files/tags/scopes; changed decisions or rejected
   assumptions; changed phase order / dependencies / ownership / success criteria.
3. Search every artifact for old terms, superseded assumptions, and duplicate embedded drafts from
   each delta.
4. Reconcile across files, not only the one that triggered the finding — especially the BF-xxx / §6.5
   / §4.3 traceability chain (the SRS→BASIC→TECH→ITC link `cbr-verify` consumes).
5. Check `PLAN.md` overview, phase text, requirements, steps, success criteria, risk notes, and the
   red-team/validation logs for contradictions.
6. A conflict you cannot resolve with current evidence → add to unresolved questions, **do not**
   recommend `cbr-implement` yet.

**Output** (append under the current `## Validation Log` or `## Red Team Review`):

```markdown
### Whole-Plan Consistency Sweep
- Files reread: PLAN.md, SRS.md, BASIC.md, TECH.md
- Decision deltas checked: N
- Reconciled stale references: N
- Unresolved contradictions: N
```

If `Unresolved contradictions > 0`, list each with its affected files and ask the user before any
downstream stage.

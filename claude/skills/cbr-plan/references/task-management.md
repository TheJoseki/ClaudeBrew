# Task Hydration — bridging `PLAN.md` and live tasks

The **plan is persistent, tasks are ephemeral.** `plan/PLAN.md` in the stream is the durable source
of truth; `TaskCreate`/`TaskUpdate`/`TaskGet`/`TaskList` entries live only for the session. Hydration
bridges the two so `cbr-implement` can track live progress against a plan written in an earlier
session — the Hydrate → Work → Sync-back cycle:

```
plan/PLAN.md  ──hydrate──►  live tasks        (cbr-plan's Plan phase, on write)
  [ ] Phase 1                pending
  [ ] Phase 2                pending
                               │ work          (cbr-implement, real-time)
                               ▼
plan/PLAN.md  ◄──sync-back──  task updates      (cbr-implement, Step 4 / Hand-off)
  [x] Phase 1                completed
  [ ] Phase 2                in_progress
```

**Fallback (never block on tasks).** The Task tools are unavailable in some environments (e.g. the
VSCode extension's `isTTY` guard). If any Task call errors, drop straight to **plan-file-as-source-of-
truth**: `cbr-implement` reads `PLAN.md`'s unchecked `[ ]` items directly and syncs `[x]` back by
editing the file. Hydration is an optimization, not a requirement — the plan file alone is always
enough.

## When to hydrate (the 3-Task Rule)

- **Default: on** — `cbr-plan`'s Plan internal phase hydrates after writing `PLAN.md`.
- **Skip when `PLAN.md` has fewer than 3 phases** — the tracking overhead exceeds the benefit for a
  trivial plan; just implement it directly.
- **Skip under `--fast`** — the low-ceremony mode folds AC into `PLAN.md` and doesn't hydrate.

## Hydrate — `cbr-plan`'s Plan phase (on write)

After writing `plan/PLAN.md`, create one task per phase (CBR's `PLAN.md` is a single file with
`### Phase N` sections, not claudekit's multi-file `phase-*.md` — so a task maps to a phase section,
and its `phaseFile` metadata is the one `plan/PLAN.md` path plus the phase id):

```
TaskCreate(
  subject: "Phase 2 — payment service + endpoints",   // imperative, <60 chars
  activeForm: "Building the payment service",
  description: "PaymentService.createIntent/confirm/refund + POST /payments. See plan/PLAN.md Phase 2.",
  metadata: { phase: 2, priority: "P1",
              streamDir: "docs/streams/payment-20260813/",
              planFile: "docs/streams/payment-20260813/plan/PLAN.md" }
)
```

Then chain the sequenced phases with `addBlockedBy` (a later `TaskUpdate` referencing the earlier
phase's task id), so a phase auto-unblocks when its predecessor completes. Truly independent phases
(the `--parallel` groups in `plan-structure.md`) share no blocker.

- **Required metadata**: `phase`, `priority`, `streamDir`, `planFile`. **Optional**: `step`,
  `critical`, `riskLevel`.
- For a high-risk step *inside* a phase, an extra step-level task is worth it — same shape, add
  `step: "2.3"`, `critical: true`, and an `addBlockedBy` on its phase's task.

## Pick up — `cbr-implement`'s Implement phase (entry)

At the top of its Implement internal phase, `cbr-implement`:

1. `TaskList` — **same session**: the tasks `cbr-plan` hydrated are already there; pick them up, don't
   re-create.
2. `TaskList` returns empty — **cross-session** (a fresh `cbr-implement` run resuming an old plan):
   re-hydrate from `PLAN.md`'s unchecked `[ ]` items (already-`[x]` items are done, skip them).
3. Any Task call errors — **fallback**: work straight from `PLAN.md`'s unchecked items; no tasks.

Mark a task `in_progress` when you start it, `completed` when its done-condition is met.

## Sync-back — `cbr-implement`'s Step 4 / Hand-off (after the work, before it stops)

`cbr-implement` has no step literally named "finalize" — its sync-back attaches at **Step 4
(Self-Check + Work Log) → Hand off**, right before the skill stops:

1. `TaskUpdate` any remaining session tasks to their real status.
2. **Full-plan backfill sweep**: reconcile completed tasks against `PLAN.md` *by metadata* (`phase`),
   flip stale `[ ]` → `[x]` for every completed phase — **across all phases, not just the current
   one** — and update `PLAN.md`'s status/progress line from the actual checkbox state.
3. Any completed task that can't be mapped back to a `PLAN.md` phase → report the unresolved mapping,
   don't silently claim completion.
4. Then the mandatory stream upkeep (`{{CBR_ROOT}}/docs/references/sdlc-reference.md`): update
   `STREAM.md`'s board to match.

## Quality checks after hydration

- The `addBlockedBy` chain has no cycle.
- Every phase has a task (or the whole thing was skipped by the 3-Task Rule).
- Required metadata present on each task.
- Task count matches `PLAN.md`'s unchecked `[ ]` phase count.
- Report: `✓ Hydrated N phase tasks with dependency chain` (or `✓ <3 phases — hydration skipped`).

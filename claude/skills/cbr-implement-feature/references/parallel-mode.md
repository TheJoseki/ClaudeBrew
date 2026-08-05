# Parallel Mode — Slice by File Ownership

> Shared by every execution skill (`implement-feature`, `design-screen`,
> `design-function`, `unit-test` Mode A, `integration-test` Mode A).
> Other skills reference this file at
> `{{CBR_ROOT}}/skills/cbr-implement-feature/references/parallel-mode.md` —
> do not copy it.

Parallel mode is **opt-in**: it runs only when the invocation carries
`--parallel`. Without the flag the skill works single-stream in the main
context, which is the correct default for anything small or entangled.

---

## Who the workers are

Parallel workers are **always `cbr-developer`** — the pool's implementation
capability, which already carries the file-ownership persona and a `model`
tier.

**`cbr-reviewer` and `cbr-tester` are reserved for gate verdicts and must never
be spawned as parallel workers.** Their value at G4/G5a/G6/G7 is that they have
not seen the work being judged; using them to *produce* work destroys exactly
that. If no agent pool is installed, fall back to `general-purpose` — never to
`reviewer`/`tester`.

---

## Step 1 — Decide whether the scope splits at all

Split only when the slices are genuinely independent. Run single-stream when
any of these is true:

- Slices would touch the same file (shared router, barrel index, migration
  sequence, generated artifact, global config, locale files).
- One slice's output is the next slice's input (schema → service → controller
  is a *chain*, not a fan-out).
- The whole job is 1–2 files. Coordination cost exceeds the win.
- Scope is unclear. Ambiguity plus concurrency multiplies the damage.

**Two or fewer slices is not worth parallelizing.** Prefer 3–5.

Natural seams by skill:

| Skill | Splits cleanly by |
|-------|-------------------|
| `implement-feature` | Independent modules / bounded contexts; backend module vs frontend feature |
| `design-screen` | One screen (or screen group) per worker |
| `design-function` | One bounded context / service boundary per worker |
| `unit-test` (Mode A) | One test target per worker (service, controller, component) |
| `integration-test` (Mode A) | One workflow / endpoint chain per worker |

## Step 2 — Assign disjoint file ownership

Before spawning anything, write the ownership map. Every file that will be
created or modified belongs to **exactly one** worker.

```
Worker 1 — orders module
  OWNS: src/orders/**, tests/orders/**
Worker 2 — payments module
  OWNS: src/payments/**, tests/payments/**
Shared / NOT OWNED (main context handles after synthesis):
  src/app.module.ts, src/router.ts, locales/*.json, migrations/
```

Files no worker owns are integrated by the main context in Step 4. That is the
rule that keeps concurrent edits from colliding: **shared files are never
delegated.**

## Step 3 — Spawn the workers

Spawn all workers in a **single message** so they run concurrently. Each spawn
prompt carries the four things `cbr-developer` expects:

1. The spec section for that slice (path + section, not pasted content).
2. Its **File Ownership** list — the exact paths it may create/modify.
3. Acceptance criteria for the slice.
4. Its work-log path, e.g. `docs/streams/[feature]-[YYYYMMDD]/work-logs/DEV-[slice].md`.

```
Agent(subagent_type="cbr-developer",
      prompt="Implement the <slice> slice of <feature>.
              SPEC: docs/streams/<feature>-<YYYYMMDD>/design/TECH.md § <section>
              FILE OWNERSHIP: <explicit paths — you may modify nothing else>
              ACCEPTANCE: <criteria>
              WORK LOG: docs/streams/<feature>-<YYYYMMDD>/work-logs/DEV-<slice>.md")
```

### File Ownership Rules (hard — restate these in every spawn prompt)

- **NEVER modify a file not listed in your File Ownership section.** Read others
  for context only.
- If you need to touch an unowned file, or detect a conflict with another
  worker's files, **STOP and report immediately** — do not edit around it.
- Match existing patterns/conventions in the files you touch; do not "improve"
  adjacent code.

## Step 4 — Synthesize in the main context

1. Collect every worker's `Status:` line and work log.
2. **Any `BLOCKED` / conflict report → stop and surface it to the user.** Do not
   re-spawn a worker over the same files hoping the conflict resolves itself.
3. Integrate the shared/unowned files yourself (registrations, routing, barrel
   exports, locale merges, migration ordering).
4. Run the skill's normal self-check across the merged result — each worker only
   verified its own slice, so integration breakage shows up only here.
5. Write the skill's single consolidated artifact. N workers produce **one**
   stage artifact, not N.

## Step 5 — Stop

Parallel mode changes **how the stage is executed, not what happens next.** The
skill still stops after its own artifact. Do not spawn `review-code`,
`unit-test`, or any downstream stage — the user decides when the next stage
begins.

# The input-contract — detecting the source of truth

`plan-writing`'s Step 1 is mandatory: a plan is only as trustworthy as the source it is
built on. This reference is the full method behind the priority table in `SKILL.md` — how
to detect the source of truth, what to do when several exist, and how to refuse cleanly
when there is nothing to plan from.

## Why this is a hard gate

The orphan version of this skill planned from `$ARGUMENTS` — whatever prose the user typed.
That let it fabricate scope: invent requirements the code never had, or plan against a
half-remembered idea. The input-contract removes that failure mode. Every plan names the
concrete artifact (or the code) it was built from, so the next stage — and the user — can
trace each task back to a real source.

## The priority order (most authoritative first)

1. **SRS** — `requirements/SRS.md`. Approved requirements. The greenfield / spec-first
   source; highest authority because a human approved it at G1.
2. **Brainstorm** — `brainstorm/BRAINSTORM.md`. An approved *direction* that predates a
   formal SRS. Enough to plan a spike or an early slice from.
3. **Research report** — `research/RES-*.md`. A scout's or the `researcher` agent's findings
   about existing code, prior art, or a library. This is the brownfield bridge: it turns
   "the code is the source of truth" into a readable artifact a plan can cite.
4. **Code** — the repository itself, read via `Glob`/`Grep`. The brownfield / maintenance
   source: when the code *is* the spec, plan the change directly against it.

The order reflects authority, not preference — a present SRS outranks a brainstorm because
it is downstream and approved. It is **not** "use only the top one": see below.

## Resolution rules

**Exactly one source present** → use it directly. State in the plan's overview which source
it was built from (e.g. "Source of truth: `requirements/SRS.md`").

**More than one source present** → this is a never-guess moment. Do **not** silently apply
the priority order and pick the top one — the priority order breaks *ties of authority*, it
does not decide *intent*. Surface what you found and ask:

> Pre-analyzed `AskUserQuestion`, one question, options grounded in what is actually on disk:
>
> - **Header:** "Plan from"
> - **Question:** "I found more than one source of truth for this work. Which should the plan
>   be built from?"
> - **Options** (only those that exist):
>   - `SRS (requirements/SRS.md)` — plan against approved requirements.
>   - `Brainstorm (brainstorm/BRAINSTORM.md)` — plan against the approved direction.
>   - `Research report (research/RES-<topic>.md)` — plan against the code findings.
>   - `Code (existing implementation)` — plan a change directly against the code.
>   - (The user may pick one as primary and mention another as a constraint — e.g. "SRS, but
>     honor the research report's perf finding". Record both in the plan.)

State the chosen source in the plan, and — if the user folded in a secondary source as a
constraint — note that too.

**Nothing to plan from** → **refuse to plan.** Code counts as a source of truth only when the
user **points you at the specific area to change** — a bare feature name ("plan the billing
system") is not a pointer, even if a same-named directory happens to exist; scouting it into
"familiar" to plan anyway is the fabricate-scope failure this gate exists to stop. When there is
no artifact and no pointed-at code, inventing scope is exactly that failure. Respond along these
lines:

> "There's no source of truth to plan from here — no `requirements/SRS.md`, no
> `brainstorm/BRAINSTORM.md`, no `research/RES-*.md`, and I can't safely plan against code I
> haven't been pointed at. Run the `explore` / scout skill or the `researcher` agent first to
> produce a `research/RES-*.md`, or start with `brainstorming` if the direction isn't decided
> yet — then I can plan from it."

Do not fabricate requirements, and do not silently plan against the whole repo. (The
`explore` scout skill is greenlit as the next stream after this one; until it ships,
`researcher` is the scout front-door.)

## Greenfield is not regressed

When `requirements/SRS.md` is present it is the top-priority input. The established
`brainstorming → analyze-requirement (SRS) → plan-writing` flow is unchanged: the plan
consumes the SRS first, exactly as before the rewrite. The input-contract only *adds*
lower-priority sources (brainstorm, research, code) for the flows that had none — it never
demotes the SRS.

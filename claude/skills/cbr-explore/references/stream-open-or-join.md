# Open or join the work-stream — the topic-slug law

`explore` is one of the SDLC's three stream **openers**. All three obey one law, stated
normatively in `rules/references/sdlc-reference.md` ("Stream openers & lanes"):

> **Open-if-none / join-if-exists — resolved by topic-slug.** Before opening a stream, check
> whether one already governs *this topic*. If it does, JOIN it. If not, OPEN a new one — even
> if unrelated streams are in flight.

The three openers and their lanes:

| Opener | When it opens | Lane |
|--------|---------------|------|
| `cbr-brainstorming` | a new idea with no matching stream | `greenfield` |
| `cbr-explore` | a scout/discovery with no matching stream | `brownfield` (code) / `greenfield` (prior-art) |
| `cbr-plan-writing` | brownfield maintenance with no matching stream (stream-light) | `brownfield` |

## Deriving the slug

Reduce the topic to a short, stable `[a-z0-9-]` kebab slug (invariant 5): lowercase, spaces →
`-`, strip every character outside `[a-z0-9-]`, collapse repeats. This is the same slug the
stream folder is named with (`docs/streams/<slug>-<YYYYMMDD>/`) and the same shape
`sdlc_state.py`'s `slug_from_stream_dir` recovers from a folder name. Sanitizing here is also
the path-traversal guard — a slug can never contain `/`, `.`, or `..`.

## The lookup (prose, no Python call)

1. `Glob docs/streams/*` → each entry is `<existing-slug>-<YYYYMMDD>`.
2. For each, recover `<existing-slug>` by stripping the trailing `-<YYYYMMDD>` date.
3. Compare to the target `<slug>`:
   - **exactly one match → JOIN** that stream.
   - **no match → OPEN** a new stream.
   - **more than one match → ask** (`AskUserQuestion`) which to join, and **always** include an
     explicit *"open a new stream for this topic"* option (never force a wrong join).

Do **not** use `sdlc_state.py resolve_active_feature()`: it answers "what is the single
in-flight stream in the whole repo", not "does a stream govern THIS topic" — it is topic-blind,
and it is a hook-internal library with no entry point a prose skill can call. The glob-and-slug
match above is the mechanism.

## OPEN (no match)

1. Create `docs/streams/<slug>-<YYYYMMDD>/` and its `research/` subdir.
2. Scaffold the manifest `STREAM.md` from `{{CBR_ROOT}}/docs/_templates/STREAM.md`.
3. Set `lane:` in the manifest frontmatter — `brownfield` for a code-scout, `greenfield` for a
   prior-art scout. (`lane:` is descriptive metadata; gate authority stays with
   `sdlc_state.py`.) A later `cbr-brainstorming` on the same slug will JOIN this stream.

## JOIN (exactly one match) — strictly additive

Joining an existing stream **must not destroy** what another opener authored:

- **Never re-scaffold `STREAM.md`** from the template — it would wipe the existing membership
  table and task board. Append your RES row and a board entry only.
- **Never overwrite** an existing artifact. A re-scout of the same topic writes a **new round**
  (`RES-<topic>-R[n+1].md`, see `res-report.md`), it does not clobber `R1`.
- Stamp `stream: <slug>-<YYYYMMDD>` in the RES frontmatter so it carries the stream identity.

The same additive discipline binds `cbr-brainstorming`'s JOIN branch (it appends
`brainstorm/BRAINSTORM.md`, never re-scaffolds the manifest).

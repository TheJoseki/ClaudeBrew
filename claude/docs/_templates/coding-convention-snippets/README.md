# Coding-Convention Snippets

Progressive-disclosure companion to `../CODING_CONVENTION.md`. The core convention file is **stack-neutral** — naming, imports, comments, error handling, tests, git — so it holds no matter the framework. The concrete code exemplars (module / service / component skeletons) live here, one file per stack, and load **only when needed**: a skill reads the project's stack from `PROJECT.md` (the Backend / Frontend / ORM fields) and pulls in the single matching `<stack>.md`, instead of the core carrying every framework's boilerplate.

## Selecting a snippet

Match `PROJECT.md` → Tech Stack to a file name:

- `<stack>.md` uses a lowercase, hyphenated stack tag — `[backend]-[frontend].md`, or a single-tier tag when only one applies. Examples: `nestjs-vue.md`, `django-react.md`, `fastapi.md`, `express.md`.
- No exact match? Copy `generic-example.md`, adapt the skeletons to the detected stack, and save it under the matching `<stack>.md` name so the next feature reuses it.

## Files

- `generic-example.md` — a framework-agnostic **example** (one module + service + UI-component skeleton) showing the *shape* the core convention implies. Copy and adapt; it is a starting point, not a mandate.
- `<stack>.md` — per-stack exemplars a project adds as its stack is pinned.

# Generic Example Snippet

> **This is an EXAMPLE to copy and adapt — not a mandate.** It shows the *shape* the stack-neutral `CODING_CONVENTION.md` implies: one feature module, one service, one UI component. The syntax is deliberately pseudo-code — framework decorators, imports, and types are omitted on purpose. Replace `<placeholders>` and the pseudo-syntax with your actual stack (see `PROJECT.md`), then save the result as `docs/_templates/coding-convention-snippets/<stack>.md` for reuse.

## 1. Feature module skeleton

A feature groups its own HTTP surface, business logic, data access, types, and tests — grouped by feature, not by technical type (core §1):

```
<feature>/
  <feature>.routes.<ext>       # HTTP surface: validate input -> call service -> shape response
  <feature>.service.<ext>      # business rules; no framework / HTTP types leak in here
  <feature>.repository.<ext>   # data access; the only layer that talks to the ORM / DB
  <feature>.types.<ext>        # entity + DTO shapes
  <feature>.spec.<ext>         # co-located tests
```

## 2. Service skeleton

Grouped imports (core §2), a doc comment on the public method (core §3.2), section dividers, and loud error handling (core §4):

```
// -- imports: framework core / third-party / project-shared / same-module / types --

/**
 * List <entities> for the current user, paginated.
 * @param query - page, pageSize, search
 * @returns { results, total, page, pageSize }
 * @throws NotFoundError when <precondition> fails
 */
async function list(query) {
  // -- validate / default --
  const page = query.page ?? 1
  const pageSize = query.pageSize ?? DEFAULT_PAGE_SIZE

  // -- fetch: delegate persistence to the repository --
  const [results, total] = await repository.findAndCount(query)

  // -- shape the response --
  return { results, total, page, pageSize }
}
```

## 3. UI component skeleton

State-first structure with all four async states handled (loading / error / empty / data):

```
// -- props / inputs --
// -- local state --
// -- derived / computed --
// -- effects / lifecycle: load on mount --
// -- handlers --
// -- view: render loading, error, empty, and data states --
```

Adapt each `<placeholder>` and the pseudo-syntax to the real framework, keeping the grouped imports, doc comments, section dividers, and four UI states the core convention requires.

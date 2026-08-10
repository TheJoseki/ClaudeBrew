# Coding Convention — [PROJECT_NAME — e.g. Acme Orders]

> Created/updated by `design-function`; consumed by `implement-feature`, `design-screen`, and `fix-bug`; enforced at the REVIEW checkpoint by `review-code` + a fresh `cbr-reviewer` verdict.
> Copy this template to `docs/CODING_CONVENTION.md` and fill in per project.
> Reference: `docs/CODING_RULES.md` (enforcement rules), `docs/ARCHITECTURE.md` (system design).

This file is the **stack-neutral** core — naming, import order, comments, error handling, tests, and git conventions that hold regardless of framework. **For code exemplars** (module / service / component skeletons), load `coding-convention-snippets/<stack>.md` matching the stack detected in `PROJECT.md` (progressive disclosure — see that folder's `README.md`).

---

## 1. File & Folder Naming

Pin one casing per artifact class and keep it consistent across the whole tree.

| Artifact | Casing | Pattern / example |
| --- | --- | --- |
| Source folders | [FOLDER_CASE — e.g. kebab-case] | [e.g. user-profile/, order-items/] |
| Modules / feature units | [MODULE_CASE — e.g. kebab-case] | [e.g. orders/orders.<role>.<ext>] |
| Classes / types | PascalCase | [e.g. OrderService, OrderStatus] |
| UI components / views | [COMPONENT_CASE — e.g. PascalCase] | [e.g. OrderList, StatusBadge] |
| Functions / variables | camelCase | [e.g. fetchOrders, pageSize] |
| Constants / enum values | [CONST_CASE — e.g. UPPER_SNAKE] | [e.g. MAX_PAGE_SIZE, DEFAULT_LIMIT] |
| Test files | [TEST_FILE_PATTERN — e.g. <name>.<test-suffix>] | [e.g. orders.spec.<ext>, order-store.test.<ext>] |

- One primary export per file; the file name matches that export.
- Group by **feature / module**, not by technical type, unless [layout exception — e.g. the framework mandates a fixed layout].
- Shared / cross-cutting code lives under [SHARED_DIR — e.g. common/, shared/, lib/].

## 2. Code Structure

- One responsibility per unit: a function does one thing; a class/module owns one concern.
- Keep functions short — [FUNCTION_MAX — e.g. ≤50 lines]; extract a helper rather than nest [NEST_MAX — e.g. 3] levels deep.
- No magic numbers or string literals — name them as constants ([CONST_CASE — e.g. UPPER_SNAKE]).
- No dead code, commented-out blocks, or unreachable branches in a commit.
- Prefer pure functions and explicit inputs/outputs over hidden shared state.

## 3. Import Ordering

Order imports in named groups with a blank line between groups. Pin the group order once; a linter / formatter [e.g. eslint-plugin-import, ruff, gofmt] should enforce it.

1. [GROUP_1 — e.g. language/runtime + framework core]
2. [GROUP_2 — e.g. third-party libraries]
3. [GROUP_3 — e.g. project-internal shared (utils, types, config)]
4. [GROUP_4 — e.g. same-module / relative imports]
5. [GROUP_5 — e.g. type-only imports, if the language separates them]

- No deep relative chains (`../../../..`) — use [PATH_ALIAS — e.g. an @/ root alias] past [DEPTH — e.g. 2] levels.
- No unused imports; no side-effect imports except [ALLOWED_SIDE_EFFECTS — e.g. global styles, polyfills].

## 4. Comments & Docs

### 4.1 Section dividers

Separate logical zones inside a file with a consistent divider: [DIVIDER — e.g. `// ── State ──`, `# --- helpers ---`].

### 4.2 Doc comments (public API)

Document every exported function / class with the language's doc-comment format [DOC_FORMAT — e.g. JSDoc, Python docstring, GoDoc]. State intent, params, return, and error conditions:

```
[DOC_COMMENT_EXAMPLE — e.g.
/**
 * [ACTION] a [entity]. [what it validates / does]
 * @param [name] - [meaning]
 * @returns [meaning]
 * @throws [error] when [condition]
 */]
```

Comment the **why**, not the **what** — code shows what happens; comments explain intent, trade-offs, and non-obvious constraints.

### 4.3 TODO markers

Tag with a category and a resolution anchor so markers stay grep-able and never silent:

- `TODO([CATEGORY — e.g. feat|perf|fix]): [description] — [ANCHOR — e.g. issue id / milestone]`
- `FIXME: [known bug or race condition]`
- `HACK: [temporary workaround] — [reason]`

Committed code carries no bare `TODO` / `FIXME` / debug print unless it names an anchor (checked at REVIEW).

## 5. Error Handling

- Fail loud, never silent: no empty catch blocks; every swallowed error is logged or rethrown with context.
- Throw typed / domain errors, not bare strings — [ERROR_TYPE — e.g. HttpException, an AppError subclass].
- User-facing messages via [MESSAGE_SOURCE — e.g. project i18n keys]; internal logs in English with the failing input's identifier (never secrets).
- Map errors to the project's standard response shape: [ERROR_SHAPE — e.g. { statusCode, message, error }] (see `docs/API_DESIGN.md`).
- Async: no unhandled rejections — every awaited path has an error owner (try / catch at the boundary or a central handler).

## 6. Testing Conventions

> Detailed methodology in `docs/TEST_VIEWPOINT.md`.

- **Location**: [TEST_LOCATION — e.g. co-located `<name>.spec.<ext>` for unit; `__tests__/` or `test/` for integration / e2e].
- **Naming**: [TEST_NAME_PATTERN — e.g. `test_<action>_<scenario>_<expected>`, or `describe(<unit>)` → `it('should <behavior> when <condition>')`]. Keep ONE pattern — it must match `docs/CODING-CHECKLIST.md`.
- Cover the happy path, each error / edge case, and each business rule.
- No shared mutable state between tests; each test sets up and tears down its own fixtures.
- Coverage floor: BE ≥[BE_COVERAGE — e.g. 80]%, FE ≥[FE_COVERAGE — e.g. 70]%.

## 7. Git Conventions

- **Commits**: [COMMIT_FORMAT — e.g. Conventional Commits `<type>(<scope>): <subject>`], imperative mood, no AI / tool references. Types: [COMMIT_TYPES — e.g. feat, fix, docs, refactor, test, chore].
- **Branches**: [BRANCH_PATTERN — e.g. `<type>/<slug>`, `feat/order-export`]. Feature work happens on an isolated branch / worktree, never on [BASE_BRANCH — e.g. main].
- One logical change per commit; keep the diff scoped to the change.

---

## Quick Reference — pin these once

| Dimension | This project |
| --- | --- |
| Folder grouping | [e.g. by feature] |
| Component case | [e.g. PascalCase] |
| Import groups | [e.g. 5 groups, alias past 2 levels] |
| Doc-comment format | [e.g. JSDoc] |
| Test name pattern | [e.g. test_<action>_<scenario>_<expected>] |
| Commit format | [e.g. Conventional Commits] |

> Code exemplars are **not** in this file. Load `coding-convention-snippets/<stack>.md` for module / service / component skeletons to copy and adapt to the stack in `PROJECT.md`.

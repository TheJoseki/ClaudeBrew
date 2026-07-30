---
name: lint-and-validate
description: "Runs linting, type checking, and static analysis after code modifications. Ensures syntax correctness and project standards compliance. Use when finishing code changes, validating code quality, or setting up linting."
allowed-tools: Read, Grep, Glob, Bash
metadata:
  version: "3.1"
  category: quality
---

# Lint and Validate

$ARGUMENTS

## Quick Start (Auto-Detect)

Run the bundled script to detect your tech stack and print the correct lint + type-check commands:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/detect_stack.sh
```

Or source the output to run automatically:

```bash
eval "$(bash ${CLAUDE_SKILL_DIR}/scripts/detect_stack.sh --export)"
$TYPE_CMD && $LINT_CMD
```

Handles: TypeScript / JavaScript / Python / Ruby / Go / Rust. Detects npm/yarn/pnpm automatically.

---

## Mandatory Rule

No code should be reported as "done" without passing lint and type checks.

---

## Procedures by Ecosystem

### Node.js / TypeScript

1. **Lint/Fix**: `npm run lint` or `npx eslint "path" --fix`
2. **Types**: `npx tsc --noEmit`
3. **Security**: `npm audit --audit-level=high`

### Python

1. **Lint**: `ruff check "path" --fix`
2. **Types**: `mypy "path"`
3. **Security**: `bandit -r "path" -ll`

### Other Ecosystems

Detect from PROJECT.md or project config files (`pyproject.toml`, `.eslintrc`, `Cargo.toml`, etc.).

---

## Quality Loop

```
1. Write/Edit Code
2. Run lint + type check
3. Analyze report
4. Fix issues and repeat
5. Only mark done when all checks pass
```

---

## Error Handling

| Situation | Action |
| --------- | ------ |
| Lint fails | Fix style/syntax issues immediately |
| Type check fails | Correct type mismatches before proceeding |
| No linter configured | Check for config files, suggest creating one |
| Security audit warnings | Report to user with severity |

---

## Detection

Read PROJECT.md for configured lint commands. If not available, detect from:
- `package.json` scripts (`lint`, `check`, `typecheck`)
- `pyproject.toml` tool sections
- `.eslintrc.*`, `tsconfig.json`, `ruff.toml`

// Package-location helpers (the npm package this CLI ships in). Node built-ins only.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/** Package root = two levels up from scripts/lib/pkg.mjs. */
export function packageRoot() {
  return dirname(dirname(dirname(fileURLToPath(import.meta.url))));
}

/** The authored payload source dir (`claude/`, installed as `.claude/`). */
export function sourceRoot(root = packageRoot()) {
  return join(root, "claude");
}

/** Version = the single source of truth in package.json. */
export function packageVersion(root = packageRoot()) {
  return JSON.parse(readFileSync(join(root, "package.json"), "utf8")).version;
}

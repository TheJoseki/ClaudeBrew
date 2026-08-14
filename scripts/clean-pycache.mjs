// Remove Python bytecode before packing. The shipped payload's hooks are Python;
// running them in dev (tests, dogfood) regenerates `__pycache__/*.pyc` under
// `claude/hooks/`. npm's `files` allowlist in package.json does NOT apply
// `.npmignore` exclusions inside the included directories, so those .pyc files
// would otherwise ship in the tarball (a leak caught repeatedly before this guard).
// Wired as the `prepack` lifecycle script, so it runs before both `npm pack` and
// `npm publish`, regardless of the dev tree's state. Node built-ins only, Node 18+.
import { readdirSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let removed = 0;

function walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return; // dir gone / unreadable — nothing to clean
  }
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const full = path.join(dir, e.name);
    if (e.name === "__pycache__") {
      rmSync(full, { recursive: true, force: true });
      removed++;
    } else if (e.name !== "node_modules" && e.name !== ".git") {
      walk(full);
    }
  }
}

// Only the shipped payload carries Python; scope the walk to it.
walk(path.join(ROOT, "claude"));
console.log(`clean-pycache: removed ${removed} __pycache__ dir(s) under claude/`);

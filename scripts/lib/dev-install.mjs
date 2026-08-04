// Dogfood dev loop for ClaudeBrew.
//
// Replaces the retired `claude --plugin-dir ./plugins/cbr` loop: copies the
// authored `claude/` payload into the repo's own `.claude/` so a Claude Code
// session in this repo discovers the skills (as project skills) and fires the
// hooks — the same tree a real `npx claudebrew install` will lay down.
//
// SAFETY (intentional, load-bearing): only the six named payload subdirs are
// ever written or removed. `.claude/settings.json` (tracked dev harness) and
// any sibling `.claude/worktrees/` are enumerated OUT by construction — this
// module never does a "wipe everything under .claude/ except X" pass, because a
// negative pattern there could delete a live worktree. Positive list only.
//
// Node built-ins only (zero runtime deps).

import { existsSync, mkdirSync, rmSync, cpSync, readdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// The six subdirs of the payload. Anything not in this list under `.claude/`
// (settings.json, worktrees/, sdlc-index.json, ...) is left untouched.
export const PAYLOAD_SUBDIRS = ["skills", "agents", "hooks", "rules", "schemas", "docs"];

/** Package root = two levels up from scripts/lib/dev-install.mjs. */
export function packageRoot() {
  return dirname(dirname(dirname(fileURLToPath(import.meta.url))));
}

/** Recursively count regular files under a directory (for the summary line). */
function countFiles(dir) {
  if (!existsSync(dir)) return 0;
  let n = 0;
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) n += countFiles(p);
    else n += 1;
  }
  return n;
}

/**
 * Copy claude/<sub> -> .claude/<sub> for each payload subdir (clean sync:
 * remove the destination subdir first so deletions in source propagate).
 *
 * @param {{root?: string, log?: (msg: string) => void}} [opts]
 * @returns {{root: string, source: string, dest: string, copied: Array<{sub: string, files: number}>}}
 */
export function devInstall(opts = {}) {
  const root = opts.root ?? packageRoot();
  const log = opts.log ?? ((m) => console.log(m));
  const source = join(root, "claude");
  const dest = join(root, ".claude");

  if (!existsSync(source)) {
    throw new Error(`dev-install: payload source not found at ${source} — run from the repo root.`);
  }
  mkdirSync(dest, { recursive: true });

  const copied = [];
  for (const sub of PAYLOAD_SUBDIRS) {
    const srcSub = join(source, sub);
    const destSub = join(dest, sub);
    if (!existsSync(srcSub)) continue; // a payload subdir may legitimately be absent
    rmSync(destSub, { recursive: true, force: true }); // clean sync — only this named subdir
    cpSync(srcSub, destSub, { recursive: true });
    const files = countFiles(destSub);
    copied.push({ sub, files });
    log(`  .claude/${sub}/  (${files} files)`);
  }

  const total = copied.reduce((n, c) => n + c.files, 0);
  log(`ClaudeBrew dev-install: synced ${total} files across ${copied.length} payload dirs into ${dest}`);
  log(`  (untouched: .claude/settings.json, .claude/worktrees/, and everything else under .claude/)`);
  return { root, source, dest, copied };
}

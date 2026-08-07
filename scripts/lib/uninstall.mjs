// File-side uninstall: remove the metadata-tracked files the user has NOT edited, then
// prune the empty dirs they leave behind — with a hard ceiling at the target .claude/
// root. Node built-ins only.
//
// Hash-aware (symmetry with update): a tracked file whose on-disk hash still equals the
// hash recorded at install is ours-and-unmodified → remove it. A tracked file the user
// edited (on-disk != recorded) is KEPT and reported, never silently destroyed — the same
// protection `update` gives. `--force` removes even edited files.
//
// The prune NEVER removes the .claude/ dir itself and NEVER ascends past it, so a sibling
// like .claude/worktrees/ (untracked, non-empty) is untouched by construction.

import { existsSync, readFileSync, rmSync, readdirSync, rmdirSync } from "node:fs";
import path from "node:path";
import { hashBytes, readManifest, manifestPath } from "./metadata.mjs";

export function uninstallFiles(target, opts = {}) {
  const { dryRun = false, force = false } = opts;
  const manifest = readManifest(target.claudeDir);
  if (!manifest) {
    throw new Error(`no metadata.json at ${target.claudeDir} — nothing CBR-tracked to uninstall`);
  }
  const recorded = manifest.files || {};
  const nativeSep = (rel) => rel.replace(/\//g, path.sep);

  const toRemove = []; // {rel, dest}
  const kept = [];     // rel (user-modified, preserved)
  for (const rel of Object.keys(recorded)) {
    const dest = path.join(target.claudeDir, nativeSep(rel));
    if (!existsSync(dest)) continue; // already gone
    const onDisk = hashBytes(readFileSync(dest));
    if (force || onDisk === recorded[rel]) toRemove.push({ rel, dest });
    else kept.push(rel);
  }

  // Retired files (removed upstream while user-edited, see update.mjs) are unmanaged by
  // decision: uninstall leaves them in place — even with --force — but reports them so
  // their existence is never silent.
  const retiredLeft = Object.keys(manifest.retired || {});

  if (dryRun) {
    return { dryRun: true, action: "uninstall", willRemove: toRemove.length, kept, retiredLeft };
  }

  const touchedDirs = new Set();
  for (const { dest } of toRemove) { rmSync(dest, { force: true }); touchedDirs.add(path.dirname(dest)); }
  // Only drop the manifest once nothing tracked-and-edited remains behind; if we kept
  // user edits, leave the manifest so a later `uninstall --force` can still find them.
  if (kept.length === 0) rmSync(manifestPath(target.claudeDir), { force: true });
  pruneEmptyDirs(touchedDirs, target.claudeDir);

  return { action: "uninstall", removed: toRemove.length, kept, retiredLeft };
}

/** Remove now-empty dirs, deepest first, stopping strictly below `ceiling`. */
function pruneEmptyDirs(dirs, ceiling) {
  const sorted = [...new Set(dirs)].sort((a, b) => b.length - a.length);
  for (let d of sorted) {
    while (d.length > ceiling.length && d.startsWith(ceiling)) {
      let empty = false;
      try { empty = readdirSync(d).length === 0; } catch { break; }
      if (!empty) break;
      try { rmdirSync(d); } catch { break; }
      d = path.dirname(d);
    }
  }
}

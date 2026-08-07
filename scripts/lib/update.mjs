// File-side update: reconcile the installed tree with a (possibly newer) payload
// without clobbering user edits. Node built-ins only.
//
// Per file, compare the on-disk hash to the hash recorded in metadata.json at install:
//   - not in metadata            → new file, add it
//   - on-disk == recorded        → we own it, unmodified: overwrite only if the newly
//                                   baked bytes differ (a real version change), else no-op
//   - on-disk != recorded        → user edited it since we wrote it: skip + report
//                                   (unless --force), never silently clobber
//   - recorded but absent upstream→ removed in this version: delete if still unmodified
//
// Because install hashed the WRITTEN (baked) bytes, a fresh-install → immediate-update
// with the same version is a clean no-op: newHash == recorded AND on-disk == recorded
// for every file. That equivalence is the guard against the hash-over-source trap.

import { readFileSync, existsSync, mkdirSync, writeFileSync, renameSync, rmSync } from "node:fs";
import path from "node:path";
import { rewriteBytes } from "./rewrite.mjs";
import { hashBytes, readManifest, buildManifest, writeManifest } from "./metadata.mjs";
import { listPayload } from "./payload.mjs";
import { packageVersion } from "./pkg.mjs";

export function updateFiles(sourceRoot, target, opts = {}) {
  const { force = false, dryRun = false, version = packageVersion() } = opts;
  const manifest = readManifest(target.claudeDir);
  if (!manifest) {
    throw new Error(`no metadata.json at ${target.claudeDir} — run 'claudebrew install' first`);
  }
  const recorded = manifest.files || {};
  const nativeSep = (rel) => rel.replace(/\//g, path.sep);

  const actions = { added: [], updated: [], unchanged: [], skipped: [], removed: [], retired: [] };
  const nextFiles = {};
  // Files retired by an EARLIER update (removed upstream while user-edited) stay out of
  // `files` — carrying them forward here is what keeps them from being re-reported as
  // "kept" on every subsequent update. A retired path re-shipped upstream is re-adopted
  // only when that is provably safe (see the added-branch guard below).
  const retired = { ...(manifest.retired || {}) };
  const writes = []; // {dest, bytes}
  const deletes = []; // dest
  const seen = new Set();

  for (const { rel, abs } of listPayload(sourceRoot)) {
    seen.add(rel);
    const bytes = rewriteBytes(readFileSync(abs), target.cbrRoot);
    const newHash = hashBytes(bytes);
    const dest = path.join(target.claudeDir, nativeSep(rel));
    const onDisk = existsSync(dest) ? hashBytes(readFileSync(dest)) : null;

    if (!(rel in recorded)) {
      // A retired file (removed upstream while user-edited) can be re-shipped later.
      // The user's edited copy gets the same protection as any managed user edit; a copy
      // the user reverted to its installed content (hash == retired hash) is safe to adopt.
      if (rel in retired && onDisk !== null && onDisk !== newHash && onDisk !== retired[rel] && !force) {
        actions.skipped.push(`${rel} (re-shipped upstream but user-modified — kept, still retired)`);
      } else {
        delete retired[rel]; // re-adopted (identical/reverted copy, absent, or --force)
        actions.added.push(rel); nextFiles[rel] = newHash; writes.push({ dest, bytes });
      }
    } else if (onDisk !== null && onDisk !== recorded[rel]) {
      if (force) { actions.updated.push(`${rel} (forced over user edit)`); nextFiles[rel] = newHash; writes.push({ dest, bytes }); }
      else { actions.skipped.push(rel); nextFiles[rel] = recorded[rel]; }
    } else if (newHash === recorded[rel] && onDisk === recorded[rel]) {
      actions.unchanged.push(rel); nextFiles[rel] = recorded[rel];
    } else {
      // ours, unmodified (or vanished from disk) but the baked bytes changed → refresh
      actions.updated.push(rel); nextFiles[rel] = newHash; writes.push({ dest, bytes });
    }
  }

  // Files we installed that no longer exist upstream: remove if the user didn't edit them.
  for (const rel of Object.keys(recorded)) {
    if (seen.has(rel)) continue;
    const dest = path.join(target.claudeDir, nativeSep(rel));
    const onDisk = existsSync(dest) ? hashBytes(readFileSync(dest)) : null;
    if (onDisk === null || onDisk === recorded[rel]) { actions.removed.push(rel); deletes.push(dest); }
    else {
      // Removed upstream but user-edited: RETIRE it — keep the file on disk, move it from
      // `files` to `retired` so it is no longer managed (and, for rules, no longer imported
      // once the caller regenerates the rules block). Reported once, on this update only.
      actions.retired.push(rel);
      retired[rel] = recorded[rel];
    }
  }

  if (dryRun) return { dryRun: true, action: "update", actions };

  for (const w of writes) {
    mkdirSync(path.dirname(w.dest), { recursive: true });
    const tmp = w.dest + ".cbrtmp";
    writeFileSync(tmp, w.bytes);
    renameSync(tmp, w.dest);
  }
  for (const d of deletes) { try { rmSync(d, { force: true }); } catch { /* best-effort */ } }

  // Preserve the settings-provenance section: update rewrites the file manifest but must
  // NOT drop the config provenance uninstall needs to un-merge settings + strip the rules block.
  const next = buildManifest({ name: manifest.name || "claudebrew", version, scope: target.scope, files: nextFiles });
  if (manifest.settings) next.settings = manifest.settings;
  if (Object.keys(retired).length) next.retired = retired;
  writeManifest(target.claudeDir, next);
  return { action: "update", actions };
}

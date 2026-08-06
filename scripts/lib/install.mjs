// File-side install: provision the payload into the target .claude/, baking residual
// {{CBR_ROOT}} tokens to absolute paths, and record a hash manifest. Node built-ins only.
//
// Transactional: stage every file to a temp sibling (`<dest>.cbrtmp`), then commit all
// via rename. If staging fails partway, the temps written so far are deleted and the
// finals are left untouched — an interrupt yields either the prior state or a complete
// install, never an untracked half-write.

import { readFileSync, mkdirSync, writeFileSync, renameSync, rmSync } from "node:fs";
import path from "node:path";
import { rewriteBytes } from "./rewrite.mjs";
import { hashBytes, buildManifest, writeManifest, readManifest } from "./metadata.mjs";
import { listPayload } from "./payload.mjs";
import { packageVersion } from "./pkg.mjs";

/**
 * @param {string} sourceRoot  the package's `claude/` dir
 * @param {{scope,claudeDir,cbrRoot}} target  from resolveTarget()
 * @param {{dryRun?:boolean, version?:string, force?:boolean}} [opts]
 */
export function installFiles(sourceRoot, target, opts = {}) {
  const { dryRun = false, version = packageVersion(), force = false } = opts;
  const nativeSep = (rel) => rel.replace(/\//g, path.sep);

  // Guard the footgun: `install` overwrites unconditionally, so a second `install`
  // would silently destroy the user edits `update` exists to protect. Refuse when an
  // install already exists unless the user forces a reinstall.
  if (!dryRun && !force && readManifest(target.claudeDir)) {
    throw new Error(`already installed at ${target.claudeDir} — use 'claudebrew update' (or 'install --force' to reinstall)`);
  }

  // Build the write plan (hash is over the POST-rewrite bytes).
  const plan = listPayload(sourceRoot).map(({ rel, abs }) => {
    const bytes = rewriteBytes(readFileSync(abs), target.cbrRoot);
    return { rel, dest: path.join(target.claudeDir, nativeSep(rel)), bytes, hash: hashBytes(bytes) };
  });

  if (dryRun) {
    return { dryRun: true, action: "install", count: plan.length, files: plan.map((p) => p.rel) };
  }

  // Stage → commit transaction.
  const staged = [];
  try {
    for (const p of plan) {
      mkdirSync(path.dirname(p.dest), { recursive: true });
      const tmp = p.dest + ".cbrtmp";
      writeFileSync(tmp, p.bytes);
      staged.push({ tmp, dest: p.dest });
    }
  } catch (e) {
    for (const s of staged) {
      try { rmSync(s.tmp, { force: true }); } catch { /* best-effort rollback */ }
    }
    throw new Error(`install staging failed (rolled back, no files changed): ${e.message}`);
  }
  for (const s of staged) renameSync(s.tmp, s.dest);

  const files = {};
  for (const p of plan) files[p.rel] = p.hash;
  writeManifest(target.claudeDir, buildManifest({ name: "claudebrew", version, scope: target.scope, files }));

  return { action: "install", installed: plan.length, claudeDir: target.claudeDir };
}

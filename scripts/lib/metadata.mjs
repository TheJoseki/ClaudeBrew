// Install manifest (.claude/metadata.json) — read/write + hashing. Node built-ins only.
//
// THE HASH TRAP (red-team M2): every file hash is taken over the POST-rewrite bytes
// actually written to disk, NOT the source bytes. The installed copy legitimately
// differs from source by the baked absolute paths; if we hashed source bytes, `update`
// would see every managed file as "user-modified" and refuse to touch anything. The
// hash answers exactly one question — "did the USER change the INSTALLED file since we
// wrote it" — so it must be computed on the written bytes at write time.
//
// The manifest is intentionally deterministic (no timestamps): a fresh install of the
// same version + scope produces byte-identical metadata, which the no-op update test
// relies on. The `settings` provenance section is reserved for the config-side phase.

import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, renameSync, existsSync } from "node:fs";
import path from "node:path";

export const METADATA_BASENAME = "metadata.json";

/** sha256 hex of a buffer/string. */
export function hashBytes(buf) {
  return createHash("sha256").update(buf).digest("hex");
}

/** Build a manifest object. `files` maps forward-slash relpaths (under .claude/) to
 *  the sha256 of the written bytes. */
export function buildManifest({ name, version, scope, files }) {
  return { name, version, scope, files };
}

/** Absolute path to the manifest inside a target .claude dir. */
export function manifestPath(claudeDir) {
  return path.join(claudeDir, METADATA_BASENAME);
}

/** Read + parse the manifest, or null if absent. Throws on parse error (caller decides
 *  the fail-closed policy). */
export function readManifest(claudeDir) {
  const p = manifestPath(claudeDir);
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf8"));
}

/** Atomically write the manifest (temp + rename). Stable 2-space JSON + trailing NL. */
export function writeManifest(claudeDir, manifest) {
  const p = manifestPath(claudeDir);
  const tmp = p + ".cbrtmp";
  writeFileSync(tmp, JSON.stringify(manifest, null, 2) + "\n");
  renameSync(tmp, p);
}

// Enumerate the payload files to install. Node built-ins only.
//
// POSITIVE enumeration of the six payload subdirs only — never "walk everything under
// the source root". settings.json (merged, not copied) and any stray dev file sit at
// the source root and must be excluded by construction.

import { readdirSync, statSync } from "node:fs";
import path from "node:path";
import { PAYLOAD_SUBDIRS } from "./paths.mjs";

/**
 * @returns {Array<{rel: string, abs: string}>} rel is forward-slash, relative to
 * sourceRoot (e.g. "hooks/verdict-gate.py").
 */
export function listPayload(sourceRoot) {
  const out = [];
  for (const sub of PAYLOAD_SUBDIRS) walk(path.join(sourceRoot, sub), sourceRoot, out);
  return out;
}

function walk(dir, root, out) {
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return; // a payload subdir may legitimately be absent
  }
  for (const name of entries) {
    const abs = path.join(dir, name);
    if (statSync(abs).isDirectory()) walk(abs, root, out);
    else out.push({ rel: path.relative(root, abs).replace(/\\/g, "/"), abs });
  }
}

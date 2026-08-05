// Scope + path resolution for the installer. Node built-ins only.
//
// Two install scopes:
//   project → <cwd>/.claude   (the user runs `npx claudebrew install` from their repo root)
//   user    → ~/.claude
//
// `cbrRoot` is the value every residual `{{CBR_ROOT}}` token bakes to: the absolute
// path of the target `.claude/` directory, forward-slash normalized (forward slashes
// resolve correctly in hook commands and Python paths on Windows, and dodge the
// backslash-escaping question inside JSON string values).

import os from "node:os";
import path from "node:path";
import { existsSync } from "node:fs";

/** Normalize a native path to forward slashes (safe for the baked token + JSON). */
export function toForward(p) {
  return p.replace(/\\/g, "/");
}

/** Walk up from cwd for the repo root (a `.git` marker) so `install` run from a
 *  subdirectory still targets the repo root, not a nested `.claude/` Claude Code won't
 *  read. Falls back to cwd when no `.git` is found. Marker is `.git` ONLY — an existing
 *  `.claude` is deliberately NOT a walk-up marker, or a run under a home dir that has
 *  `~/.claude` could resolve project scope onto the user's personal config. */
export function findProjectRoot(cwd) {
  let dir = path.resolve(cwd);
  for (;;) {
    if (existsSync(path.join(dir, ".git"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return path.resolve(cwd); // reached fs root, no marker
    dir = parent;
  }
}

/**
 * Resolve the install target for a scope.
 * @param {"project"|"user"} scope
 * @param {string} [cwd] project anchor (defaults to process.cwd())
 * @param {string} [home] user-scope home (defaults to os.homedir(); injectable for tests)
 * @returns {{scope: string, base: string, claudeDir: string, cbrRoot: string}}
 */
export function resolveTarget(scope, cwd = process.cwd(), home = os.homedir()) {
  if (scope !== "project" && scope !== "user") {
    throw new Error(`invalid scope '${scope}' — expected 'project' or 'user'`);
  }
  const base = scope === "user" ? home : findProjectRoot(cwd);
  const claudeDir = path.join(base, ".claude"); // native, for fs ops
  return {
    scope,
    base,
    claudeDir,
    cbrRoot: toForward(claudeDir), // forward-slash, for baking into refs
  };
}

/** The six payload subdirs. Enumerated POSITIVELY everywhere: the copy/rewrite pass
 *  must never "walk everything under the source root", or it would sweep in
 *  settings.json (which is merged, not copied) and any stray dev file. */
export const PAYLOAD_SUBDIRS = ["skills", "agents", "hooks", "rules", "schemas", "docs"];

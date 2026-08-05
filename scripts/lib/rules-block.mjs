// Manage the `@`-import rules block in the target CLAUDE.md. Node built-ins only.
//
// The block loads CBR's rule files into every session (a plugin auto-loaded rules/*.md;
// a bare install has no such mechanism — B2). Imports are file-RELATIVE: Claude Code
// resolves an `@` import against the CLAUDE.md's own directory, not the CWD (per its
// docs), so a relative import is stable across launch directories and needs no absolute
// path baking:
//   user scope    → @rules/<name>.md          (CLAUDE.md at ~/.claude/, rules/ sibling)
//   project scope → @.claude/rules/<name>.md   (CLAUDE.md at <project>/, rules under .claude/)
//
// The block is delimiter-fenced so uninstall can strip exactly it.

import { readFileSync, writeFileSync, renameSync, existsSync, rmSync } from "node:fs";

export const START = "<!-- cbr:rules:start -->";
export const END = "<!-- cbr:rules:end -->";

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const blockRe = () => new RegExp(`\\n*${escapeRe(START)}[\\s\\S]*?${escapeRe(END)}\\n*`);

function atomicWrite(file, content) {
  const tmp = file + ".cbrtmp";
  writeFileSync(tmp, content);
  renameSync(tmp, file);
}

export function buildRulesBlock(ruleFiles, scope) {
  const prefix = scope === "user" ? "@rules/" : "@.claude/rules/";
  return `${START}\n${ruleFiles.map((f) => prefix + f).join("\n")}\n${END}`;
}

/**
 * Write or replace the managed block in CLAUDE.md. Idempotent (a re-run replaces the
 * existing block in place). @returns provenance {file, created}.
 */
export function writeRulesBlock(claudeMdPath, ruleFiles, scope) {
  const block = buildRulesBlock(ruleFiles, scope);
  const existed = existsSync(claudeMdPath);
  const content = existed ? readFileSync(claudeMdPath, "utf8") : "";

  let next;
  if (blockRe().test(content)) {
    next = content.replace(blockRe(), `\n\n${block}\n`);
  } else {
    const head = content.trimEnd();
    next = head ? `${head}\n\n${block}\n` : `${block}\n`;
  }
  atomicWrite(claudeMdPath, next);
  return { file: claudeMdPath, created: !existed };
}

/** Remove the managed block. If CBR created the file and nothing else remains, delete it. */
export function stripRulesBlock(claudeMdPath, provenance = {}) {
  if (!existsSync(claudeMdPath)) return;
  const content = readFileSync(claudeMdPath, "utf8");
  const stripped = content.replace(blockRe(), "\n").replace(/\n{3,}/g, "\n\n").trim();
  if (provenance.created && stripped === "") {
    rmSync(claudeMdPath, { force: true });
    return;
  }
  atomicWrite(claudeMdPath, stripped ? stripped + "\n" : "");
}

// Behavioral tests for the file-side installer. Run: node --test scripts/install.test.mjs
// Uses the REAL claude/ payload installed into throwaway temp dirs.

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { resolveTarget } from "./lib/paths.mjs";
import { sourceRoot } from "./lib/pkg.mjs";
import { TOKEN } from "./lib/rewrite.mjs";
import { installFiles } from "./lib/install.mjs";
import { updateFiles } from "./lib/update.mjs";
import { uninstallFiles } from "./lib/uninstall.mjs";

const SRC = sourceRoot();

function freshTarget() {
  const cwd = mkdtempSync(path.join(os.tmpdir(), "cbr-inst-"));
  // A .git marker so resolveTarget("project") stops here and never walks up to a real
  // ancestor .git — critical: without it the walk-up could reach a home dir and target
  // the user's actual ~/.claude.
  mkdirSync(path.join(cwd, ".git"));
  return { cwd, target: resolveTarget("project", cwd) };
}
function cleanup(cwd) { rmSync(cwd, { recursive: true, force: true }); }

/** Recursively list files under dir. */
function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    const p = path.join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

test("install provisions payload, bakes tokens, writes metadata", () => {
  const { cwd, target } = freshTarget();
  try {
    const res = installFiles(SRC, target);
    assert.equal(res.action, "install");
    assert.ok(res.installed > 200, `expected >200 files, got ${res.installed}`);

    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "verdict-gate.py")), "hook file landed");
    assert.ok(existsSync(path.join(target.claudeDir, "skills", "cbr-brainstorming", "SKILL.md")), "skill landed");
    assert.ok(existsSync(path.join(target.claudeDir, "metadata.json")), "metadata written");

    // A file that carried a token is now baked to the absolute cbrRoot.
    const reviewer = readFileSync(path.join(target.claudeDir, "agents", "cbr-reviewer.md"), "utf8");
    assert.ok(reviewer.includes(`${target.cbrRoot}/schemas/`), "token baked to absolute cbrRoot");

    // ZERO tokens survive anywhere in the installed tree.
    let tokenHits = 0;
    for (const f of walk(target.claudeDir)) {
      const buf = readFileSync(f);
      if (!buf.includes(0x00) && buf.toString("utf8").includes(TOKEN)) tokenHits++;
    }
    assert.equal(tokenHits, 0, "no {{CBR_ROOT}} tokens survive in the installed tree");

    const meta = JSON.parse(readFileSync(path.join(target.claudeDir, "metadata.json"), "utf8"));
    assert.equal(meta.scope, "project");
    assert.ok(meta.files["hooks/verdict-gate.py"], "metadata records a hook");
  } finally { cleanup(cwd); }
});

test("fresh install -> immediate update is a clean no-op (hash-over-written-bytes guard)", () => {
  const { cwd, target } = freshTarget();
  try {
    const inst = installFiles(SRC, target);
    const res = updateFiles(SRC, target);
    assert.deepEqual(res.actions.added, [], "no adds");
    assert.deepEqual(res.actions.updated, [], "no updates");
    assert.deepEqual(res.actions.skipped, [], "no skips");
    assert.deepEqual(res.actions.removed, [], "no removals");
    assert.equal(res.actions.unchanged.length, inst.installed, "every file unchanged");
  } finally { cleanup(cwd); }
});

test("update preserves a user-edited managed file (skip + report, no clobber)", () => {
  const { cwd, target } = freshTarget();
  try {
    installFiles(SRC, target);
    const skillPath = path.join(target.claudeDir, "skills", "cbr-brainstorming", "SKILL.md");
    const edited = readFileSync(skillPath, "utf8") + "\n<!-- USER EDIT -->\n";
    writeFileSync(skillPath, edited);

    const res = updateFiles(SRC, target);
    assert.ok(res.actions.skipped.includes("skills/cbr-brainstorming/SKILL.md"), "user-edited file skipped");
    assert.equal(readFileSync(skillPath, "utf8"), edited, "user edit preserved");

    // --force overwrites it.
    const forced = updateFiles(SRC, target, { force: true });
    assert.ok(forced.actions.updated.some((u) => u.startsWith("skills/cbr-brainstorming/SKILL.md")), "force overwrote");
    assert.ok(!readFileSync(skillPath, "utf8").includes("USER EDIT"), "force restored shipped content");
  } finally { cleanup(cwd); }
});

test("uninstall removes tracked files + prunes empties, but never a sibling worktrees/ or user file", () => {
  const { cwd, target } = freshTarget();
  try {
    installFiles(SRC, target);
    // A sibling worktree + a user settings file the installer must never touch.
    const wt = path.join(target.claudeDir, "worktrees", "feat-x");
    mkdirSync(wt, { recursive: true });
    writeFileSync(path.join(wt, "keep.txt"), "live worktree");
    writeFileSync(path.join(target.claudeDir, "settings.json"), "{}");

    const res = uninstallFiles(target);
    assert.ok(res.removed > 200, "removed the tracked files");
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks", "verdict-gate.py")), "tracked file gone");
    assert.ok(!existsSync(path.join(target.claudeDir, "skills")), "empty payload dir pruned");
    assert.ok(!existsSync(path.join(target.claudeDir, "metadata.json")), "metadata removed");
    assert.ok(existsSync(path.join(wt, "keep.txt")), "sibling worktree untouched");
    assert.ok(existsSync(path.join(target.claudeDir, "settings.json")), "user settings untouched");
    assert.ok(existsSync(target.claudeDir), ".claude/ itself preserved (ceiling)");
  } finally { cleanup(cwd); }
});

test("install refuses over an existing install unless --force", () => {
  const { cwd, target } = freshTarget();
  try {
    installFiles(SRC, target);
    assert.throws(() => installFiles(SRC, target), /already installed/, "second install refused");
    const res = installFiles(SRC, target, { force: true });
    assert.equal(res.action, "install", "install --force reinstalls");
  } finally { cleanup(cwd); }
});

test("uninstall preserves a user-edited tracked file (hash-aware); --force removes it", () => {
  const { cwd, target } = freshTarget();
  try {
    installFiles(SRC, target);
    const skillPath = path.join(target.claudeDir, "skills", "cbr-brainstorming", "SKILL.md");
    writeFileSync(skillPath, readFileSync(skillPath, "utf8") + "\n<!-- USER EDIT -->\n");
    updateFiles(SRC, target); // skips the edit, keeps it tracked
    const res = uninstallFiles(target);
    assert.ok(res.kept.includes("skills/cbr-brainstorming/SKILL.md"), "edited file reported kept");
    assert.ok(existsSync(skillPath), "edited file survives uninstall");
    assert.ok(existsSync(path.join(target.claudeDir, "metadata.json")), "manifest retained while a kept file remains");
    const forced = uninstallFiles(target, { force: true });
    assert.ok(!existsSync(skillPath), "uninstall --force removes the edited file");
    assert.ok(!existsSync(path.join(target.claudeDir, "metadata.json")), "manifest gone once nothing kept");
  } finally { cleanup(cwd); }
});

test("--dry-run install mutates nothing", () => {
  const { cwd, target } = freshTarget();
  try {
    const res = installFiles(SRC, target, { dryRun: true });
    assert.equal(res.dryRun, true);
    assert.ok(res.count > 200);
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks")), "no files written on dry-run");
  } finally { cleanup(cwd); }
});

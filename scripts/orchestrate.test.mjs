// Integration tests for the full install/uninstall flow (files + settings + rules block).
// Run: node --test scripts/orchestrate.test.mjs   (requires a real Python on PATH)

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { resolveTarget } from "./lib/paths.mjs";
import { fullInstall, fullUninstall } from "./lib/orchestrate.mjs";
import { parseSettings } from "./lib/settings-merge.mjs";

function freshTarget() {
  const cwd = mkdtempSync(path.join(os.tmpdir(), "cbr-orch-"));
  mkdirSync(path.join(cwd, ".git")); // repo-root marker (keeps resolveTarget off any real ~/.claude)
  return { cwd, target: resolveTarget("project", cwd) };
}
const rm = (cwd) => rmSync(cwd, { recursive: true, force: true });

test("full install: files + settings.local.json merge + CLAUDE.md rules block, no tokens, no gate by default", () => {
  const { cwd, target } = freshTarget();
  try {
    const res = fullInstall(target);
    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "guard-bash.py")), "payload provisioned");

    const sp = path.join(target.claudeDir, "settings.local.json");
    assert.ok(existsSync(sp), "project scope merges into settings.local.json (M4 default)");
    const s = JSON.parse(readFileSync(sp, "utf8"));
    assert.equal(s.teammateMode, "in-process");
    const sj = JSON.stringify(s);
    assert.ok(!sj.includes("{{CBR_ROOT}}"), "no tokens survive in merged settings");
    assert.ok(sj.includes(`${target.cbrRoot}/hooks/`), "hook commands baked to cbrRoot");
    assert.ok(!sj.includes("enforce-worktree"), "worktree gate NOT registered by default (S-3)");
    assert.equal(res.gate, false);

    const md = path.join(cwd, "CLAUDE.local.md");
    assert.ok(existsSync(md), "project rules block goes into gitignored CLAUDE.local.md");
    assert.ok(readFileSync(md, "utf8").includes("@.claude/rules/sdlc-conventions.md"), "relative rules import");
  } finally { rm(cwd); }
});

test("full install --gate registers the enforce-worktree hook", () => {
  const { cwd, target } = freshTarget();
  try {
    const res = fullInstall(target, { gate: true });
    assert.equal(res.gate, true);
    const s = readFileSync(path.join(target.claudeDir, "settings.local.json"), "utf8");
    assert.ok(s.includes("enforce-worktree.py"), "gate registered on opt-in");
    assert.ok(s.includes(`${target.cbrRoot}/hooks/enforce-worktree.py`), "gate command baked absolute");
  } finally { rm(cwd); }
});

test("full install rolls back the payload when the settings merge fails (no wedged half-install)", () => {
  const { cwd, target } = freshTarget();
  try {
    mkdirSync(target.claudeDir, { recursive: true });
    writeFileSync(path.join(target.claudeDir, "settings.local.json"), "{ not: valid json,,,"); // fail-closed trigger
    assert.throws(() => fullInstall(target), /not valid JSON/, "install aborts on unparseable settings");
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks", "guard-bash.py")), "payload rolled back");
    assert.ok(!existsSync(path.join(target.claudeDir, "metadata.json")), "metadata rolled back");
  } finally { rm(cwd); }
});

test("user scope installs into ~/.claude, merges ~/.claude/settings.json, writes ~/.claude/CLAUDE.md rules block", () => {
  const home = mkdtempSync(path.join(os.tmpdir(), "cbr-home-"));
  try {
    // Inject a fake home so user scope never touches the real ~/.claude.
    const target = resolveTarget("user", process.cwd(), home);
    fullInstall(target);
    assert.ok(existsSync(path.join(home, ".claude", "hooks", "guard-bash.py")), "payload provisioned under ~/.claude");

    const sp = path.join(home, ".claude", "settings.json");
    assert.ok(existsSync(sp), "user scope merges into ~/.claude/settings.json");
    const s = readFileSync(sp, "utf8");
    assert.ok(!s.includes("{{CBR_ROOT}}") && s.includes(`${target.cbrRoot}/hooks/`), "hook commands baked to the user's absolute path");

    const md = path.join(home, ".claude", "CLAUDE.md");
    assert.ok(existsSync(md) && readFileSync(md, "utf8").includes("@rules/sdlc-conventions.md"), "user-scope relative rules import (@rules/)");

    fullUninstall(target);
    assert.ok(!existsSync(path.join(home, ".claude", "hooks", "guard-bash.py")), "uninstall removed the payload");
  } finally { rmSync(home, { recursive: true, force: true }); }
});

test("full uninstall un-merges settings + strips rules block + removes files (pre-install state restored)", () => {
  const { cwd, target } = freshTarget();
  try {
    mkdirSync(target.claudeDir, { recursive: true });
    const sp = path.join(target.claudeDir, "settings.local.json");
    writeFileSync(sp, JSON.stringify({ model: "opus", env: { KEEP: "1" } }));
    const tracked = path.join(cwd, "CLAUDE.md"); // the user's tracked project memory
    writeFileSync(tracked, "# Project\n\nuser notes here\n");
    const local = path.join(cwd, "CLAUDE.local.md");

    fullInstall(target);
    assert.ok(existsSync(local) && readFileSync(local, "utf8").includes("cbr:rules"), "block written to CLAUDE.local.md");
    assert.ok(!readFileSync(tracked, "utf8").includes("cbr:rules"), "tracked CLAUDE.md never touched");

    fullUninstall(target);
    assert.deepEqual(parseSettings(sp), { model: "opus", env: { KEEP: "1" } }, "settings restored to pre-install (semantic equality)");
    assert.ok(!existsSync(local), "CBR-created CLAUDE.local.md removed on uninstall");
    assert.equal(readFileSync(tracked, "utf8"), "# Project\n\nuser notes here\n", "tracked CLAUDE.md byte-unchanged throughout");
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks", "guard-bash.py")), "payload files removed");
  } finally { rm(cwd); }
});

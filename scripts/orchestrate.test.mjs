// Integration tests for the full install/uninstall flow (files + settings + rules block).
// Run: node --test scripts/orchestrate.test.mjs   (requires a real Python on PATH)

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, existsSync, readFileSync, writeFileSync, mkdirSync, cpSync, readdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { resolveTarget } from "./lib/paths.mjs";
import { fullInstall, fullUninstall, fullUpdate } from "./lib/orchestrate.mjs";
import { parseSettings } from "./lib/settings-merge.mjs";
import { readManifest, writeManifest } from "./lib/metadata.mjs";
import { sourceRoot } from "./lib/pkg.mjs";

// Any currently-shipped rule file works for the set-change tests; picked dynamically so a
// future rules re-architecture (which deletes/renames rule files) cannot ENOENT them.
const PROBE_RULE = readdirSync(path.join(sourceRoot(), "rules")).find((f) => f.endsWith(".md"));

function freshTarget() {
  const cwd = mkdtempSync(path.join(os.tmpdir(), "cbr-orch-"));
  mkdirSync(path.join(cwd, ".git")); // repo-root marker (keeps resolveTarget off any real ~/.claude)
  return { cwd, target: resolveTarget("project", cwd) };
}
const rm = (cwd) => rmSync(cwd, { recursive: true, force: true });

/** A private copy of the real payload with a mutation applied — simulates a newer
 *  version whose rule-file SET differs (the operation update must propagate). */
function mutatedPayload(mutate) {
  const dir = mkdtempSync(path.join(os.tmpdir(), "cbr-payload-"));
  cpSync(sourceRoot(), dir, { recursive: true });
  mutate(dir);
  return dir;
}

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

test("fullUpdate regenerates the rules @-import block on a rules-set change", () => {
  const { cwd, target } = freshTarget();
  const payloadB = mutatedPayload((d) => {
    rmSync(path.join(d, "rules", PROBE_RULE));
    writeFileSync(path.join(d, "rules", "zz-probe-rule.md"), "# Probe rule\n");
  });
  try {
    fullInstall(target);
    const md = path.join(cwd, "CLAUDE.local.md");
    assert.ok(readFileSync(md, "utf8").includes(`@.claude/rules/${PROBE_RULE}`), "precondition: old rule imported");

    const res = fullUpdate(target, { src: payloadB });
    const block = readFileSync(md, "utf8");
    assert.ok(!block.includes(PROBE_RULE), "deleted rule's import removed from the block");
    assert.ok(block.includes("@.claude/rules/zz-probe-rule.md"), "added rule imported");
    assert.equal(res.claudeMd, md, "update reports the refreshed block target");
    assert.ok(existsSync(path.join(target.claudeDir, "rules", "zz-probe-rule.md")), "new rule file landed on disk");
    assert.ok(readManifest(target.claudeDir).settings, "settings provenance survives the update");

    fullUninstall(target);
    assert.ok(!existsSync(md), "uninstall still strips the (regenerated) block cleanly");
  } finally { rm(cwd); rm(payloadB); }
});

test("update retires a removed-upstream user-edited rule: kept on disk, dropped from block + files manifest, reported once", () => {
  const { cwd, target } = freshTarget();
  const REL = `rules/${PROBE_RULE}`;
  const payloadB = mutatedPayload((d) => rmSync(path.join(d, "rules", PROBE_RULE)));
  try {
    fullInstall(target);
    const installed = path.join(target.claudeDir, "rules", PROBE_RULE);
    writeFileSync(installed, readFileSync(installed, "utf8") + "\n<!-- user tweak -->\n");

    const res1 = fullUpdate(target, { src: payloadB });
    assert.deepEqual(res1.actions.retired, [REL], "retire reported on the update that drops it");
    assert.ok(existsSync(installed), "user-edited file kept on disk");
    assert.ok(!readFileSync(path.join(cwd, "CLAUDE.local.md"), "utf8").includes(PROBE_RULE), "retired rule no longer imported");
    const meta = readManifest(target.claudeDir);
    assert.ok(!(REL in (meta.files || {})), "retired rule left the files manifest");
    assert.ok(meta.retired && meta.retired[REL], "recorded under manifest.retired");

    const res2 = fullUpdate(target, { src: payloadB });
    assert.deepEqual(res2.actions.retired, [], "retire is reported once, not on every update");
    assert.deepEqual(res2.actions.skipped, [], "no repeated kept-file spam for retired entries");

    const res3 = fullUninstall(target);
    assert.ok(res3.retiredLeft.includes(REL), "uninstall reports the retired leftover");
    assert.ok(existsSync(installed), "retired file stays on disk after uninstall (unmanaged by decision)");
  } finally { rm(cwd); rm(payloadB); }
});

test("fullUpdate WARNS (not silently skips) when the manifest lacks rules-block provenance", () => {
  const { cwd, target } = freshTarget();
  try {
    fullInstall(target);
    const meta = readManifest(target.claudeDir);
    delete meta.settings;
    writeManifest(target.claudeDir, meta);

    const res = fullUpdate(target);
    assert.equal(res.claudeMd, null, "no block target reported");
    assert.match(res.rulesBlockSkipped, /no stored rules-block provenance/, "loud skip reason for the reporter");
    assert.ok(readManifest(target.claudeDir), "manifest still readable after the warned update");
  } finally { rm(cwd); }
});

test("install --force refuses a corrupt or malformed manifest BEFORE touching the payload", () => {
  const { cwd, target } = freshTarget();
  try {
    fullInstall(target);
    const meta = readManifest(target.claudeDir);
    meta.settings.provenance = "not-a-provenance-object"; // malformed shape
    writeManifest(target.claudeDir, meta);

    assert.throws(() => fullInstall(target, { force: true }), /malformed settings\.provenance/, "named, actionable error");
    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "guard-bash.py")), "payload untouched — no rollback destruction");
  } finally { rm(cwd); }
});

test("install --force over a live install preserves original settings provenance (uninstall restores pre-CBR state)", () => {
  const { cwd, target } = freshTarget();
  try {
    mkdirSync(target.claudeDir, { recursive: true });
    const sp = path.join(target.claudeDir, "settings.local.json");
    writeFileSync(sp, JSON.stringify({ model: "opus" }));

    fullInstall(target);
    fullInstall(target, { force: true }); // the documented recovery path — must not poison provenance

    fullUninstall(target);
    assert.deepEqual(parseSettings(sp), { model: "opus" }, "pre-CBR settings restored despite forced reinstall");
    assert.ok(!existsSync(path.join(cwd, "CLAUDE.local.md")), "CBR-created rules file removed (created flag survived --force)");
  } finally { rm(cwd); }
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

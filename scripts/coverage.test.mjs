// Targeted tests for the error/edge branches the lifecycle tests don't reach — driven
// by a SYNTHETIC payload we can mutate between install and update (the real claude/ is
// immutable). Run: node --test scripts/coverage.test.mjs

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, existsSync, writeFileSync, readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { resolveTarget, findProjectRoot } from "./lib/paths.mjs";
import { installFiles } from "./lib/install.mjs";
import { updateFiles } from "./lib/update.mjs";
import { uninstallFiles } from "./lib/uninstall.mjs";
import { computeUnmerge, computeMerge } from "./lib/settings-merge.mjs";
import { stripRulesBlock } from "./lib/rules-block.mjs";
import { resolvePython } from "./lib/doctor.mjs";

const V = "1.0.0";
const rm = (d) => rmSync(d, { recursive: true, force: true });

/** A minimal, mutable payload with only skills/ + hooks/ (agents/rules/schemas/docs
 *  absent → also exercises listPayload's missing-subdir path). Returns {dir, src, target}. */
function fakeInstall() {
  const dir = mkdtempSync(path.join(os.tmpdir(), "cbr-cov-"));
  mkdirSync(path.join(dir, ".git"));
  const src = path.join(dir, "claude");
  mkdirSync(path.join(src, "skills", "cbr-a"), { recursive: true });
  writeFileSync(path.join(src, "skills", "cbr-a", "SKILL.md"), "# A\nschema: {{CBR_ROOT}}/schemas/x.json\n");
  mkdirSync(path.join(src, "hooks"), { recursive: true });
  writeFileSync(path.join(src, "hooks", "h.py"), "print('h')\n");
  const target = resolveTarget("project", dir);
  installFiles(src, target, { version: V });
  return { dir, src, target };
}

test("update: add-new file, refresh-on-content-change, upstream-remove, keep-user-modified, dry-run", () => {
  const { dir, src, target } = fakeInstall();
  try {
    // add-new
    writeFileSync(path.join(src, "hooks", "new.py"), "new\n");
    let r = updateFiles(src, target, { version: V });
    assert.ok(r.actions.added.includes("hooks/new.py"), "new file added");
    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "new.py")));

    // refresh: source content changes → baked bytes differ, on-disk still ours-unmodified
    writeFileSync(path.join(src, "hooks", "h.py"), "print('h v2')\n");
    r = updateFiles(src, target, { version: V });
    assert.ok(r.actions.updated.includes("hooks/h.py"), "changed file refreshed");
    assert.match(readFileSync(path.join(target.claudeDir, "hooks", "h.py"), "utf8"), /h v2/);

    // upstream-remove of an unmodified file → deleted
    rmSync(path.join(src, "hooks", "new.py"));
    r = updateFiles(src, target, { version: V });
    assert.ok(r.actions.removed.includes("hooks/new.py"), "upstream-removed file deleted");
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks", "new.py")));

    // upstream-remove of a USER-MODIFIED file → kept + reported
    writeFileSync(path.join(target.claudeDir, "hooks", "h.py"), "USER EDITED\n");
    rmSync(path.join(src, "hooks", "h.py"));
    r = updateFiles(src, target, { version: V });
    assert.ok(r.actions.skipped.some((s) => s.startsWith("hooks/h.py")), "user-modified upstream-removed file kept");
    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "h.py")), "kept file survives");

    // dry-run mutates nothing and reports the plan
    writeFileSync(path.join(src, "hooks", "z.py"), "z\n");
    r = updateFiles(src, target, { version: V, dryRun: true });
    assert.equal(r.dryRun, true);
    assert.ok(!existsSync(path.join(target.claudeDir, "hooks", "z.py")), "dry-run wrote nothing");
  } finally { rm(dir); }
});

test("update: --force overwrites a user-edited file", () => {
  const { dir, src, target } = fakeInstall();
  try {
    const onDisk = path.join(target.claudeDir, "hooks", "h.py");
    writeFileSync(onDisk, "USER EDIT\n");
    const r = updateFiles(src, target, { version: V, force: true });
    assert.ok(r.actions.updated.some((u) => u.startsWith("hooks/h.py")), "forced over user edit");
    assert.ok(!readFileSync(onDisk, "utf8").includes("USER EDIT"), "shipped content restored");
  } finally { rm(dir); }
});

test("install: staging failure rolls back (a file where a payload dir must go)", () => {
  const { dir, src, target } = fakeInstall();
  try {
    // Fresh target so the install guard doesn't short-circuit.
    const dir2 = mkdtempSync(path.join(os.tmpdir(), "cbr-cov2-"));
    mkdirSync(path.join(dir2, ".git"));
    const t2 = resolveTarget("project", dir2);
    mkdirSync(t2.claudeDir, { recursive: true });
    writeFileSync(path.join(t2.claudeDir, "hooks"), "blocker"); // a FILE where the hooks/ dir must be created
    assert.throws(() => installFiles(src, t2, { version: V }), /staging failed/, "rolled back on staging error");
    rm(dir2);
  } finally { rm(dir); }
});

test("uninstall: no metadata throws; dry-run reports without removing", () => {
  const empty = mkdtempSync(path.join(os.tmpdir(), "cbr-cov3-"));
  mkdirSync(path.join(empty, ".git"));
  try {
    assert.throws(() => uninstallFiles(resolveTarget("project", empty)), /nothing CBR-tracked/);
  } finally { rm(empty); }

  const { dir, target } = fakeInstall();
  try {
    const r = uninstallFiles(target, { dryRun: true });
    assert.equal(r.dryRun, true);
    assert.ok(r.willRemove >= 2, "dry-run counts tracked files");
    assert.ok(existsSync(path.join(target.claudeDir, "hooks", "h.py")), "dry-run removed nothing");
  } finally { rm(dir); }
});

test("paths: invalid scope throws; findProjectRoot walks to .git and falls back", () => {
  assert.throws(() => resolveTarget("bogus"), /invalid scope/);

  const d = mkdtempSync(path.join(os.tmpdir(), "cbr-cov4-"));
  try {
    mkdirSync(path.join(d, ".git"));
    mkdirSync(path.join(d, "a", "b"), { recursive: true });
    assert.equal(findProjectRoot(path.join(d, "a", "b")), path.resolve(d), "walks up to the .git root");
  } finally { rm(d); }

  const d2 = mkdtempSync(path.join(os.tmpdir(), "cbr-cov5-")); // no .git → walk to fs root, fall back to cwd
  try {
    assert.equal(typeof findProjectRoot(d2), "string", "no-.git walk returns a path");
  } finally { rm(d2); }
});

test("settings-merge computeUnmerge: a provenance path into a non-object is a no-op", () => {
  const user = { a: 5 };
  const prov = { keys: [{ path: "a.b.c", had: false }], hooks: [], createdContainers: [] };
  assert.deepEqual(computeUnmerge(user, prov), { a: 5 }, "cannot recurse into a scalar → left unchanged");
});

test("settings-merge: a NESTED created container is fully pruned on un-merge (deleteIfEmpty recursion)", () => {
  const { merged, provenance } = computeMerge({}, { nest: { deep: { key: "v" } } }, { cbrRoot: "R", python: "py" });
  assert.ok(provenance.createdContainers.includes("nest") && provenance.createdContainers.includes("nest.deep"));
  assert.deepEqual(computeUnmerge(merged, provenance), {}, "install then uninstall leaves a nested-created tree gone");
});

test("update: no metadata throws (run install first)", () => {
  const dir = mkdtempSync(path.join(os.tmpdir(), "cbr-cov-upd-"));
  mkdirSync(path.join(dir, ".git"));
  try {
    assert.throws(() => updateFiles(path.join(dir, "claude"), resolveTarget("project", dir), { version: V }),
      /run 'claudebrew install' first/);
  } finally { rm(dir); }
});

test("rules-block stripRulesBlock: absent file is a no-op", () => {
  const p = path.join(os.tmpdir(), "cbr-cov-nonexistent", "CLAUDE.md");
  stripRulesBlock(p, {}); // must not throw
  assert.ok(!existsSync(p));
});

test("doctor resolvePython: a candidate that makes spawn throw is skipped (returns null)", () => {
  assert.equal(resolvePython([String.fromCharCode(0)]), null, "NUL-byte command throws in spawnSync, is caught, and skipped");
});

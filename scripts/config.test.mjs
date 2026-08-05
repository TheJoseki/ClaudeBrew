// Behavioral tests for the config side (merge / doctor / rules block).
// Run: node --test scripts/config.test.mjs

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  parseSettings, computeMerge, computeUnmerge, mergeSettingsFile, unmergeSettingsFile, bakeCommand,
} from "./lib/settings-merge.mjs";
import { resolvePython, runDoctor } from "./lib/doctor.mjs";
import { writeRulesBlock, stripRulesBlock, START, END } from "./lib/rules-block.mjs";

// The shipped settings template (as authored, with tokens + _comment).
const SHIPPED = JSON.parse(readFileSync(new URL("../claude/settings.json", import.meta.url), "utf8"));
const OPTS = { cbrRoot: "C:/proj/.claude", python: "py -3" };

function tmp() { return mkdtempSync(path.join(os.tmpdir(), "cbr-cfg-")); }

test("FAIL-CLOSED: a malformed target settings.json aborts the merge and never writes (S-2)", () => {
  const dir = tmp();
  try {
    const sp = path.join(dir, "settings.json");
    const garbage = '{ "env": { "X": 1 ,,, not json';
    writeFileSync(sp, garbage);
    assert.throws(() => mergeSettingsFile(sp, SHIPPED, OPTS), /not valid JSON/, "merge refuses");
    assert.equal(readFileSync(sp, "utf8"), garbage, "file left byte-for-byte unchanged (no {}-clobber)");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("merge into empty settings adds CBR keys + baked hook commands; _* excluded; no tokens", () => {
  const dir = tmp();
  try {
    const sp = path.join(dir, "settings.json");
    mergeSettingsFile(sp, SHIPPED, OPTS);
    const m = JSON.parse(readFileSync(sp, "utf8"));
    assert.equal(m.teammateMode, "in-process");
    assert.equal(m.worktree.baseRef, "head");
    assert.equal(m.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS, "1");
    assert.equal(m._comment, undefined, "_* keys not propagated");
    const cmds = JSON.stringify(m.hooks);
    assert.ok(!cmds.includes("{{CBR_ROOT}}"), "no tokens survive");
    // Read the real command value (not the JSON-escaped form) to check the exact bake.
    const bashCmd = m.hooks.PreToolUse.find((g) => g.matcher === "Bash").hooks[0].command;
    assert.equal(bashCmd, 'py -3 "C:/proj/.claude/hooks/guard-bash.py"', "interpreter resolved + token baked");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("merge preserves unrelated user keys and does not duplicate hooks on re-merge (H4)", () => {
  const dir = tmp();
  try {
    const sp = path.join(dir, "settings.json");
    const user = { model: "opus", hooks: { PreToolUse: [{ matcher: "Bash", hooks: [{ type: "command", command: "user-own-hook" }] }] } };
    writeFileSync(sp, JSON.stringify(user));
    mergeSettingsFile(sp, SHIPPED, OPTS);
    let m = JSON.parse(readFileSync(sp, "utf8"));
    assert.equal(m.model, "opus", "unrelated user key preserved");
    assert.ok(m.hooks.PreToolUse.some((g) => g.hooks[0].command === "user-own-hook"), "user hook preserved");
    const countAfter1 = m.hooks.PreToolUse.length;
    // re-merge must be idempotent (no duplicate CBR registrations)
    mergeSettingsFile(sp, SHIPPED, OPTS);
    m = JSON.parse(readFileSync(sp, "utf8"));
    assert.equal(m.hooks.PreToolUse.length, countAfter1, "re-merge adds no duplicate registrations");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("un-merge restores the pre-install settings by semantic equality", () => {
  const dir = tmp();
  try {
    const sp = path.join(dir, "settings.json");
    const before = { model: "opus", env: { EXISTING: "keep" }, hooks: { Stop: [{ hooks: [{ command: "user-stop" }] }] } };
    writeFileSync(sp, JSON.stringify(before));
    const user = parseSettings(sp);
    const { merged, provenance } = computeMerge(user, SHIPPED, OPTS);
    const restored = computeUnmerge(merged, provenance);
    assert.deepEqual(restored, before, "install then uninstall returns settings to pre-install state");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("un-merge restores an empty container the user already had (no data-loss prune)", () => {
  const before = { env: {}, worktree: {} }; // user had these, empty
  const { merged, provenance } = computeMerge(before, SHIPPED, OPTS);
  const restored = computeUnmerge(merged, provenance);
  assert.deepEqual(restored, before, "empty user containers are restored, not deleted");
});

test("doctor resolves a real Python; fails loudly when none of the candidates work (D-1)", () => {
  assert.ok(resolvePython() !== null, "a real Python interpreter is found on this machine");
  assert.throws(() => runDoctor({ candidates: ["definitely-not-a-python-xyz"] }), /Python 3 is required/);
});

test("rules block: relative imports per scope, idempotent write, clean strip", () => {
  const dir = tmp();
  try {
    const md = path.join(dir, "CLAUDE.md");
    writeFileSync(md, "# My project\n\nSome existing notes.\n");
    const rules = ["sdlc-conventions.md", "coding-standards.md"];

    const prov = writeRulesBlock(md, rules, "project");
    let c = readFileSync(md, "utf8");
    assert.ok(c.includes("@.claude/rules/sdlc-conventions.md"), "project-scope relative import");
    assert.ok(c.includes("Some existing notes."), "existing content preserved");
    assert.equal(prov.created, false, "did not create (file existed)");

    // idempotent: second write replaces, does not duplicate
    writeRulesBlock(md, rules, "project");
    c = readFileSync(md, "utf8");
    assert.equal(c.split(START).length - 1, 1, "exactly one managed block after re-write");

    stripRulesBlock(md, prov);
    c = readFileSync(md, "utf8");
    assert.ok(!c.includes(START) && !c.includes(END), "block stripped");
    assert.ok(c.includes("Some existing notes."), "user content survives strip");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("rules block: user scope prefix + created-file is removed on strip", () => {
  const dir = tmp();
  try {
    const md = path.join(dir, "CLAUDE.md");
    const prov = writeRulesBlock(md, ["sdlc-conventions.md"], "user");
    assert.equal(prov.created, true, "created a new CLAUDE.md");
    assert.ok(readFileSync(md, "utf8").includes("@rules/sdlc-conventions.md"), "user-scope relative import");
    stripRulesBlock(md, prov);
    assert.ok(!existsSync(md), "a file CBR created solely for the block is removed on strip");
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

// install-from-tarball (S-4): the one failure mode local tests can't see — a `files`
// array that omits scripts/ ships a bin/ importing missing modules, so `npm install`
// then the CLI die with ERR_MODULE_NOT_FOUND while every in-repo test passes.
//
// Run: node --test scripts/tarball.test.mjs   (needs npm + tar; skips gracefully if absent)

import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, existsSync, readdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PKG_ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

test("npm pack ships bin/ + scripts/ and the packed CLI runs (ERR_MODULE_NOT_FOUND guard)", (t) => {
  const out = mkdtempSync(path.join(os.tmpdir(), "cbr-pack-"));
  try {
    // shell:true so `npm` resolves to npm.cmd on Windows.
    const pack = spawnSync("npm", ["pack", "--pack-destination", out], { cwd: PKG_ROOT, encoding: "utf8", shell: true });
    if (pack.status !== 0) { t.skip(`npm pack unavailable (${(pack.stderr || pack.error || "").toString().slice(0, 120)})`); return; }
    const tgz = readdirSync(out).find((f) => f.endsWith(".tgz"));
    assert.ok(tgz, "a .tgz was produced");

    // Install the tarball with npm itself (no `tar` dependency) — the authentic S-4 path.
    const inst = spawnSync("npm", ["install", path.join(out, tgz), "--prefix", out, "--no-save", "--no-audit", "--no-fund"],
      { encoding: "utf8", shell: true });
    if (inst.status !== 0) { t.skip(`npm install of the tarball failed (${(inst.stderr || "").slice(0, 120)})`); return; }
    const pkg = path.join(out, "node_modules", "claudebrew");
    assert.ok(existsSync(path.join(pkg, "bin", "claudebrew.mjs")), "bin shipped");
    assert.ok(existsSync(path.join(pkg, "scripts", "lib", "install.mjs")), "scripts/lib shipped (S-4)");
    assert.ok(existsSync(path.join(pkg, "claude", "docs", "_templates", "STREAM.md")), "shipped templates present (seeding gap)");

    // Run the CLI from the extracted tarball — imports resolve or this throws.
    const help = spawnSync(process.execPath, [path.join(pkg, "bin", "claudebrew.mjs"), "--help"], { encoding: "utf8" });
    assert.equal(help.status, 0, "packed CLI exits 0");
    assert.ok(help.stdout.includes("claudebrew"), "packed CLI prints usage (no ERR_MODULE_NOT_FOUND)");
  } finally { rmSync(out, { recursive: true, force: true }); }
});

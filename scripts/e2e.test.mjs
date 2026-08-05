// End-to-end tests for the CLI: drive main() in-process through the real
// install → update → uninstall lifecycle and every dispatch / exit-code path.
// In-process (not spawned) so it also covers bin/claudebrew.mjs + dev-install.mjs.
// Run: node --test scripts/e2e.test.mjs   (needs a real Python on PATH)

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { main } from "../bin/claudebrew.mjs";

/** A throwaway git repo (the .git marker keeps resolveTarget off any real ~/.claude). */
function repo() {
  const cwd = mkdtempSync(path.join(os.tmpdir(), "cbr-e2e-"));
  mkdirSync(path.join(cwd, ".git"));
  writeFileSync(path.join(cwd, "CLAUDE.md"), "# E2E repo\n");
  return cwd;
}
function cap() {
  const lines = [];
  const sink = (...a) => lines.push(a.join(" "));
  return { log: sink, err: sink, text: () => lines.join("\n") };
}
const quiet = { log: () => {}, err: () => {} };
const rm = (d) => rmSync(d, { recursive: true, force: true });

test("E2E: install -> update (no-op) -> uninstall lifecycle via main()", () => {
  const cwd = repo();
  try {
    let out = cap();
    assert.equal(main(["install"], { cwd, ...out }), 0, "install exits 0");
    assert.ok(existsSync(path.join(cwd, ".claude", "hooks", "guard-bash.py")), "payload installed");
    assert.ok(existsSync(path.join(cwd, ".claude", "settings.local.json")), "settings merged");
    assert.ok(existsSync(path.join(cwd, "CLAUDE.local.md")), "rules block written");
    assert.match(out.text(), /Installed \d+ files/);

    out = cap();
    assert.equal(main(["update"], { cwd, ...out }), 0);
    assert.match(out.text(), /\+0 added, ~0 updated/, "update is a clean no-op");

    out = cap();
    assert.equal(main(["uninstall"], { cwd, ...out }), 0);
    assert.ok(!existsSync(path.join(cwd, ".claude", "hooks", "guard-bash.py")), "payload removed");
    assert.ok(!existsSync(path.join(cwd, "CLAUDE.local.md")), "rules file removed");
    assert.match(out.text(), /Uninstalled \d+ tracked files/);
  } finally { rm(cwd); }
});

test("E2E: install --dry-run mutates nothing; --gate registers the gate; second install refused (exit 1)", () => {
  const cwd = repo();
  try {
    let out = cap();
    assert.equal(main(["install", "--dry-run"], { cwd, ...out }), 0);
    assert.ok(!existsSync(path.join(cwd, ".claude", "hooks")), "dry-run wrote nothing");
    assert.match(out.text(), /\[dry-run\] would install \d+ files/);

    assert.equal(main(["install", "--gate"], { cwd, ...quiet }), 0);
    assert.ok(readFileSync(path.join(cwd, ".claude", "settings.local.json"), "utf8").includes("enforce-worktree"), "gate registered");

    out = cap();
    assert.equal(main(["install"], { cwd, ...out }), 1, "second install without --force → exit 1");
    assert.match(out.text(), /already installed/);

    main(["uninstall"], { cwd, ...quiet });
  } finally { rm(cwd); }
});

test("E2E: uninstall --dry-run reports without removing; --scope=user via home override", () => {
  const cwd = repo();
  const home = mkdtempSync(path.join(os.tmpdir(), "cbr-e2ehome-"));
  try {
    main(["install"], { cwd, ...quiet });
    const out = cap();
    assert.equal(main(["uninstall", "--dry-run"], { cwd, ...out }), 0);
    assert.ok(existsSync(path.join(cwd, ".claude", "hooks")), "dry-run removed nothing");
    assert.match(out.text(), /\[dry-run\] would remove \d+ tracked files/);
    main(["uninstall"], { cwd, ...quiet });

    // user scope (--scope=… form) into an injected home
    assert.equal(main(["install", "--scope=user"], { cwd, home, ...quiet }), 0);
    assert.ok(existsSync(path.join(home, ".claude", "hooks", "guard-bash.py")), "user-scope install under injected home");
    main(["uninstall", "--scope", "user"], { cwd, home, ...quiet });
    assert.ok(!existsSync(path.join(home, ".claude", "hooks", "guard-bash.py")), "user-scope uninstall");
  } finally { rm(cwd); rm(home); }
});

test("E2E: exit codes — help 0, no-command 2, unknown-command 2, unknown-flag 2", () => {
  const out = cap();
  assert.equal(main(["--help"], out), 0);
  assert.ok(out.text().includes("Usage:"));
  assert.equal(main([], quiet), 2, "no command → 2");
  assert.equal(main(["frobnicate"], quiet), 2, "unknown command → 2");
  assert.equal(main(["install", "--bogus"], quiet), 2, "unknown flag → 2");
});

test("E2E: update --dry-run report; update reports a kept user-edited file", () => {
  const cwd = repo();
  try {
    main(["install"], { cwd, ...quiet });

    let out = cap();
    assert.equal(main(["update", "--dry-run"], { cwd, ...out }), 0);
    assert.match(out.text(), /\[dry-run\] add \d+, update \d+/);

    const f = path.join(cwd, ".claude", "hooks", "guard-bash.py");
    writeFileSync(f, readFileSync(f, "utf8") + "\n# user edit\n");
    out = cap();
    assert.equal(main(["update"], { cwd, ...out }), 0);
    assert.match(out.text(), /kept: hooks\/guard-bash\.py/, "update reports the kept user-edited file");

    main(["uninstall"], { cwd, ...quiet });
  } finally { rm(cwd); }
});

test("E2E: install --dev re-syncs the repo's own .claude payload (dogfood loop)", () => {
  // Runs the real devInstall against the package root (idempotent re-sync of the
  // gitignored .claude/ payload) — covers the --dev branch + dev-install.mjs.
  assert.equal(main(["install", "--dev"], quiet), 0);
});

test("E2E: main() falls back to console.log/error when log/err are not injected", () => {
  const origLog = console.log, origErr = console.error;
  console.log = () => {};
  console.error = () => {};
  try {
    assert.equal(main(["--help"]), 0, "default log path"); // exercises the default log arrow
    assert.equal(main(["definitely-not-a-command"]), 2, "default err path"); // exercises the default err arrow
  } finally {
    console.log = origLog;
    console.error = origErr;
  }
});

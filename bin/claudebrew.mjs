#!/usr/bin/env node
// ClaudeBrew installer CLI — entry point.
//
// Phase 4 wires the FILE side: install/update/uninstall provision the `claude/` payload
// into the target `.claude/`, baking residual {{CBR_ROOT}} tokens to absolute paths and
// tracking a hash manifest. The CONFIG side (Python doctor, settings deep-merge, rules
// block, opt-in worktree gate) is layered on next — `install` here does file provisioning
// only. `install --dev` remains the dogfood self-install loop.
//
// Node built-ins only (zero runtime deps).

import { resolveTarget } from "../scripts/lib/paths.mjs";
import { sourceRoot } from "../scripts/lib/pkg.mjs";
import { installFiles } from "../scripts/lib/install.mjs";
import { updateFiles } from "../scripts/lib/update.mjs";
import { uninstallFiles } from "../scripts/lib/uninstall.mjs";
import { fullInstall, fullUninstall } from "../scripts/lib/orchestrate.mjs";
import { devInstall } from "../scripts/lib/dev-install.mjs";

const USAGE = `claudebrew — install the ClaudeBrew SDLC skills into your Claude Code environment

Usage:
  claudebrew install   [--scope project|user] [--dev] [--shared] [--dry-run]
  claudebrew update    [--scope project|user] [--force] [--dry-run]
  claudebrew uninstall [--scope project|user] [--dry-run]

Flags:
  --scope <project|user>  target .claude/ (repo root) or ~/.claude/ (default: project)
  --dev                   dogfood: sync the local claude/ payload into this repo's .claude/
  --shared                project scope only — merge into settings.json (tracked), not settings.local.json
  --gate                  install: also register the opt-in base-branch worktree gate (default: off)
  --force                 install: reinstall over an existing install; update: overwrite user-modified files
  --dry-run               print the file plan without touching disk
  -h, --help              show this help
`;

/** Minimal argv parser: first bare token = command; recognizes the known flags. */
function parseArgs(argv) {
  const flags = { scope: "project", dev: false, shared: false, gate: false, force: false, dryRun: false, help: false };
  let command = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "-h":
      case "--help": flags.help = true; break;
      case "--dev": flags.dev = true; break;
      case "--shared": flags.shared = true; break;
      case "--gate": flags.gate = true; break;
      case "--force": flags.force = true; break;
      case "--dry-run": flags.dryRun = true; break;
      case "--scope": flags.scope = argv[++i]; break;
      default:
        if (a.startsWith("--scope=")) flags.scope = a.slice("--scope=".length);
        else if (!a.startsWith("-") && command === null) command = a;
        else { console.error(`Unknown argument: ${a}\n`); console.error(USAGE); process.exit(2); }
    }
  }
  return { command, flags };
}

function reportActions(res) {
  if (res.dryRun) {
    if (res.action === "install") console.log(`[dry-run] would install ${res.count} files`);
    else if (res.action === "uninstall") console.log(`[dry-run] would remove ${res.willRemove} tracked files`);
    else {
      const a = res.actions;
      console.log(`[dry-run] add ${a.added.length}, update ${a.updated.length}, skip ${a.skipped.length}, remove ${a.removed.length}, unchanged ${a.unchanged.length}`);
    }
    return;
  }
  if (res.action === "install") {
    console.log(`Installed ${res.installed} files into ${res.claudeDir}`);
    if (res.settingsFile) console.log(`  settings merged → ${res.settingsFile}`);
    if (res.claudeMd) console.log(`  rules block → ${res.claudeMd}`);
    if (res.python) console.log(`  Python interpreter: ${res.python}`);
    console.log(`  worktree gate: ${res.gate ? "registered (opt-in)" : "not registered (pass --gate to enable)"}`);
  } else if (res.action === "uninstall") {
    console.log(`Uninstalled ${res.removed} tracked files`);
    if (res.kept && res.kept.length) {
      console.log(`  kept ${res.kept.length} user-modified file(s) (use uninstall --force to remove):`);
      for (const k of res.kept) console.log(`    ${k}`);
    }
  }
  else {
    const a = res.actions;
    console.log(`Update: +${a.added.length} added, ~${a.updated.length} updated, ${a.skipped.length} kept (user-modified), -${a.removed.length} removed, ${a.unchanged.length} unchanged`);
    for (const s of a.skipped) console.log(`  kept: ${s}`);
  }
}

function main() {
  const { command, flags } = parseArgs(process.argv.slice(2));

  if (flags.help || command === null) {
    console.log(USAGE);
    process.exit(command === null && !flags.help ? 2 : 0);
  }

  try {
    switch (command) {
      case "install":
        if (flags.dev) { devInstall(); return; }
        if (flags.dryRun) { reportActions(installFiles(sourceRoot(), resolveTarget(flags.scope), { dryRun: true })); return; }
        reportActions(fullInstall(resolveTarget(flags.scope), { shared: flags.shared, gate: flags.gate, force: flags.force }));
        return;
      case "update":
        reportActions(updateFiles(sourceRoot(), resolveTarget(flags.scope), { force: flags.force, dryRun: flags.dryRun }));
        return;
      case "uninstall":
        if (flags.dryRun) { reportActions(uninstallFiles(resolveTarget(flags.scope), { dryRun: true })); return; }
        reportActions(fullUninstall(resolveTarget(flags.scope), { force: flags.force }));
        return;
      default:
        console.error(`Unknown command: ${command}\n`);
        console.error(USAGE);
        process.exit(2);
    }
  } catch (e) {
    console.error(`claudebrew ${command}: ${e.message}`);
    process.exit(1);
  }
}

main();

#!/usr/bin/env node
// ClaudeBrew installer CLI — entry point.
//
// `install|update|uninstall` provision the `claude/` payload into the target `.claude/`,
// baking residual {{CBR_ROOT}} tokens to absolute paths, deep-merging settings, and
// writing the rules block. `install --dev` is the dogfood self-install loop.
//
// main() is a PURE dispatcher: it returns an exit code (never calls process.exit), takes
// cwd/home/log/err by injection (never reads process.cwd() directly), so it is fully
// testable in-process. The entry guard below runs it only when invoked as the CLI.
//
// Node built-ins only (zero runtime deps).

import { pathToFileURL } from "node:url";
import { resolveTarget } from "../scripts/lib/paths.mjs";
import { sourceRoot } from "../scripts/lib/pkg.mjs";
import { installFiles } from "../scripts/lib/install.mjs";
import { uninstallFiles } from "../scripts/lib/uninstall.mjs";
import { fullInstall, fullUninstall, fullUpdate } from "../scripts/lib/orchestrate.mjs";
import { devInstall } from "../scripts/lib/dev-install.mjs";

export const USAGE = `claudebrew — install the ClaudeBrew SDLC skills into your Claude Code environment

Usage:
  claudebrew install   [--scope project|user] [--dev] [--shared] [--gate] [--dry-run]
  claudebrew update    [--scope project|user] [--force] [--dry-run]
  claudebrew uninstall [--scope project|user] [--force] [--dry-run]

Flags:
  --scope <project|user>  target .claude/ (repo root) or ~/.claude/ (default: project)
  --dev                   dogfood: sync the local claude/ payload into this repo's .claude/
  --shared                project scope only — merge into settings.json (tracked), not settings.local.json
  --gate                  install: also register the opt-in base-branch worktree gate (default: off)
  --force                 install: reinstall over an existing install; update: overwrite user-modified files
  --dry-run               print the file plan without touching disk
  -h, --help              show this help
`;

/** Minimal argv parser: first bare token = command; recognizes the known flags. On an
 *  unknown argument it records `badArg` (main turns that into exit code 2). */
export function parseArgs(argv) {
  const flags = { scope: "project", dev: false, shared: false, gate: false, force: false, dryRun: false, help: false };
  let command = null;
  let badArg = null;
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
        else if (badArg === null) badArg = a;
    }
  }
  return { command, flags, badArg };
}

function reportActions(res, log) {
  if (res.dryRun) {
    if (res.action === "install") log(`[dry-run] would install ${res.count} files`);
    else if (res.action === "uninstall") log(`[dry-run] would remove ${res.willRemove} tracked files`);
    else {
      const a = res.actions;
      log(`[dry-run] add ${a.added.length}, update ${a.updated.length}, skip ${a.skipped.length}, remove ${a.removed.length}, retire ${(a.retired || []).length}, unchanged ${a.unchanged.length}`);
    }
    return;
  }
  if (res.action === "install") {
    log(`Installed ${res.installed} files into ${res.claudeDir}`);
    if (res.settingsFile) log(`  settings merged → ${res.settingsFile}`);
    if (res.claudeMd) log(`  rules block → ${res.claudeMd}`);
    if (res.python) log(`  Python interpreter: ${res.python}`);
    log(`  worktree gate: ${res.gate ? "registered (opt-in)" : "not registered (pass --gate to enable)"}`);
  } else if (res.action === "uninstall") {
    log(`Uninstalled ${res.removed} tracked files`);
    if (res.kept && res.kept.length) {
      log(`  kept ${res.kept.length} user-modified file(s) (use uninstall --force to remove):`);
      for (const k of res.kept) log(`    ${k}`);
    }
    if (res.retiredLeft && res.retiredLeft.length) {
      log(`  ${res.retiredLeft.length} retired file(s) (upstream-removed, user-edited) left in place:`);
      for (const r of res.retiredLeft) log(`    ${r}`);
    }
  } else {
    const a = res.actions;
    log(`Update: +${a.added.length} added, ~${a.updated.length} updated, ${a.skipped.length} kept (user-modified), -${a.removed.length} removed, ${a.unchanged.length} unchanged`);
    for (const s of a.skipped) log(`  kept: ${s}`);
    for (const r of a.retired || []) log(`  retired: ${r} (removed upstream, user-edited — kept on disk, no longer managed or loaded)`);
    if (res.claudeMd) log(`  rules block refreshed → ${res.claudeMd}`);
    if (res.rulesBlockSkipped) log(`  WARNING: rules block NOT refreshed — ${res.rulesBlockSkipped}`);
  }
}

/**
 * Dispatch a CLI invocation. Pure: returns an exit code (0/1/2), never exits the process.
 * @param {string[]} argv  args after the node/script (process.argv.slice(2))
 * @param {{cwd?:string, home?:string, log?:Function, err?:Function}} [opts]
 * @returns {number} exit code
 */
export function main(argv, opts = {}) {
  const cwd = opts.cwd ?? process.cwd();
  const home = opts.home; // undefined → resolveTarget uses os.homedir()
  const log = opts.log ?? ((...a) => console.log(...a));
  const err = opts.err ?? ((...a) => console.error(...a));
  const rt = (scope) => resolveTarget(scope, cwd, home);

  const { command, flags, badArg } = parseArgs(argv);
  if (badArg) { err(`Unknown argument: ${badArg}\n`); err(USAGE); return 2; }
  if (flags.help || command === null) { log(USAGE); return command === null && !flags.help ? 2 : 0; }

  try {
    switch (command) {
      case "install":
        if (flags.dev) { devInstall(); return 0; }
        if (flags.dryRun) { reportActions(installFiles(sourceRoot(), rt(flags.scope), { dryRun: true }), log); return 0; }
        reportActions(fullInstall(rt(flags.scope), { shared: flags.shared, gate: flags.gate, force: flags.force }), log);
        return 0;
      case "update":
        reportActions(fullUpdate(rt(flags.scope), { force: flags.force, dryRun: flags.dryRun }), log);
        return 0;
      case "uninstall":
        if (flags.dryRun) { reportActions(uninstallFiles(rt(flags.scope), { dryRun: true }), log); return 0; }
        reportActions(fullUninstall(rt(flags.scope), { force: flags.force }), log);
        return 0;
      default:
        err(`Unknown command: ${command}\n`);
        err(USAGE);
        return 2;
    }
  } catch (e) {
    err(`claudebrew ${command}: ${e.message}`);
    return 1;
  }
}

// Entry guard — run main only when invoked directly as the CLI, not when imported by tests.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}

#!/usr/bin/env node
// ClaudeBrew installer CLI — entry point.
//
// Phase 1 stub: argument parsing + verb/flag dispatch only. The real
// provisioning (install/update/uninstall) lands in Phases 4–5. The one verb
// wired to real logic here is `install --dev`, the dogfood self-install loop
// that replaces the retired `claude --plugin-dir ./plugins/cbr`.
//
// Node built-ins only (zero runtime deps).

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
  --force                 update: overwrite user-modified managed files
  --dry-run               print the plan without touching disk
  -h, --help              show this help
`;

/** Minimal argv parser: first bare token = command; recognizes the known flags. */
function parseArgs(argv) {
  const flags = { scope: "project", dev: false, shared: false, force: false, dryRun: false, help: false };
  let command = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "-h":
      case "--help": flags.help = true; break;
      case "--dev": flags.dev = true; break;
      case "--shared": flags.shared = true; break;
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

const NOT_YET = (verb) => {
  console.error(`\`claudebrew ${verb}\` is not implemented yet (lands in Phases 4–5).`);
  console.error(`For local development, use: claudebrew install --dev`);
  process.exit(1);
};

function main() {
  const { command, flags } = parseArgs(process.argv.slice(2));

  if (flags.help || command === null) {
    console.log(USAGE);
    process.exit(command === null && !flags.help ? 2 : 0);
  }

  switch (command) {
    case "install":
      if (flags.dev) { devInstall(); return; }
      return NOT_YET("install");
    case "update":
      return NOT_YET("update");
    case "uninstall":
      return NOT_YET("uninstall");
    default:
      console.error(`Unknown command: ${command}\n`);
      console.error(USAGE);
      process.exit(2);
  }
}

main();

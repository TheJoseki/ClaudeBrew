// Full install/uninstall flow: compose the file side (Phase 4) with the config side.
// Node built-ins only.
//
//   install:   doctor (fail-loud if no Python) → provision files → deep-merge settings →
//              write CLAUDE.md rules block → [opt-in worktree gate] → record provenance
//   uninstall: un-merge settings + strip rules block (from provenance) → remove files
//
// Every config mutation is provenance-tracked in metadata.json so uninstall restores the
// user's pre-install state.

import path from "node:path";
import { readFileSync, readdirSync } from "node:fs";
import { installFiles } from "./install.mjs";
import { uninstallFiles } from "./uninstall.mjs";
import { runDoctor } from "./doctor.mjs";
import { mergeSettingsFile, unmergeSettingsFile } from "./settings-merge.mjs";
import { writeRulesBlock, stripRulesBlock } from "./rules-block.mjs";
import { readManifest, writeManifest } from "./metadata.mjs";
import { sourceRoot } from "./pkg.mjs";

/** Where CBR's settings are merged. Project scope defaults to the gitignored, per-machine
 *  settings.local.json (M4 trust model); --shared opts into the tracked settings.json. */
function settingsFileFor(target, shared) {
  if (target.scope === "user") return path.join(target.claudeDir, "settings.json");
  return path.join(target.claudeDir, shared ? "settings.json" : "settings.local.json");
}

/** Host file for the rules block. User scope → the user's global memory ~/.claude/CLAUDE.md.
 *  Project scope → CLAUDE.local.md at the repo root: a docs-supported, gitignored, per-machine
 *  memory file (auto-loaded alongside CLAUDE.md). Using it — symmetric with the
 *  settings.local.json default — keeps the block out of the tracked CLAUDE.md and avoids
 *  leaving 13 dangling @-imports for teammates who clone but have not run the installer. */
function claudeMdFor(target) {
  return target.scope === "user"
    ? path.join(target.claudeDir, "CLAUDE.md")
    : path.join(target.base, "CLAUDE.local.md");
}

function shippedRuleFiles(src) {
  return readdirSync(path.join(src, "rules")).filter((f) => f.endsWith(".md")).sort();
}

/** The opt-in worktree gate registration (token + bare `python` — baked by the merge). */
function gateShipped() {
  return {
    hooks: {
      PreToolUse: [
        { matcher: "Edit|Write|NotebookEdit", hooks: [{ type: "command", command: 'python "{{CBR_ROOT}}/hooks/enforce-worktree.py"' }] },
      ],
    },
  };
}

export function fullInstall(target, opts = {}) {
  const { shared = false, gate = false, force = false } = opts;
  const src = sourceRoot();

  const { python } = runDoctor(); // D-1: fail the install if no Python
  const mergeOpts = { cbrRoot: target.cbrRoot, python };

  const fileRes = installFiles(src, target, { force }); // writes metadata (files section)

  // The config stages can fail on purpose — the fail-closed guard throws on an unparseable
  // user settings.json. Roll the payload back so that path leaves the prior state, not a
  // wedged half-install whose only recovery is `install --force`.
  try {
    const settingsFile = settingsFileFor(target, shared);
    const shipped = JSON.parse(readFileSync(path.join(src, "settings.json"), "utf8"));
    const provenance = mergeSettingsFile(settingsFile, shipped, mergeOpts);

    let gateAdded = false;
    if (gate) {
      const gp = mergeSettingsFile(settingsFile, gateShipped(), mergeOpts);
      provenance.hooks.push(...gp.hooks);
      gateAdded = gp.hooks.length > 0;
    }

    const claudeMd = claudeMdFor(target);
    const rulesProvenance = writeRulesBlock(claudeMd, shippedRuleFiles(src), target.scope);

    const meta = readManifest(target.claudeDir);
    meta.settings = { settingsFile, provenance, claudeMd, rulesProvenance, gate: gateAdded, python };
    writeManifest(target.claudeDir, meta);

    return { ...fileRes, action: "install", settingsFile, claudeMd, gate: gateAdded, python };
  } catch (e) {
    try { uninstallFiles(target, { force: true }); } catch { /* best-effort payload rollback */ }
    throw e;
  }
}

export function fullUninstall(target, opts = {}) {
  const meta = readManifest(target.claudeDir);
  if (!meta) throw new Error(`no metadata.json at ${target.claudeDir} — nothing CBR-tracked to uninstall`);

  const s = meta.settings;
  if (s) {
    if (s.settingsFile && s.provenance) unmergeSettingsFile(s.settingsFile, s.provenance);
    if (s.claudeMd) stripRulesBlock(s.claudeMd, s.rulesProvenance || {});
  }
  const fileRes = uninstallFiles(target, { force: opts.force }); // removes files + (if nothing kept) metadata
  return { ...fileRes, action: "uninstall", settingsUnmerged: !!s };
}

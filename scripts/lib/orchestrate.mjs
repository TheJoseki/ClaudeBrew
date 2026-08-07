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
import { updateFiles } from "./update.mjs";
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

  // A forced reinstall runs over settings that already contain CBR's own values. Re-merging
  // there would record CBR as the user's "prior" state and poison uninstall (it would
  // restore CBR values, leaving e.g. hooks registered for removed files). Capture the
  // ORIGINAL provenance — still the truth about the pre-CBR state — before installFiles
  // rewrites the manifest, and carry it through instead of re-deriving it. Any manifest
  // problem must throw HERE, before installFiles mutates anything: the config catch below
  // rolls the payload back, which on a forced reinstall would destroy a working install.
  const prior = force ? readPriorManifest(target) : null;
  const priorSettings = prior?.settings ?? null;

  const fileRes = installFiles(src, target, { force }); // writes metadata (files section)

  // The config stages can fail on purpose — the fail-closed guard throws on an unparseable
  // user settings.json. Roll the payload back so that path leaves the prior state, not a
  // wedged half-install whose only recovery is `install --force`.
  try {
    const settingsFile = priorSettings?.settingsFile ?? settingsFileFor(target, shared);
    let provenance = priorSettings?.provenance;
    let gateAdded = priorSettings?.gate ?? false;
    if (!priorSettings) {
      const shipped = JSON.parse(readFileSync(path.join(src, "settings.json"), "utf8"));
      provenance = mergeSettingsFile(settingsFile, shipped, mergeOpts);
    }

    if (gate && !gateAdded) {
      const gp = mergeSettingsFile(settingsFile, gateShipped(), mergeOpts);
      provenance.hooks.push(...gp.hooks);
      gateAdded = gp.hooks.length > 0;
    }

    const claudeMd = priorSettings?.claudeMd ?? claudeMdFor(target);
    const rp = writeRulesBlock(claudeMd, shippedRuleFiles(src), target.scope);
    // On reinstall the file already exists, so rp.created is false — but whether CBR
    // originally created it is what uninstall needs. Preserve the original flag.
    const rulesProvenance = priorSettings
      ? { file: rp.file, created: priorSettings.rulesProvenance?.created ?? rp.created }
      : rp;

    const meta = readManifest(target.claudeDir);
    meta.settings = { settingsFile, provenance, claudeMd, rulesProvenance, gate: gateAdded, python };
    // Retired files (removed upstream, user-edited) must survive a forced reinstall, or a
    // later re-ship of the same path would silently clobber the user's kept copy.
    if (prior?.retired && Object.keys(prior.retired).length) meta.retired = prior.retired;
    writeManifest(target.claudeDir, meta);

    return { ...fileRes, action: "install", settingsFile, claudeMd, gate: gateAdded, python };
  } catch (e) {
    try { uninstallFiles(target, { force: true }); } catch { /* best-effort payload rollback */ }
    throw e;
  }
}

/** Read + validate the prior manifest for a forced reinstall. A corrupt manifest or a
 *  malformed settings.provenance fails with an actionable error instead of a mid-flight
 *  TypeError (which would trigger the payload rollback while leaving settings merged). */
function readPriorManifest(target) {
  let meta;
  try {
    meta = readManifest(target.claudeDir);
  } catch (e) {
    throw new Error(`metadata.json at ${target.claudeDir} is unreadable (${e.message}) — fix or delete it, then re-run 'claudebrew install --force'`);
  }
  const s = meta?.settings;
  if (s) {
    const p = s.provenance;
    if (!p || !Array.isArray(p.keys) || !Array.isArray(p.hooks) || !Array.isArray(p.createdContainers)) {
      throw new Error(`metadata.json at ${target.claudeDir} has a malformed settings.provenance — cannot safely force-reinstall over it; run 'claudebrew uninstall' first`);
    }
  }
  return { settings: s ?? null, retired: meta?.retired ?? null };
}

/**
 * Update = file reconciliation + config refresh. The config half is the reason this
 * exists: the rules `@`-import block must be regenerated from the NEW payload's rule
 * listing, or a rules-set change lands on disk but is never (un)loaded in any session.
 * `opts.src` is injectable for tests that simulate a different-version payload.
 */
export function fullUpdate(target, opts = {}) {
  const { force = false, dryRun = false, src = sourceRoot() } = opts;
  const fileRes = updateFiles(src, target, { force, dryRun });
  if (dryRun) return fileRes;

  const meta = readManifest(target.claudeDir);
  const s = meta?.settings;
  if (s?.claudeMd) {
    const rp = writeRulesBlock(s.claudeMd, shippedRuleFiles(src), target.scope);
    s.rulesProvenance = { file: rp.file, created: s.rulesProvenance?.created ?? rp.created };
    writeManifest(target.claudeDir, meta);
    return { ...fileRes, claudeMd: s.claudeMd };
  }
  // No stored rules-block location (install predates provenance tracking): report loudly —
  // a silently stale block is exactly the failure mode this function exists to prevent.
  return {
    ...fileRes,
    claudeMd: null,
    rulesBlockSkipped: "no stored rules-block provenance (metadata.settings.claudeMd missing) — run 'claudebrew install --force' once to record it",
  };
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

// Deep-merge CBR's shipped settings into the user's settings.json, reversibly.
// Node built-ins only.
//
// This is a REAL recursive merge (the old hooks/settings_merge.py is a single-purpose
// gate registrar, NOT reusable). Guarantees:
//   - FAIL-CLOSED (S-2): if the target file doesn't parse, throw — never write, never
//     replace it with {}. A truncated/garbage settings.json stops Claude from starting,
//     so we refuse rather than risk clobbering a valid-but-unreadable file.
//   - Objects merge recursively; scalars CBR owns are set (prior value recorded for
//     un-merge); hook registrations UNION with dedup on (matcher, commands) so re-install
//     never appends a duplicate (H4).
//   - `_*` keys in the shipped template never propagate to user config.
//   - Every mutation is recorded as provenance so uninstall restores the pre-install state.

import { readFileSync, writeFileSync, renameSync, existsSync } from "node:fs";
import { TOKEN } from "./rewrite.mjs";

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

/** Parse a settings file. Absent → {}. Unparseable → throw (fail-closed). */
export function parseSettings(file) {
  if (!existsSync(file)) return {};
  const raw = readFileSync(file, "utf8");
  if (raw.trim() === "") return {};
  try {
    const v = JSON.parse(raw);
    if (!isObject(v)) throw new Error("top-level value is not an object");
    return v;
  } catch (e) {
    throw new Error(`refusing to merge: ${file} is not valid JSON (${e.message}). Fix or remove it, then retry — CBR will not overwrite a settings file it cannot parse.`);
  }
}

/** Bake a shipped hook command: resolve the interpreter + the {{CBR_ROOT}} token. */
export function bakeCommand(command, cbrRoot, python) {
  const withPy = command.startsWith("python ") ? python + command.slice("python".length) : command;
  return withPy.split(TOKEN).join(cbrRoot);
}

/** Two hook groups are "the same registration" if matcher + the command list match. */
function sameGroup(a, b) {
  const cmds = (g) => JSON.stringify((g.hooks || []).map((h) => h.command));
  return (a.matcher || "") === (b.matcher || "") && cmds(a) === cmds(b);
}

/** Strip `_*` keys (internal annotations) and bake hook commands in the shipped object. */
function prepareShipped(shipped, cbrRoot, python) {
  const out = {};
  for (const [k, v] of Object.entries(shipped)) {
    if (k.startsWith("_")) continue;
    if (k === "hooks" && isObject(v)) {
      out.hooks = {};
      for (const [event, groups] of Object.entries(v)) {
        out.hooks[event] = groups.map((g) => ({
          ...g,
          hooks: (g.hooks || []).map((h) => ({ ...h, command: bakeCommand(h.command, cbrRoot, python) })),
        }));
      }
    } else {
      out[k] = v;
    }
  }
  return out;
}

/**
 * Merge shipped into user, collecting provenance.
 * @returns {{merged: object, provenance: {keys: Array, hooks: Array}}}
 * provenance.keys: {path (dotted), had: bool, prev: any} — leaves CBR set
 * provenance.hooks: {event, group} — registration groups CBR appended
 */
export function computeMerge(userSettings, shippedRaw, { cbrRoot, python }) {
  const shipped = prepareShipped(shippedRaw, cbrRoot, python);
  const provenance = { keys: [], hooks: [], createdContainers: [] };
  const merged = structuredClone(userSettings);

  for (const [key, sval] of Object.entries(shipped)) {
    if (key === "hooks") {
      merged.hooks = mergeHooks(merged.hooks, sval, provenance);
    } else {
      merged[key] = mergeLeaf(merged[key], sval, key, provenance);
    }
  }
  return { merged, provenance };
}

function mergeLeaf(uval, sval, dotted, provenance) {
  if (isObject(sval) && isObject(uval)) {
    const out = { ...uval };
    for (const [k, v] of Object.entries(sval)) out[k] = mergeLeaf(uval[k], v, `${dotted}.${k}`, provenance);
    return out;
  }
  if (isObject(sval) && uval === undefined) {
    // CBR CREATED this container — record it so un-merge deletes it (and only it). A
    // container the user already had (even empty {}) is never pruned. Also record each leaf.
    provenance.createdContainers.push(dotted);
    for (const [k, v] of Object.entries(sval)) mergeLeaf(undefined, v, `${dotted}.${k}`, provenance);
    return structuredClone(sval);
  }
  // scalar (or type override): CBR owns this key; record prior for un-merge.
  provenance.keys.push({ path: dotted, had: uval !== undefined, prev: uval });
  return sval;
}

function mergeHooks(userHooks, shippedHooks, provenance) {
  if (!isObject(userHooks)) provenance.createdContainers.push("hooks"); // CBR created the hooks object
  const out = isObject(userHooks) ? structuredClone(userHooks) : {};
  for (const [event, groups] of Object.entries(shippedHooks)) {
    out[event] = out[event] || [];
    for (const group of groups) {
      if (!out[event].some((g) => sameGroup(g, group))) {
        out[event].push(structuredClone(group));
        provenance.hooks.push({ event, group: structuredClone(group) });
      }
    }
  }
  return out;
}

/** Reverse a merge from provenance: restore prior scalar values (or delete added keys),
 *  remove appended hook groups. Returns the un-merged settings object. */
export function computeUnmerge(userSettings, provenance) {
  const out = structuredClone(userSettings);
  // hooks: remove groups CBR appended (by identity); drop an event array CBR emptied.
  for (const { event, group } of provenance.hooks || []) {
    if (!Array.isArray(out.hooks?.[event])) continue;
    out.hooks[event] = out.hooks[event].filter((g) => !sameGroup(g, group));
    if (out.hooks[event].length === 0) delete out.hooks[event];
  }
  // scalar leaves: restore the prior value (had) or delete the key CBR added.
  for (const { path, had, prev } of [...(provenance.keys || [])].reverse()) {
    setLeaf(out, path.split("."), had, prev);
  }
  // Prune ONLY containers CBR created (incl. "hooks"), deepest first — a container the
  // user already had (even empty) is left exactly as it was. This is the fix for the
  // "empty {} restored as deleted" data-loss bug.
  for (const cpath of [...(provenance.createdContainers || [])].sort((a, b) => b.length - a.length)) {
    deleteIfEmpty(out, cpath.split("."));
  }
  return out;
}

function setLeaf(obj, parts, had, prev) {
  const [head, ...rest] = parts;
  if (rest.length === 0) {
    if (had) obj[head] = prev;
    else delete obj[head];
    return;
  }
  if (!isObject(obj[head])) return;
  setLeaf(obj[head], rest, had, prev);
}

function deleteIfEmpty(obj, parts) {
  const [head, ...rest] = parts;
  if (rest.length === 0) {
    if (isObject(obj[head]) && Object.keys(obj[head]).length === 0) delete obj[head];
    return;
  }
  if (!isObject(obj[head])) return;
  deleteIfEmpty(obj[head], rest);
}

/** Atomic write (temp + rename) of a settings object. */
export function writeSettings(file, obj) {
  const tmp = file + ".cbrtmp";
  writeFileSync(tmp, JSON.stringify(obj, null, 2) + "\n");
  renameSync(tmp, file);
}

/** Orchestrator: parse (fail-closed) → merge → atomic write. Returns provenance.
 *  If the target is unparseable, parseSettings throws BEFORE any write happens. */
export function mergeSettingsFile(settingsPath, shipped, opts) {
  const user = parseSettings(settingsPath); // fail-closed: throws before we touch disk
  const { merged, provenance } = computeMerge(user, shipped, opts);
  writeSettings(settingsPath, merged);
  return provenance;
}

/** Orchestrator: parse → un-merge from provenance → atomic write. */
export function unmergeSettingsFile(settingsPath, provenance) {
  const user = parseSettings(settingsPath);
  writeSettings(settingsPath, computeUnmerge(user, provenance));
}

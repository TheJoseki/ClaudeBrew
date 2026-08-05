// Preflight doctor. Node built-ins only.
//
// D-1: Python is a HARD runtime prerequisite — every CBR hook is Python (the one bash
// hook was ported). A "warn and proceed" doctor would ship an installer whose hooks
// silently no-op. So: resolve a real Python interpreter; if none works, FAIL the install
// with an actionable message. The resolved invocation is baked into the hook commands
// so they run the interpreter the doctor actually verified, not a bare `python` guess.

import { spawnSync } from "node:child_process";

// Standard, quote-free invocations (no absolute paths → no space-quoting headaches).
export const PYTHON_CANDIDATES = ["python", "python3", "py -3"];

/** Return the first invocation that runs and reports a Python version, else null. */
export function resolvePython(candidates = PYTHON_CANDIDATES) {
  for (const invocation of candidates) {
    const [cmd, ...args] = invocation.split(" ");
    let r;
    try {
      r = spawnSync(cmd, [...args, "--version"], { encoding: "utf8" });
    } catch {
      continue;
    }
    const out = `${r.stdout || ""}${r.stderr || ""}`;
    if (r.status === 0 && /Python \d/.test(out)) return invocation;
  }
  return null;
}

/** Fail-loud Python check. Throws when no interpreter resolves. */
export function runDoctor(opts = {}) {
  const python = resolvePython(opts.candidates);
  if (!python) {
    throw new Error(
      "Python 3 is required to run ClaudeBrew's hooks but none was found on PATH. " +
        "Install it (https://www.python.org/downloads/) so that `python`, `python3`, or `py -3` " +
        "works, then re-run the installer.",
    );
  }
  return { python };
}

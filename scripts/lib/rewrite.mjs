// The content-rewrite primitive: bake residual `{{CBR_ROOT}}` tokens to an absolute
// path. Node built-ins only.
//
// CRITICAL (delimiter safety): the payload contains 111+ unrelated `{{…}}` sequences
// (JSX `style={{…}}`, escaped Python f-string braces). We replace the EXACT literal
// token string only — via split/join, never a `{{…}}` regex — so none of those are
// touched. `grep '{{CBR_ROOT}}'` (exact) is the manifest; a brace pattern would corrupt.

export const TOKEN = "{{CBR_ROOT}}";

/** True if the buffer looks like text (no NUL byte) AND contains the token. Binary
 *  payload files (fonts, etc.) are left byte-identical — decoding them as UTF-8 to
 *  "bake" would be lossy and they never contain the token anyway. */
export function needsBake(buf) {
  if (buf.includes(0x00)) return false; // NUL => treat as binary, never bake
  return buf.toString("utf8").includes(TOKEN);
}

/** Replace every exact `{{CBR_ROOT}}` with cbrRoot. Pure string op (exact literal). */
export function bake(text, cbrRoot) {
  return text.split(TOKEN).join(cbrRoot);
}

/**
 * Given source bytes and the target cbrRoot, return the bytes to write.
 * Text-with-token → baked UTF-8; everything else → the original buffer verbatim.
 * @param {Buffer} buf
 * @param {string} cbrRoot
 * @returns {Buffer}
 */
export function rewriteBytes(buf, cbrRoot) {
  if (!needsBake(buf)) return buf;
  return Buffer.from(bake(buf.toString("utf8"), cbrRoot), "utf8");
}

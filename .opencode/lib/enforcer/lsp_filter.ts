// OMT++ LSP diagnostics allowlist filter (feature_090; meta_harness_dsl R2 module).
//
//   • parseAllowlist / loadAllowlist — read + validate .meta/lsp_allowlist.json
//     ({ "<repo-rel path>": ["<pyright code>", ...] } — tracked DATA, not a
//     harness surface; no receipt round-robin to update it).
//   • applyLspAllowlist             — PURE core: drop allowlisted (file, code)
//     severity-1 entries from a tool result's metadata.diagnostics AND from
//     the rendered "LSP errors detected …" text section (byte-preserving
//     surgery on survivors). Null on no-op OR any surprise (fail-open).
//   • lspAfterEdit                  — thin after-hook entry (edit/write/patch
//     only): mutates output in place (the SDK-documented
//     tool.execute.after mechanism), never blocks.
//
// Render contract (pinned from live opencode.db samples, pyright 1.1.408 —
// recorded fixtures live in tests/scripts/omt/test_scaffolds_lsp_allowlist.py):
//   <base>\n\n
//   LSP errors detected in this file, please fix:      (or "in other files:")
//   <diagnostics file="<abs>">
//   ERROR [L+1:C+1] <message first line>
//   <message continuation lines — pyright indents with U+00A0 inside message>
//   </diagnostics>
//   [\n\n next block …]                                 (text ends with no
//   trailing newline; only files with non-empty arrays render; blocks follow
//   metadata map order; the edited file's block says "this file").
//
// Static-allowlist tradeoff (mh3 §3.12, accepted): a NEW error with the SAME
// (file, code) pair stays hidden; a different code in the same file surfaces.
// Fail-open on ANY surprise — text↔metadata desync, unrecognized severity
// renders (e.g. WARNING […] lines), malformed entries — the result is then
// left completely untouched (text AND metadata). Two severity-1 entries at
// the SAME position are suppressed only when ALL of them are allowlisted
// (safe direction: over-show, never hide).

import { existsSync, readFileSync } from "node:fs"
import { isAbsolute, join, relative } from "node:path"
import type { EnforcerEnv } from "./session_state"

// Tools whose results carry LSP diagnostics (opencode.jsonc "lsp": true).
const LSP_TOOLS = new Set(["edit", "write", "patch"])

const HEADER_THIS = "LSP errors detected in this file, please fix:"
const HEADER_OTHER = "LSP errors detected in other files:"

function isHeaderLine(ln: string | undefined): boolean {
  return ln === HEADER_THIS || ln === HEADER_OTHER
}

// --- allowlist IO ------------------------------------------------------------

// Pure: parse + validate the allowlist JSON. Null on ANY surprise (invalid
// JSON, non-object root, non-string-array values) — callers treat null as
// "no allowlist" and leave results unfiltered (fail-open).
export function parseAllowlist(text: string): Record<string, string[]> | null {
  let raw: any
  try { raw = JSON.parse(text) } catch { return null }
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null
  const out: Record<string, string[]> = {}
  for (const [k, v] of Object.entries(raw)) {
    if (!k || !Array.isArray(v) || !v.every((c) => typeof c === "string" && c)) return null
    out[k.split("\\").join("/")] = v
  }
  return out
}

// Read <root>/.meta/lsp_allowlist.json (no caching — a mid-session edit of
// the DATA file takes effect on the next tool result).
export function loadAllowlist(root: string): Record<string, string[]> | null {
  try {
    const p = join(root, ".meta", "lsp_allowlist.json")
    if (!existsSync(p)) return null
    return parseAllowlist(readFileSync(p, "utf8"))
  } catch { return null }
}

// abs metadata key -> repo-rel allowlist key (forward-slash normalized).
function allowlistCodesFor(
  allowlist: Record<string, string[]>, file: string, root: string,
): string[] | null {
  const key = (isAbsolute(file) ? relative(root, file) : file).split("\\").join("/")
  return allowlist[key] ?? null
}

// "L+1:C+1" position key for a metadata entry (null on a malformed shape).
function posKeyOf(e: any): string | null {
  const s = e?.range?.start
  if (!s || typeof s.line !== "number" || typeof s.character !== "number") return null
  return `${s.line + 1}:${s.character + 1}`
}

// --- pure core ---------------------------------------------------------------

export interface LspFilterApplied {
  text: string
  diags: Record<string, any[]>
  dropped: number
}

// TA: xref: feature_090 (mh8 T2-7 / mh3 P3-11) — the render contract above is pinned from live opencode.db samples (pyright 1.1.408); fixtures in tests/scripts/omt/test_scaffolds_lsp_allowlist.py. If opencode's LSP render format ever changes (headers/block shape/ERROR prefix), this strict parser fails OPEN (null → unfiltered output) — update parser + fixtures together. The allowlist file is DATA (.meta/lsp_allowlist.json), NOT a harness surface: editing it needs NO e2e receipt round.
export function applyLspAllowlist(
  text: string,
  diags: Record<string, any[]>,
  allowlist: Record<string, string[]>,
  root: string,
): LspFilterApplied | null {
  // Pass 1 — index severity-1 entries by (file, "L:C") position.
  const errByPos = new Map<string, Map<string, any[]>>()
  for (const [file, entries] of Object.entries(diags)) {
    if (!Array.isArray(entries)) return null
    let fm = errByPos.get(file)
    if (!fm) { fm = new Map(); errByPos.set(file, fm) }
    for (const e of entries) {
      if (e?.severity !== 1) continue
      const pos = posKeyOf(e)
      if (pos === null) return null
      const cur = fm.get(pos)
      if (cur) cur.push(e); else fm.set(pos, [e])
    }
  }

  // Pass 2 — decide suppressed positions; build the filtered metadata map.
  const supPos = new Map<string, Set<string>>()
  const newDiags: Record<string, any[]> = {}
  let dropped = 0
  for (const [file, entries] of Object.entries(diags)) {
    const fm = errByPos.get(file)!
    const codes = allowlistCodesFor(allowlist, file, root)
    const sup = new Set<string>()
    const kept: any[] = []
    for (const e of entries) {
      const pos = e?.severity === 1 ? posKeyOf(e) : null
      // Suppress a position only when EVERY severity-1 entry at it is
      // allowlisted (twin diagnostics at one position: over-show, never hide).
      if (pos !== null && codes && fm.get(pos)!.every((x) => codes.includes(x.code))) {
        sup.add(pos)
        dropped++
        continue
      }
      kept.push(e)
    }
    if (sup.size) {
      const s = supPos.get(file)
      if (s) { for (const p of sup) s.add(p) } else supPos.set(file, sup)
    }
    if (!sup.size) newDiags[file] = entries // untouched — keep the reference
    else if (kept.length) newDiags[file] = kept
    /* else: every entry suppressed — omit the key (renderer skips empties) */
  }
  if (dropped === 0) return null

  // Pass 3 — byte-preserving surgery on the rendered text section.
  const lines = text.split("\n")
  const hs = lines.findIndex(isHeaderLine)
  if (hs === -1) return null // metadata says errors, text has no section
  if (hs > 0 && lines[hs - 1] !== "") return null // no separator before the section
  const prefix = lines.slice(0, hs)
  const outBlocks: string[][] = []
  const seenFiles = new Set<string>()
  let trailingNl = false
  let i = hs
  while (i < lines.length) {
    if (!isHeaderLine(lines[i])) return null
    const openM = /^<diagnostics file="(.*)">$/.exec(lines[i + 1] ?? "")
    if (!openM) return null
    const file = openM[1]
    let e = -1
    for (let k = i + 2; k < lines.length; k++) {
      if (lines[k] === "</diagnostics>") { e = k; break }
      if (isHeaderLine(lines[k]) || lines[k].startsWith("<diagnostics ")) return null
    }
    if (e === -1) return null
    seenFiles.add(file)
    // Split the body into ERROR groups (a group = ERROR line + continuation
    // lines of its multi-line message).
    const groups: { s: number; e2: number; pos: string }[] = []
    for (let k = i + 2; k < e; k++) {
      const ln = lines[k]
      const m = /^ERROR \[(\d+):(\d+)\](?: .*)?$/.exec(ln)
      if (m) groups.push({ s: k, e2: k, pos: `${Number(m[1])}:${Number(m[2])}` })
      else if (/^[A-Z]+ \[\d+:\d+\]/.test(ln)) return null // non-ERROR severity render
      else if (groups.length) groups[groups.length - 1].e2 = k
      else return null // body line before any ERROR line
    }
    if (!groups.length) return null // an empty body never renders legitimately
    const fm = errByPos.get(file)
    const sup = supPos.get(file)
    const blk: string[] = [lines[i], lines[i + 1]]
    for (const g of groups) {
      if (!fm || !fm.has(g.pos)) return null // text line with no metadata entry → desync
      if (sup && sup.has(g.pos)) continue // suppressed — drop the group
      for (let k = g.s; k <= g.e2; k++) blk.push(lines[k])
    }
    blk.push("</diagnostics>")
    if (blk.length > 3) outBlocks.push(blk) // survives when ≥ 1 group kept
    // advance past the block (only end / single trailing "" / ""+header legal)
    if (e === lines.length - 1) break
    if (lines[e + 1] === "" && e + 1 === lines.length - 1) { trailingNl = true; break }
    if (lines[e + 1] === "" && isHeaderLine(lines[e + 2] ?? "")) { i = e + 2; continue }
    return null // trailing junk after the section
  }
  // every file we dropped entries from must have had a rendered block
  for (const f of supPos.keys()) if (!seenFiles.has(f)) return null

  const out = [...prefix]
  if (!outBlocks.length) {
    if (out.length && out[out.length - 1] === "") out.pop() // strip the separator
  } else {
    outBlocks.forEach((blk, idx) => {
      if (idx > 0) out.push("")
      out.push(...blk)
    })
    if (trailingNl) out.push("")
  }
  return { text: out.join("\n"), diags: newDiags, dropped }
}

// --- thin after-hook entry -----------------------------------------------------

// Mutate the edit/write/patch result in place. Keys off input.tool +
// output.metadata.diagnostics (NOT the edited path), so it runs before the
// root's raw early-return. Fail-open: never blocks, never throws.
export async function lspAfterEdit(env: EnforcerEnv, input: any, output: any): Promise<void> {
  try {
    const tool = input?.tool
    if (typeof tool !== "string" || !LSP_TOOLS.has(tool)) return
    const md = output?.metadata
    const diags = md?.diagnostics
    if (!diags || typeof diags !== "object" || Array.isArray(diags)) return
    const allowlist = loadAllowlist(env.directory)
    if (!allowlist) return
    const res = applyLspAllowlist(
      typeof output.output === "string" ? output.output : "",
      diags, allowlist, env.directory)
    if (!res) return
    output.output = res.text
    md.diagnostics = res.diags
    env.safeLog("info", `lsp_filter: suppressed ${res.dropped} allowlisted LSP diagnostic(s)`)
  } catch (e: any) {
    env.safeLog("warn", "lsp_filter failed open: " + (e?.message || e))
  }
}

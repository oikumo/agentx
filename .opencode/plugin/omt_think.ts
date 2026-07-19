// OMT++ Think Anywhere — persistent inline TA: thought-tag layer (feature_021,
// hardened by feature_022 Tier A: anchored thought pattern, explicit extension
// map, string-context insertion guard, filter/dedup/EOL correctness; Tier B1:
// after:/symbol: anchor-based insertion — drift-resistant, anchor in index;
// Tier C: omt_think_verify placement-integrity lifecycle (verified/stale),
// digest stale count, per-file consult records).
//
// Adapts the Think-Anywhere paper's on-demand reasoning to the META HARNESS as a
// PERSISTENT, grep-friendly annotation/memory layer. opencode drops compact
// `TA:` comment tags inline in real (non-protected) files so hard-won context
// survives across sessions. Retrieval is grep-backed (O(hits) tokens); a
// per-session digest surfaces accumulated thoughts; a blocking think-gate
// (in omt_enforcer.ts) refuses to edit thought-carrying files until consulted.
//
// Contract (mirrors omt_nav.ts / omt_status.ts — feature_020 defect-free):
//   • import { tool } from "@opencode-ai/plugin"; args + tool.schema.* (DEFECT-C safe)
//   • async execute(args, context) returns a plain string (DEFECT-D safe)
//   • default export async () => ({ tool, "session.start" })
//   • NO named tool-object exports (DEFECT-A safe); only the default factory
//   • file ops via execFileSync/readFileSync/writeFileSync (no shell — H3 safe)

import { tool } from "@opencode-ai/plugin"
import { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync } from "node:fs"
import { join, relative, isAbsolute, extname, dirname } from "node:path"
import { execFileSync } from "node:child_process"

const REPO_ROOT = process.cwd()
const THOUGHTS_INDEX = join(REPO_ROOT, ".meta", ".omt", "thoughts.jsonl")
const LEDGER_PATH = join(REPO_ROOT, ".meta", ".omt", "ledger.jsonl")

// Anchored TA: thought pattern (feature_022 A1 / F3): matches only real
// comment-opener thought lines, never prose mentions (META:/DATA:/string
// literals). Covers every opener buildThoughtLine can emit (#, //, /*, <!--,
// --) so list/gate are never blind to what omt_think wrote. grep -E / JS
// RegExp compatible (\s is a GNU-grep ERE extension — confirmed on box).
// keep in sync with omt_enforcer.ts (byte-identical; structural test asserts).
const THOUGHT_PATTERN = "^\\s*(#|//|/\\*|<!--|--)\\s*TA:"

// Protected files: TA: tags are NEVER written here (AGENTS.md NEVER set + JSON).
const PROTECTED_FILES = new Set(["README.md", "uv.lock", "LICENSE", ".env"])
function isProtectedPath(rel: string): boolean {
  if (typeof rel !== "string") return true
  return rel === ".env" || rel.startsWith(".env.") ||
    PROTECTED_FILES.has(rel) || rel === "README.md" || rel.endsWith("/README.md")
}

// Escape a user-supplied string for safe interpolation into a grep -E / JS
// regex pattern (feature_022 A4 / F7).
function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

// Language-aware comment wrapper (feature_022 A2): EXPLICIT extension map —
// unknown/none → null (denied). The v1 "hash is safe for most text formats"
// default was unsafe (F2: e.g. .sql would have gotten '#' comments). .json has
// no comments → denied (dedicated message at the call site). .jsonc allows //.
// NOT exported: opencode's loader calls every named export at load time with a
// non-string arg, which would crash `(ext||"").toLowerCase` (DEFECT-A load-crash
// class). Only `export default` may leave this module — mirrors omt_nav.ts.
function commentSyntaxFor(ext: string): { open: string; close: string } | null {
  const e = (ext || "").toLowerCase()
  if (e === ".json") return null
  if ([".py", ".toml", ".cfg", ".ini", ".sh", ".yml", ".yaml", ".rb", ".r", ".pl"].includes(e))
    return { open: "#", close: "" }
  if ([".ts", ".js", ".mjs", ".cjs", ".tsx", ".jsx", ".jsonc",
    ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".swift", ".kt", ".scala"].includes(e))
    return { open: "//", close: "" }
  if ([".md", ".mdx", ".html", ".xml", ".vue", ".svelte"].includes(e))
    return { open: "<!--", close: "-->" }
  if ([".css", ".scss", ".less"].includes(e))
    return { open: "/*", close: "*/" }
  if (e === ".sql") return { open: "--", close: "" }
  return null
}

function relOf(raw: string): string {
  const abs = isAbsolute(raw) ? raw : join(REPO_ROOT, raw)
  return relative(REPO_ROOT, abs).split("\\").join("/")
}

function toAbs(rel: string): string {
  return isAbsolute(rel) ? rel : join(REPO_ROOT, rel)
}

// Append a record to the JSONL index (best-effort structured sidecar; inline
// TA: tags remain the source of truth).
function appendIndex(record: Record<string, unknown>): void {
  try {
    mkdirSync(dirname(THOUGHTS_INDEX), { recursive: true })
    appendFileSync(THOUGHTS_INDEX, JSON.stringify({ ts: new Date().toISOString(), ...record }) + "\n")
  } catch { /* best-effort */ }
}

// Rewrite the index without records matching {path, line} (reconcile on remove).
// Kind-agnostic: add AND verify records for the slot are dropped, so a removed
// thought leaves no zombie verify state and a re-added thought starts
// unverified (feature_022 C1).
function reconcileIndex(path: string, line: number): void {
  if (!existsSync(THOUGHTS_INDEX)) return
  try {
    const kept = readFileSync(THOUGHTS_INDEX, "utf8")
      .split("\n").filter(s => s.trim())
      .map(l => { try { return JSON.parse(l) } catch { return null } })
      .filter(Boolean)
      .filter((r: any) => !(r.path === path && r.line === line))
    writeFileSync(THOUGHTS_INDEX, kept.map(r => JSON.stringify(r)).join("\n") + "\n")
  } catch { /* best-effort */ }
}

// Read the JSONL index (feature_022 C1 — first read-consumer; partial F8
// progress, full strategy is E1). Skips corrupt lines, fail-open [].
function readThoughtsIndex(): any[] {
  if (!existsSync(THOUGHTS_INDEX)) return []
  try {
    const out: any[] = []
    for (const line of readFileSync(THOUGHTS_INDEX, "utf8").split("\n")) {
      const s = line.trim()
      if (!s) continue
      try { out.push(JSON.parse(s)) } catch { /* skip corrupt line */ }
    }
    return out
  } catch { return [] }
}

// Latest verify status per "path:line" (verify records are append-only; the
// latest record per slot wins). Used by the digest stale count (C1).
function latestVerifyStatus(recs: any[]): Map<string, string> {
  const m = new Map<string, string>()
  for (const r of recs) {
    if (r && r.kind === "verify" && typeof r.path === "string" && typeof r.line === "number") {
      m.set(`${r.path}:${r.line}`, r.status)
    }
  }
  return m
}

// Record a think_consult in the shared ledger so the enforcer's think-gate
// clears. C2: per-file granularity — files = rel paths the listing actually
// matched (what the agent was shown), capped at 200 (+ files_truncated flag;
// a truncated record covers only listed files — safe direction). Empty result
// → files: [] (covers nothing; no clearance granted).
function recordConsult(session: string | undefined, files: string[]): void {
  try {
    mkdirSync(dirname(LEDGER_PATH), { recursive: true })
    appendFileSync(LEDGER_PATH, JSON.stringify({
      ts: new Date().toISOString(), kind: "think_consult", session: session || "",
      files: files.slice(0, 200),
      ...(files.length > 200 ? { files_truncated: true } : {}),
    }) + "\n")
  } catch { /* best-effort */ }
}

// grep thought lines across a target (file or dir), honoring excludes. Returns
// parsed {file,line,content} hits. Uses execFileSync (array argv — no shell,
// H3 safe). -E: callers pass ERE patterns (THOUGHT_PATTERN-based, feature_022
// A1). A1b: .venv/__pycache__ excluded (noise dirs that polluted the digest).
function grepThoughts(pattern: string, target: string): { file: string; line: number; content: string }[] {
  const results: { file: string; line: number; content: string }[] = []
  const absTarget = isAbsolute(target) ? target : join(REPO_ROOT, target)
  if (!existsSync(absTarget)) return results
  try {
    const output = execFileSync("grep", [
      "-rnHE",
      "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=.omt",
      "--exclude-dir=.venv", "--exclude-dir=__pycache__",
      "--exclude=*.env*",
      "--", pattern, absTarget,
    ], { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] })
    for (const line of output.trim().split("\n")) {
      if (!line) continue
      const match = line.match(/^(.+?):(\d+):(.*)$/)
      if (match) {
        const [, file, lineNum, content] = match
        results.push({
          file: relative(REPO_ROOT, file).split("\\").join("/"),
          line: parseInt(lineNum, 10),
          content: content.trim(),
        })
      }
    }
  } catch { /* grep returns non-zero when no matches — fine */ }
  return results
}

// Build the rendered TA: line for a given extension/category/thought.
function buildThoughtLine(ext: string, category: string | undefined, thought: string): string | null {
  const wrap = commentSyntaxFor(ext)
  if (!wrap) return null
  // strip a user-prepended "TA:" so we control the marker uniformly
  let t = thought.replace(/\s+/g, " ").trim()
  t = t.replace(/^TA:\s*/i, "")
  // A4: category normalized to lowercase at insert (F7 case defect).
  const cat = category ? `${category.trim().toLowerCase()}: ` : ""
  const tail = wrap.close ? ` ${wrap.close}` : ""
  return `${wrap.open} TA: ${cat}${t}${tail}`
}

// Parse a rendered thought line into {cat, text} for dedup comparison (A4).
// Returns null for non-thought lines (anchored-pattern test first), so prose
// mentions never collide with real thoughts.
function parseThoughtLine(line: string): { cat: string; text: string } | null {
  if (!new RegExp(THOUGHT_PATTERN).test(line)) return null
  let t = line.trim()
  t = t.replace(/^(#|\/\/|\/\*|<!--|--)\s*/, "") // comment opener
  t = t.replace(/^TA:\s*/, "") // marker
  t = t.replace(/\s*(-->|\*\/)$/, "") // trailing html/block closer
  t = t.replace(/\s+/g, " ").trim()
  let cat = ""
  const m = t.match(/^([a-z0-9_-]+):\s+(.*)$/)
  if (m) { cat = m[1]; t = m[2] }
  return { cat, text: t.trim() }
}

// A3: naïve parity guard — is the insertion point (0-based index into lines)
// inside a triple-quoted string (.py) or a code fence (.md/.mdx)? Odd parity
// of delimiters seen BEFORE the insertion point ⇒ inside. Same-line open+close
// counts 2 ⇒ outside. Failure direction is refuse, which is safe. (Other exts
// ⇒ false; .ts template literals deferred beyond Tier A — documented.)
function inStringContext(lines: string[], insertAt: number, ext: string): boolean {
  const e = (ext || "").toLowerCase()
  const before = lines.slice(0, Math.max(0, insertAt))
  if (e === ".py") {
    let dq = 0, sq = 0
    for (const l of before) {
      dq += l.split('"""').length - 1
      sq += l.split("'''").length - 1
    }
    return dq % 2 === 1 || sq % 2 === 1
  }
  if (e === ".md" || e === ".mdx") {
    let fences = 0
    for (const l of before) {
      if (/^\s*(```|~~~)/.test(l)) fences++
    }
    return fences % 2 === 1
  }
  return false
}

// B1 (feature_022): resolve after:/symbol: anchors to an insertion index.
// after: literal substring (case-sensitive, no regex path). symbol: per-family
// definition regex with the name escapeRegex'd (metachars treated literally).
// Match policy (both modes): 0 → not-found refusal; >1 → ambiguity refusal
// listing up to 5 candidate lines (forces drift-resistant anchors — same
// philosophy as A2's deny-unknown-extension; first-match-on-ambiguous would
// silently retarget, reintroducing the F6 fragility this tier removes).
// Module-local (DEFECT-A: no named exports — opencode's loader calls every
// export at load time).
function resolveAnchor(
  lines: string[],
  ext: string,
  rel: string,
  after: string | undefined | null,
  symbol: string | undefined | null,
): { ok: true; insertAt: number; anchor: { kind: "after" | "symbol"; value: string } } | { ok: false; err: string } {
  const preview = (s: string) => {
    const p = s.replace(/\s+/g, " ").trim()
    return p.length > 60 ? p.slice(0, 60) + "…" : p
  }
  const matches: number[] = []
  let kind: "after" | "symbol"
  let value: string
  if (after !== undefined && after !== null) {
    kind = "after"
    value = after
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(value)) matches.push(i)
    }
  } else {
    kind = "symbol"
    value = symbol as string
    const e = (ext || "").toLowerCase()
    const name = escapeRegex(value)
    let rx: RegExp
    if (e === ".py") {
      rx = new RegExp(`^\\s*(?:async\\s+def|def|class)\\s+${name}\\b`)
    } else if ([".ts", ".js", ".mjs", ".cjs", ".tsx", ".jsx"].includes(e)) {
      rx = new RegExp(`(?:^|\\s)(?:export\\s+)?(?:default\\s+)?(?:async\\s+)?(?:function|class|const|let|var)\\s+${name}\\b`)
    } else {
      return {
        ok: false,
        err: `⛔ TA: refused — symbol addressing is not supported for '${ext || "(none)"}'; ` +
          `use after: with a literal anchor.`,
      }
    }
    for (let i = 0; i < lines.length; i++) {
      if (rx.test(lines[i])) matches.push(i)
    }
  }
  if (matches.length === 0) {
    return { ok: false, err: `⛔ TA: refused — anchor not found in ${rel}: '${preview(value)}'` }
  }
  if (matches.length > 1) {
    const candidates = matches.slice(0, 5).map((i) => i + 1).join(", ")
    return {
      ok: false,
      err: `⛔ TA: refused — anchor matches ${matches.length} lines in ${rel} ` +
        `(e.g. lines ${candidates}). Use a more specific anchor.`,
    }
  }
  // Insert AFTER the anchor line — same convention as line mode.
  return { ok: true, insertAt: matches[0] + 1, anchor: { kind, value } }
}

// --- omt_think: add a thought inline ---------------------------------------
const omt_think = tool({
  description:
    "Add a persistent TA: thought-tag inline in a non-protected file (feature_021). " +
    "The thought becomes a language-valid single-line comment so it survives across " +
    "sessions and is grep-retrievable. Bypasses phase/canary gates (annotation, not code). " +
    "Address by line (1-based), after (literal substring anchor), or symbol " +
    "(definition-name anchor, .py/.ts-family) — at most one (feature_022 B1).",
  args: {
    path: tool.schema.string().describe("repo-relative target file (must already exist)"),
    thought: tool.schema.string().describe("the thought text (single line; newlines stripped)"),
    line: tool.schema.number().optional().describe("1-based line to insert AFTER (default: append at EOF)"),
    after: tool.schema.string().optional().describe(
      "literal substring anchor; insert AFTER the unique matching line (0 or >1 matches → refused)"),
    symbol: tool.schema.string().optional().describe(
      "definition-name anchor (.py def/class/async def; .ts/.js-family function/class/const); insert AFTER the unique definition line"),
    category: tool.schema.string().optional().describe(
      "lowercase token: gotcha|why|risk|xref|todo|... (enables `TA: <category>:` filtering)"),
  },
  async execute(args, context) {
    const rawPath = args?.path ?? ""
    const thought = args?.thought ?? ""
    const lineArg = args?.line
    const afterArg = args?.after
    const symbolArg = args?.symbol
    const category = args?.category
    if (!rawPath) return "❌ 'path' is required."
    if (!thought) return "❌ 'thought' is required."
    // B1: at most one addressing mode (none → EOF append, back-compat).
    const modes = [
      lineArg !== undefined && lineArg !== null ? "line" : null,
      afterArg !== undefined && afterArg !== null ? "after" : null,
      symbolArg !== undefined && symbolArg !== null ? "symbol" : null,
    ].filter(Boolean)
    if (modes.length > 1) {
      return `⛔ TA: refused — pass at most one of line, after, symbol (got ${modes.join("+")}).`
    }
    const rel = relOf(rawPath)
    if (isProtectedPath(rel)) {
      return `⛔ TA: refused — '${rel}' is protected (.env*, README.md, uv.lock, LICENSE).`
    }
    const ext = extname(rel)
    if (ext.toLowerCase() === ".json") {
      return `⛔ TA: refused — '.json' has no comments (would break parsing). Use .jsonc instead.`
    }
    const abs = toAbs(rel)
    if (!existsSync(abs)) {
      return `⛔ TA: refused — '${rel}' does not exist. (omt_think never creates files.)`
    }
    const newLine = buildThoughtLine(ext, category, thought)
    if (!newLine) {
      // A2: unknown extension → deny (F2: no unsafe default comment syntax).
      return `⛔ TA: refused — unsupported file type '${ext || "(none)"}'. ` +
        `Add an explicit mapping in commentSyntaxFor (omt_think.ts, feature_022) ` +
        `only if a real comment syntax exists.`
    }
    const content = readFileSync(abs, "utf8")
    // A4: preserve the file's own EOL style (F9: no mixed CRLF/LF endings).
    const eol = content.includes("\r\n") ? "\r\n" : "\n"
    const lines = content.split(/\r?\n/)
    // A4 dedup: refuse an identical (category, thought) pair already present.
    const normText = thought.replace(/\s+/g, " ").trim().replace(/^TA:\s*/i, "")
    const normCat = (category || "").trim().toLowerCase()
    for (let i = 0; i < lines.length; i++) {
      const p = parseThoughtLine(lines[i])
      if (p && p.cat === normCat && p.text === normText) {
        return `⛔ TA: refused — duplicate of existing thought at ${rel}:${i + 1}.`
      }
    }
    // If the file ends with a trailing newline, split produces a trailing "".
    // Insert the thought AFTER `line` (1-based), clamped to EOF.
    let insertAt: number
    // B1: anchor mode resolves to an insertion index carrying its anchor for
    // the index record (consumed later by E1 drift-repair), then flows through
    // the same pipeline as line mode (trailing-newline adjust → A3 → splice).
    let anchor: { kind: "after" | "symbol"; value: string } | null = null
    if ((afterArg !== undefined && afterArg !== null) || (symbolArg !== undefined && symbolArg !== null)) {
      const r = resolveAnchor(lines, ext, rel, afterArg, symbolArg)
      if (!r.ok) return r.err
      insertAt = r.insertAt
      anchor = r.anchor
    } else if (lineArg === undefined || lineArg === null) {
      insertAt = lines.length // append at very end
    } else {
      insertAt = Math.min(Math.max(1, Math.floor(lineArg)), lines.length)
    }
    // If there's a trailing "" from a final newline, insert before it.
    if (lines.length > 0 && lines[lines.length - 1] === "" && insertAt >= lines.length) {
      insertAt = lines.length - 1
    }
    // A3: never splice INTO a string literal / code fence (F1 class: broke
    // Textual CSS via a triple-quoted string in main_screen.py).
    if (inStringContext(lines, insertAt, ext)) {
      return `⛔ TA: refused — insertion point ${rel}:${insertAt + 1} lies inside a ` +
        `string/code-fence (F1 class: broke Textual CSS via triple-quoted string). ` +
        `Choose a line outside the literal.`
    }
    lines.splice(insertAt, 0, newLine)
    writeFileSync(abs, lines.join(eol), "utf8")
    const newLineNo = insertAt + 1 // 1-based line number of the inserted line
    appendIndex({ path: rel, line: newLineNo, category: normCat || null, thought: normText, anchor })
    return `✅ TA: ${normText} → ${rel}:${newLineNo}`
  },
})

// --- omt_think_list: retrieve thoughts (grep-backed, authoritative inline) --
const omt_think_list = tool({
  description:
    "List TA: thought-tags (feature_021). Grep-backed retrieval over inline tags " +
    "(the source of truth). Marks the session consulted, clearing the think-gate " +
    "for exactly the files the listing matched (feature_022 C2 per-file consult). " +
    "Also usable as plain `grep -rn \"TA:\" <path>`. Caps output at 50 lines.",
  args: {
    path: tool.schema.string().optional().describe("restrict to a file/dir (default: whole repo)"),
    category: tool.schema.string().optional().describe("filter `TA: <category>:`"),
    query: tool.schema.string().optional().describe("extra substring filter"),
  },
  async execute(args, context) {
    const session = context?.sessionID
    const pathArg = args?.path
    const category = args?.category
    const query = args?.query
    // A1: anchored base pattern (F3 prose false-positives). A4: category
    // lowercased; both filters regex-escaped before interpolation (F7).
    let pattern = THOUGHT_PATTERN
    const cat = category ? category.trim().toLowerCase() : ""
    if (cat) pattern += "\\s*" + escapeRegex(cat) + ":"
    if (query) pattern += ".*" + escapeRegex(query)
    const target = pathArg || "."
    const hits = grepThoughts(pattern, target)
    // Always record consult (clears the think-gate) — even on empty results.
    // C2: the record carries the consulted file set (what the agent was shown).
    const consultedFiles = [...new Set(hits.map(h => h.file))]
    recordConsult(session, consultedFiles)
    if (hits.length === 0) {
      return `0 thoughts${category ? ` matching category '${category}'` : ""}${query ? ` / query '${query}'` : ""}.\n` +
        `Add one with omt_think{path, thought}.`
    }
    const cap = 50
    const shown = hits.slice(0, cap)
    const rendered = shown.map(h => `${h.file}:${h.line}: ${h.content}`).join("\n")
    const fileCount = consultedFiles.length
    let out = `${rendered}\n\n${hits.length} thought${hits.length === 1 ? "" : "s"} across ${fileCount} file${fileCount === 1 ? "" : "s"}.`
    if (hits.length > cap) {
      out += ` … (+${hits.length - cap} more: omt_think_list{${category ? `category:"${category}"` : "path:\"<subdir>\""}})`
    }
    return out
  },
})

// --- omt_think_remove: remove a thought -------------------------------------
const omt_think_remove = tool({
  description:
    "Remove a TA: thought-tag line from a file (feature_021) and reconcile the JSONL index.",
  args: {
    path: tool.schema.string().describe("target file"),
    line: tool.schema.number().describe("1-based line of the TA: comment to remove"),
  },
  async execute(args, context) {
    const rawPath = args?.path ?? ""
    const lineArg = args?.line
    if (!rawPath) return "❌ 'path' is required."
    if (lineArg === undefined || lineArg === null) return "❌ 'line' is required."
    const rel = relOf(rawPath)
    if (isProtectedPath(rel)) {
      return `⛔ TA: refused — '${rel}' is protected.`
    }
    const abs = toAbs(rel)
    if (!existsSync(abs)) {
      return `⛔ TA: refused — '${rel}' does not exist.`
    }
    const content = readFileSync(abs, "utf8")
    const lines = content.split("\n")
    const idx = Math.floor(lineArg) - 1
    if (idx < 0 || idx >= lines.length) {
      return `⛔ TA: refused — line ${lineArg} out of range (file has ${lines.length} lines).`
    }
    // A1: only real anchored thought lines are removable (prose mentions refused).
    if (!new RegExp(THOUGHT_PATTERN).test(lines[idx])) {
      return `⛔ TA: refused — line ${lineArg} is not a TA: comment:\n  ${lines[idx]}`
    }
    lines.splice(idx, 1)
    writeFileSync(abs, lines.join("\n"), "utf8")
    reconcileIndex(rel, Math.floor(lineArg))
    return `🗑 removed TA: at ${rel}:${lineArg}`
  },
})

// --- omt_think_verify: structural placement-integrity check (feature_022 C1) -
// Re-checks that a thought exists where expected AND that its B1 anchor still
// resolves to it. STRUCTURAL, not semantic: never judges whether the thought's
// claim is still true (the agent's job at consult/read time). This is the
// RLVR-analogue feedback signal: drifted/detached thoughts are flagged stale
// instead of silently persisting as trustworthy.
const omt_think_verify = tool({
  description:
    "Re-check a TA: thought's placement integrity (feature_022 C1): existence at " +
    "the given line plus, when the index add-record carries an anchor, re-resolution " +
    "of that anchor (drift/ambiguity/removal → stale). Structural only — never judges " +
    "semantic truth. Appends a verified/stale record to the index (latest per " +
    "path:line wins); the digest + think-gate surface stale thoughts.",
  args: {
    path: tool.schema.string().describe("repo-relative file carrying the TA: comment"),
    line: tool.schema.number().describe("1-based line of the TA: comment to verify"),
  },
  async execute(args, context) {
    const rawPath = args?.path ?? ""
    const lineArg = args?.line
    if (!rawPath) return "❌ 'path' is required."
    if (lineArg === undefined || lineArg === null) return "❌ 'line' is required."
    const rel = relOf(rawPath)
    if (isProtectedPath(rel)) {
      return `⛔ TA: refused — '${rel}' is protected.`
    }
    const abs = toAbs(rel)
    if (!existsSync(abs)) {
      return `⛔ TA: refused — '${rel}' does not exist.`
    }
    const content = readFileSync(abs, "utf8")
    const lines = content.split(/\r?\n/)
    const lineNo = Math.floor(lineArg)
    const idx = lineNo - 1
    if (idx < 0 || idx >= lines.length) {
      return `⛔ TA: refused — line ${lineArg} out of range (file has ${lines.length} lines).`
    }
    if (!new RegExp(THOUGHT_PATTERN).test(lines[idx])) {
      return `⛔ TA: refused — line ${lineArg} is not a TA: comment:\n  ${lines[idx]}`
    }
    const parsed = parseThoughtLine(lines[idx])
    const text = parsed?.text || ""
    const cat = parsed?.cat || null
    // Index lookup: latest ADD-record (no kind field) at (path,line); drift
    // fallback: latest ADD-record with (path, thought-text). Latest wins.
    const adds = readThoughtsIndex().filter(r => r && !r.kind && r.path === rel)
    let rec = [...adds].reverse().find(r => r.line === lineNo)
    if (!rec) rec = [...adds].reverse().find(r => r.thought === text)
    let status: "verified" | "stale"
    let basis: "anchor" | "exists"
    let reason = ""
    if (rec?.anchor) {
      basis = "anchor"
      const r = resolveAnchor(lines, extname(rel), rel,
        rec.anchor.kind === "after" ? rec.anchor.value : null,
        rec.anchor.kind === "symbol" ? rec.anchor.value : null)
      if (r.ok && r.insertAt + 1 === lineNo) {
        status = "verified"
      } else {
        status = "stale"
        reason = r.ok
          ? `anchor moved (thought at ${lineNo}, anchor resolves to ${r.insertAt + 1})`
          : r.err.replace(/^⛔ TA: refused — /, "").replace(/\.$/, "")
      }
    } else {
      // No record or anchor:null → weaker verification: existence only.
      basis = "exists"
      status = "verified"
    }
    appendIndex({ kind: "verify", path: rel, line: lineNo, category: cat, thought: text, status, basis })
    if (status === "verified") {
      return basis === "anchor"
        ? `✅ TA: verified — ${rel}:${lineNo} (basis: anchor)`
        : `✅ TA: verified — ${rel}:${lineNo} (basis: exists — placement only, no anchor recorded)`
    }
    return `⚠️ TA: STALE — ${rel}:${lineNo} — ${reason}. ` +
      `Re-place with omt_think or remove with omt_think_remove.`
  },
})

// --- session.start: mechanical per-session digest ---------------------------
function thinkDigest(): string {
  const hits = grepThoughts(THOUGHT_PATTERN, ".")
  const files = new Set(hits.map(h => h.file)).size
  if (hits.length === 0) {
    return "💡 THINK-ANYWHERE (feature_021): 0 thoughts yet. " +
      "Add one with omt_think{path, thought} when you learn a gotcha."
  }
  // C1: surface current thoughts whose latest verify record is stale (drift
  // signal). Index unreadable/corrupt → 0 stale (fail-open — the digest never
  // breaks session.start).
  const verify = latestVerifyStatus(readThoughtsIndex())
  const stale = hits.filter(h => verify.get(`${h.file}:${h.line}`) === "stale")
  const cap = 30
  const shown = hits.slice(0, cap)
  const rendered = shown.map(h => `${h.file}:${h.line}: ${h.content}`).join("\n")
  let out = `💡 THINK-ANYWHERE (feature_021): ${hits.length} thought${hits.length === 1 ? "" : "s"} indexed across ${files} file${files === 1 ? "" : "s"}.` +
    (stale.length ? ` ⚠️ ${stale.length} stale — re-check with omt_think_verify{path, line}.` : "") +
    `\n${rendered}`
  if (hits.length > cap) {
    out += `\n… (+${hits.length - cap} more: omt_think_list)`
  }
  out += `\nDrop new thoughts with omt_think{path, thought}; review before editing thought-carrying files (think-gate).`
  return out
}

// Standalone opencode plugin (mirrors omt_nav.ts / omt_status.ts).
// NO named tool-object exports — opencode's loader requires every export to be a
// function (DEFECT-A safe). Only the default factory is exported.
export default async () => ({
  tool: { omt_think, omt_think_list, omt_think_remove, omt_think_verify },
  "session.start": async () => thinkDigest(),
})
// TA: xref: feature_022.meta_harness_think_anywhere_v2 FEATURE.md catalogs 13 flaws of this v1 (string-unaware insertion F1, unsafe # default F2, gate substring false-positives F3) + tiered fixes A-E — read before modifying

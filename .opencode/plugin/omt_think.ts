// OMT++ Think Anywhere — persistent inline TA: thought-tag layer (feature_021).
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

// Protected files: TA: tags are NEVER written here (AGENTS.md NEVER set + JSON).
const PROTECTED_FILES = new Set(["README.md", "uv.lock", "LICENSE", ".env"])
function isProtectedPath(rel: string): boolean {
  if (typeof rel !== "string") return true
  return rel === ".env" || rel.startsWith(".env.") ||
    PROTECTED_FILES.has(rel) || rel === "README.md" || rel.endsWith("/README.md")
}

// Language-aware comment wrapper. Returns {open, close} or null (denied).
// .json has no comments → denied. .jsonc allows // comments.
// NOT exported: opencode's loader calls every named export at load time with a
// non-string arg, which would crash `(ext||"").toLowerCase` (DEFECT-A load-crash
// class). Only `export default` may leave this module — mirrors omt_nav.ts.
function commentSyntaxFor(ext: string): { open: string; close: string } | null {
  const e = (ext || "").toLowerCase()
  if (e === ".json") return null
  if ([".py", ".toml", ".cfg", ".ini", ".sh", ".yml", ".yaml", ".rb", ".r", ".pl"].includes(e))
    return { open: "#", close: "" }
  if ([".ts", ".js", ".mjs", ".cjs", ".tsx", ".jsx", ".jsonc"].includes(e))
    return { open: "//", close: "" }
  if ([".md", ".mdx"].includes(e))
    return { open: "<!--", close: "-->" }
  if (e === ".css")
    return { open: "/*", close: "*/" }
  // default: hash is safe for most text formats
  return { open: "#", close: "" }
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

// Record a think_consult in the shared ledger so the enforcer's think-gate clears.
function recordConsult(session: string | undefined): void {
  try {
    mkdirSync(dirname(LEDGER_PATH), { recursive: true })
    appendFileSync(LEDGER_PATH, JSON.stringify({
      ts: new Date().toISOString(), kind: "think_consult", session: session || "",
    }) + "\n")
  } catch { /* best-effort */ }
}

// grep `TA:` across a target (file or dir), honoring excludes. Returns parsed
// {file,line,content} hits. Uses execFileSync (array argv — no shell, H3 safe).
function grepThoughts(pattern: string, target: string): { file: string; line: number; content: string }[] {
  const results: { file: string; line: number; content: string }[] = []
  const absTarget = isAbsolute(target) ? target : join(REPO_ROOT, target)
  if (!existsSync(absTarget)) return results
  try {
    const output = execFileSync("grep", [
      "-rnH",
      "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=.omt",
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

// grep `TA:` in a SINGLE file (cheap; used by the enforcer think-gate).
// NOT exported (same DEFECT-A load-crash reason as commentSyntaxFor above).
function fileThoughts(rel: string): { line: number; content: string }[] {
  const abs = toAbs(rel)
  if (!existsSync(abs)) return []
  try {
    const output = execFileSync("grep", ["-nH", "--", "TA:", abs], {
      encoding: "utf8", stdio: ["pipe", "pipe", "ignore"],
    })
    const out: { line: number; content: string }[] = []
    for (const line of output.trim().split("\n")) {
      if (!line) continue
      const match = line.match(/^(?:.+?):(\d+):(.*)$/)
      if (match) out.push({ line: parseInt(match[1], 10), content: match[2].trim() })
    }
    return out
  } catch { return [] }
}

// Build the rendered TA: line for a given extension/category/thought.
function buildThoughtLine(ext: string, category: string | undefined, thought: string): string | null {
  const wrap = commentSyntaxFor(ext)
  if (!wrap) return null
  // strip a user-prepended "TA:" so we control the marker uniformly
  let t = thought.replace(/\s+/g, " ").trim()
  t = t.replace(/^TA:\s*/i, "")
  const cat = category ? `${category}: ` : ""
  const tail = wrap.close ? ` ${wrap.close}` : ""
  return `${wrap.open} TA: ${cat}${t}${tail}`
}

// --- omt_think: add a thought inline ---------------------------------------
const omt_think = tool({
  description:
    "Add a persistent TA: thought-tag inline in a non-protected file (feature_021). " +
    "The thought becomes a language-valid single-line comment so it survives across " +
    "sessions and is grep-retrievable. Bypasses phase/canary gates (annotation, not code).",
  args: {
    path: tool.schema.string().describe("repo-relative target file (must already exist)"),
    thought: tool.schema.string().describe("the thought text (single line; newlines stripped)"),
    line: tool.schema.number().optional().describe("1-based line to insert AFTER (default: append at EOF)"),
    category: tool.schema.string().optional().describe(
      "lowercase token: gotcha|why|risk|xref|todo|... (enables `TA: <category>:` filtering)"),
  },
  async execute(args, context) {
    const rawPath = args?.path ?? ""
    const thought = args?.thought ?? ""
    const lineArg = args?.line
    const category = args?.category
    if (!rawPath) return "❌ 'path' is required."
    if (!thought) return "❌ 'thought' is required."
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
      return `⛔ TA: refused — unsupported file type '${ext || "(none)"}'.`
    }
    const content = readFileSync(abs, "utf8")
    const lines = content.split("\n")
    // If the file ends with a trailing newline, split produces a trailing "".
    // Insert the thought AFTER `line` (1-based), clamped to EOF.
    let insertAt: number
    if (lineArg === undefined || lineArg === null) {
      insertAt = lines.length // append at very end
    } else {
      insertAt = Math.min(Math.max(1, Math.floor(lineArg)), lines.length)
    }
    // If there's a trailing "" from a final newline, insert before it.
    if (lines.length > 0 && lines[lines.length - 1] === "" && insertAt >= lines.length) {
      insertAt = lines.length - 1
    }
    lines.splice(insertAt, 0, newLine)
    writeFileSync(abs, lines.join("\n"), "utf8")
    const newLineNo = insertAt + 1 // 1-based line number of the inserted line
    appendIndex({ path: rel, line: newLineNo, category: category || null, thought: thought.replace(/\s+/g, " ").trim() })
    return `✅ TA: ${thought.replace(/\s+/g, " ").trim().replace(/^TA:\s*/i, "")} → ${rel}:${newLineNo}`
  },
})

// --- omt_think_list: retrieve thoughts (grep-backed, authoritative inline) --
const omt_think_list = tool({
  description:
    "List TA: thought-tags (feature_021). Grep-backed retrieval over inline tags " +
    "(the source of truth). Marks the session consulted, clearing the think-gate. " +
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
    let pattern = "TA:"
    if (category) pattern = `TA: ${category}:`
    if (query) pattern = pattern + (category ? `.*${query}` : `.*${query}`)
    const target = pathArg || "."
    const hits = grepThoughts(pattern, target)
    // Always record consult (clears the think-gate) — even on empty results.
    recordConsult(session)
    if (hits.length === 0) {
      return `0 thoughts${category ? ` matching category '${category}'` : ""}${query ? ` / query '${query}'` : ""}.\n` +
        `Add one with omt_think{path, thought}.`
    }
    const cap = 50
    const shown = hits.slice(0, cap)
    const rendered = shown.map(h => `${h.file}:${h.line}: ${h.content}`).join("\n")
    const files = new Set(hits.map(h => h.file)).size
    let out = `${rendered}\n\n${hits.length} thought${hits.length === 1 ? "" : "s"} across ${files} file${files === 1 ? "" : "s"}.`
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
    if (!lines[idx].includes("TA:")) {
      return `⛔ TA: refused — line ${lineArg} is not a TA: comment:\n  ${lines[idx]}`
    }
    lines.splice(idx, 1)
    writeFileSync(abs, lines.join("\n"), "utf8")
    reconcileIndex(rel, Math.floor(lineArg))
    return `🗑 removed TA: at ${rel}:${lineArg}`
  },
})

// --- session.start: mechanical per-session digest ---------------------------
function thinkDigest(): string {
  const hits = grepThoughts("TA:", ".")
  const files = new Set(hits.map(h => h.file)).size
  if (hits.length === 0) {
    return "💡 THINK-ANYWHERE (feature_021): 0 thoughts yet. " +
      "Add one with omt_think{path, thought} when you learn a gotcha."
  }
  const cap = 30
  const shown = hits.slice(0, cap)
  const rendered = shown.map(h => `${h.file}:${h.line}: ${h.content}`).join("\n")
  let out = `💡 THINK-ANYWHERE (feature_021): ${hits.length} thought${hits.length === 1 ? "" : "s"} indexed across ${files} file${files === 1 ? "" : "s"}.\n` +
    rendered
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
  tool: { omt_think, omt_think_list, omt_think_remove },
  "session.start": async () => thinkDigest(),
})

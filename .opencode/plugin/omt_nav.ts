// OMT++ Navigation Tool — structured navigation for META HARNESS documentation
// Provides grep-based navigation using SECTION:/XREF_/CMD_/ERR_/WRN_/QUICK_ tags
// Returns structured results for agent consumption

import { tool } from "@opencode-ai/plugin"
import { existsSync, readFileSync, readdirSync } from "node:fs"
import { join, relative } from "node:path"
import { execFileSync } from "node:child_process"

const REPO_ROOT = process.cwd()
const META_ROOT = join(REPO_ROOT, ".meta")

// Auto-discover .meta/doc/omt++/*.md so newly added docs are covered without
// editing this list. Sorted for deterministic output.
const OMT_PP_DIR = join(META_ROOT, "doc", "omt++")
const omtPpFiles: string[] = existsSync(OMT_PP_DIR)
  ? readdirSync(OMT_PP_DIR).filter(f => f.endsWith(".md")).sort().map(f => `.meta/doc/omt++/${f}`)
  : []

// Core documentation files in the META HARNESS ecosystem
const META_FILES = [
  ".meta/META_HARNESS.md",
  ".meta/META.md",
  ".meta/software_development_process/META.md",
  ".meta/software_development_process/omt_agent_guide.md",
  ...omtPpFiles,
  "AGENTS.md",
  "WORK.md",
]

// Tag patterns for structured navigation.
// NOTE: these validate the `tag_type` input and document the canonical tag
// shapes. The actual grep patterns are built per-tool in runGrep(); grep uses
// BRE by default, so `+` is literal there — see omt_list_sections for the
// BRE-safe one-or-more-`#` pattern (`^##* SECTION:`).
const TAG_PATTERNS = {
  SECTION: /^#+ SECTION:/m,
  RULE_: /^RULE_[A-Z0-9]+:/m,
  ERR_: /^ERR_[A-Z0-9]+:/m,
  WRN_: /^WRN_[A-Z0-9]+:/m,
  CMD_: /^CMD_[A-Z0-9]+:/m,
  QUICK_: /^QUICK_[A-Z0-9_]+:/m,
  XREF_: /^XREF_[A-Z0-9_]+:/m,
  TT_: /^TT_[A-Z0-9_]+:/m,
  PHASE_: /^PHASE_[A-Z0-9_]+:/m,
  FEAT_: /^FEAT_[A-Z0-9_]+:/m,
}

interface NavResult {
  file: string
  line: number
  tag: string
  content: string
  context?: string
}

interface NavResponse {
  query: string
  results: NavResult[]
  files_searched: string[]
  suggestions: string[]
}

// Execute grep command and parse results.
// Uses execFileSync with array argv (no shell) so the pattern is passed as a
// literal argument — no shell injection and no quoting breakage. grep still
// interprets the pattern as a BRE regex, which is intentional for tag nav.
function runGrep(pattern: string, files: string[]): NavResult[] {
  const results: NavResult[] = []
  const existingFiles = files.filter(f => existsSync(join(REPO_ROOT, f)))

  if (existingFiles.length === 0) return results

  try {
    const absFiles = existingFiles.map(f => join(REPO_ROOT, f))
    const output = execFileSync("grep", ["-n", "--", pattern, ...absFiles], {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    })

    for (const line of output.trim().split("\n")) {
      if (!line) continue
      // Parse grep output: file:line:content
      // Non-greedy file group binds to the first :<digits>: (the real line
      // number), so colons/digits inside content don't misparse.
      const match = line.match(/^(.+?):(\d+):(.*)$/)
      if (match) {
        const [, file, lineNum, content] = match
        const relPath = relative(REPO_ROOT, file)
        results.push({
          file: relPath,
          line: parseInt(lineNum, 10),
          tag: pattern,
          content: content.trim(),
        })
      }
    }
  } catch {
    // grep returns non-zero when no matches, which is fine
  }

  return results
}

// Get context around a match (3 lines before and after)
function getContext(filePath: string, lineNum: number, contextLines: number = 3): string {
  const fullPath = join(REPO_ROOT, filePath)
  if (!existsSync(fullPath)) return ""
  
  try {
    const content = readFileSync(fullPath, "utf8")
    const lines = content.split("\n")
    const start = Math.max(0, lineNum - 1 - contextLines)
    const end = Math.min(lines.length, lineNum - 1 + contextLines + 1)
    return lines.slice(start, end).join("\n")
  } catch {
    return ""
  }
}

// --- omt_nav: Main navigation tool ---
const omt_nav = tool({
  name: "omt_nav",
  description: "Navigate META HARNESS documentation using structured tags (SECTION:/XREF_/CMD_/ERR_/etc.)",
  input: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query: tag prefix (e.g., 'SECTION:', 'CMD_', 'ERR_') or keyword",
      },
      file: {
        type: "string",
        description: "Optional: specific file to search (e.g., '.meta/META_HARNESS.md')",
      },
      tag_type: {
        type: "string",
        description: "Optional: restrict to specific tag type (SECTION, RULE, ERR, WRN, CMD, QUICK, XREF, TT, PHASE, FEAT)",
        enum: ["SECTION", "RULE", "ERR", "WRN", "CMD", "QUICK", "XREF", "TT", "PHASE", "FEAT", "all"],
      },
      include_context: {
        type: "boolean",
        description: "Include surrounding context for each match (default: false)",
        default: false,
      },
    },
    required: ["query"],
  },
  execute: async (input: { 
    query: string
    file?: string
    tag_type?: string
    include_context?: boolean
  }): Promise<NavResponse> => {
    const { query, file, tag_type = "all", include_context = false } = input
    
    // Determine which files to search
    const filesToSearch = file ? [file] : META_FILES.filter(f => existsSync(join(REPO_ROOT, f)))
    
    // Build grep pattern based on tag type
    let pattern = query
    if (tag_type !== "all" && TAG_PATTERNS[tag_type as keyof typeof TAG_PATTERNS]) {
      // If query looks like a tag, use it as-is; otherwise prepend tag prefix
      if (!query.startsWith(tag_type)) {
        pattern = `${tag_type}_.*${query}`
      }
    }
    
    // Run grep search
    const rawResults = runGrep(pattern, filesToSearch)
    
    // Enrich results with context if requested
    const results: NavResult[] = rawResults.map(r => ({
      ...r,
      ...(include_context ? { context: getContext(r.file, r.line) } : {}),
    }))
    
    // Generate suggestions based on query
    const suggestions: string[] = []
    if (query.startsWith("SECTION:")) {
      suggestions.push("Try 'CMD_' to find tool commands")
      suggestions.push("Try 'QUICK_' to find workflow patterns")
      suggestions.push("Try 'XREF_' to find cross-references")
    } else if (query.startsWith("CMD_")) {
      suggestions.push("Use omt_phase, omt_status, omt_skip, omt_complete tools")
      suggestions.push("Check META_HARNESS.md SECTION:CMDS for full command catalog")
    } else if (query.startsWith("ERR_") || query.startsWith("WRN_")) {
      suggestions.push("Check mvc_check.py for implementation of these error codes")
      suggestions.push("See META_HARNESS.md SECTION:ERRORS for error/warning catalog")
    }
    
    // If no results, suggest common patterns
    if (results.length === 0) {
      suggestions.push("Common patterns: 'SECTION:RULES', 'CMD_OMT_PHASE', 'ERR_', 'QUICK_START'")
      suggestions.push("Use tag_type parameter to restrict search: SECTION, CMD, ERR, WRN, QUICK, XREF")
    }
    
    return {
      query,
      results,
      files_searched: filesToSearch,
      suggestions,
    }
  },
})

// --- omt_list_sections: List all SECTION: headers across META HARNESS ---
const omt_list_sections = tool({
  name: "omt_list_sections",
  description: "List all SECTION: headers across META HARNESS documentation with file locations",
  input: {
    type: "object",
    properties: {
      file: {
        type: "string",
        description: "Optional: specific file to list sections from",
      },
    },
    required: [],
  },
  execute: async (input: { file?: string }): Promise<{ sections: { file: string; line: number; title: string }[] }> => {
    const { file } = input
    const filesToSearch = file ? [file] : META_FILES
    
    // BRE-safe "one or more leading '#'": `##*` = first '#' literal, then
    // zero-or-more '#' (i.e. one-or-more '#'). Matches the `# SECTION:` style
    // used across META HARNESS docs. (`^##+` would be wrong in BRE: `+` is
    // literal there, and even in ERE `##+` requires two-or-more '#'.)
    const rawResults = runGrep("^##* SECTION:", filesToSearch)
    
    const sections = rawResults.map(r => {
      // Extract section title from content (remove ## and SECTION: prefix)
      const title = r.content.replace(/^#+ SECTION:\s*/, "").trim()
      return {
        file: r.file,
        line: r.line,
        title,
      }
    })
    
    return { sections }
  },
})

// --- omt_cross_ref: Resolve cross-references ---
const omt_cross_ref = tool({
  name: "omt_cross_ref",
  description: "Resolve XREF_ cross-references to find related documentation sections",
  input: {
    type: "object",
    properties: {
      xref: {
        type: "string",
        description: "Cross-reference ID (e.g., 'XREF_GUIDE', 'XREF_RULES')",
      },
    },
    required: ["xref"],
  },
  execute: async (input: { xref: string }): Promise<{ xref: string; references: { file: string; line: number; content: string }[] }> => {
    const { xref } = input
    const pattern = xref.startsWith("XREF_") ? xref : `XREF_.*${xref}`
    
    const results = runGrep(pattern, META_FILES)
    
    return {
      xref,
      references: results.map(r => ({
        file: r.file,
        line: r.line,
        content: r.content,
      })),
    }
  },
})

// --- omt_quick_ref: Get quick workflow patterns ---
const omt_quick_ref = tool({
  name: "omt_quick_ref",
  description: "Get QUICK_ workflow patterns for common agent tasks",
  input: {
    type: "object",
    properties: {
      workflow: {
        type: "string",
        description: "Workflow name or keyword (e.g., 'START_MAJOR', 'TDD', 'DEBUG')",
      },
    },
    required: [],
  },
  execute: async (input: { workflow?: string }): Promise<{ workflows: { file: string; line: number; name: string; pattern: string }[] }> => {
    const { workflow = "" } = input
    const pattern = workflow ? `QUICK_.*${workflow}` : "^QUICK_"
    
    const results = runGrep(pattern, META_FILES)
    
    const workflows = results.map(r => {
      // Parse QUICK_NAME: pattern format
      const match = r.content.match(/^(QUICK_[A-Z0-9_]+):\s*(.+)$/)
      return {
        file: r.file,
        line: r.line,
        name: match ? match[1] : "QUICK_UNKNOWN",
        pattern: match ? match[2] : r.content,
      }
    })
    
    return { workflows }
  },
})

// Standalone opencode plugin. This file lives under .opencode/plugin/, so it
// must export a default plugin FUNCTION. opencode's plugin loader (sk/nk)
// iterates Object.values(module) and requires EACH export to be a function (or
// an object with a .server function). The tool objects below are NOT functions,
// so they must NOT be named-exported from this file — only the default export
// is allowed. Mirrors omt_status.ts lines 364-366.
//
// (Prior defect A: this file ended with a named tool-object export only — no
// default factory — so opencode rejected it with "Plugin export is not a
// function" and the nav tools were never registered, making the feature_020
// nav-gate a catch-22. The test fixture _nav_runner.mjs now retrieves the tools
// via the default export's `tool` property instead of named imports.)
export default async () => ({
  tool: { omt_nav, omt_list_sections, omt_cross_ref, omt_quick_ref },
})
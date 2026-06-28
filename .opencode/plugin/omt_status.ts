// OMT++ Status Tool — returns complete process context for the agent
// Reads ledger + workspace state, computes actionable summary
// Uses only Node.js standard library (no external deps)

import { tool } from "@opencode-ai/plugin"
import { existsSync, readFileSync, readdirSync, mkdirSync } from "node:fs"
import { join, relative, dirname } from "node:path"
import { execSync } from "node:child_process"

const REPO_ROOT = process.cwd()
const LEDGER_PATH = join(REPO_ROOT, ".meta", ".omt", "ledger.jsonl")
const WORK_MD_PATH = join(REPO_ROOT, "WORK.md")
const DESIGN_ROOT = join(REPO_ROOT, ".meta", "software_development_process", "4.design", "features")

const VALID_PHASES = ["Analysis", "Design", "Programming", "Testing"]
const VALID_TASK_TYPES = ["bug_fix", "minor_feature", "major_feature", "new_screen", "refactor", "test", "docs"]
const ARTIFACT_REQUIRED = new Set(["major_feature", "new_screen"])

const VALID_TRANSITIONS: Record<string, string[]> = {
  Analysis: ["Design", "Testing"],
  Design: ["Programming", "Analysis"],
  Programming: ["Testing", "Design", "Analysis"],
  Testing: ["Analysis", "Design", "Programming", "Done"],
}

interface LedgerRecord {
  ts: string
  kind: "phase" | "skip"
  session?: string
  task_type?: string
  phase?: string
  scope?: string
  feature?: string
  design_doc?: string
  reason?: string
  tests_approved?: boolean
}

function readLedger(): LedgerRecord[] {
  if (!existsSync(LEDGER_PATH)) return []
  const lines = readFileSync(LEDGER_PATH, "utf8").trim().split("\n")
  return lines.map(l => {
    try { return JSON.parse(l) } catch { return null }
  }).filter(Boolean) as LedgerRecord[]
}

function getActiveUnlock(sessionId?: string): LedgerRecord | null {
  const recs = readLedger().filter(r => r.kind === "phase" || r.kind === "skip")
  if (!recs.length) return null

  if (sessionId) {
    const mine = recs.filter(r => r.session === sessionId)
    if (mine.length) return mine[mine.length - 1]
  }

  const now = Date.now()
  const recent = recs.filter(r => {
    const t = Date.parse(r.ts || "")
    return !Number.isNaN(t) && now - t < 8 * 60 * 60 * 1000
  })
  return recent.length ? recent[recent.length - 1] : null
}

function resolveDesignArtifact(feature: string, explicitDoc?: string): string | null {
  if (explicitDoc && existsSync(join(REPO_ROOT, explicitDoc))) return explicitDoc
  if (!feature) return null

  const m = feature.match(/feature_(\d+)/)
  if (!m) return null
  const num = m[1]
  const base = join(DESIGN_ROOT)
  if (!existsSync(base)) return null

  for (const d of readdirSync(base)) {
    if (d === `feature_${num}` || d.startsWith(`feature_${num}.`) || d.startsWith(`feature_${num}_`)) {
      const files = readdirSync(join(base, d))
      const hit = files.find(f => /design.*\.md$/i.test(f)) || files.find(f => f.toLowerCase().endsWith(".md"))
      if (hit) return join(".meta", "software_development_process", "4.design", "features", d, hit)
    }
  }
  return null
}

function getArtifactStatus(feature: string, taskType: string): {
  required: string[]
  missing: string[]
  present: string[]
} {
  const required: string[] = []
  const missing: string[] = []
  const present: string[] = []

  if (!feature) return { required, missing, present }

  // Normalize feature slug: extract number part (feature_004.modern_ui -> feature_004)
  const featureNum = feature.match(/feature_(\d+)/)?.[0] || feature
  const PROCESS_ROOT = ".meta/software_development_process"

  const checks: [string, string, string][] = [
    ["Requirements", "FEATURE.md", `${PROCESS_ROOT}/2.requirements/features/${feature}/FEATURE.md`],
    ["Analysis", "analysis_001_*.md", `${PROCESS_ROOT}/3.analysis/features/${featureNum}/analysis_001_*.md`],
    ["Design", "design_001_*.md", `${PROCESS_ROOT}/4.design/features/${featureNum}/design_001_*.md`],
    ["Implementation", "*.md", `${PROCESS_ROOT}/5.implementation/features/${featureNum}/*.md`],
    ["Testing", "test_report.md", `${PROCESS_ROOT}/6.testing/features/${featureNum}/test_report.md`],
  ]

  for (const [phase, pattern, relPath] of checks) {
    let exists = false
    try {
      // Get directory: everything before the last "/"
      const lastSlash = relPath.lastIndexOf("/")
      const dir = lastSlash >= 0 ? join(REPO_ROOT, relPath.substring(0, lastSlash)) : REPO_ROOT
      if (existsSync(dir)) {
        const files = readdirSync(dir)
        exists = files.some(f => new RegExp(pattern.replace("*", ".*")).test(f))
      }
    } catch { /* ignore */ }

    if (exists) {
      present.push(`${phase}: ${pattern}`)
    } else if (phase === "Requirements" || ARTIFACT_REQUIRED.has(taskType) || phase === "Design") {
      required.push(`${phase}: ${pattern}`)
      missing.push(`${phase}: ${pattern}`)
    }
  }
  return { required, missing, present }
}

function runLintBaseline(): { errors: number; warnings: number; timestamp: string } {
  try {
    const out = execSync("uv run scripts/omt/mvc_check.py --json", {
      cwd: REPO_ROOT,
      encoding: "utf8",
      timeout: 30000,
      stdio: ["ignore", "pipe", "ignore"]
    })
    const data = JSON.parse(out || "{}")
    return { errors: data.errors || 0, warnings: data.warnings || 0, timestamp: new Date().toISOString() }
  } catch {
    return { errors: -1, warnings: -1, timestamp: new Date().toISOString() }
  }
}

function getWorkMdNextTask(): string | null {
  if (!existsSync(WORK_MD_PATH)) return null
  const content = readFileSync(WORK_MD_PATH, "utf8")
  const lines = content.split("\n")
  for (const line of lines) {
    if (line.trim().startsWith("- [ ]") || line.trim().startsWith("- [~]")) {
      return line.trim().replace(/^-\s*\[[ ~]\]\s*/, "")
    }
  }
  return null
}

function computeFeatureHealth(feature: string): {
  requirements: number
  analysis: number
  design: number
  implementation: number
  testing: number
  overall: number
} {
  const { present, required } = getArtifactStatus(feature, "major_feature")
  const phases = ["Requirements", "Analysis", "Design", "Implementation", "Testing"]
  const scores = phases.map(p => present.some(x => x.startsWith(p)) ? 1 : required.some(x => x.startsWith(p)) ? 0 : 0.5)
  const overall = scores.reduce((a, b) => a + b, 0) / scores.length
  return {
    requirements: scores[0],
    analysis: scores[1],
    design: scores[2],
    implementation: scores[3],
    testing: scores[4],
    overall: Math.round(overall * 100) / 100
  }
}

function formatDuration(ms: number): string {
  if (ms < 60000) return `${Math.round(ms / 1000)}s`
  if (ms < 3600000) return `${Math.round(ms / 60000)}m`
  return `${Math.round(ms / 3600000)}h`
}

export const omt_status = tool({
  description:
    "Returns complete OMT++ process context: current phase, unlock state, artifact status, lint baseline, " +
    "valid next phases, and WORK.md next task. Call at start of each turn to restore context.",
  args: {},
  async execute(_args, context) {
    const sessionId = context?.sessionID
    const unlock = getActiveUnlock(sessionId)
    const ledger = readLedger()
    const recent = ledger.filter(r => r.kind === "phase" || r.kind === "skip").slice(-5)

    let currentPhase = "None"
    let activeUnlock = null
    let expiresIn = "N/A"

    if (unlock) {
      currentPhase = unlock.phase || "Unknown"
      const started = Date.parse(unlock.ts || "")
      const elapsed = Date.now() - started
      const remaining = Math.max(0, 8 * 60 * 60 * 1000 - elapsed)
      expiresIn = remaining > 0 ? formatDuration(remaining) : "expired"

      activeUnlock = {
        task_type: unlock.task_type || "unknown",
        phase: unlock.phase || "",
        scope: unlock.scope || "",
        feature: unlock.feature || "",
        design_doc: unlock.design_doc || "",
        session: unlock.session || "",
        started_at: unlock.ts || "",
        expires_in: expiresIn
      }
    }

    const feature = unlock?.feature || ""
    const taskType = unlock?.task_type || ""
    const { required, missing, present } = getArtifactStatus(feature, taskType)

    const lint = runLintBaseline()

    const nextPhases = currentPhase !== "None" && currentPhase !== "Unknown"
      ? VALID_TRANSITIONS[currentPhase] || []
      : ["Analysis", "Design", "Programming", "Testing"]

    const featureHealth: Record<string, any> = {}
    if (feature) {
      featureHealth[feature] = computeFeatureHealth(feature)
    }

    const nextTask = getWorkMdNextTask()

    const result = {
      current_phase: currentPhase,
      active_unlock: activeUnlock,
      artifacts_required: required,
      artifacts_missing: missing,
      artifacts_present: present,
      lint_baseline: lint,
      next_valid_phases: nextPhases,
      work_md_next_task: nextTask,
      feature_health: featureHealth,
      recent_ledger: recent
    }

    const lines = [
      "📊 OMT++ STATUS",
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      `Current Phase: ${currentPhase}`,
      activeUnlock ? `Active Unlock: ${activeUnlock.task_type} (${activeUnlock.phase}) — expires in ${activeUnlock.expires_in}` : "Active Unlock: None (src/ blocked)",
      "",
      `Artifacts Required: ${required.length || "none"}`,
      ...missing.map(m => `  ❌ ${m}`),
      ...present.map(p => `  ✅ ${p}`),
      "",
      `Lint Baseline: ${lint.errors >= 0 ? `${lint.errors} errors, ${lint.warnings} warnings` : "unavailable"}`,
      "",
      `Valid Next Phases: ${nextPhases.join(", ")}`,
      "",
      `WORK.md Next Task: ${nextTask || "none pending"}`,
      "",
      "Feature Health:",
      ...Object.entries(featureHealth).map(([f, h]) =>
        `  ${f}: overall ${Math.round(h.overall * 100)}% (R:${h.requirements} A:${h.analysis} D:${h.design} I:${h.implementation} T:${h.testing})`
      ),
      "",
      "Recent Ledger:",
      ...recent.map(r =>
        `  [${r.ts?.slice(11, 19)}] ${r.kind} ${r.task_type || ""} ${r.phase || ""} ${r.feature || ""} ${r.reason ? `— ${r.reason}` : ""}`
      )
    ]

    return {
      structured: result,
      summary: lines.join("\n")
    }
  }
})
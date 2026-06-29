// OMT++ Process Enforcer — opencode plugin (feature_006).
//
// Turns AGENTS.md's *voluntary* process checkpoints into a *real* gate, tuned for a
// solo-dev learning scaffold: it blocks the edit that would skip a phase, but every block
// is a teaching message that names the OMT++ rule and the exact next command. Internal
// errors fail OPEN (never brick a working session); only genuine process violations block.
//
// Mechanics:
//   • omt_phase  custom tool → agent declares task_type/phase/scope; recorded in the ledger.
//   • omt_skip   custom tool → logged escape hatch that unlocks edits for the session.
//   • tool.execute.before → gate edits to src/ (needs a phase), tests/ (needs approval),
//     and hard-deny README/.env/uv.lock/LICENSE.
//   • tool.execute.after  → run the MVC++ linter on touched src/*.py, surface warnings.
//
// Ledger: .meta/.omt/ledger.jsonl  (gitignored runtime state, one JSON record per line)
//
// API note (verify on opencode 1.17.x via the Step-0 probe): assumes `input.sessionID`
// on tool.execute.before and `context.sessionID` on custom-tool execute. If absent, the
// gate falls back to an 8-hour time window so it still functions for a single user.

import { tool } from "@opencode-ai/plugin"
import { appendFileSync, mkdirSync, existsSync, readFileSync, readdirSync, writeFileSync, statSync } from "node:fs"
import { join, relative, isAbsolute, dirname } from "node:path"
import { execFileSync } from "node:child_process"

const EDIT_TOOLS = new Set(["edit", "write", "patch", "multiedit"])
const VALID_TASK_TYPES = new Set([
  "bug_fix", "minor_feature", "major_feature", "new_screen", "refactor", "test", "docs",
])
// Task types that may not touch src/ until a design artifact exists on disk (guide §12).
const ARTIFACT_REQUIRED = new Set(["major_feature", "new_screen"])
const OMT_HARNESS_E2E_COMMAND = "uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q"
const OMT_HARNESS_E2E_RECEIPT = join(".meta", ".omt", "omt_harness_e2e_last_run.json")
const OMT_HARNESS_E2E_TEST = "tests/scripts/omt/test_omt_harness_e2e.py"

// Valid phase transitions per guide §12
const VALID_TRANSITIONS: Record<string, string[]> = {
  Analysis: ["Design", "Testing"],
  Design: ["Programming", "Analysis"],
  Programming: ["Testing", "Design", "Analysis"],
  Testing: ["Analysis", "Design", "Programming", "Done"],
}

// Phase exit requirements per guide §12 — only enforced for ARTIFACT_REQUIRED task types
const PHASE_EXIT_REQUIREMENTS: Record<string, { phase: string; patterns: string[]; description: string }[]> = {
  // Analysis → Design requires: Use case, Operation list, Analysis artifacts
  Analysis: [
    { phase: "Requirements", patterns: ["FEATURE.md"], description: "Use case / FEATURE.md" },
    { phase: "Analysis", patterns: ["analysis_001_*.md"], description: "Analysis docs (analysis_001_*.md)" },
  ],
  // Design → Programming requires: Design class diagram, Operation specs
  Design: [
    { phase: "Design", patterns: ["design_001_*.md"], description: "Design doc (design_001_*.md)" },
    { phase: "Operations", patterns: ["operation_spec_*.md", "operations.md"], description: "Operation specifications (operation_spec_*.md or operations.md)" },
  ],
  // Programming → Testing requires: Unit tests, Integration tests
  Programming: [
    { phase: "Implementation", patterns: ["*.md"], description: "Implementation notes (5.implementation/features/...)" },
    { phase: "Unit tests", patterns: ["test_*.py", "*_test.py"], description: "Unit tests (tests/features/<feature>/...)" },
  ],
  // Testing → Done requires: System tests
  Testing: [
    { phase: "System tests", patterns: ["test_report.md"], description: "System test report (6.testing/features/...)" },
  ],
}

// Resolve the actual feature subdirectory under a `features/` parent.
// The repo uses TWO naming conventions for non-requirements phase dirs:
//   - short: "feature_004"                 (older features: analysis/design/impl/testing)
//   - full:  "feature_007.agentx_intelligent_agent_behaviour"  (new_feature.py scaffolder)
// `feature` is the full slug; `featureNum` is the short "feature_NNN" prefix.
// Without this, full-slug features (the scaffolder default) are never found and
// phase-exit artifact checks report false negatives.
function resolveFeatureDir(featuresParent: string, feature: string, featureNum: string): string | null {
  try {
    if (!existsSync(featuresParent)) return null
    const entries = readdirSync(featuresParent, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name)
    // 1. exact matches (full slug first, then short)
    for (const c of [feature, featureNum]) {
      if (c && entries.includes(c)) return join(featuresParent, c)
    }
    // 2. prefix match: a full-slug dir that starts with "feature_NNN." or "feature_NNN_"
    for (const p of [featureNum + ".", featureNum + "_"]) {
      if (!featureNum || p === "." || p === "_") continue
      const m = entries.find(e => e.startsWith(p))
      if (m) return join(featuresParent, m)
    }
    return null
  } catch { return null }
}

// Check if required artifacts for a phase exist for a feature
function checkPhaseExitArtifacts(repoRoot: string, feature: string, fromPhase: string): { ok: boolean; missing: string[] } {
  if (!feature) return { ok: true, missing: [] }
  const requirements = PHASE_EXIT_REQUIREMENTS[fromPhase]
  if (!requirements) return { ok: true, missing: [] }

  const featureNum = feature.match(/feature_(\d+)/)?.[0] || feature
  const PROCESS_ROOT = ".meta/software_development_process"
  const missing: string[] = []

  for (const req of requirements) {
    let exists = false
    for (const pattern of req.patterns) {
      let dir: string | null = null
      if (req.phase === "Requirements") {
        dir = resolveFeatureDir(join(repoRoot, PROCESS_ROOT, "2.requirements", "features"), feature, featureNum)
      } else if (req.phase.startsWith("Analysis")) {
        dir = resolveFeatureDir(join(repoRoot, PROCESS_ROOT, "3.analysis", "features"), feature, featureNum)
      } else if (req.phase === "Design" || req.phase === "Operations") {
        dir = resolveFeatureDir(join(repoRoot, PROCESS_ROOT, "4.design", "features"), feature, featureNum)
      } else if (req.phase === "Implementation") {
        dir = resolveFeatureDir(join(repoRoot, PROCESS_ROOT, "5.implementation", "features"), feature, featureNum)
      } else if (req.phase.startsWith("Unit tests")) {
        dir = resolveFeatureDir(join(repoRoot, "tests", "features"), feature, featureNum)
      } else if (req.phase.startsWith("System tests")) {
        dir = resolveFeatureDir(join(repoRoot, PROCESS_ROOT, "6.testing", "features"), feature, featureNum)
      } else {
        continue
      }

      try {
        if (dir) {
          const files = readdirSync(dir, { recursive: true })
          exists = files.some(f => new RegExp(pattern.replace("*", ".*")).test(f))
          if (exists) break
        }
      } catch { /* ignore */ }
    }
    if (!exists) missing.push(req.description)
  }
  return { ok: missing.length === 0, missing }
}
const UNLOCK_WINDOW_MS = 8 * 60 * 60 * 1000

class OmtBlock extends Error {}

export const OmtEnforcer = async ({ client, $, directory }) => {
  const ledgerPath = join(directory, ".meta", ".omt", "ledger.jsonl")

  // --- ledger helpers ------------------------------------------------------
  const nowIso = () => new Date().toISOString()

  const writeLedger = (record) => {
    mkdirSync(dirname(ledgerPath), { recursive: true })
    appendFileSync(ledgerPath, JSON.stringify({ ts: nowIso(), ...record }) + "\n")
  }

  const readLedger = () => {
    if (!existsSync(ledgerPath)) return []
    const out = []
    for (const line of readFileSync(ledgerPath, "utf8").split("\n")) {
      const s = line.trim()
      if (!s) continue
      try { out.push(JSON.parse(s)) } catch { /* skip corrupt line */ }
    }
    return out
  }

  // Latest phase/skip unlocking edits for this session (exact match preferred,
  // else any record within the time window — keeps the gate usable if sessionID
  // is not threaded through on this opencode version).
  const getActiveUnlock = (session) => {
    const recs = readLedger().filter((r) => r.kind === "phase" || r.kind === "skip")
    if (!recs.length) return null
    const mine = session ? recs.filter((r) => r.session === session) : []
    let chosen = mine.length ? mine[mine.length - 1] : null
    if (!chosen) {
      const now = Date.now()
      const recent = recs.filter((r) => {
        const t = Date.parse(r.ts || "")
        return !Number.isNaN(t) && now - t < UNLOCK_WINDOW_MS
      })
      chosen = recent.length ? recent[recent.length - 1] : null
    }
    return chosen ? { type: chosen.kind, record: chosen } : null
  }

  // Latest phase record for a specific feature. Exact session match is preferred,
  // then we fall back to the recent single-user window. Unlike getActiveUnlock(),
  // this ignores skip records and unrelated features so omt_complete cannot be
  // shadowed by a later skip or another task's phase declaration.
  const getActiveFeaturePhase = (feature, session) => {
    const recs = readLedger().filter((r) => r.kind === "phase" && r.feature === feature)
    if (!recs.length) return null
    const mine = session ? recs.filter((r) => r.session === session) : []
    let chosen = mine.length ? mine[mine.length - 1] : null
    if (!chosen) {
      const now = Date.now()
      const recent = recs.filter((r) => {
        const t = Date.parse(r.ts || "")
        return !Number.isNaN(t) && now - t < UNLOCK_WINDOW_MS
      })
      chosen = recent.length ? recent[recent.length - 1] : null
    }
    return chosen
  }

  // Auto-detect a feature's design artifact from its slug (hardening — guide §12),
  // so the gate doesn't depend on the agent passing design_doc by hand.
  const detectDesignArtifact = (feature) => {
    if (!feature) return null
    const m = String(feature).match(/feature_(\d+)/)
    if (!m) return null
    const num = m[1]
    const rel = join(".meta", "software_development_process", "4.design", "features")
    const base = join(directory, rel)
    if (!existsSync(base)) return null
    let dirs
    try { dirs = readdirSync(base) } catch { return null }
    for (const d of dirs) {
      const match = d === `feature_${num}` || d.startsWith(`feature_${num}.`) || d.startsWith(`feature_${num}_`)
      if (!match) continue
      let files
      try { files = readdirSync(join(base, d)) } catch { continue }
      // Strict matching: only design_NNN_*.md files count as design artifacts (guide §12)
      const hit = files.find((f) => /^design_\d+_.+\.md$/i.test(f))
      // Optional: warn if .md files exist but no design_*.md (logged, not blocking)
      if (!hit && files.some(f => f.toLowerCase().endsWith(".md"))) {
        safeLog("warn", `Feature ${feature} has .md files but no design_NNN_*.md artifact in ${d}/`)
      }
      if (hit) return join(rel, d, hit)
    }
    return null
  }

  // Resolve the design artifact for a phase record: explicit design_doc first,
  // else auto-detected from the feature slug. Returns repo-relative path or null.
  const resolveArtifact = (record) => {
    if (record.design_doc && existsSync(join(directory, record.design_doc))) return record.design_doc
    const auto = detectDesignArtifact(record.feature)
    return auto && existsSync(join(directory, auto)) ? auto : null
  }
  const artifactPresent = (record) => !!resolveArtifact(record)

  // --- MVC++ lint delta (block only NEWLY introduced hard errors) ----------
  const lintFindings = async (abs) => {
    try {
      const res = await $`uv run scripts/omt/mvc_check.py ${abs} --json`.cwd(directory).quiet().nothrow()
      return JSON.parse(res.stdout.toString() || "{}").findings || []
    } catch { return [] }
  }
  const countByRule = (findings) => {
    const m = {}
    for (const f of findings) m[f.rule] = (m[f.rule] || 0) + 1
    return m
  }
  const hardSnapshot = new Map()  // abs path -> {rule: errorCount} captured pre-edit

  const safeLog = (level, message) => {
    try { client?.app?.log?.({ service: "omt-enforcer", level, message }) }
    catch { /* logging is best-effort */ }
  }

  const notify = async (message) => {
    // Non-blocking surfacing: try a toast, always fall back to the log.
    try { await client?.tui?.showToast?.({ message, variant: "warning" }) } catch { /* ignore */ }
    safeLog("warn", message)
  }

  // --- path classification -------------------------------------------------
  const relOf = (raw) => {
    const abs = isAbsolute(raw) ? raw : join(directory, raw)
    return { abs, rel: relative(directory, abs).split("\\").join("/") }
  }
  const isProtected = (rel) =>
    rel === "README.md" || rel === "uv.lock" || rel === "LICENSE" ||
    rel === ".env" || rel.startsWith(".env.")
  const isTests = (rel) => rel === "tests" || rel.startsWith("tests/")
  const isSrc = (rel) => rel.startsWith("src/")
  const isOmtHarness = (rel) =>
    rel === "AGENTS.md" || rel === "opencode.jsonc" ||
    rel === ".meta/software_development_process/omt_agent_guide.md" ||
    rel.startsWith(".opencode/plugin/omt_") ||
    rel.startsWith("scripts/omt/") ||
    rel.startsWith(".meta/templates/") ||
    rel.startsWith(".meta/software_development_process/2.requirements/features/feature_006.opencode_process_enforcement/") ||
    rel.startsWith("tests/scripts/omt/")

  const receiptTimestampMs = () => {
    const receipt = join(directory, OMT_HARNESS_E2E_RECEIPT)
    if (!existsSync(receipt)) return 0
    let parsed = 0
    try {
      const data = JSON.parse(readFileSync(receipt, "utf8") || "{}")
      const t = Date.parse(data.passed_at || data.timestamp || "")
      parsed = Number.isNaN(t) ? 0 : t
    } catch { /* ignore invalid receipt */ }
    try { return Math.max(parsed, statSync(receipt).mtimeMs) } catch { return parsed }
  }

  const isGitDirty = (rel) => {
    try {
      const out = execFileSync("git", ["status", "--porcelain", "--", rel], {
        cwd: directory,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"],
      })
      return out.trim().length > 0
    } catch {
      // If git is unavailable, fail open. The e2e test still verifies the source guard.
      return false
    }
  }

  const omtHarnessE2eStatus = (rel, abs) => {
    if (!isOmtHarness(rel)) return { ok: true, message: "" }
    if (rel === OMT_HARNESS_E2E_TEST || rel === OMT_HARNESS_E2E_RECEIPT) {
      return { ok: true, message: "" }
    }
    if (!existsSync(abs)) return { ok: true, message: "" }
    if (!isGitDirty(rel)) return { ok: true, message: "" }

    const lastPassed = receiptTimestampMs()
    let targetMtime = 0
    try { targetMtime = statSync(abs).mtimeMs } catch { return { ok: true, message: "" } }
    if (lastPassed >= targetMtime) return { ok: true, message: "" }

    return {
      ok: false,
      message:
        `⛔ OMT++ gate: '${rel}' is part of the META HARNESS / OMT enforcement surface ` +
        `and already has unverified changes. Run the comprehensive harness e2e test before ` +
        `editing it again:\n  ${OMT_HARNESS_E2E_COMMAND}\n` +
        `This test refreshes ${OMT_HARNESS_E2E_RECEIPT}.`,
    }
  }

  // --- teaching messages ---------------------------------------------------
  const denyMsg = (rel) =>
    `⛔ OMT++ gate: '${rel}' is protected by AGENTS.md (Core Directives — NEVER modify ` +
    `README.md / .env / uv.lock / LICENSE). Edit refused. If this is truly intended, ask the user.`

  const testsMsg = (rel) =>
    `⛔ OMT++ gate: editing '${rel}' requires explicit canary-test approval (AGENTS.md ` +
    `Stop Point #4). Get approval, then unlock with: omt_skip{reason:"approved canary test", scope:"tests"}.`

  const noPhaseMsg = (rel) =>
    `⛔ OMT++ gate: declare your OMT++ phase before editing src/ ('${rel}'). ` +
    `Run omt_phase{ task_type, scope } first (guide §2, §13). ` +
    `Trivial fix? omt_phase{task_type:"bug_fix", scope:"..."} is enough. To override: omt_skip{reason:"..."}.`

  const artifactMsg = (tt, record) =>
    `⛔ OMT++ gate: task_type '${tt}' may not edit src/ until a design artifact exists ` +
    `(guide §12). The gate auto-detects one under 4.design/features/feature_<n>/ from your ` +
    `feature slug ('${record.feature || "<none declared>"}'), or you can pass ` +
    `omt_phase{..., design_doc:"<path>"}. Scaffold one with: ` +
    `uv run scripts/omt/new_feature.py "<name>" --type ${tt}.`

  // --- custom tools --------------------------------------------------------
  // omt_status is registered by .opencode/plugin/omt_status.ts as its own
  // standalone plugin. Keeping it out of this enforcer avoids dynamic-import
  // cache/loading failures and duplicate tool registration.

  const omt_phase = tool({
    description:
      "Declare your OMT++ phase before editing src/. Records task_type/phase/scope to the " +
      "process ledger and unlocks edits according to the guide §12 matrix. This is the real " +
      "version of AGENTS.md's PROCESS CHECK. Call once per task before touching src/.",
    args: {
      task_type: tool.schema.string().describe(
        "one of: bug_fix, minor_feature, major_feature, new_screen, refactor, test, docs"),
      scope: tool.schema.string().describe("one sentence describing what 'done' looks like"),
      phase: tool.schema.string().optional().describe("Analysis | Design | Programming | Testing"),
      feature: tool.schema.string().optional().describe("feature slug, e.g. feature_006.x"),
      design_doc: tool.schema.string().optional().describe(
        "repo-relative path to the design/analysis artifact (required for major_feature/new_screen)"),
    },
    async execute(args, context) {
      const tt = String(args.task_type || "").trim()
      if (!VALID_TASK_TYPES.has(tt)) {
        return `❌ invalid task_type '${tt}'. Use one of: ${[...VALID_TASK_TYPES].join(", ")}.`
      }
      const session = context?.sessionID || undefined
      const newPhase = args.phase || ""

      // Phase exit validation: if transitioning FROM a feature-sized phase,
      // check artifacts exist. Bug fixes/refactors/tests intentionally keep the
      // lightweight §12 path: a recorded phase is enough.
      if (newPhase && args.feature) {
        const prevPhaseRecord = getActiveFeaturePhase(args.feature, session)
        if (prevPhaseRecord?.phase && prevPhaseRecord.phase !== newPhase) {
          const exitTaskType = prevPhaseRecord.task_type || tt
          if (ARTIFACT_REQUIRED.has(exitTaskType)) {
            const { ok, missing } = checkPhaseExitArtifacts(directory, args.feature, prevPhaseRecord.phase)
            if (!ok) {
              return `⛔ OMT++ gate: cannot leave ${prevPhaseRecord.phase} phase — missing required artifacts (guide §12):\n` +
                missing.map(m => `  • ${m}`).join("\n") +
                `\nComplete these before transitioning to ${newPhase}.`
            }
          }
        }
      }

      writeLedger({
        kind: "phase", session, task_type: tt, phase: args.phase || "",
        scope: args.scope || "", feature: args.feature || "", design_doc: args.design_doc || "",
      })
      const lines = [
        "📋 OMT++ PROCESS CHECK (recorded)",
        `- Task type: ${tt}`,
        `- Phase: ${args.phase || "(unspecified)"}`,
        `- Scope: ${args.scope || "(none)"}`,
      ]
      if (ARTIFACT_REQUIRED.has(tt)) {
        const found = resolveArtifact({ design_doc: args.design_doc, feature: args.feature })
        lines.push(found
          ? `- Artifact: ✅ ${found}`
          : `- Artifact: ⚠️ none found (checked design_doc + 4.design/features/${args.feature || "<feature>"}/) ` +
            `— src/ stays BLOCKED until a design doc exists ` +
            `(scaffold: uv run scripts/omt/new_feature.py "<name>" --type ${tt}).`)
      }
      lines.push("✅ src/ edits unlocked for this session" +
        (ARTIFACT_REQUIRED.has(tt) ? " once the artifact check passes." : "."))
      return lines.join("\n")
    },
  })

  const omt_skip = tool({
    description:
      "Logged escape hatch. Unlocks edits without a full phase declaration; the reason is " +
      "recorded in the ledger for audit. Use sparingly (emergencies, approved canary tests).",
    args: {
      reason: tool.schema.string().describe("why the process is being skipped"),
      scope: tool.schema.string().optional().describe("src | tests | all (default: all)"),
    },
    async execute(args, context) {
      const session = context?.sessionID || undefined
      const scope = args.scope || "all"
      writeLedger({
        kind: "skip", session, reason: args.reason || "(none)", scope,
        tests_approved: scope === "tests" || scope === "all",
      })
      return `⚠️ OMT++ skip recorded (scope=${scope}): "${args.reason}". Edits unlocked; ` +
        "this override is logged in .meta/.omt/ledger.jsonl."
    },
  })

  // --- omt_complete: Verify phase completion and optionally advance ---
  const omt_complete = tool({
    description:
      "Verify that all required artifacts for the current phase exist, then optionally advance to the next phase. " +
      "Use this to formally complete a phase and unlock the next one with artifact validation.",
    args: {
      feature: tool.schema.string().describe("feature slug, e.g. feature_006.x"),
      advance_to: tool.schema.string().optional().describe("optional: phase to advance to after verification (Design | Programming | Testing | Done)"),
    },
    async execute(args, context) {
      const session = context?.sessionID || undefined
      const feature = args.feature || ""
      const advanceTo = args.advance_to || ""

      if (!feature) {
        return `❌ feature slug required (e.g., feature_006.x)`
      }

      const phaseRecord = getActiveFeaturePhase(feature, session)
      if (!phaseRecord) {
        return `❌ no active phase for feature ${feature} in this session`
      }

      const currentPhase = phaseRecord.phase
      if (!currentPhase) {
        return `❌ no current phase declared for this feature`
      }

      // Check exit artifacts for feature-sized work only. For bug fixes,
      // refactors, tests, and docs, omt_complete should verify the declared
      // process step without inventing major-feature artifact requirements.
      if (ARTIFACT_REQUIRED.has(phaseRecord.task_type || "")) {
        const { ok, missing } = checkPhaseExitArtifacts(directory, feature, currentPhase)
        if (!ok) {
          return `⛔ Phase ${currentPhase} incomplete — missing required artifacts:\n` +
            missing.map(m => `  • ${m}`).join("\n") +
            `\nCreate these before completing ${currentPhase}.`
        }
      }

      // All artifacts present - record completion
      writeLedger({
        kind: "complete",
        session,
        feature,
        phase: currentPhase,
        ts: new Date().toISOString(),
      })

      let result = `✅ Phase ${currentPhase} complete for ${feature} — all artifacts verified.`

      // Advance to next phase if requested
      if (advanceTo) {
        const validNext = VALID_TRANSITIONS[currentPhase] || []
        if (!validNext.includes(advanceTo)) {
          return result + `\n⚠️ Invalid transition: ${currentPhase} → ${advanceTo}. Valid: ${validNext.join(", ")}`
        }

        // Declare new phase (will be validated on next omt_phase call, but we can pre-check)
        writeLedger({
          kind: "phase", session, task_type: phaseRecord.task_type || "major_feature",
          phase: advanceTo, scope: phaseRecord.scope || "", feature, design_doc: "",
        })
        result += `\n➡️ Advanced to ${advanceTo} phase.`
      }

      // Auto-sync WORK.md
      try { await syncWorkMdFromLedger() } catch { /* ignore */ }

      return result
    },
  })

  // --- WORK.md auto-sync from ledger ---
  async function syncWorkMdFromLedger() {
    const workMdPath = join(directory, "WORK.md")
    if (!existsSync(workMdPath)) return

    const ledger = readLedger()
    const completedFeatures = new Set<string>()

    // Find all completed phases from ledger
    for (const rec of ledger) {
      if (rec.kind === "complete" && rec.feature) {
        completedFeatures.add(rec.feature)
      }
    }

    let content = readFileSync(workMdPath, "utf8")
    let modified = false

    // Update checkboxes for completed features
    for (const feature of completedFeatures) {
      // Match both full slug (feature_006.opencode_process_enforcement) 
      // and short form (feature_006) since WORK.md may use either
      const shortFeature = feature.match(/feature_\d+/)?.[0]
      const matchPatterns = [feature]
      if (shortFeature && shortFeature !== feature) {
        matchPatterns.push(shortFeature)
      }

      const lines = content.split("\n")
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        // Check if this line contains any of our match patterns and is an unchecked checkbox
        if (line.trim().startsWith("- [ ]")) {
          for (const pattern of matchPatterns) {
            if (line.includes(pattern)) {
              lines[i] = line.replace("- [ ]", "- [x]")
              modified = true
              break
            }
          }
        }
      }
      content = lines.join("\n")
    }

    if (modified) {
      writeFileSync(workMdPath, content, "utf8")
    }
  }

  // --- hooks ---------------------------------------------------------------
  return {
    tool: { omt_phase, omt_skip, omt_complete },

    "tool.execute.before": async (input, output) => {
      try {
        if (!EDIT_TOOLS.has(input?.tool)) return
        const raw = output?.args?.filePath ?? output?.args?.path ?? output?.args?.file
        if (!raw) return
        const { abs, rel } = relOf(raw)

        if (isProtected(rel)) throw new OmtBlock(denyMsg(rel))

        const e2e = omtHarnessE2eStatus(rel, abs)
        if (!e2e.ok) throw new OmtBlock(e2e.message)

        const session = input?.sessionID || undefined

        if (isTests(rel)) {
          const unlock = getActiveUnlock(session)
          const approved = unlock && (unlock.type === "skip"
            ? unlock.record.tests_approved
            : unlock.record.tests_approved === true)
          if (!approved) throw new OmtBlock(testsMsg(rel))
          return
        }

        if (isSrc(rel)) {
          const unlock = getActiveUnlock(session)
          if (!unlock) throw new OmtBlock(noPhaseMsg(rel))
          if (unlock.type === "phase") {
            const tt = unlock.record.task_type
            if (ARTIFACT_REQUIRED.has(tt) && !artifactPresent(unlock.record)) {
              throw new OmtBlock(artifactMsg(tt, unlock.record))
            }
          }
          // Gate passed → snapshot pre-edit hard errors so the after-hook blocks
          // only violations THIS edit introduces (pre-existing legacy errors don't block).
          if (rel.endsWith(".py")) {
            const pre = existsSync(abs)
              ? countByRule((await lintFindings(abs)).filter((f) => f.severity === "error"))
              : {}
            hardSnapshot.set(abs, pre)
          }
        }
      } catch (e) {
        if (e instanceof OmtBlock) throw e          // intentional gate → block the edit
        safeLog("warn", "before-hook internal error (failing open): " + (e?.message || e))
      }
    },

    "tool.execute.after": async (input, output) => {
      if (!EDIT_TOOLS.has(input?.tool)) return
      const raw = output?.args?.filePath ?? output?.args?.path ?? output?.args?.file
      if (!raw) return
      const { abs, rel } = relOf(raw)
      if (!isSrc(rel) || !rel.endsWith(".py")) return

      let findings
      try {
        findings = await lintFindings(abs)
      } catch (e) {
        safeLog("warn", "after-hook mvc_check failed: " + (e?.message || e))
        hardSnapshot.delete(abs)
        return
      }

      const before = hardSnapshot.get(abs) || {}
      hardSnapshot.delete(abs)
      const afterHard = countByRule(findings.filter((f) => f.severity === "error"))
      // NEW hard violations = error rules whose count rose vs the pre-edit snapshot.
      const introduced = findings.filter(
        (f) => f.severity === "error" && (afterHard[f.rule] || 0) > (before[f.rule] || 0))

      if (introduced.length) {
        const lines = introduced.map((f) => `  ${f.rule} (${f.file}:${f.line}) ${f.message}`).join("\n")
        // Block (decision: hard-errors block, soft warns). The file was written;
        // the agent must correct it forward before continuing.
        throw new OmtBlock(
          `⛔ OMT++ gate: your edit introduced a hard MVC++ violation in ${rel} (guide §16). ` +
          `Fix it now (correct the file forward):\n${lines}`)
      }

      const warns = findings.filter((f) => f.severity === "warning")
      if (warns.length) {
        const top = warns.slice(0, 3).map((f) => `  ${f.rule} (${f.file}:${f.line})`).join("\n")
        await notify(`MVC++ on ${rel}: ${warns.length} warning(s) (advisory).\n${top}\n` +
          `Run: uv run scripts/omt/mvc_check.py ${rel}`)
      }
    },

    event: async ({ event }) => {
      if (event?.type !== "session.idle") return
      try {
        const res = await $`uv run scripts/omt/mvc_check.py --json`.cwd(directory).quiet().nothrow()
        const data = JSON.parse(res.stdout.toString() || "{}")
        if ((data.errors || 0) > 0) {
          await notify(`MVC++ sweep: ${data.errors} architecture error(s) in src/. ` +
            "Run: uv run scripts/omt/mvc_check.py")
        }
      } catch (e) {
        safeLog("warn", "session.idle sweep failed: " + (e?.message || e))
      }
    },
  }
}

// OMT++ Interrogative Tool (feature_026.omt_q_interrogative_first_ops).
// Read-only layer that crosses the v1 substrates (gate IR + ledger + thoughts +
// KB IR + e2e receipt + KNOWN_SUITE_FAILURES) to answer the three resume
// questions:
//   op:state  — the 5-read snapshot folded into one envelope (Phase-A surface).
//   op:plan   — predict the real before-gate chain for {path, tool} via the
//               additive runBeforeGatesDry sibling (U2 + U11 receipt fold).
//   op:drift  — KB-vs-source classification + count_drift direction-b only.
//   op:audit  — T1-2 design↔testing schema audit + project-autolink fix-it
//               (joins 4.design/features vs 6.testing/features/test_report.md).
//   op:graph  — T1-3 transitive risk over kb.ir.json refs[] + thoughts join
//               (BFS depth 1..3 from symbol; HQL grammar explicitly NOT built
//               until graph proves novel asks).
//
// Every response wraps in envelope: {as_of_commit:"<HEAD-sha>", op, ...} where
// as_of_commit is parsed live via `git rev-parse HEAD` per call. Each call
// appends a kind:"q" ledger record (v1.3 schema + v1.4 op_set/fold_used/
// latency_ms + v1.5 as_of:"HEAD").
//
// The plugin mirrors omt_nav.ts factory structure exactly:
//   - export default async ({directory, worktree}) => { initOmtShared(worktree
//     ?? directory); const {omt_q} = createQTools(); return {tool:{omt_q}} }
//   - tools built inside createQTools() AFTER initOmtShared (descriptions read
//     the IR under the injected root — F2/F17).
//
// Additive only: no changes to runBeforeGates body, IMPLS, FALLBACK_GATES, or
// any of the 8 existing omt_* plugins. The single mechanical touch is the
// sibling runBeforeGatesDry in gate_driver.ts (behaviour-preserving — the real
// throw-path is byte-identical).

import { tool } from "@opencode-ai/plugin"
import { execFileSync } from "node:child_process"
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs"
import { join } from "node:path"
import {
  initOmtShared, repoRoot, loadIr, readLedger, readLedgerAll, appendLedger,
  readThoughtsIndex, loadKbIr, omtHarnessE2eStatus,
  irToolDescription,
  gitShow, readLedgerAt, readLedgerAllAt, loadIrAt, loadKbIrAt,
  readThoughtsAt, resolveGitRef,
  UNLOCK_WINDOW_MS, THOUGHT_PATTERN, relOf,
} from "../lib/omt_shared"
import {
  getActiveFeaturePhase, hasNavUnlock, createSessionState,
  type EnforcerEnv,
} from "../lib/enforcer/session_state"
import { type GateCtx, runBeforeGatesDry } from "../lib/enforcer/gate_driver"

// ---------------------------------------------------------------------------
// headSha — parse `git rev-parse HEAD` live per call (v1.5 envelope). Falls
// back to the literal "HEAD" when git fails (e.g. a tmp probe root has no
// .git directory — the tests cover both paths).
// ---------------------------------------------------------------------------
function headSha(): string {
  try {
    return execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: repoRoot(), encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim()
  } catch {
    return "HEAD"
  }
}

// ---------------------------------------------------------------------------
// KNOWN_SUITE_FAILURES extractor (U10). Reads scripts/omt/tdd/state.py and
// regex-extracts the frozenset literal (parse-not-import — the constant
// move/rename surfaces immediately to the agent via
// known_suite_failures_parse_failed:true). feature_051/A1: the allowlist is
// PERMANENTLY EMPTY — the `[^}]*` quantifier parses the empty frozenset({})
// literal, so the field is a live invariant probe (non-empty output means
// someone regrew the allowlist = reverting A1). Fail-open on missing /
// unreadable file.
// ---------------------------------------------------------------------------
// feature_077 (T1-4): takes source TEXT (live read or gitShow at as_of) so
// historical replay never touches the working tree. Fail-open on null.
function parseKnownSuiteFailures(srcText: string | null): {
  nodeIds: string[]
  parse_failed: boolean
} {
  try {
    if (srcText == null) return { nodeIds: [], parse_failed: true }
    const src = srcText
    const m = src.match(/KNOWN_SUITE_FAILURES\s*=\s*frozenset\(\{([^}]*)\}\)/)
    if (!m) return { nodeIds: [], parse_failed: true }
    const ids = (m[1].match(/['"]([^'"]+)['"]/g) || [])
      .map((s) => s.slice(1, -1))
    return { nodeIds: ids, parse_failed: false }
  } catch {
    return { nodeIds: [], parse_failed: true }
  }
}

// ---------------------------------------------------------------------------
// Fold helpers (U6/U7/U8/U9/U10/U11/U13 + count_drift + synthetic env).
// Kept as local functions (REFACTOR phase may lift them into local helpers —
// they already are; just grouped clearly).
// ---------------------------------------------------------------------------

// Deterministic ts comparator (fail-open on NaN ts — those sort last).
function tsOf(r: any): number {
  const t = Date.parse(r?.ts || "")
  return Number.isNaN(t) ? 0 : t
}

// U6 stranded_red: per-test_node, latest state=="red" with NO later green at the
// SAME test_node. (A node that went red → green → red again is "currently red"
// — we look only at the latest state per node.)
function foldStrandedReds(records: any[], feature?: string): string[] {
  const recs = records.filter(
    (r) => r.kind === "tdd" && (!feature || r.feature === feature),
  )
  // group latest state per test_node
  const latestByNode = new Map<string, any>()
  for (const r of recs) {
    const node = r.test_node || ""
    if (!node) continue
    const prev = latestByNode.get(node)
    if (!prev || tsOf(r) > tsOf(prev)) latestByNode.set(node, r)
  }
  const stranded: string[] = []
  for (const [node, latest] of latestByNode) {
    if (String(latest.state || "").toLowerCase() === "red") stranded.push(node)
  }
  return stranded.sort()
}

// U7 closed_via_skip: latest complete record (for feature) with any
// checklist.{suite_passes, refactor_recorded, naming_ok} == false + a LATER
// skip scoped to the SAME feature within 1h whose reason contains "Override
// permits" OR "pre-existing baseline". CROSS-FEATURE FP GUARD: a skip for
// feature_Y does NOT flip feature_X (the skip.feature must equal the queried
// feature, OR the skip.scope text explicitly mentions the queried feature).
function foldClosedViaSkip(records: any[], feature?: string): boolean {
  if (!feature) return false
  const recs = records.filter(
    (r) => r.kind === "complete" || r.kind === "skip",
  )
  // latest not-done complete for this feature
  const completes = recs
    .filter((r) => r.kind === "complete" && r.feature === feature)
    .sort((a, b) => tsOf(b) - tsOf(a))
  if (!completes.length) return false
  const lastDone = completes[0]
  const cl = lastDone.checklist || {}
  const notDone =
    cl.suite_passes === false ||
    cl.refactor_recorded === false ||
    cl.naming_ok === false
  if (!notDone) return false
  // find a later skip scoped to the SAME feature within 1h, reason keyphrases
  const windowMs = 60 * 60 * 1000
  const doneTs = tsOf(lastDone)
  const qualifying = recs.some((r) => {
    if (r.kind !== "skip") return false
    if (tsOf(r) <= doneTs) return false
    if (tsOf(r) - doneTs > windowMs) return false
    // CROSS-FEATURE FP GUARD: skip must be for THIS feature. skip.feature
    // takes precedence; fallback to scope-text mention.
    const skipFeature = r.feature
    if (skipFeature && skipFeature === feature) {
      const reason = String(r.reason || "")
      return reason.includes("Override permits") ||
        reason.includes("pre-existing baseline")
    }
    // if skip.feature is missing or different, check scope text mentions
    // the feature slug (the existing omt_skip semantics write feature as
    // best-effort metadata; scope text can name the feature).
    const scope = String(r.scope || "")
    return scope.includes(feature)
  })
  return qualifying
}

// U8 decree_health: {slug_variants[], empty_slug_records[{ts,scope}],
// invalid_phase_records[{ts,phase}], phase_cycle_count}. NEAR-COLLISION GUARD:
// feature_004 != feature_04 (bare). We compare feature slugs by exact string;
// "feature_004.foo" and "feature_04" are distinct slugs by string equality
// (prefix "feature_004" != "feature_04" at position 10/11).
function foldDecreeHealth(records: any[], feature?: string): {
  slug_variants: string[]
  empty_slug_records: { ts: string; scope: string }[]
  invalid_phase_records: { ts: string; phase: string }[]
  phase_cycle_count: number
} {
  const VALID_PHASES = new Set([
    "Analysis", "Design", "Programming", "Testing", "Done", "",
  ])
  // Health checks (slug_variants / empty_slug / invalid_phase) are GLOBAL scans
  // across all phase records — a "decree" is corrupted regardless of which
  // feature the agent asked about (the empty-slug record doesn't carry a
  // feature to filter on). Only phase_cycle_count narrows to the queried
  // feature (per design §Functional Flow U8: count of phase records within the
  // query scope).
  const allPhaseRecs = records.filter((r) => r.kind === "phase")
  // slug variants (distinct feature fields anywhere in the ledger)
  const slugSet = new Set<string>()
  for (const r of allPhaseRecs) {
    const f = String(r.feature || "")
    if (f) slugSet.add(f)
  }
  const slug_variants = Array.from(slugSet).sort()
  // empty slug records (feature field missing/empty across ALL phase records)
  const empty_slug_records: { ts: string; scope: string }[] = []
  for (const r of allPhaseRecs) {
    if (!String(r.feature || "")) {
      empty_slug_records.push({ ts: String(r.ts || ""), scope: String(r.scope || "") })
    }
  }
  // invalid phase records (phase not in the FSM allowed set, across ALL)
  const invalid_phase_records: { ts: string; phase: string }[] = []
  for (const r of allPhaseRecs) {
    const phase = String(r.phase || "")
    if (!VALID_PHASES.has(phase)) {
      invalid_phase_records.push({ ts: String(r.ts || ""), phase })
    }
  }
  // phase_cycle_count: count of phase records within the query scope — when a
  // feature is given, only that feature's phase records; otherwise the count
  // of distinct features ever mentioned (the universe of phase cycles).
  const scopedPhaseRecs = feature
    ? allPhaseRecs.filter((r) => r.feature === feature)
    : allPhaseRecs
  const phase_cycle_count = feature
    ? scopedPhaseRecs.length
    : slug_variants.length
  return { slug_variants, empty_slug_records, invalid_phase_records, phase_cycle_count }
}

// T1 (feature_028, user-approved 2026-08-16): op=state default = summary
// projection (counts + top-N, truncated payloads) — the full dump measured
// 24–36KB/call in opencode.db (44KB live: risky_thoughts 31.6KB,
// recent_consults 5.9KB, decree_health 5.2KB); the agent asking "state" needs
// phase/tdd_position/stranded_red (~500B). verbose:true bypasses the
// projection and restores the byte-identical pre-T1 full dump.
const _trunc = (s: string, n: number) =>
  (s.length <= n ? s : s.slice(0, n - 1) + "…")

function summarizeDecreeHealth(h: {
  slug_variants: string[]
  empty_slug_records: { ts: string; scope: string }[]
  invalid_phase_records: { ts: string; phase: string }[]
  phase_cycle_count: number
}) {
  return {
    slug_variants_count: h.slug_variants.length,
    slug_variants_sample: h.slug_variants.slice(0, 3),
    empty_slug_count: h.empty_slug_records.length,
    empty_slug_sample: h.empty_slug_records.slice(0, 3)
      .map((r) => ({ ts: r.ts, scope: _trunc(r.scope, 80) })),
    invalid_phase_count: h.invalid_phase_records.length,
    phase_cycle_count: h.phase_cycle_count,
  }
}

function summarizeThoughts(thoughts: any[]) {
  return {
    count: thoughts.length,
    top: thoughts.slice(0, 3).map((t) => ({
      path: String(t?.path ?? ""), line: Number(t?.line ?? 0),
      thought: _trunc(String(t?.thought ?? ""), 120),
    })),
  }
}

function summarizeConsults(consults: { files: string[]; ts: string; session: string }[]) {
  const latest = consults.reduce((m, r) => Math.max(m, tsOf(r)), 0)
  return {
    count: consults.length,
    latest_ts: latest > 0 ? new Date(latest).toISOString() : "",
  }
}

// U9 skip_reason_tally: top-3 reason STEMS + counts. live_smoke_count is a
// named SEPARATE field — count of skip records whose reason contains "live
// smoke" stem (case-insensitive), scoped to nav-or-all.
function foldSkipReasonTally(records: any[]): {
  tally: { stem: string; count: number }[]
  live_smoke_count: number
} {
  const skips = records.filter((r) => r.kind === "skip")
  const stemOf = (reason: string): string => {
    // first 2-3 words as the stem
    const words = String(reason || "").trim().split(/\s+/).slice(0, 3).join(" ")
    return words
  }
  const counts = new Map<string, number>()
  let live_smoke_count = 0
  for (const r of skips) {
    const reason = String(r.reason || "")
    const stem = stemOf(reason)
    if (stem) counts.set(stem, (counts.get(stem) || 0) + 1)
    if (/live smoke/i.test(reason)) live_smoke_count += 1
  }
  const tally = Array.from(counts.entries())
    .map(([stem, count]) => ({ stem, count }))
    .sort((a, b) => b.count - a.count || a.stem.localeCompare(b.stem))
    .slice(0, 3)
  return { tally, live_smoke_count }
}

// U13 recent_consults: think_consult records within UNLOCK_WINDOW_MS (8h).
// Returns [{files[], ts, session}]. consult_needed: files NOT in
// recent_consults within the 8h window (when a feature is given, files
// referenced by active-feature activity that haven't been recently consulted).
function foldRecentConsults(records: any[], feature?: string): {
  recent_consults: { files: string[]; ts: string; session: string }[]
  consult_needed: string[]
} {
  const now = Date.now()
  const recs = records.filter(
    (r) => r.kind === "think_consult" &&
      now - tsOf(r) < UNLOCK_WINDOW_MS,
  )
  const recent_consults = recs.map((r) => ({
    files: Array.isArray(r.files) ? r.files : [],
    ts: String(r.ts || ""),
    session: String(r.session || ""),
  }))
  // consult_needed: when a feature is given, lint files that touched under the
  // feature (target_src from tdd records) that are NOT in recent consults.
  const recentlyConsultedFiles = new Set<string>()
  for (const r of recent_consults) {
    for (const f of r.files) recentlyConsultedFiles.add(f)
  }
  const consult_needed: string[] = []
  if (feature) {
    const tddRecs = records.filter(
      (r) => r.kind === "tdd" && r.feature === feature && Array.isArray(r.target_src),
    )
    for (const r of tddRecs) {
      for (const f of r.target_src) {
        if (!recentlyConsultedFiles.has(String(f))) {
          if (!consult_needed.includes(String(f))) consult_needed.push(String(f))
        }
      }
    }
  }
  return { recent_consults, consult_needed }
}

// U11 receipt_detail: populated when path is in @var.harness_paths.
// {receipt_required:true, file_mtime, receipt_passed_at, stale, refresh_tests,
// refresh_cmd}.
function foldReceiptDetail(rel: string, abs: string): {
  receipt_required: boolean
  file_mtime: number
  receipt_passed_at: number
  stale: boolean
  refresh_tests: string[]
  refresh_cmd: string
} | null {
  const ir = loadIr()
  let isHarnessPath = false
  if (ir?.harness_paths) {
    const exact = Array.isArray(ir.harness_paths.exact) ? ir.harness_paths.exact : []
    const prefix = Array.isArray(ir.harness_paths.prefix) ? ir.harness_paths.prefix : []
    if (exact.includes(rel) || prefix.some((p: string) => rel.startsWith(p))) {
      isHarnessPath = true
    }
  } else {
    // FOLD: the g.receipt gate applies only to harness surface files; if the IR
    // is missing, fall back to the omtHarnessE2eStatus classification (it
    // internally falls back to the FALLBACK_HARNESS_PATHS literal — never die
    // open). When isOmtHarness returns false, receipt_required:false.
    const status = omtHarnessE2eStatus(rel, abs)
    isHarnessPath = !status.ok || status.message !== ""
  }
  if (!isHarnessPath) return null
  const E2E_TEST = "tests/scripts/omt/test_omt_harness_e2e.py"
  const E2E_CMD = `uv run pytest ${E2E_TEST} -q`
  let file_mtime = 0
  let receipt_passed_at = 0
  let stale = false
  try {
    if (existsSync(abs)) file_mtime = statSync(abs).mtimeMs
  } catch { /* fail open */ }
  // receipt timestamp from omt_harness_e2e_last_run.json
  try {
    const rp = join(repoRoot(), ".meta", ".omt", "omt_harness_e2e_last_run.json")
    if (existsSync(rp)) {
      const data = JSON.parse(readFileSync(rp, "utf8") || "{}")
      const t = Date.parse(String(data.passed_at || data.timestamp || ""))
      receipt_passed_at = Number.isNaN(t) ? 0 : t
    }
  } catch { /* fail open */ }
  stale = file_mtime > receipt_passed_at && file_mtime > 0
  return {
    receipt_required: true,
    file_mtime,
    receipt_passed_at,
    stale,
    refresh_tests: [E2E_TEST],
    refresh_cmd: E2E_CMD,
  }
}

// T3-2 delegate-advisory fold (feature_071): advisory-only delegate_hint.
// Research-heavy = session with >=1 complete (re-deriving KB/nav via paired
// think_consult) OR fresh feature resume (feature with prior completes).
// Research-shaped plan tools = grep|glob|rg|find|read|explore (read-only fanout).
// Never enforced — agent free to ignore. Ledger-session scoping in prompt so
// parallel probes don't shadow canary.
const RESEARCH_TOOLS = new Set(["grep", "glob", "rg", "find", "read", "explore"]);

function foldDelegateHint(
  records: any[],
  opts: { feature?: string; session?: string; tool?: string; path?: string },
): { subagent_type: string; suggested_prompt: string } | null {
  const { feature, session, tool: toolName, path } = opts;
  const completes = records.filter((r) => r?.kind === "complete");
  const sessionHasComplete = session
    ? completes.some((r) => String(r?.session || "") === session)
    : false;
  const featureHasComplete = feature
    ? completes.some((r) => String(r?.feature || "") === feature)
    : false;
  const isResearchTool = toolName ? RESEARCH_TOOLS.has(String(toolName)) : false;

  // plan path: research-shaped tool -> explore (read-only fanout)
  if (toolName && isResearchTool) {
    const scope = session ? `session '${session}'` : "current session";
    return {
      subagent_type: "explore",
      suggested_prompt:
        `Delegate research for path '${path ?? ""}' (tool '${toolName}') to subagent_type 'explore' ` +
        `in ${scope}: explore(read-only) → propose → approval → execute. ` +
        `Scope ledger reads to ${scope} so parallel probes don't shadow canary. ` +
        `Advisory only — safe to ignore.`,
    };
  }
  // state resume: research-heavy session -> explore (orientation read);
  // plan edit in research-heavy session -> general (broader delegation)
  if (sessionHasComplete) {
    if (toolName) {
      return {
        subagent_type: "general",
        suggested_prompt:
          `Delegate follow-up for path '${path ?? ""}' in research-heavy session '${session}' ` +
          `to subagent_type 'general': explore(read-only) → propose → approval → execute. ` +
          `Scope ledger reads to session '${session}' so parallel probes don't shadow canary. ` +
          `Advisory only — safe to ignore.`,
      };
    }
    const who = feature ? `feature '${feature}'` : "resume";
    return {
      subagent_type: "explore",
      suggested_prompt:
        `Delegate orientation read for ${who} in session '${session}' to subagent_type 'explore': ` +
        `explore(read-only) → propose → approval → execute. ` +
        `Scope ledger reads to session '${session}' so parallel probes don't shadow canary. ` +
        `Advisory only — safe to ignore.`,
    };
  }
  // fresh feature resume (no session, but feature has priors) -> explore
  if (!session && feature && featureHasComplete) {
    return {
      subagent_type: "explore",
      suggested_prompt:
        `Delegate orientation read for fresh resume of feature '${feature}' to subagent_type 'explore': ` +
        `explore(read-only) → propose → approval → execute. ` +
        `Scope ledger reads to feature '${feature}' so parallel probes don't shadow canary. ` +
        `Advisory only — safe to ignore.`,
    };
  }
  // resume with feature history but fresh session -> explore (orientation read)
  if (feature && featureHasComplete && session) {
    return {
      subagent_type: "explore",
      suggested_prompt:
        `Delegate orientation read for feature '${feature}' in session '${session}' to subagent_type 'explore': ` +
        `explore(read-only) → propose → approval → execute. ` +
        `Scope ledger reads to session '${session}' so parallel probes don't shadow canary. ` +
        `Advisory only — safe to ignore.`,
    };
  }
  return null;
}

// U3 drift: KB-vs-source classification + count_drift direction-b only.
// KB>skeleton IS drift; KB<skeleton is NOT drift (per edge case #5 + the v1
// "new = not-yet-tracked is NOT drift" rule).
// feature_077 (T1-4): optional `commit` replays KB records AND the referenced
// source files via gitShow (no working-tree reads) — drift-at-<commit>.
function foldDrift(commit?: string): {
  drift_records: any[]
  count_drift: { kb: number; skeleton: number; direction_b_only: boolean }
} {
  const kb = commit ? loadKbIrAt(commit) : loadKbIr()
  const records = Array.isArray(kb?.records) ? kb.records : []
  const readSrcText = (rel: string): string | null => {
    if (commit) return gitShow(commit, rel)
    const absPath = join(repoRoot(), rel)
    if (!existsSync(absPath)) return null
    try { return readFileSync(absPath, "utf8") } catch { return null }
  }
  const drift_records: any[] = []
  let skeleton = 0
  for (const r of records) {
    const src = String(r?.src || "")
    const line = Number(r?.line || 0)
    if (!src || line < 1) continue
    const srcText = readSrcText(src)
    if (srcText == null) {
      drift_records.push({ ...r, classification: "GONE" })
      continue
    }
    const lines = srcText.split("\n")
    skeleton += 1 // count KB records whose source is at least intact
    const recLine = lines[line - 1] || ""
    // Check if the line at the recorded position still looks like a thought marker.
    // THOUGHT_PATTERN matches lines like "# TA:" / "// TA:" / "<!-- TA:". The
    // ^\s* prefix anchors at start-of-line; we pass the stale recLine as a
    // single-line string so ^ matches at position 0 (m flag with multi-line
    // text would also work; here we compare the actual source line in isolation).
    const re = new RegExp(THOUGHT_PATTERN, "")
    if (!re.test(recLine)) {
      drift_records.push({ ...r, classification: "MOVED", line_drift: true })
      continue
    }
    // The recorded thought text may have shifted; we don't auto-migrate.
  }
  return {
    drift_records,
    count_drift: {
      kb: records.length,
      skeleton,
      direction_b_only: true,
    },
  }
}

// ---------------------------------------------------------------------------
// T1-3 (feature_078, mh8): transitive risk over kb.ir.json refs[] + thoughts
// join (read-only). BFS from `symbol` following refs[] up to `depth` (clamped
// 1..3, default 1). depth_sets[d] = nodes first reached at exactly depth d;
// risk_nodes = union excluding the root symbol. related_thoughts = thoughts
// whose text mentions the symbol or any risk node (case-insensitive substring,
// capped at 5, 120-char truncation like summarizeThoughts). HQL grammar is
// explicitly NOT built here — parked until graph proves novel asks (per T1-3
// acceptance). Fail-open: unknown symbol → {error} envelope, empty risk.
// feature_077 (T1-4) pattern: optional `commit` replays kb.ir + thoughts via
// gitShow/readThoughtsAt (no working-tree reads).
// ---------------------------------------------------------------------------
function foldGraph(
  symbol: string,
  depth: number,
  commit?: string,
): {
  risk_nodes: string[]
  depth_sets: Record<string, string[]>
  related_thoughts: { path: string; line: number; thought: string }[]
  error?: string
} {
  const maxDepth = Math.min(3, Math.max(1, Math.floor(depth) || 1))
  const kb = commit ? loadKbIrAt(commit) : loadKbIr()
  const records = Array.isArray(kb?.records) ? kb.records : []
  const refsById = new Map<string, string[]>()
  for (const r of records) {
    const id = String(r?.id || "")
    if (!id) continue
    const refs = Array.isArray(r?.refs) ? r.refs.map((x: any) => String(x)) : []
    refsById.set(id, refs)
  }
  if (!refsById.has(symbol)) {
    return {
      risk_nodes: [], depth_sets: {},
      related_thoughts: [],
      error: `unknown symbol '${symbol}' (not a kb.ir.json record id)`,
    }
  }
  const visited = new Set<string>([symbol])
  const depth_sets: Record<string, string[]> = {}
  let frontier = [symbol]
  for (let d = 1; d <= maxDepth; d++) {
    const next = new Set<string>()
    for (const id of frontier) {
      for (const ref of refsById.get(id) || []) {
        if (!visited.has(ref)) next.add(ref)
      }
    }
    const level = Array.from(next).sort()
    depth_sets[String(d)] = level
    for (const id of level) visited.add(id)
    frontier = level
    if (!frontier.length) {
      for (let fill = d + 1; fill <= maxDepth; fill++) depth_sets[String(fill)] = []
      break
    }
  }
  visited.delete(symbol)
  const risk_nodes = Array.from(visited).sort()
  // Thoughts join: mention of the symbol or any risk node in thought text.
  const needles = [symbol, ...risk_nodes].map((s) => s.toLowerCase())
  const related_thoughts: { path: string; line: number; thought: string }[] = []
  try {
    const thoughts = commit ? readThoughtsAt(commit) : readThoughtsIndex()
    for (const t of thoughts) {
      const text = String(t?.thought || "").toLowerCase()
      if (!text) continue
      if (needles.some((n) => n && text.includes(n))) {
        related_thoughts.push({
          path: String(t?.path ?? ""),
          line: Number(t?.line ?? 0),
          thought: _trunc(String(t?.thought ?? ""), 120),
        })
        if (related_thoughts.length >= 5) break
      }
    }
  } catch { /* fail open */ }
  return { risk_nodes, depth_sets, related_thoughts }
}

// Synthetic GateCtx builder (U2 plan op). Mirrors the SDK before-hook shape:
// input={tool}, output={args:{filePath}} — the BUG-A pin literal.
function buildCtxFromInputs(args: {
  path: string
  tool?: string
  session?: string
}): GateCtx {
  const { abs, rel } = relOf(args.path)
  const toolName = args.tool ?? "edit"
  const env: EnforcerEnv = {
    state: createSessionState(),
    directory: repoRoot(),
    safeLog: () => {},
    notify: async () => {},
    client: {},
    $: {},
  }
  if (args.session) {
    env.state.nav.set(args.session, { usedNav: !!hasNavUnlock(args.session) })
  }
  return {
    env,
    session: args.session,
    tool: toolName,
    input: { tool: toolName },
    output: { args: { filePath: args.path } },
    rel,
    abs,
    memo: new Map(),
  }
}

// feature_077 (T1-4): historical phase pick over an as-of ledger — mirrors
// session_state.getActiveFeaturePhase's latest-record semantics + tombstone
// retirement, minus the 8h liveness window (a commit's records are ALL "past";
// the window is meaningless for replay). "abandoned" records never win.
function featurePhaseAt(records: any[], feature: string, session?: string): any | null {
  const idx: number[] = []
  records.forEach((r: any, i: number) => {
    if (r?.kind === "phase" && r?.feature === feature && r?.phase &&
        r.phase !== "abandoned") idx.push(i)
  })
  if (!idx.length) return null
  const live = idx.filter((i) => !records.slice(i + 1).some((x: any) =>
    x?.kind === "phase" && x?.phase === "abandoned" &&
    x?.feature === feature && x?.abandons === records[i].phase))
  if (!live.length) return null
  if (session && live.some((i) => records[i].session === session)) {
    const mine = live.filter((i) => records[i].session === session)
    return records[mine[mine.length - 1]]
  }
  return records[live[live.length - 1]]
}

// Shared envelope emit + ledger append (consolidates the 3-op duplication:
// latency_ms + appendLedger{kind:"q"} + JSON.stringify). Fail-open on ledger.
function emitQEnvelope(
  start: number, op: string,
  op_set: string[], fold_used: string,
  extra: Record<string, any>,
  ledger_extra: Record<string, any> = {},
): string {
  const latency_ms = Date.now() - start
  try {
    appendLedger({
      kind: "q", op, ts: new Date().toISOString(),
      op_set, fold_used, latency_ms, as_of: "HEAD",
      ...ledger_extra,
    })
  } catch { /* ledger fail-open */ }
  return JSON.stringify({ op, ...extra })
}

// ---------------------------------------------------------------------------
// createQTools: built post-init (mirrors omt_nav's createNavTools).
// ---------------------------------------------------------------------------
function createQTools() {
  const omt_state = tool({
    description: "op=state impl (unregistered; dispatched via omt_q).",
    args: {
      feature: tool.schema.string().optional(),
      session: tool.schema.string().optional(),
      as_of: tool.schema.string().optional(),
      verbose: tool.schema.boolean().optional(),
    },
    async execute(args, context) {
      const start = Date.now()
      const verbose = args?.verbose === true
      const feature = args?.feature
      const session = args?.session
      // feature_077 (T1-4): as_of replays ledger/thoughts/kb/state.py at the
      // resolved commit; phase uses a tombstone-aware historical pick
      // (featurePhaseAt) instead of the live 8h-window selector.
      const asOfSha = args?.as_of ? (resolveGitRef(args.as_of) ?? args.as_of) : null
      const as_of_commit = asOfSha ?? headSha()
      const records = asOfSha ? readLedgerAt(asOfSha) : readLedger()
      try {
        // phase (U1 pipe-through via getActiveFeaturePhase, fails to "Unknown")
        let phase = "Unknown"
        if (feature) {
          const phaseRec = asOfSha
            ? featurePhaseAt(records, feature, session)
            : getActiveFeaturePhase(feature, session)
          if (phaseRec && phaseRec.phase) phase = String(phaseRec.phase)
        }
        // tdd_position: latest kind:tdd for feature, joined to tdd_testlist
        let tdd_position: any = null
        if (feature) {
          const tddRecs = records
            .filter((r) => r.kind === "tdd" && r.feature === feature)
            .sort((a, b) => tsOf(b) - tsOf(a))
          if (tddRecs.length) {
            const latest = tddRecs[0]
            tdd_position = {
              state: String(latest.state || ""),
              test_node: String(latest.test_node || ""),
              target_src: Array.isArray(latest.target_src) ? latest.target_src : [],
              verified: !!latest.verified,
              exit_code: Number(latest.exit_code ?? 0),
            }
          }
        }
        // U6 stranded_red
        const stranded_red = foldStrandedReds(records, feature)
        // U7 closed_via_skip (+ cross-feature FP guard)
        const closed_via_skip = foldClosedViaSkip(records, feature)
        // U8 decree_health
        const decree_health = foldDecreeHealth(records, feature)
        // U9 skip_reason_tally + live_smoke_count
        const { tally: skip_reason_tally, live_smoke_count } =
          foldSkipReasonTally(records)
        // U10 known_suite_failures (T1-4: source at as_of commit when set)
        const ksf = parseKnownSuiteFailures(
          asOfSha
            ? gitShow(asOfSha, "scripts/omt/tdd/state.py")
            : (() => {
                const p = join(repoRoot(), "scripts", "omt", "tdd", "state.py")
                if (!existsSync(p)) return null
                try { return readFileSync(p, "utf8") } catch { return null }
              })())
        // U13 recent_consults + consult_needed
        const { recent_consults, consult_needed } =
          foldRecentConsults(records, feature)
        // last_activity_ts: max ts across feature-scoped records (or hot max)
        const scopedRecs = feature
          ? records.filter((r) => r.feature === feature)
          : records
        const last_activity_ts = scopedRecs.length
          ? String(scopedRecs[0].ts || "")
          : ""
        const tsMax = scopedRecs.reduce((max, r) => {
          const t = tsOf(r)
          return t > max ? t : max
        }, 0)
        // risky_thoughts: thoughts on files touched under feature (re-scan source)
        const risky_thoughts: any[] = []
        try {
          const thoughts = asOfSha ? readThoughtsAt(asOfSha) : readThoughtsIndex()
          risky_thoughts.push(...thoughts)
        } catch { /* fail open */ }
        // T3-2 delegate-advisory fold (feature_071): advisory hint on resume.
        let delegateHint: { subagent_type: string; suggested_prompt: string } | null = null;
        try {
          const allRecs = asOfSha ? readLedgerAllAt(asOfSha) : readLedgerAll();
          delegateHint = foldDelegateHint(allRecs.length ? allRecs : records, { feature, session });
        } catch {
          try { delegateHint = foldDelegateHint(records, { feature, session }); } catch { delegateHint = null; }
        }
        return emitQEnvelope(
          start, "state",
          ["U1", "U6", "U7", "U8", "U9", "U10", "U13", "T3-2"],
          "U1,U6,U7,U8,U9,U10,U13,T3-2",
          {
            as_of_commit,
            feature, session, phase, tdd_position,
            stranded_red, closed_via_skip,
            decree_health: verbose ? decree_health : summarizeDecreeHealth(decree_health),
            skip_reason_tally, live_smoke_count,
            known_suite_failures: ksf.nodeIds,
            known_suite_failures_parse_failed: ksf.parse_failed,
            recent_consults: verbose ? recent_consults : summarizeConsults(recent_consults),
            consult_needed,
            last_activity_ts: tsMax > 0 ? new Date(tsMax).toISOString() : "",
            risky_thoughts: verbose ? risky_thoughts : summarizeThoughts(risky_thoughts),
            ...(delegateHint ? { delegate_hint: delegateHint } : {}),
            ...(asOfSha ? { as_of_scope: "replayed:ir+ledger+thoughts+kb+state_py" } : {}),
          },
          { feature, session, ...(asOfSha ? { as_of: as_of_commit } : {}) },
        )
      } catch {
        const envelope = {
          as_of_commit, op: "state", feature, session, phase: "Unknown",
        }
        return JSON.stringify(envelope)
      }
    },
  })

  const omt_plan = tool({
    description: "op=plan impl (unregistered; dispatched via omt_q).",
    args: {
      path: tool.schema.string().describe("repo-relative or absolute target path"),
      tool: tool.schema.string().optional().describe("edit|write|patch|multiedit|grep|glob|rg|find (default edit)"),
      session: tool.schema.string().optional(),
      as_of: tool.schema.string().optional(),
    },
    async execute(args, context) {
      const start = Date.now()
      const path = args?.path ?? ""
      // feature_077 (T1-4): as_of replays the gate SET (IR at commit) + the
      // ledger-side folds (last_escape, delegate hint). Live-only by design:
      // gate impls evaluate the LIVE session/phase state and receipts — a
      // historical "would this have blocked?" verdict is out of scope (the
      // envelope's as_of_scope says exactly this).
      const asOfSha = args?.as_of ? (resolveGitRef(args.as_of) ?? args.as_of) : null
      const as_of_commit = asOfSha ?? headSha()
      try {
        if (!path) {
          const envelope = { as_of_commit, op: "plan", path, error: "path required" }
          return JSON.stringify(envelope)
        }
        const ctx = buildCtxFromInputs({
          path,
          tool: args?.tool,
          session: args?.session,
        })
        const decisions = await runBeforeGatesDry(
          ctx, asOfSha ? loadIrAt(asOfSha) : undefined)
        // T3-1 escape-replay fold (feature_070): read-only last_escape attach.
        // For each BLOCKED gate, find most-recent matching skip (scope allow-list
        // per gate). Agent must still call omt_skip — this is advisory only.
        let lastEscapeByGate: Record<string, any> = {}
        try {
          const recs = asOfSha ? readLedgerAllAt(asOfSha) : readLedgerAll()
          const scopeAllow: Record<string, string[]> = {
            "g.nav": ["nav", "all"],
            "g.protect": ["all"],
            "g.receipt": ["all"],
            "g.tests": ["tests", "all"],
            "g.net": ["all"],
            "g.phase": ["src", "all"],
          }
          for (const d of decisions) {
            if (!d.blocked) continue
            const allow = scopeAllow[d.gate_id] || []
            if (!allow.length) continue
            let best: any = null
            let bestTs = 0
            for (const r of recs) {
              if (r?.kind !== "skip") continue
              const sc = String(r?.scope || "")
              if (!allow.includes(sc)) continue
              const t = tsOf(r)
              if (t > bestTs) { bestTs = t; best = r }
            }
            if (best) {
              lastEscapeByGate[d.gate_id] = {
                scope: String(best.scope || ""),
                reason: String(best.reason || ""),
                ts: String(best.ts || ""),
              }
            }
          }
        } catch { /* fail-open: no last_escape */ }
        const predicted_chain = decisions.map((d) => ({
          gate_id: d.gate_id,
          blocked: d.blocked,
          msg: d.msg,
          skip_ok: d.skip_ok,
          ...(d.blocked && lastEscapeByGate[d.gate_id]
            ? { last_escape: lastEscapeByGate[d.gate_id] } : {}),
        }))
        const first_blocker = decisions.find((d) => d.blocked) || null
        // U11 receipt_detail
        let receipt_detail: any = null
        if (ctx.rel && ctx.abs) {
          receipt_detail = foldReceiptDetail(ctx.rel, ctx.abs)
        }
        // T3-2 delegate-advisory fold (feature_071): advisory hint on research-shaped plan.
        let delegateHint: { subagent_type: string; suggested_prompt: string } | null = null;
        try {
          const allRecs = asOfSha ? readLedgerAllAt(asOfSha) : readLedgerAll();
          delegateHint = foldDelegateHint(allRecs, {
            session: args?.session,
            tool: args?.tool ?? "edit",
            path,
          });
        } catch { delegateHint = null; }
        return emitQEnvelope(
          start, "plan", ["U2", "U11", "T3-1", "T3-2"], "U2,U11,T3-1,T3-2",
          {
            as_of_commit, path,
            tool: args?.tool ?? "edit",
            session: args?.session,
            predicted_chain, first_blocker, receipt_detail,
            ...(delegateHint ? { delegate_hint: delegateHint } : {}),
            ...(asOfSha ? { as_of_scope: "replayed:ir+ledger; live:session-state+receipt" } : {}),
          },
          { path, tool: args?.tool, session: args?.session, ...(asOfSha ? { as_of: as_of_commit } : {}) },
        )
      } catch {
        const envelope = {
          as_of_commit, op: "plan", path,
          error: "plan op failed (fail-open)",
        }
        return JSON.stringify(envelope)
      }
    },
  })


// ---------------------------------------------------------------------------
// feature_030: project-lifecycle drift (read-only). Full ledger fold — links
// span months. Additive `project_drift` envelope field (U3 surface untouched).
// ---------------------------------------------------------------------------
function foldProjectDrift(): any[] {
  const root = repoRoot()
  const records = readLedgerAll()
  const out: any[] = []
  const links = new Map<string, any>()
  const creates = new Map<string, string>()
  const lastEvent = new Map<string, any>()
  for (const r of records) {
    if (r.kind === "project_link" && r.feature && r.project) links.set(r.feature, r)
    if (r.kind === "project" && r.project) {
      lastEvent.set(r.project, r)
      if (r.op === "create" && !creates.has(r.project)) creates.set(r.project, r.ts || "")
    }
  }
  const hasLink = (slug: string) => [...links.values()].some((l) => l.project === slug)
  const derivedState = (slug: string): string => {
    const ev = lastEvent.get(slug)
    if (!ev) return "unknown"
    if (ev.op === "close") return "complete"
    if (ev.op === "archive") return "archived"
    return hasLink(slug) ? "active" : "draft"
  }
  const homesRoot = join(root, ".projects", "meta")
  const featsRoot = join(root, ".meta", "software_development_process", "2.requirements", "features")
  const topLogDate = (csPath: string): string => {
    try {
      const m = readFileSync(csPath, "utf8").match(/^## (\d{4}-\d{2}-\d{2})/m)
      return m ? m[1] : ""
    } catch { return "" }
  }
  for (const [feature, link] of links) {
    const home = join(homesRoot, link.project)
    if (!existsSync(home) && derivedState(link.project) !== "archived") {
      out.push({ class: "phantom-link", feature, project: link.project, detail: `project home missing — fix: uv run scripts/omt/project.py link ${feature} ${link.project} --origin inferred` })
    }
    if (/^feature_\d+\./.test(feature) && !existsSync(join(featsRoot, feature))) {
      out.push({ class: "phantom-link", feature, project: link.project,
                 detail: `feature dir missing in 2.requirements/features/ — fix: uv run scripts/omt/project.py link ${feature} ${link.project} --origin inferred` })
    }
    // terminal ships only: a phase:"Analysis/Design/Programming" complete is
    // mid-flight, not a ship; legacy records without phase count as terminal.
    const completes = records.filter((r) => r.kind === "complete" && r.feature === feature
      && (!r.phase || r.phase === "Testing" || r.phase === "Done"))
    if (completes.length) {
      const lastDone = String(completes[completes.length - 1].ts || "").slice(0, 10)
      const top = topLogDate(join(home, "CURRENT_STATE.md"))
      if (lastDone && top && lastDone > top) {
        out.push({ class: "stale-log", feature, project: link.project,
                   detail: `shipped ${lastDone} > top log entry ${top}` })
      }
    }
  }
  for (const r of records) {
    if (r.kind !== "phase" || !r.design_doc || !r.feature) continue
    const m = String(r.design_doc).match(/^\.projects\/meta\/([^/]+)\//)
    if (m && links.get(r.feature)?.project !== m[1]) {
      out.push({ class: "unlinked-project-backed", feature: r.feature, project: m[1],
                 detail: `design_doc under .projects/ without project_link — fix: uv run scripts/omt/project.py link ${r.feature} ${m[1]} --origin inferred` })
    }
  }
  const now = Date.now()
  for (const [slug, ts] of creates) {
    const ageDays = ts ? (now - Date.parse(ts)) / 86400000 : 0
    if (!hasLink(slug) && derivedState(slug) === "draft" && ageDays > 21) {
      out.push({ class: "aging-draft", project: slug,
                 detail: `draft ${Math.floor(ageDays)}d, no linked features` })
    }
  }
  try {
    for (const slug of readdirSync(homesRoot)) {
      let header = ""
      try {
        const m = readFileSync(join(homesRoot, slug, "PROJECT.md"), "utf8")
          .match(/> Status: \*\*([a-z]+)\*\*/)
        header = m ? m[1] : ""
      } catch { continue }
      const derived = derivedState(slug)
      if (derived !== "unknown" && header && header !== derived) {
        out.push({ class: "status-drift", project: slug,
                   detail: `header '${header}' != derived '${derived}' — project.py sync` })
      }
      try {
        const lastChange = execFileSync(
          "git", ["log", "-1", "--format=%cs", "--", `.projects/meta/${slug}/PROJECT.md`],
          { cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim()
        const top = topLogDate(join(homesRoot, slug, "CURRENT_STATE.md"))
        if (lastChange && top && lastChange > top) {
          out.push({ class: "iteration-log", project: slug,
                     detail: `PROJECT.md changed ${lastChange} > top log entry ${top}` })
        }
      } catch { /* git unavailable (probe tmp root) — class omitted */ }
    }
  } catch { /* no homes root */ }
  return out
}

// ---------------------------------------------------------------------------
// T1-2 (feature_068, mh8): design↔testing schema audit (read-only). Joins
// 4.design/features/<slug> vs 6.testing/features/<slug>/test_report.md.
// design_only = in design but not testing (the 5 known live gaps: 004, 006,
// 017_chat, 018.chat, 018.react). testing_only = in testing but not design.
// Each record carries a runnable project.py link fix-it pointer per the
// project-autolink half of T1-2 (mh7 P1-3). Hermetic: reads under repoRoot()
// so tmp-root probes with seeded trees exercise generic join logic.
// ---------------------------------------------------------------------------
function foldSchemaAudit(): {
  design_only: { slug: string; side: string; detail: string }[]
  testing_only: { slug: string; side: string; detail: string }[]
  fix_it: string
} {
  const root = repoRoot()
  const designRoot = join(root, ".meta", "software_development_process", "4.design", "features")
  const testingRoot = join(root, ".meta", "software_development_process", "6.testing", "features")
  let designSlugs: string[] = []
  let testingSlugs: string[] = []
  try {
    if (existsSync(designRoot)) designSlugs = readdirSync(designRoot).filter((n) => !n.startsWith("."))
  } catch { /* fail open */ }
  try {
    if (existsSync(testingRoot)) testingSlugs = readdirSync(testingRoot).filter((n) => !n.startsWith("."))
  } catch { /* fail open */ }
  const designSet = new Set(designSlugs)
  const testingSet = new Set(testingSlugs)
  const design_only = designSlugs.filter((s) => !testingSet.has(s)).sort()
    .map((slug) => ({
      slug, side: "design_only",
      detail: `in 4.design/features but missing in 6.testing/features — fix: uv run scripts/omt/project.py link ${slug} <project> --origin inferred`,
    }))
  const testing_only = testingSlugs.filter((s) => !designSet.has(s)).sort()
    .map((slug) => {
      const report = join(testingRoot, slug, "test_report.md")
      const hasReport = existsSync(report)
      return {
        slug, side: "testing_only",
        detail: `in 6.testing/features but missing in 4.design/features${hasReport ? " (has test_report.md)" : " (no test_report.md)"} — fix: uv run scripts/omt/project.py link ${slug} <project> --origin inferred`,
      }
    })
  return {
    design_only, testing_only,
    fix_it: "uv run scripts/omt/project.py link <feature> <project> --origin inferred",
  }
}

  const omt_audit = tool({
    description: "op=audit impl (unregistered; dispatched via omt_q).",
    args: { as_of: tool.schema.string().optional() },
    async execute(args, context) {
      const start = Date.now()
      const as_of_commit = headSha()
      try {
        const { design_only, testing_only, fix_it } = foldSchemaAudit()
        return emitQEnvelope(
          start, "audit", ["T1-2"], "T1-2",
          { as_of_commit, design_only, testing_only, fix_it, project_drift: foldProjectDrift() },
        )
      } catch {
        const envelope = {
          as_of_commit, op: "audit",
          design_only: [], testing_only: [],
          fix_it: "uv run scripts/omt/project.py link <feature> <project> --origin inferred",
          project_drift: [],
        }
        return JSON.stringify(envelope)
      }
    },
  })

  const omt_drift = tool({
    description: "op=drift impl (unregistered; dispatched via omt_q).",
    args: { as_of: tool.schema.string().optional() },
    async execute(args, context) {
      const start = Date.now()
      // feature_077 (T1-4): as_of replays kb.ir records + source reads at the
      // commit; project_drift stays LIVE (ledger-all + homes + git log are
      // current-state by design — flagged via as_of_scope).
      const asOfSha = args?.as_of ? (resolveGitRef(args.as_of) ?? args.as_of) : null
      const as_of_commit = asOfSha ?? headSha()
      try {
        const { drift_records, count_drift } = foldDrift(asOfSha ?? undefined)
        return emitQEnvelope(
          start, "drift", ["U3"], "U3",
          {
            as_of_commit, drift_records, count_drift, project_drift: foldProjectDrift(),
            ...(asOfSha ? { as_of_scope: "replayed:kb+src; live:project_drift" } : {}),
          },
          asOfSha ? { as_of: as_of_commit } : {},
        )
      } catch {
        const envelope = {
          as_of_commit, op: "drift",
          drift_records: [], count_drift: { kb: 0, skeleton: 0, direction_b_only: true }, project_drift: [],
        }
        return JSON.stringify(envelope)
      }
    },
  })

  const omt_graph = tool({
    description: "op=graph impl (unregistered; dispatched via omt_q).",
    args: {
      symbol: tool.schema.string().describe("kb.ir.json record id (e.g. doc.mvcpp)"),
      depth: tool.schema.number().optional().describe("BFS depth 1..3 (default 1)"),
      as_of: tool.schema.string().optional(),
    },
    async execute(args, context) {
      const start = Date.now()
      const symbol = String(args?.symbol || "")
      const depth = Number(args?.depth ?? 1)
      const asOfSha = args?.as_of ? (resolveGitRef(args.as_of) ?? args.as_of) : null
      const as_of_commit = asOfSha ?? headSha()
      try {
        if (!symbol) {
          return JSON.stringify({
            as_of_commit, op: "graph", symbol, depth,
            error: "symbol required (kb.ir.json record id)",
            risk_nodes: [], depth_sets: {}, related_thoughts: [],
          })
        }
        const { risk_nodes, depth_sets, related_thoughts, error } =
          foldGraph(symbol, depth, asOfSha ?? undefined)
        return emitQEnvelope(
          start, "graph", ["T1-3"], "T1-3",
          {
            as_of_commit, symbol, depth: Math.min(3, Math.max(1, Math.floor(depth) || 1)),
            risk_nodes, depth_sets, related_thoughts,
            ...(error ? { error } : {}),
            ...(asOfSha ? { as_of_scope: "replayed:kb+thoughts" } : {}),
          },
          { symbol, ...(asOfSha ? { as_of: as_of_commit } : {}) },
        )
      } catch {
        const envelope = {
          as_of_commit, op: "graph", symbol, depth,
          risk_nodes: [], depth_sets: {}, related_thoughts: [],
          error: "graph op failed (fail-open)",
        }
        return JSON.stringify(envelope)
      }
    },
  })

  const omt_q = tool({
    description: irToolDescription(
      "omt_q",
      "TA: Interrogative layer — read-only. op=state(feature?,session?,as_of?,verbose?) | plan(path,tool?,session?,as_of?) | drift(as_of?) | audit(as_of?) | graph(symbol,depth?,as_of?). state ≤2KB; verbose=full. Returns JSON envelope with as_of_commit=HEAD-sha.",
    ),
    // NOTE: the literal "TA:" appears in the description above — that's
    // intentional: omt_q is in @var.harness_paths (so editing this file trips
    // g.receipt) AND contains "TA:" (so it trips g.think). op:plan on this
    // very file is the v1.3 thesis demonstration (the interrogative tool
    // predicts the receipt+think gates on itself).
    args: {
      op: tool.schema.string().describe("state|plan|drift|audit|graph"),
      feature: tool.schema.string().optional(),
      session: tool.schema.string().optional(),
      path: tool.schema.string().optional(),
      tool: tool.schema.string().optional(),
      as_of: tool.schema.string().optional(),
      verbose: tool.schema.boolean().optional()
        .describe("state: restore the full dump (default = ≤2KB summary)"),
      symbol: tool.schema.string().optional()
        .describe("graph: kb.ir.json record id (e.g. doc.mvcpp)"),
      depth: tool.schema.number().optional()
        .describe("graph: BFS depth 1..3 (default 1)"),
    },
    async execute(args, context) {
      switch (args?.op ?? "") {
        case "state": return omt_state.execute(args, context)
        case "plan": return omt_plan.execute(args, context)
        case "drift": return omt_drift.execute(args, context)
        case "audit": return omt_audit.execute(args, context)
        case "graph": return omt_graph.execute(args, context)
        default:
          return "⛔ omt_q: unknown op — want state|plan|drift|audit|graph"
      }
    },
  })

  return { omt_q }
}

// Standalone opencode plugin factory — mirrors omt_nav.ts exactly. The loader
// iterates Object.values and requires every export to be a function (or
// {}.server). The tool objects are NOT functions, so only the default export
// is allowed.
export default async ({ directory, worktree }: { directory: string; worktree?: string }) => {
  initOmtShared(worktree ?? directory)
  const { omt_q } = createQTools()
  return {
    tool: { omt_q },
  }
}

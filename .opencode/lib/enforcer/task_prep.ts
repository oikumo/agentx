// T3-5 task-prep op slice (feature_073.task_prep_op_slice).
//
// Vertical C+B slice for routine bugfixes: ONE bounded prep response that
// assembles applicable obligations + relevant context in a single call.
//
// Foundation (Improvement002 B + Suggested sequence C+B):
//   - P0-1 preflight (preflightProjection, feature_062) is the SINGLE source
//     for restrictions/next-action — prep.blocked == preflight.would_block and
//     prep.first_blocker == preflight.first_blocker (no second gate engine).
//   - T4-1 typed policy (evaluatePolicy, feature_072) is the SINGLE source for
//     the g.net activation/exception note — preflight == enforcement == explain.
//   - Risk model by change characteristics (not task label alone): affected
//     contracts, data handling, reversibility, arch boundaries, shared
//     resources, uncertainty. A small bugfix touching a permission check
//     escalates even when task_type == bug_fix.
//
// Guardrails (B acceptance):
//   - READ-ONLY: no ledger writes, no auto-registration, no shell-outs.
//   - Never fabricates consultation or approval: consulted:false,
//     approved:false always — pointers suggest what to call, never claim it.
//   - Bounded: JSON ≤ ~2KB (truncated fields, concise lists).
//   - Measure-before-broaden: standalone module (no new tool wiring yet);
//     broadening to a tool surface happens only after option-A measurement.
//
// Usage (routine bugfix):
//   const prep = await buildTaskPrep({ path:"src/foo.py", tool:"edit",
//     session:"ses_a", feature:"feature_073.task_prep_op_slice",
//     task_type:"bug_fix", description:"fix null check in foo" })

import { preflightProjection } from "./preflight"
import { evaluatePolicy } from "./policy_decision"

export interface TaskPrepInput {
  path: string
  tool?: string
  session?: string
  feature?: string
  task_type?: string
  description?: string
  netMarking?: { work_active: number; activeHolders: string[] } | null
}

export type RiskLevel = "low" | "medium" | "high"

export interface RiskSignals {
  affectsContracts: boolean
  dataHandling: boolean
  irreversible: boolean
  archBoundary: boolean
  sharedResource: boolean
  uncertain: boolean
}

export interface TaskPrepResponse {
  op: "task_prep"
  identity: { path: string; rel: string | null; tool: string; session?: string; feature?: string; task_type: string }
  risk: { level: RiskLevel; signals: RiskSignals; reasons: string[] }
  knowledge: { consulted: false; pointers: string[]; note: string }
  restrictions: { gate_id: string; blocked: boolean; clearing_action: string }[]
  policy: { via: string; explanation: string }
  evidence: string[]
  next_action: string
  preflight: { would_block: number; first_blocker: string | null }
  blocked: boolean
  first_blocker: string | null
  approved: false
  scope: { path: string; tool: string }
  note: string
}

const _trunc = (s: string, n: number): string =>
  s.length <= n ? s : s.slice(0, n - 1) + "…"

// Risk model by change characteristics (B: labels are defaults only).
export function riskOf(input: TaskPrepInput): { level: RiskLevel; signals: RiskSignals; reasons: string[] } {
  const path = String(input.path || "")
  const desc = String(input.description || "").toLowerCase()
  const signals: RiskSignals = {
    affectsContracts: /contract|api|schema|policy|permission|gate/i.test(path + " " + desc),
    dataHandling: /auth|pii|token|secret|password|credential|personal|payment/i.test(path + " " + desc),
    irreversible: /migrat|delete|drop|irrevers|destruct|purge/i.test(path + " " + desc),
    archBoundary: /cross-layer|arch |boundary|\.opencode\/|scripts\/omt\//i.test(path + " " + desc) ||
      path.startsWith(".opencode/") || path.startsWith("scripts/omt/"),
    sharedResource: /concurrent|shared|ledger|net_|receipt|harness/i.test(path + " " + desc) ||
      path.startsWith(".opencode/") || path.startsWith("scripts/omt/") || path.startsWith("tests/"),
    uncertain: /unknown|unsure|maybe|\?\?\?|tbd|unclear/i.test(desc) || desc.trim().length < 20,
  }
  const reasons: string[] = []
  if (signals.affectsContracts) reasons.push("touches contracts/policy surface")
  if (signals.dataHandling) reasons.push("handles sensitive data/auth")
  if (signals.irreversible) reasons.push("irreversible (migration/delete)")
  if (signals.archBoundary) reasons.push("crosses arch/harness boundary")
  if (signals.sharedResource) reasons.push("touches shared/harness resource")
  if (signals.uncertain) reasons.push("uncertain scope (short/vague description)")
  // Escalation: data+irreversible => high; >=2 strong signals => high;
  // 1 strong or harness-shared => medium; else low.
  const strong = [signals.affectsContracts, signals.dataHandling, signals.irreversible].filter(Boolean).length
  const anyShared = signals.archBoundary || signals.sharedResource
  let level: RiskLevel = "low"
  if ((signals.dataHandling && signals.irreversible) || strong >= 2) level = "high"
  else if (strong >= 1 || anyShared) level = "medium"
  // Uncertainty alone never lowers risk — it can only raise low->medium.
  if (level === "low" && signals.uncertain && (signals.affectsContracts || signals.dataHandling || anyShared)) level = "medium"
  return { level, signals, reasons }
}

function evidenceFor(level: RiskLevel, taskType: string): string[] {
  const base = ["repro/behavioral test for the fix", "targeted suite green, no new MVC hard violations"]
  if (level === "low") return base
  if (level === "medium") return [...base, "KB consult for touched surface (omt_kb_nav)", "e2e receipt when harness surface edited"]
  return [...base, "full suite green", "explicit user approval before irreversible step", "no scope-all skip (break-glass audited only)"]
}

// ONE prep call: identity + risk + knowledge pointers + restrictions (preflight)
// + evidence + next action. block == preflight decision by construction.
export async function buildTaskPrep(input: TaskPrepInput): Promise<TaskPrepResponse> {
  const toolName = String(input.tool || "edit")
  const taskType = String(input.task_type || "bug_fix")
  const proj: any = await preflightProjection(input.path, toolName, input.session)
  const before: any[] = Array.isArray(proj?.before) ? proj.before : []
  const restrictions = before.filter((r: any) => r.fired).map((r: any) => ({
    gate_id: String(r.gate_id),
    blocked: !!r.blocked,
    clearing_action: _trunc(String(r.clearing_action || ""), 160),
  }))
  const would_block = Number(proj?.summary?.would_block ?? restrictions.filter((r) => r.blocked).length)
  const first_blocker: string | null = proj?.summary?.first_blocker ?? restrictions.find((r) => r.blocked)?.gate_id ?? null
  // T4-1 reuse: g.net note via ONE evaluator (solo default; live concurrency
  // still needs fire(work_start) — same dry caveat as preflight).
  const marking = input.netMarking !== undefined ? input.netMarking : { work_active: 1, activeHolders: ["f1_active"] }
  let policy = { via: "defer_untyped", explanation: "" }
  try {
    const d: any = evaluatePolicy({ gate: "g.net", session: input.session, nowMs: Date.now(), records: [], netMarking: marking })
    policy = { via: String(d.via), explanation: _trunc(String(d.explanation || ""), 160) }
  } catch { /* fail-open: policy note omitted */ }
  const { level, signals, reasons } = riskOf(input)
  const evidence = evidenceFor(level, taskType)
  const knowledge = {
    consulted: false as const,
    pointers: [
      `omt_kb_nav{op:"nav", query:"${_trunc(String(input.path).split("/").slice(-1)[0] || input.path, 40)}"} for touched surface`,
      `omt_nav{op:"quick_ref", workflow:"${level === "low" ? "TDD" : "START_MAJOR"}"} for procedure`,
    ],
    note: "pointers only — call the tools to consult; prep never claims understanding from retrieval",
  }
  const next_action = first_blocker
    ? `clear ${first_blocker}: ${restrictions.find((r) => r.gate_id === first_blocker)?.clearing_action || "see preflight"}`
    : `edit ${input.path} with ${toolName}, then validate: ${evidence[0]}`

  return {
    op: "task_prep",
    identity: {
      path: input.path, rel: proj?.rel ?? null, tool: toolName,
      ...(input.session ? { session: input.session } : {}),
      ...(input.feature ? { feature: input.feature } : {}),
      task_type: taskType,
    },
    risk: { level, signals, reasons },
    knowledge,
    restrictions,
    policy,
    evidence,
    next_action: _trunc(next_action, 280),
    preflight: { would_block, first_blocker },
    blocked: would_block > 0,
    first_blocker,
    approved: false,
    scope: { path: input.path, tool: toolName },
    note: "changing scope (path/tool) refreshes restrictions — re-call prep; no approval fabricated",
  }
}

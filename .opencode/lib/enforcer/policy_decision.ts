// T4-1 typed policy semantics (feature_072.typed_policy_semantics).
//
// ONE evaluator for preflight / enforcement / explain over a small set of
// typed primitives. Incremental slice of Improvement002 C: the .omt @gate
// text still owns prose, but g.net's activation (concurrent-only, C1) and its
// break-glass exception (expiring scope=all, audited) are now explicit typed
// data evaluated by ONE function — instead of prose-only divergences between
// preflightProjection, gate_driver's impl, and net/gate.py.
//
// Separation (C contract):
//   durable progress  = phase records per feature (task advancement; survives
//                       temp-grant expiry; feature-scoped so A cannot move B)
//   temp grant        = skip records per session/scope (authorization; 8h
//                       expiry removes authority, never progress)
//   consult evidence  = nav/kb/think consults (relevance, never authority)
// Progressing a phase never revokes a valid grant; expiry never deletes progress.
//
// Wiring: gate_driver g.net calls evaluatePolicy for the activation +
// exception pre-checks (live shell-out to net_check.py stays the authority
// for the concurrent permission verdict); preflightProjection reuses the same
// dry chain so preflight == enforcement on activation/exception, with the
// live-permission caveat kept explicit. omt_q op:plan explains via
// explainDecision — identical text everywhere.

import { UNLOCK_WINDOW_MS } from "../omt_shared"

export type GateId = string

// Closed activation vocabulary (C: no unrestricted language).
export type ActivationKind = "always" | "concurrent_only"
// Closed exception vocabulary — break-glass is the ONLY typed override.
export type ExceptionKind = "none" | "break_glass_all"

export interface TypedGatePolicy {
  gate: GateId
  activation: ActivationKind
  exception: ExceptionKind
}

// Explicit compiled-data mirror of the .omt prose (single source in TS until
// the DSL gains typed exception/activation fields — then harnessc emits it).
export const TYPED_POLICIES: Record<string, TypedGatePolicy> = {
  "g.net": { gate: "g.net", activation: "concurrent_only", exception: "break_glass_all" },
}

export interface NetMarking {
  work_active: number
  activeHolders: string[]
}

export interface PolicySnapshot {
  gate: GateId
  session?: string
  feature?: string
  rel?: string
  nowMs: number
  records: any[]
  netMarking: NetMarking | null
}

export type PolicyVia =
  | "activation_solo_skip"
  | "exception_break_glass"
  | "deny_concurrent_no_grant"
  | "defer_untyped"

export interface PolicyDecision {
  allowed: boolean
  via: PolicyVia
  reason: string
  explanation: string
  activation?: string
  exception?: string
}

function recordTsMs(r: any): number {
  const t = Date.parse(String(r?.ts || ""))
  return Number.isNaN(t) ? 0 : t
}

function isAlive(r: any, nowMs: number): boolean {
  if (!r || (r as any).phase === "abandoned") return false
  const t = recordTsMs(r)
  return t > 0 && nowMs - t < UNLOCK_WINDOW_MS
}

// Break-glass: kind=skip, scope=all, alive, audited (non-empty reason).
// Session-matched preferred; else window-recent (explicit fallback — the
// rule getActiveUnlock applied implicitly before).
export function findBreakGlass(
  records: any[], session: string | undefined, nowMs: number,
): any | null {
  const cands = (records || []).filter((r) =>
    r?.kind === "skip" && String(r?.scope || "") === "all" &&
    typeof r?.reason === "string" && String(r.reason).trim().length > 0 &&
    isAlive(r, nowMs))
  if (!cands.length) return null
  if (session) {
    const mine = cands.filter((r) => String(r?.session || "") === session)
    if (mine.length) return mine[mine.length - 1]
  }
  return cands[cands.length - 1]
}

// Durable progress: alive phase record for THIS feature (feature-scoped —
// feature A can never satisfy feature B). Tombstone-retired phases excluded
// (abandon with abandons==phase retires the earlier record).
export function hasDurableProgress(
  records: any[], feature: string | undefined, session: string | undefined, nowMs: number,
): boolean {
  if (!feature) return false
  const recs = records || []
  const phases = recs.filter((r) => r?.kind === "phase" && String(r?.feature || "") === feature)
  if (!phases.length) return false
  const retired = new Set<number>()
  recs.forEach((x: any) => {
    if (x?.kind === "phase" && x?.phase === "abandoned" && x?.feature === feature && x?.abandons) {
      phases.forEach((p: any) => {
        if (String(p?.phase || "") === String(x.abandons)) retired.add(recs.indexOf(p))
      })
    }
  })
  const alive = phases.filter((p: any) => isAlive(p, nowMs) && !retired.has(recs.indexOf(p)))
  if (!alive.length) return false
  if (session && phases.some((p: any) => String(p?.session || "") === session)) {
    return alive.some((p: any) => String(p?.session || "") === session)
  }
  return true
}

export function isConcurrentMarking(m: NetMarking | null): boolean {
  if (!m) return false // unreadable bundle engages (fail-closed) — caller decides
  if ((m.work_active ?? 0) > 1) return true
  return (m.activeHolders ?? []).length > 1
}

// ONE evaluator — preflight, enforcement pre-check, and explain share it.
export function evaluatePolicy(snap: PolicySnapshot): PolicyDecision {
  const policy = TYPED_POLICIES[snap.gate]
  if (!policy) {
    const d: PolicyDecision = {
      allowed: true, via: "defer_untyped",
      reason: `gate ${snap.gate} is untyped in this slice — defer to existing impl`,
      explanation: `defer: ${snap.gate} untyped (T4-1 slice types g.net only)`,
    }
    return d
  }
  // Activation: concurrent_only — solo skips to phase-gate only (C1).
  if (policy.activation === "concurrent_only" && !isConcurrentMarking(snap.netMarking)) {
    // Null marking (unreadable bundle) must NOT solo-skip — fail closed.
    if (snap.netMarking === null) {
      const d: PolicyDecision = {
        allowed: false, via: "deny_concurrent_no_grant",
        reason: "net marking unreadable — engage fail-closed (solo must be proven)",
        explanation: "deny g.net: marking unreadable → engage (fail-closed)",
        activation: "concurrent_only",
      }
      return d
    }
    const d: PolicyDecision = {
      allowed: true, via: "activation_solo_skip",
      reason: "solo session — g.net skips to phase-gate only (C1)",
      explanation: "allow g.net: solo activation skip (C1)",
      activation: "solo_skip",
    }
    return d
  }
  // Exception: expiring audited break-glass scope=all.
  if (policy.exception === "break_glass_all") {
    const bg = findBreakGlass(snap.records || [], snap.session, snap.nowMs)
    if (bg) {
      const d: PolicyDecision = {
        allowed: true, via: "exception_break_glass",
        reason: `break-glass scope=all (reason "${String(bg.reason).slice(0, 80)}", session '${String(bg.session || "")}') — expiring, audited`,
        explanation: "allow g.net: break-glass scope=all (expiring, audited)",
        exception: "break_glass_all",
      }
      return d
    }
  }
  const d: PolicyDecision = {
    allowed: false, via: "deny_concurrent_no_grant",
    reason: "concurrent without live net grant — fire(work_start) or break-glass scope=all required",
    explanation: "deny g.net: concurrent, no live grant (fire work_start or break-glass scope=all)",
    activation: "concurrent_only",
  }
  return d
}

// Single explain surface — preflight lines, enforcement blocks, and
// omt_q plan notes render THIS text so the three never diverge.
export function explainDecision(gate: GateId, d: PolicyDecision): string {
  return `${d.explanation} [${d.via}]`
}

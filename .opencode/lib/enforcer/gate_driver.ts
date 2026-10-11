// OMT++ HDL-2 gate driver (improvement006/OPT-F).
//
// The before-hook gate chain is DATA-DRIVEN: .meta/META_HARNESS.omt @gate
// records (compiled into harness.ir.json gates[]) declare on/tools/when/
// requires/msg/hard/skip_ok/order per gate. This driver iterates the IR
// before-gates in ascending order=, matches tools=, evaluates when= through
// the closed @pred registry (HDL-1: data only; TS owns builtins), and delegates the gate-specific
// remainder the DSL does not yet express to the registered impl (IMPLS):
// design-artifact matrix, TDD-hat deferral, per-file consult, protected
// override, tests-stop.
//
// .omt-only operations (no TS edit, no receipt round-robin ×7):
//   • reorder gates (order=)      • retarget a gate's tool set (tools=)
//   • retarget when= path sets    • change ANY gate's block/warn text (@msg payload — R8/OPT-G)
//   • ADD a pred-composed before-gate (unregistered id → genericImpl)
// TS-required: new @pred builtins, new specialized impls (before IMPLS /
// after AFTER_IMPLS — improvement007 R7: after-gates are data-driven too).
//
// Fallback philosophy (isDocPath heritage): if the IR is missing/corrupt the
// chain must never die open — FALLBACK_GATES mirrors the .omt order/tools.

import { existsSync, readFileSync } from "node:fs"
import { createHash } from "node:crypto"
import {
  loadIr, relOf, globToRegex, readLedger, readThoughtsIndex,
  omtHarnessE2eStatus, UNLOCK_WINDOW_MS, protectList, matchesProtect, gateMsg,
} from "../omt_shared"
import {
  OmtBlock, getActiveUnlock, hasNavUnlock, hasFastPathUnlock,
  hasStickyKbConsult, hasRecentRead, type EnforcerEnv,
} from "./session_state"
import { getSearchPath, navCacheHint, navGateDecision } from "./nav_gate"
import {
  guardProtectedPath, guardHarnessReceipt, guardTestsPath,
} from "./receipt_guard"
import { guardSrcPath } from "./phase_gate"
import { guardThoughts, fileThoughtsIn } from "./think_gate"
import { evaluatePolicy } from "./policy_decision"
import { mvcAfterEdit } from "./mvc_after"
import { tddAfterEdit } from "./tdd_hats"

export interface GateCtx {
  env: EnforcerEnv
  session: string | undefined
  tool: string
  input: any
  output: any
  rel: string | null  // edit tools: target file; search tools: search scope
  abs: string | null
  memo: Map<string, boolean> // per-invocation pred cache (e.g. file_has greps)
}

// --- @pred builtins (HDL-1 closed vocabulary) --------------------------------

function pathEntries(spec: string, ir: any): string[] {
  const m = spec.match(/^@var\.([a-z0-9_]+)$/)
  const raw = m ? String(ir?.vars?.[m[1]] ?? "") : spec
  return raw.split(",").map((e) => e.trim()).filter(Boolean)
}

function pathIn(rel: string, spec: string, ir: any): boolean {
  if (spec === "@protect.*") {
    // improvement007 R6 (HDL-2 die-open fix): with the IR missing, ir?.protect
    // evaluates to [] and the when= pre-filter skipped g.protect entirely —
    // protected files were UNGUARDED on the fallback chain. Fall back to the
    // shared-lib accessor (FALLBACK_PROTECT literal) — never die open.
    const list = Array.isArray(ir?.protect) && ir.protect.length
      ? ir.protect : protectList()
    return list.some((p: any) => matchesProtect(rel, p))
  }
  return pathEntries(spec, ir).some((e) => {
    if (e.includes("*")) return globToRegex(e).test(rel)
    return e.endsWith("/") ? rel.startsWith(e) : rel === e
  })
}

// feature_054 C2: bug_fix/test phase record satisfies g.nav+g.kb in one
// write — session_state.hasFastPathUnlock is the single ledger-backed
// implementation (session-matched, window fallback; major/new_screen stay
// hard). The phase tool also flips the in-memory flags for immediacy.
const SESSION_FLAGS: Record<string, (ctx: GateCtx) => boolean> = {
  nav_used: (ctx) => {
    const s = ctx.session ? ctx.env.state.nav.get(ctx.session) : undefined
    return !!s?.usedNav || hasNavUnlock(ctx.session) || hasFastPathUnlock(ctx.session)
  },
  // feature_kb_akb: g.kb gate's `session_flag(kb_consulted)` predicate. Set by
  // kbTrack on any omt_kb_nav op call (nav_gate.ts); guards src/ edit-tools.
  // feature_088 T2-5: per-file Read-recency exemption — a recent Read of the
  // SAME rel satisfies g.kb for THAT file only (NOT a session-wide unlock).
  // Order: session flag → fast-path → sticky → recent-read (cheapest first;
  // recent-read is a Map lookup, no ledger I/O). Never-read files still block.
  kb_consulted: (ctx) => {
    const s = ctx.session ? ctx.env.state.kb.get(ctx.session) : undefined
    return !!s?.consulted ||
      hasFastPathUnlock(ctx.session) ||
      // meta_harness_7 P0-3 kb_sticky_per_feature: a kb_consult record for the
      // active feature (majors: same scope) satisfies g.kb across sessions.
      hasStickyKbConsult(ctx.session) ||
      hasRecentRead(ctx.env.state.reads, ctx.session, ctx.rel)
  },
}

function ledgerHas(ctx: GateCtx, arg: string, ir: any): boolean {
  // ledger_has(kind,k=v,window) — window may be a @var ref (numeric in IR vars)
  const [kind, kv, win] = arg.split(",").map((s) => s.trim())
  const winVar = (win || "").match(/^@var\.([a-z0-9_]+)$/)
  const windowMs = winVar ? Number(ir?.vars?.[winVar[1]]) : Number(win)
  const [k, v] = (kv || "").split("=").map((s) => s.trim())
  const now = Date.now()
  return readLedger().some((r) => {
    if (r.kind !== kind) return false
    if (k && String(r[k] ?? "") !== v) return false
    if (ctx.session && r.session === ctx.session) return true
    const t = Date.parse(r.ts || "")
    return !Number.isNaN(t) && now - t < (windowMs || UNLOCK_WINDOW_MS)
  })
}

function evalPred(call: string, ctx: GateCtx, ir: any): boolean {
  const m = call.match(/^(!?)\s*([a-z_][a-z0-9_]*)\s*\((.*)\)\s*$/)
  if (!m) return true // unevaluable → fail open (never brick a session)
  const [, neg, name, argStr] = m
  const arg = argStr.trim().replace(/^"(.*)"$/, "$1")
  let out: boolean
  switch (name) {
    case "path_in":
      out = ctx.rel !== null && pathIn(ctx.rel, argStr.trim(), ir)
      break
    case "file_has": {
      if (!ctx.abs || !existsSyncSafe(ctx.abs)) { out = false; break }
      out = arg === "TA:"
        ? memo(ctx, `file_has:TA:${ctx.abs}`, () => fileThoughtsIn(ctx.abs!).length > 0)
        : memo(ctx, `file_has:${arg}:${ctx.abs}`, () =>
            readFileSyncSafe(ctx.abs!).includes(arg))
      break
    }
    case "session_flag":
      out = SESSION_FLAGS[arg]?.(ctx) ?? false
      break
    case "ledger_has":
      out = ledgerHas(ctx, argStr, ir)
      break
    case "receipt_fresh":
      out = !!ctx.rel && !!ctx.abs && omtHarnessE2eStatus(ctx.rel, ctx.abs).ok
      break
    case "risk_high":
      out = !!ctx.rel && readThoughtsIndex().some((r) =>
        r.path === ctx.rel && r.category === "risk")
      break
    case "cmd_match": {
      const cmd = String(ctx.output?.args?.command ?? "")
      out = !!cmd && (ir?.deny ?? []).some((d: any) =>
        d.scope === "bash" && globToRegex(d.match).test(cmd))
      break
    }
    case "fsm_allows":
      // Generic-gate evaluation of the TDD hats is not supported — the
      // specialized impls (g.tests/g.phase) own TDD deferral. Fail open.
      ctx.env.safeLog("warn", `pred fsm_allows has no generic evaluator (gate ${call})`)
      out = true
      break
    default:
      ctx.env.safeLog("warn", `unknown @pred '${name}' — failing open`)
      out = true
  }
  return neg === "!" ? !out : out
}

function memo(ctx: GateCtx, key: string, fn: () => boolean): boolean {
  if (!ctx.memo.has(key)) ctx.memo.set(key, fn())
  return ctx.memo.get(key)!
}

function existsSyncSafe(p: string): boolean {
  try { return existsSync(p) } catch { return false }
}

function readFileSyncSafe(p: string): string {
  try { return readFileSync(p, "utf8") } catch { return "" }
}

function evalPredExpr(expr: string, ctx: GateCtx, ir: any): boolean {
  // when=/requires= are single pred calls in HDL-1 (optionally !-negated).
  return evalPred(expr, ctx, ir)
}

// --- specialized impls (the remainder the DSL does not express) --------------

type GateImpl = (gate: any, ctx: GateCtx) => Promise<void | "stop">

const IMPLS: Record<string, GateImpl> = {
// TA: risk: risk (feature_050 wrap-up @ .sandbox/pause_2026-09-05c.md): (1) g.net impl carries a // DEBUG block writing /tmp/gate_debug.log — remove with its require("node:fs"); (2) .omt @gate g.net skip_ok=true contradicts TS fallback skip_ok:false + design_001 — IR is the functional source so ANY session skip bypasses the net gate; fix .omt to skip_ok=false (break-glass scope=all only, net_enforced_harness D3) + harnessc rebuild
  // feature_020: block doc-scoped searches until a nav tool was used.
  "g.nav": async (_gate, ctx) => {
    if (!ctx.session) return
    const state = ctx.env.state.nav.get(ctx.session)
    const decision = navGateDecision({
      tool: ctx.tool,
      targetRel: ctx.rel,
      usedNav: state?.usedNav ?? false,
      // feature_054 C2: a bug_fix/test phase record satisfies the nav gate
      // too (impl-owned — this impl never evaluates requires=).
      navUnlock: hasNavUnlock(ctx.session) || hasFastPathUnlock(ctx.session),
    })
    if (decision === "block") {
      ctx.env.safeLog("warn", `Session ${ctx.session}: blocked ${ctx.tool} (doc search '${ctx.rel || "repo"}') without prior navigation`)
      // meta_harness_7 P0-4 (feature_061.nav_cache_hit): append what the nav
      // index already knows about the query — message-only; null = the denial
      // stays byte-identical to the pre-P0-4 text (no policy change).
      const hint = navCacheHint(ctx.output)
      throw new OmtBlock(`⛔ OMT++ gate: ${gateMsg("nav_required")}` + (hint ? `\n${hint}` : ""))
    }
  },
  // AGENTS.md NEVER paths; .env* hard, README/uv.lock/LICENSE via scope=all.
  "g.protect": async (_gate, ctx) =>
    (await guardProtectedPath(ctx.env, ctx.session, ctx.rel!)) ? "stop" : undefined,
  // Harness-surface second-edit guard (per-file git-dirty + mtime vs receipt).
  "g.receipt": async (_gate, ctx) => { await guardHarnessReceipt(ctx.rel!, ctx.abs!) },
  // tests/ canary (TDD-hat deferral inside); tests/ edits stop the chain.
  "g.tests": async (_gate, ctx) => {
    await guardTestsPath(ctx.env, ctx.session, ctx.rel!)
    return "stop"
  },
  // src/ phase + §12 artifact gate (+ TDD two-hats + snapshots inside).
  "g.phase": async (_gate, ctx) => { await guardSrcPath(ctx.env, ctx.session, ctx.rel!, ctx.abs!) },
  // Thought-carrying files need a per-file omt_think{op:list} consult (not skip-able).
  "g.think": async (_gate, ctx) => { await guardThoughts(ctx.env, ctx.session, ctx.rel!, ctx.abs!) },
  // KB consult gate: src/ edits need prior omt_kb_nav consult (genericImpl handles requires=).
  "g.kb": undefined,
  // feature_050.net_as_gate: net permission-to-act gate (Alt A Net-as-Gate).
  // Runs after g.tests:30, before g.phase:40. Calls Python net.gate helper.
  // feature_053 C1 @pred net_marking(active>1): solo sessions skip the shell
  // entirely and revert to phase-gate only — the gate engages only under real
  // concurrency (2+ active works). Unreadable bundle → engage (fail-closed;
  // solo must be proven, never assumed). Python net/gate.is_concurrent is the
  // authority for the shell path; this fs-read mirrors it for the fast path.
  "g.net": async (_gate, ctx) => {
    const abs = ctx.abs || ""
    const rel = ctx.rel || ""
    if (!abs || !rel) return
    // Only gate src/, tests/, and harness-surface paths.
    const isSrc = rel.startsWith("src/")
    const isTests = rel.startsWith("tests/")
    const isHarness = rel.startsWith(".opencode/") || rel.startsWith("scripts/omt/")
    if (!isSrc && !isTests && !isHarness) return
    // T4-1 (feature_072): activation + exception via ONE typed evaluator
    // (policy_decision.evaluatePolicy) — shared with preflight/explain.
    // Solo → skip to phase-gate only (C1); valid break-glass scope=all →
    // allow pre-shell; concurrent otherwise → live shell-out decides.
    // Unreadable bundle engages (fail-closed; solo must be proven).
    const marking = ((): { work_active: number; activeHolders: string[] } | null => {
      try {
        const dir = (typeof process !== "undefined" && (process as any)?.env?.OMT_NET_DIR)
          || `${ctx.env.directory}/.meta/.omt`
        const sidecar = JSON.parse(readFileSync(`${dir}/net_state.sidecar.json`, "utf8"))
        const live: unknown = (sidecar as any)?.live_marking
        if (!Array.isArray(live)) return null
        let order: string[] = []
        try {
          const netJson = JSON.parse(readFileSync(`${dir}/META_NET.petri.json`, "utf8"))
          order = Array.isArray((netJson as any)?.places)
            ? (netJson as any).places.map((p: any) => String(p?.name ?? ""))
            : []
        } catch { return null }
        const byName: Record<string, number> = {}
        order.forEach((name, i) => { byName[name] = Number((live as any[])[i] ?? 0) })
        return {
          work_active: byName["work_active"] ?? 0,
          activeHolders: Object.keys(byName).filter((k) => /^f\d+_active$/.test(k) && (byName[k] ?? 0) > 0),
        }
      } catch { return null }
    })()
    const verdict = evaluatePolicy({
      gate: "g.net", session: ctx.session, nowMs: Date.now(),
      records: readLedger(), netMarking: marking,
    })
    if (verdict.via === "activation_solo_skip") return
    if (verdict.via === "exception_break_glass") return
    // Dry-run / synthetic ctx: V2 preflight sets env.dryRun; V1-era probes
    // (split_proof E2, bench) construct env with `$: {}` (non-function) to
    // mark synthetic contexts — preserve that skip so hermetic probes never
    // shell out (V1: `typeof env.$ !== "function"`).
    if ((ctx.env as any).dryRun) return
    if ("$" in (ctx.env as any) && typeof (ctx.env as any).$ !== "function") return
    // Call net.gate to check permission (V2: node:child_process).
    let data: any = { allowed: false, code: "ERR_NET_NOT_ENABLED" }
    try {
      const { execFileSync: _exec } = await import("node:child_process")
      const out = _exec("uv", ["run", "scripts/omt/net_check.py", "gate", "--path", rel, "--session", ctx.session || ""], {
        cwd: ctx.env.directory, encoding: "utf8", timeout: 30000,
        stdio: ["ignore", "pipe", "ignore"],
      } as any)
      data = JSON.parse(String(out || '{"allowed":false,"code":"ERR_NET_NOT_ENABLED"}'))
    } catch (e: any) {
      const stdout = String((e as any)?.stdout || "").trim()
      if (stdout) {
        try { data = JSON.parse(stdout) } catch { /* keep default deny */ }
      }
    }
    if (!data.allowed) throw new OmtBlock(`⛔ OMT++ gate (g.net): ${data.message || data.code}`)
  },
  // feature_138 E2: split-proof membrane advisory (Oracle `split_proof` v2,
  // V7 §E). Pure over the preflight snapshot + pinned certs + ledger chain:
  // NEVER shells out, never runs the suite. Fail-open locally (advisory
  // notify), fail-closed in CI (CI=1/true/yes). Break-glass scope=all
  // bypasses (audited emergency, mirrors g.net). Missing/stale/tampered
  // certs advise; only a fresh clean chain is silent. Trust split: this gate
  // is a freshness signal — CI re-proves from scratch (the authority); the
  // cert_sha recompute + chain-row presence below both fail SAFE (any
  // recompute/format doubt degrades to advisory, never to a silent pass).
  "g.split_proof": async (_gate, ctx) => {
    const rel = ctx.rel || ""
    if (!rel) return
    const unlock = getActiveUnlock(ctx.session)
    if (unlock?.type === "skip" && (unlock as any)?.record?.scope === "all") return
    const dir = ctx.env.directory || ""
    const meta = `${dir}/.meta/.omt`
    const shaHex = (s: string): string => createHash("sha256").update(s, "utf8").digest("hex")
    // Mirror of split_proof.GENESIS_SHA (sha256 of the empty chain): intact
    // by checkCertShaTs first, so GENESIS always means "cut against an empty
    // chain" (row 0). A live cert never carries it (real ledger never empty).
    const GENESIS_TS = shaHex("")
    let ledgerRaw = ""
    try { ledgerRaw = readFileSync(`${meta}/ledger.jsonl`, "utf8") } catch { ledgerRaw = "" }
    const ledgerLines = ledgerRaw.split("\n").filter((l) => l.length > 0)
    // Mirror of split_proof._ledger_prefix_match (append-only growth): row
    // count K whose K-line prefix sha matches, else null.
    const prefixRows = (want: string): number | null => {
      if (shaHex(ledgerRaw) === want) return ledgerLines.length
      if (want === GENESIS_TS) return 0
      let acc = ""
      for (let i = 0; i < ledgerLines.length; i++) {
        acc += ledgerLines[i] + "\n"
        if (shaHex(acc) === want) return i + 1
      }
      return null
    }
    // Mirror of split_proof.check_cert_sha (LOCKED field order, compact
    // separators, ASCII payloads): any doubt → false → advisory, never pass.
    const LOCKED_TS = ["oracle", "lane", "file_rev", "live_rev", "ledger_sha",
      "firewall_verdict", "ta_ast_hash", "newcomer", "tokens_ms", "cert_sha"]
    const checkCertShaTs = (c: any): boolean => {
      try {
        for (const f of LOCKED_TS) if (c[f] === undefined) return false
        const canon = "{" + LOCKED_TS.filter((f) => f !== "cert_sha")
          .map((f) => JSON.stringify(f) + ":" + JSON.stringify(c[f])).join(",") + "}"
        return shaHex(canon) === c.cert_sha
      } catch { return false }
    }
    const strict = ["1", "true", "yes"].includes(
      String((process as any)?.env?.CI ?? "").toLowerCase())
    const clearing = "clear: uv run scripts/omt/split_proof.py prove --lane both --out .meta/.omt (pins fresh certs + chain rows)"
    const advise = async (why: string): Promise<void> => {
      const base = `${gateMsg("split_proof", { rel })} — ${why}. ${clearing}`
      if (strict) throw new OmtBlock(`⛔ OMT++ gate (g.split_proof): ${base}`)
      ctx.env.safeLog("warn", `g.split_proof advisory: ${why} (${rel})`)
      await ctx.env.notify(`⚠️ OMT++ gate (g.split_proof, advisory — local edits never block): ${base}`)
    }
    const certs: any[] = []
    for (const lane of ["product", "harness"]) {
      try {
        certs.push(JSON.parse(readFileSync(`${meta}/split_proof_${lane}.cert.json`, "utf8")))
      } catch { continue }
    }
    if (!certs.length) {
      await advise("no pinned split_proof certs (.meta/.omt/split_proof_{product,harness}.cert.json)")
      return
    }
    for (const c of certs) {
      const lane = String(c?.lane ?? "?")
      if (c?.oracle !== "split_proof/v1" || c?.firewall_verdict !== "clean") {
        await advise(`lane ${lane}: verdict '${c?.firewall_verdict ?? "unreadable"}' (want clean)`)
        return
      }
      if (!checkCertShaTs(c)) {
        await advise(`lane ${lane}: cert_sha recompute mismatch (tamper/drift)`)
        return
      }
      if (prefixRows(String(c.ledger_sha ?? "")) === null) {
        await advise(`lane ${lane}: ledger advanced past the cut (re-prove for a fresh chain link)`)
        return
      }
      let chained = false
      for (const ln of ledgerLines) {
        try {
          const r = JSON.parse(ln)
          if (r?.kind === "split_proof.cert" && r?.cert_sha === c.cert_sha) { chained = true; break }
        } catch { continue }
      }
      if (!chained) {
        await advise(`lane ${lane}: no split_proof.cert chain row for this cert`)
        return
      }
    }
  },
}

// Generic impl: a before-gate with NO registered impl is fully pred-composed —
// requires= fails → block (or warn) with the IR msg text. skip_ok honors a
// logged omt_skip (any scope) as the escape hatch.
async function genericImpl(gate: any, ctx: GateCtx): Promise<void> {
  const ir = loadIr()
  if (gate.requires && evalPredExpr(gate.requires, ctx, ir)) return
  if (gate.skip_ok && getActiveUnlock(ctx.session)?.type === "skip") return
  const text = gateMsg(String(gate.msg ?? gate.id), { rel: ctx.rel })
  if (!gate.hard) {
    await ctx.env.notify(`⚠️ OMT++ gate (${gate.id}): ${text}`)
    return
  }
  throw new OmtBlock(`⛔ OMT++ gate (${gate.id}): ${text}`)
}

// IR-missing fallback (never die open): mirrors .meta/META_HARNESS.omt @gate
// order/tools — keep in sync; verify-projections + the IR pins make drift a
// build error long before this path runs.
const FALLBACK_GATES = [
  { id: "g.nav", on: "before", tools: "grep|glob|rg|find", when: "path_in(@var.doc_paths)", requires: "", msg: "nav_required", hard: true, skip_ok: true, order: 0 },
  { id: "g.protect", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(@protect.*)", requires: "", msg: "protect_file", hard: true, skip_ok: true, order: 10 },
  { id: "g.receipt", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(@var.harness_paths)", requires: "receipt_fresh()", msg: "receipt_stale", hard: true, skip_ok: false, order: 20 },
  { id: "g.tests", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(tests/)", requires: "", msg: "tests_canary", hard: true, skip_ok: true, order: 30 },
  { id: "g.net", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(@var.net_paths)", requires: "", msg: "net_required", hard: true, skip_ok: false, order: 35 },
  { id: "g.split_proof", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(@var.harness_paths)", requires: "", msg: "split_proof", hard: false, skip_ok: false, order: 37 },
  { id: "g.phase", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(src/)", requires: "", msg: "no_phase", hard: true, skip_ok: true, order: 40 },
  { id: "g.think", on: "before", tools: "edit|write|patch|multiedit", when: 'file_has("TA:")', requires: "", msg: "think_gate", hard: true, skip_ok: false, order: 50 },
  { id: "g.kb", on: "before", tools: "edit|write|patch|multiedit", when: "path_in(src/)", requires: "session_flag(kb_consulted)", msg: "kb_required", hard: true, skip_ok: false, order: 55 },
]

// Composition-root entry point (HDL-2): run every IR before-gate in order=.
// rawEditPath: the before-hook filePath (output.args per the SDK contract —
// the caller keeps the BUG-A pin literal); search tools get their scope from
// getSearchPath instead.
export async function runBeforeGates(
  env: EnforcerEnv,
  session: string | undefined,
  input: any,
  output: any,
  rawEditPath: string | null,
): Promise<void> {
  const ir = loadIr()
  const gates = (Array.isArray(ir?.gates) && ir.gates.length ? ir.gates : FALLBACK_GATES)
    .filter((g: any) => g.on === "before")
    .sort((a: any, b: any) => a.order - b.order)
  const tool = input?.tool ?? ""
  let rel: string | null = null
  let abs: string | null = null
  if (rawEditPath) {
    ({ abs, rel } = relOf(rawEditPath))
  } else {
    rel = getSearchPath(output)
  }
  const ctx: GateCtx = { env, session, tool, input, output, rel, abs, memo: new Map() }
  // feature_099 S2 (F03): obligations compose — a "stop" (g.protect override /
  // g.tests) no longer suppresses unrelated later gates on the live path. The
  // chain evaluates every applicable gate (dry-path continue-all contract);
  // the first OmtBlock still refuses the edit. A pure-stop chain still returns
  // without throwing (same allow semantics), but nothing is silently skipped.
  let stopped = false
  for (const gate of gates) {
    const tools = String(gate.tools ?? "").split("|").filter(Boolean)
    if (tools.length && !tools.includes(tool)) continue
    // when= pre-filter: decisive only for a known non-null target (a null/whole-
    // repo target stays with the impl, matching the pre-HDL-2 semantics).
    if (rel !== null && gate.when && !evalPredExpr(gate.when, ctx, ir)) continue
    const impl = IMPLS[gate.id] ?? genericImpl
    if ((await impl(gate, ctx)) === "stop") stopped = true
  }
  void stopped
}

// Phase-A interrogative layer (feature_026.omt_q_interrogative_first_ops):
// a dryRun variant of the before-chain that captures OmtBlock per-gate and
// returns decision rows instead of throwing. The existing runBeforeGates is
// byte-identical — real edits still throw OmtBlock as today; this sibling is
// omt_q{op:plan}'s "predict what would block" path. NEVER used by the real
// composition root (runBeforeGates remains the throw path).
export type GateDecision = {
  gate_id: string
  blocked: boolean
  msg: string
  skip_ok: boolean
  // feature_055 A4 gate_preflight: fired=false → when= did not match (the
  // gate is not applicable to this target — a "will fire" projection must
  // distinguish miss from pass); stop=true → this gate halted the chain
  // (g.protect override / g.tests) so later gates never evaluated. Both
  // optional: omt_q's predicted_chain mapping (gate_id/blocked/msg/skip_ok)
  // is unchanged.
  fired?: boolean
  stop?: boolean
}

// feature_077 (T1-4): optional irOverride lets omt_q{op:plan, as_of:<commit>}
// replay the gate set as of a past commit (loadIrAt); live callers pass
// nothing and behavior is byte-identical.
export async function runBeforeGatesDry(ctx: GateCtx, irOverride?: any): Promise<GateDecision[]> {
  const ir = irOverride ?? loadIr()
  const gates = (Array.isArray(ir?.gates) && ir.gates.length ? ir.gates : FALLBACK_GATES)
    .filter((g: any) => g.on === "before")
    .sort((a: any, b: any) => a.order - b.order)
  const decisions: GateDecision[] = []
  const tool = ctx.tool
  for (const gate of gates) {
    const tools = String(gate.tools ?? "").split("|").filter(Boolean)
    if (tools.length && !tools.includes(tool)) continue
    if (ctx.rel !== null && gate.when && !evalPredExpr(gate.when, ctx, ir)) {
      decisions.push({ gate_id: gate.id, blocked: false, msg: "", skip_ok: !!gate.skip_ok, fired: false })
      continue
    }
    const impl = IMPLS[gate.id] ?? genericImpl
    try {
      const r = await impl(gate, ctx)
      decisions.push({
        gate_id: gate.id, blocked: false, msg: "", skip_ok: !!gate.skip_ok, fired: true,
        ...(r === "stop" ? { stop: true } : {}),
      })
      if (r === "stop") break
    } catch (e) {
      if (e instanceof OmtBlock) {
        decisions.push({
          gate_id: gate.id,
          blocked: true,
          msg: e.message,
          skip_ok: !!gate.skip_ok,
          fired: true,
        })
        // dryRun never propagates — capture and continue (so the agent sees
        // ALL before-gates that would fire, not just the first blocker).
        continue
      }
      throw e // non-OmtBlock errors are real failures — propagate
    }
  }
  return decisions
}

// --- after-gates (improvement007 R7 / OPT-F): data-driven like the before-chain
//
// The root's after-hook keeps composition-only concerns (session bootstrap,
// read-time thought injection, the raw/null path guard); the edit-tools and
// src/**.py filters that used to live there are exactly the gates' tools=/
// when= attrs. g.mvc's "lint failed ⇒ skip the TDD after-edit" sequencing
// falls out of order= 60<70 plus the before-chain's "stop" adapter contract.
// OmtBlock (mvc hard violation, tdd revert) propagates to the root un-caught
// — the pre-R7 root's posture.

type AfterImpl = (gate: any, ctx: GateCtx) => Promise<void | "stop">

const AFTER_IMPLS: Record<string, AfterImpl> = {
  // MVC++ delta gate: throws on NEW hard violations; false ⇒ the lint itself
  // failed → stop the chain (skip g.tdd_after), the monolith's early return.
  "g.mvc": async (_gate, ctx) =>
    (await mvcAfterEdit(ctx.env, ctx.abs!, ctx.rel!)) === false ? "stop" : undefined,
  // TDD after-edit: advisory + REFACTOR revert check (ir.hats via R5).
  "g.tdd_after": async (_gate, ctx) => {
    await tddAfterEdit(ctx.env, ctx.input, ctx.abs!, ctx.rel!)
  },
}

// IR-missing fallback (never die open): mirrors the .omt after-gates on the
// FIELDS the driver consumes; requires=/run= stay impl-owned (excluded).
const FALLBACK_AFTER_GATES = [
  { id: "g.mvc", on: "after", tools: "edit|write|patch|multiedit", when: "path_in(src/**/*.py)", msg: "mvc_new_hard", hard: true, skip_ok: false, order: 60 },
  { id: "g.tdd_after", on: "after", tools: "edit|write|patch|multiedit", when: "path_in(src/)", msg: "tdd_revert", hard: false, skip_ok: false, order: 70 },
]

// Composition-root entry point: run every IR after-gate in order=. Every
// after-gate is edit-targeted — a null rawEditPath means nothing to do (the
// root keeps the raw/null guard; this is belt-and-braces for direct calls).
export async function runAfterGates(
  env: EnforcerEnv,
  session: string | undefined,
  input: any,
  output: any,
  rawEditPath: string | null,
): Promise<void> {
  if (!rawEditPath) return
  const ir = loadIr()
  const gates = (Array.isArray(ir?.gates) && ir.gates.length ? ir.gates : FALLBACK_AFTER_GATES)
    .filter((g: any) => g.on === "after")
    .sort((a: any, b: any) => a.order - b.order)
  const tool = input?.tool ?? ""
  const { abs, rel } = relOf(rawEditPath)
  const ctx: GateCtx = { env, session, tool, input, output, rel, abs, memo: new Map() }
  for (const gate of gates) {
    const tools = String(gate.tools ?? "").split("|").filter(Boolean)
    if (tools.length && !tools.includes(tool)) continue
    // when= pre-filter: same semantics as the before-chain (always decisive
    // here — rel is non-null past the rawEditPath guard above).
    if (gate.when && !evalPredExpr(gate.when, ctx, ir)) continue
    const impl = AFTER_IMPLS[gate.id]
    if (!impl) {
      // No generic after-impl: after semantics (run= deltas, fsm reverts) are
      // impl-owned by definition — fail open, never brick the after-hook.
      env.safeLog("warn", `after-gate ${gate.id} has no registered impl — skipped (fail open)`)
      continue
    }
    if ((await impl(gate, ctx)) === "stop") return
  }
}

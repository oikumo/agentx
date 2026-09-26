// Reason Check — Tier-1 advisory pilot for harness.reason.
// Non-harness on purpose: filename has NO `omt_` prefix so it stays OUTSIDE
// `.meta/META_HARNESS.omt` @var harness_paths (exact/prefix) + e2e receipt guard.
// Small non-harness cost only: one `reason_check: allow` line in opencode.jsonc
// OUTSIDE the harnessc perm blocks; no @tool row, no harnessc build, no receipt.
//
// Closed op enum check|explain|compare|concretize (plan WITHHELD until stage 2).
// Thin proxy to `uv run scripts/reason/check.py` with per-op argv whitelist
// mirroring the Python subparsers plus pinned arg tests. TS-layer advisory guard
// rejects any op spelling that would write net/ledger state, move tokens, or mint
// grants before argv is even built. Output is the §5 envelope (≤ ~2KB summaries).
// TA: why: `reason_check` (no omt_ prefix) stays outside harness registry churn like `reason_table` — advisory JSON only, never throws the session, never touches net/ledger/src.

import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"
import { join, isAbsolute, resolve as resolvePath } from "node:path"

const OPS = ["check", "explain", "compare", "concretize"] as const
type Op = (typeof OPS)[number]

// Per-op argv whitelist — mirrors scripts/reason/check.py subparsers exactly.
const ALLOW: Record<Op, string[]> = {
  check: ["--program", "--context", "--contract"],
  explain: ["--program", "--node", "--context", "--contract"],
  compare: ["--program-a", "--program-b", "--contract"],
  concretize: ["--row", "--bound"],
}

const CONTRACTS = ["files-only-v1", "completion-relevant-v1"]
const PROTECTED = [/\.env($|\.)/, /(^|\/)uv\.lock$/, /(^|\/)README\.md$/, /(^|\/)LICENSE$/]

function advisoryFail(reason: string) {
  return { title: "Reason Check", output: `CHECK: unknown (reason: ${reason})`, metadata: { agent: { ok: false, reason } } } as any
}

function guard(op: string, args: Record<string, string>, root: string): string | null {
  if (!(OPS as readonly string[]).includes(op)) {
    return `unknown op ${JSON.stringify(op)}; closed enum check|explain|compare|concretize (plan withheld)`
  }
  const allowed = ALLOW[op as Op]
  for (const k of Object.keys(args)) {
    const flag = k.startsWith("--") ? k : `--${k}`
    if (!allowed.includes(flag)) return `flag ${flag} not whitelisted for op ${op} (allowed: ${allowed.join(", ")})`
  }
  const vals = Object.values(args).join(" ")
  if (/net_rev|ledger|grant|lease|mint|token.*move|fire\(|claim/i.test(vals) && /write|move|mint|fire|claim/i.test(vals)) {
    return "advisory guard: check/compare never write net/ledger, move tokens, or mint grants"
  }
  for (const v of Object.values(args)) {
    for (const re of PROTECTED) {
      if (re.test(v)) return `protected path refused: ${v}`
    }
    if (v.includes(";") && (v.includes("rm ") || v.includes("&&") || v.includes("|"))) {
      return `shell interpolation refused in arg: ${v.slice(0, 60)}`
    }
  }
  if (op === "compare" && args["contract"] && !(CONTRACTS as readonly string[]).includes(args["contract"])) {
    // Unknown contracts are advisory-unknown, not a guard reject — let Python answer unknown.
  }
  if (op === "concretize" && args["bound"]) {
    const b = Number(args["bound"])
    if (!Number.isInteger(b) || b < 1 || b > 64) return `bound must be int 1..64 (got ${args["bound"]})`
  }
  // Resolve program paths inside repo root only.
  for (const k of ["program", "program-a", "program-b"]) {
    const flag = k === "program" ? "--program" : `--${k}`
    const v = (args as any)[k] ?? (args as any)[flag]
    if (typeof v === "string" && v && !v.trim().startsWith("{") && !v.trim().startsWith("[")) {
      const p = isAbsolute(v) ? v : join(root, v)
      const rel = resolvePath(p).startsWith(resolvePath(root)) ? "ok" : "outside"
      if (rel !== "ok") return `program path outside repo root refused: ${v}`
    }
  }
  return null
}

function toArgv(op: Op, args: Record<string, string>): string[] {
  const out: string[] = [op]
  for (const flag of ALLOW[op]) {
    const key = flag.replace(/^--/, "")
    const v = (args as any)[key] ?? (args as any)[flag]
    if (v !== undefined && v !== "") out.push(flag, String(v))
  }
  return out
}

function renderPlain(op: string, env: any): string {
  if (!env || typeof env !== "object") return `CHECK: unknown (reason: empty envelope)`
  if (env.ok === false) return `CHECK: unknown (reason: ${env.reason || "proxy error"})`
  if (env.slice) {
    const s = env.slice
    if (s.verdict === "unknown") return [`SLICE ${s.node}:`, `- unknown (${s.reason}); acquire: ${s.next_obligation}`, `- ref: ${s.detail_ref}`].join("\n")
    const f = s.first_unsupported || {}
    return [`SLICE ${s.node}:`, `- first unsupported: ${f.code || "?"} (exp ${f.expected || "?"} vs obs ${f.observed || "?"})`, `- via: ${f.via || "?"}; acquire: ${f.next_obligation || "?"}`, `- ref: ${s.detail_ref}`].slice(0, 15).join("\n")
  }
  if (env.verdict) {
    const w = env.witness ? ` witness=${JSON.stringify(env.witness)}` : ""
    const r = env.reason ? ` reason=${env.reason}` : ""
    return [`COMPARE: ${env.verdict} (contract=${env.contract || "?"})${r}${w}`, env.detail_ref ? `- ref: ${env.detail_ref}` : `- next: ${env.next_obligation || "none"}`].join("\n")
  }
  if (env.realizations) {
    return [`CONCRETIZE: ${env.count} realizations [${(env.distinguishing_info || []).join(", ")}]`, ...env.realizations.slice(0, 4).map((o: any) => `- ${JSON.stringify(o)}`), env.detail_ref ? `- ref: ${env.detail_ref}` : `- budget ok`].slice(0, 15).join("\n")
  }
  const d = env.data || env.summary || {}
  const lines = [`CERT: structural=${d.structural || "?"} premises=${d.premises || "?"} execution=${d.execution || "?"} goal=${d.goal || "?"}`, `- program: ${d.program_digest || "?"} ctx: ${d.context_id || "?"}`]
  for (const i of (d.issues || []).slice(0, 3)) lines.push(`- issue ${i.node}: ${i.code} (exp ${i.expected} vs obs ${i.observed}); acquire: ${i.next_obligation}`)
  for (const u of (d.unknowns || []).slice(0, 3)) lines.push(`- unknown ${u.node}: ${u.reason} need=${u.needed}`)
  lines.push(`- digest: ${d.certificate_digest || "?"}${env.detail_ref ? ` ref: ${env.detail_ref}` : ""}`)
  return lines.slice(0, 30).join("\n")
}

function createReasonCheckTool(root: string) {
  return tool({
    description: "Tier-1 advisory pilot. OUTPUT (user-only): CERT/SLICE/COMPARE/CONCRETIZE plain lines (≤2KB) + detail_ref. METADATA.agent: full envelope. Args: op=check|explain|compare|concretize (plan withheld), program/programA/programB/row/node/contract/bound/context.",
    args: {
      op: tool.schema.string().describe("closed enum: check|explain|compare|concretize (plan withheld)"),
      program: tool.schema.string().optional().describe("PATH under .sandbox/harness_reason or raw JSON (check/explain)"),
      programA: tool.schema.string().optional().describe("first program (compare)"),
      programB: tool.schema.string().optional().describe("second program (compare)"),
      row: tool.schema.string().optional().describe("JSON e.g. '{\"row\":\"d3\"}' (concretize)"),
      node: tool.schema.string().optional().describe("node/obligation ID (explain)"),
      contract: tool.schema.string().optional().describe("files-only-v1|completion-relevant-v1 (compare/check)"),
      bound: tool.schema.string().optional().describe("int 1..64 (concretize)"),
      context: tool.schema.string().optional().describe("context id (check/explain)"),
    },
    async execute(args) {
      const a = (args as any) || {}
      const op = String(a.op || "")
      const kv: Record<string, string> = {}
      for (const [k, v] of Object.entries({ program: a.program, "program-a": a.programA, "program-b": a.programB, row: a.row, node: a.node, contract: a.contract, bound: a.bound, context: a.context })) {
        if (typeof v === "string" && v !== "") {
          const flagKey = k === "program-a" || k === "program-b" ? k : k.replace(/^programA$/, "program-a").replace(/^programB$/, "program-b")
          kv[flagKey] = v
        }
      }
      // Normalize programA/programB aliases.
      if (a.programA && !kv["program-a"]) kv["program-a"] = String(a.programA)
      if (a.programB && !kv["program-b"]) kv["program-b"] = String(a.programB)
      const blocked = guard(op, kv, root)
      if (blocked) return advisoryFail(blocked)
      const argv = toArgv(op as Op, kv)
      const script = join(root, "scripts/reason/check.py")
      const r = spawnSync("uv", ["run", "--no-sync", script, ...argv], { encoding: "utf8", timeout: 30000, cwd: root })
      if (r.error) return advisoryFail(`proxy spawn failed: ${String((r.error as Error).message || r.error).slice(0, 200)}`)
      const out = String(r.stdout || "").trim() || String(r.stderr || "").trim()
      let env: any = null
      try { env = JSON.parse(out) } catch { return advisoryFail(`SSOT returned non-JSON (exit ${r.status}): ${out.slice(0, 200)}`) }
      const plain = renderPlain(op, env)
      const summary = JSON.stringify(env).length <= 2048 ? plain : `${plain}\n- detail_ref: ${(env as any).detail_ref || (env as any).data?.certificate_digest || "see envelope"}`
      return { title: "Reason Check", output: [`Reason check — Tier-1 advisory (${op}, plan withheld):`, ``, summary].join("\n"), metadata: { agent: { op, envelope: env } } } as any
    },
  })
}

export default async ({ directory, worktree }: { directory: string; worktree?: string }) => {
  const root = worktree ?? directory
  const reason_check = createReasonCheckTool(root)
  return {
    tool: { reason_check },
  }
}

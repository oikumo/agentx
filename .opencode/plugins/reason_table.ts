// Reason Table — Tier-0 prompt-side renderer for harness.reason artifacts.
// Non-harness on purpose: filename has NO `omt_` prefix so it stays OUTSIDE
// `.meta/META_HARNESS.omt` @var harness_paths (exact/prefix) + e2e receipt guard.
// No registry change, no opencode.jsonc perm change — pure formatter, stdlib only.
//
// Formats §2 programs (stage0_ir.json: Obs/D/A schemas, HarnessObs d1/d2/d3,
// DetailedD three-row, F preserves, aligned query, refresh compute) and §5
// certificates/summaries (structural/premises/execution/goal + digests +
// derivation, ≤2KB summary or detail_ref envelope, never truncation) plus UC8
// `explain` slices (minimal premise-to-conclusion, first unsupported connection)
// as plain text. Parses digests (`sha256:*`, `cert:sha256:*`) and `detail_ref`s.
// TA: why: `reason_table` (no omt_ prefix) avoids isOmtHarness + TOOL registry churn — new `omt_*` plugin would need @tool row + harnessc build + e2e receipt; template stays usable prompt-side with zero harness edits.

import { tool } from "@opencode-ai/plugin"
import { existsSync, readFileSync } from "node:fs"
import { join, isAbsolute } from "node:path"

type IrRow = { d: string; verdict?: string; [k: string]: any }
type CertIssue = { node?: string; code?: string; expected?: string; observed?: string; via?: string; next_obligation?: string; [k: string]: any }
type CertUnknown = { node?: string; reason?: string; needed?: string; [k: string]: any }

function tryParseJson(text: string): any | null {
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

function resolveInput(raw: string | undefined, root: string): string {
  if (!raw || !raw.trim()) return ""
  const t = raw.trim()
  // File path first (relative to repo root or absolute), then raw JSON string.
  const candidates = [t, join(root, t), join(root, ".sandbox/harness_reason", t)]
  for (const c of candidates) {
    try {
      if ((isAbsolute(c) || c.startsWith(root)) && existsSync(c)) {
        return readFileSync(c, "utf8")
      }
    } catch {
      /* fall through to raw string */
    }
  }
  // Also try .sandbox default for bare names like stage0_ir.json
  if (!t.startsWith("{") && !t.startsWith("[")) {
    const p = join(root, ".sandbox/harness_reason", t)
    try {
      if (existsSync(p)) return readFileSync(p, "utf8")
    } catch {
      /* raw string */
    }
  }
  return t
}

function parseDigest(ref: string): { kind: string; digest: string } | null {
  const t = (ref || "").trim()
  if (!t) return null
  let m = t.match(/^(cert:)?sha256:([0-9a-fA-F]+)$/)
  if (m) return { kind: m[1] ? "cert" : "sha256", digest: m[2] }
  m = t.match(/^detail_ref\s*[:=]\s*(.+)$/i)
  if (m) return parseDigest(m[1].trim())
  return null
}

function formatIR(ir: any): { lines: string[]; meta: any } {
  if (!ir || typeof ir !== "object") {
    return { lines: [`IR: unknown (reason: ill_typed_or_unparseable, provide stage0_ir.json)`], meta: { ir_ok: false } }
  }
  const lines: string[] = []
  const prog = ir.program || "unknown-program"
  const ver = ir.ir_version ?? "?"
  lines.push(`IR: ${prog} v${ver}`)
  const schemas = Array.isArray(ir.schemas) ? ir.schemas : []
  lines.push(`Schemas: ${schemas.map((s: any) => s?.name || "?").join(", ") || "(none)"}`)
  for (const s of schemas.slice(0, 6)) {
    const sorts = Array.isArray(s?.sorts) ? s.sorts.join("/") : "?"
    const arrows = Array.isArray(s?.arrows) ? s.arrows.map((a: any) => a?.name || "?").join(",") : "?"
    lines.push(`- ${s?.name}: sorts[${sorts}] arrows[${arrows}]`)
  }
  const models = Array.isArray(ir.models) ? ir.models : []
  for (const m of models) {
    const rows: IrRow[] = m?.tables?.rows || []
    if (m?.name === "HarnessObs") {
      const verdicts = rows.map((r) => `${r.d}=${r.verdict || "?"}`).join(" ")
      lines.push(`Model HarnessObs: ${verdicts || "(no rows)"}`)
      for (const r of rows.slice(0, 5)) {
        const fmt = (c: any) => (c && typeof c === "object" ? (c.just ? `just(${c.just})` : c.unknown ? `unknown(${c.unknown})` : JSON.stringify(c)) : String(c ?? "?"))
        lines.push(`- ${r.d}: source=${fmt((r as any).source)} recorded=${fmt((r as any).recorded)} current=${fmt((r as any).current_of_source)} -> ${r.verdict}`)
      }
    } else {
      lines.push(`Model ${m?.name || "?"}: ${rows.length} rows`)
      for (const r of rows.slice(0, 5)) {
        lines.push(`- ${r.d || "?"}: rec=${(r as any).recorded ?? "?"} cur=${(r as any).current_s ?? "?"} perm=${(r as any).perm ?? "?"} cover=${(r as any).cover ?? "?"} (${(r as any).note || r.verdict || ""})`)
      }
      if (m?.tables?.forget_projection) lines.push(`  forget: ${m.tables.forget_projection}`)
      if (m?.tables?.unit_check) lines.push(`  unit: ${m.tables.unit_check}`)
      if (m?.tables?.counit_check) lines.push(`  counit: ${m.tables.counit_check}`)
    }
  }
  const mappings = Array.isArray(ir.mappings) ? ir.mappings : []
  for (const mp of mappings.slice(0, 4)) {
    const pres = Array.isArray(mp?.preserves) ? mp.preserves.map((p: any) => p?.eq || "?").join(",") : "?"
    lines.push(`Mapping ${mp?.name || "?"}: ${mp?.from || "?"}->${mp?.to || "?"} preserves[${pres}] total=${mp?.totality ? "yes" : "?"}`)
  }
  const queries = Array.isArray(ir.queries) ? ir.queries : []
  for (const q of queries.slice(0, 4)) {
    if (q?.expected) {
      const e = q.expected
      lines.push(`Query ${q?.name}: Aligned[${(e.Aligned || []).join(",")}] Mismatched[${(e.Mismatched || []).join(",")}] Unresolved[${(e.Unresolved || []).join(",")}]`)
    } else {
      lines.push(`Query ${q?.name || "?"}: ${q?.kind || ""}`)
    }
  }
  const computes = Array.isArray(ir.computes) ? ir.computes : []
  for (const c of computes.slice(0, 4)) {
    lines.push(`Compute ${c?.name || "?"} in ${c?.in || "?"}: ${(c?.steps || []).join(" -> ")}`)
  }
  if (ir.round_trip_probe7) lines.push(`Probe7: ${ir.round_trip_probe7}`)
  // Budget: IR ≤40 lines.
  const trimmed = lines.slice(0, 40)
  const meta = { ir_ok: true, program: prog, schemas: schemas.length, models: models.length, truncated: lines.length > 40 }
  if (lines.length > 40) trimmed.push(`... (${lines.length - 40} more lines, see detail_ref)`)
  return { lines: trimmed, meta }
}

function normalizeCert(cert: any): any {
  if (!cert || typeof cert !== "object") return null
  // Full envelope {ok,data} or direct data or summary envelope {summary,detail_ref}.
  if (cert.data && typeof cert.data === "object") return { kind: "full", data: cert.data, ok: cert.ok }
  if (cert.summary && cert.detail_ref) return { kind: "summary", data: cert }
  if (cert.structural && cert.goal) return { kind: "full", data: cert, ok: true }
  return null
}

function formatCert(cert: any): { lines: string[]; meta: any } {
  const n = normalizeCert(cert)
  if (!n) {
    return { lines: [`CERT: unknown (reason: ill_typed_or_unparseable, need structural/premises/execution/goal)`], meta: { cert_ok: false } }
  }
  if (n.kind === "summary") {
    const s = n.data.summary || {}
    const lines = [
      `CERT summary: structural=${s.structural || "?"} goal=${s.goal || "?"} open_obligations=${s.open_obligations ?? "?"}`,
      `detail_ref: ${n.data.detail_ref}`,
      `note: ${n.data.note || "full certificate addressable by digest; summary is not the certificate"}`,
    ]
    return { lines, meta: { cert_ok: true, summary: true, detail_ref: n.data.detail_ref } }
  }
  const d = n.data
  const lines = [
    `CERT: structural=${d.structural || "?"} premises=${d.premises || "?"} execution=${d.execution || "?"} goal=${d.goal || "?"}`,
    `program=${d.program_digest || "?"} catalog=${d.catalog_version || "?"} model=${d.model_version || "?"} interp=${d.interpreter_version || "?"}`,
    `context=${d.context_id || "?"} contract=${d.observation_contract || "?"} unit_counit=${d.unit_counit || "?"}`,
  ]
  const issues: CertIssue[] = Array.isArray(d.issues) ? d.issues : []
  const unknowns: CertUnknown[] = Array.isArray(d.unknowns) ? d.unknowns : []
  lines.push(`Issues: ${issues.length} Unknowns: ${unknowns.length}`)
  for (const i of issues.slice(0, 6)) {
    lines.push(`- ${i.node || "?"}: ${i.code || "?"} exp=${i.expected || "?"} obs=${i.observed || "?"} via=${i.via || "?"} next=${i.next_obligation || "?"}`)
  }
  for (const u of unknowns.slice(0, 6)) {
    lines.push(`- ${u.node || "?"}: unknown(${u.reason || "?"}) need=${u.needed || "?"}`)
  }
  const deriv = Array.isArray(d.derivation) ? d.derivation : []
  for (const r of deriv.slice(0, 4)) {
    lines.push(`derive ${r.rule || "?"}: ${(r.inputs || []).join(",")} -> ${(r.outputs || []).join(",")}`)
  }
  lines.push(`digest: ${d.certificate_digest || "?"}`)
  // Summary budget check ≤2KB.
  const text = lines.join("\n")
  const meta: any = { cert_ok: true, issues: issues.length, unknowns: unknowns.length, bytes: text.length }
  let out = lines.slice(0, 30)
  if (text.length > 2048) {
    out = [
      `CERT summary: structural=${d.structural} goal=${d.goal} open_obligations=${issues.length + unknowns.length}`,
      `detail_ref: cert:${d.certificate_digest || "?"}`,
      `note: full certificate addressable by digest; summary is not the certificate`,
    ]
    meta.summary_fallback = true
  } else if (lines.length > 30) {
    out.push(`... (${lines.length - 30} more lines, see detail_ref)`)
    meta.truncated = true
  }
  return { lines: out, meta }
}

function explainSlice(cert: any, nodeId: string): { lines: string[]; meta: any } {
  const n = normalizeCert(cert)
  if (!n || n.kind !== "full") {
    return { lines: [`SLICE: unknown (reason: need full certificate + nodeId, got ${n?.kind || "none"})`], meta: { slice_ok: false } }
  }
  const d = n.data
  const id = (nodeId || "").trim()
  const issues: CertIssue[] = Array.isArray(d.issues) ? d.issues : []
  const unknowns: CertUnknown[] = Array.isArray(d.unknowns) ? d.unknowns : []
  const hitIssue = id ? issues.find((i) => i.node === id) : issues[0]
  const hitUnknown = id ? unknowns.find((u) => u.node === id) : undefined
  if (!id) {
    if (!hitIssue && unknowns.length === 0) return { lines: [`SLICE: no open obligations (goal=${d.goal})`], meta: { slice_ok: true, empty: true } }
  }
  if (id && !hitIssue && !hitUnknown) {
    return { lines: [`SLICE: unknown (reason: unknown_node_id ${id})`], meta: { slice_ok: false, unknown_node: true } }
  }
  const lines: string[] = []
  const target: any = hitIssue || hitUnknown
  lines.push(`SLICE ${target.node || id}:`)
  if (hitIssue) {
    lines.push(`- first unsupported: ${hitIssue.code} (exp ${hitIssue.expected} vs obs ${hitIssue.observed})`)
    lines.push(`- via: ${hitIssue.via || "?"}; acquire: ${hitIssue.next_obligation || "?"}`)
    lines.push(`- source: program ${d.program_digest || "?"} @ ${d.context_id || "?"}`)
  } else if (hitUnknown) {
    lines.push(`- unresolved: unknown(${(hitUnknown as CertUnknown).reason}) need=${(hitUnknown as CertUnknown).needed}`)
    lines.push(`- acquire: provide ${(hitUnknown as CertUnknown).needed || "missing value"} then re-check`)
  }
  lines.push(`- verdicts: structural=${d.structural} premises=${d.premises} execution=${d.execution} goal=${d.goal}`)
  const out = lines.slice(0, 15)
  return { lines: out, meta: { slice_ok: true, node: target.node } }
}

function renderReason(irText: string, certText: string, nodeId: string): { markdown: string; agent: any } {
  const ir = irText ? tryParseJson(irText) : null
  const cert = certText ? tryParseJson(certText) : null
  const irPart = irText ? formatIR(ir) : { lines: [`IR: (none — pass irJson as JSON string or path to stage0_ir.json)`], meta: { ir_ok: null } }
  const certPart = certText ? formatCert(cert) : { lines: [`CERT: (none — pass certJson as JSON string or path)`], meta: { cert_ok: null } }
  const slicePart = cert && (nodeId || (normalizeCert(cert)?.kind === "full"))
    ? explainSlice(cert, nodeId || (normalizeCert(cert)?.data?.issues?.[0]?.node) || "")
    : { lines: [`SLICE: (none — pass nodeId + certJson for UC8 explain)`], meta: { slice_ok: null } }

  const intro = `Reason table — Tier-0 prompt-side render of §2 IR + §5 cert + UC8 slice (plain lines, never truncation).`
  const markdown = [intro, ``, ...irPart.lines, ``, ...certPart.lines, ``, ...slicePart.lines].join("\n")
  const agent = {
    ir: irPart.meta,
    cert: certPart.meta,
    slice: slicePart.meta,
    reply_hint: `pass irJson/certJson/nodeId (paths under .sandbox/harness_reason/ resolve automatically)`,
  }
  return { markdown, agent }
}

function createReasonTableTool(root: string) {
  return tool({
    description: "Tier-0 prompt-side renderer. OUTPUT (user-only): INTRO + IR + CERT + SLICE plain lines, digest/detail_ref parsed. METADATA.agent: digests/verdicts/counts. Args: irJson, certJson, nodeId (JSON strings or repo-relative paths).",
    args: {
      irJson: tool.schema.string().optional().describe("§2 IR JSON string or path (e.g. .sandbox/harness_reason/stage0_ir.json)"),
      certJson: tool.schema.string().optional().describe("§5 certificate/summary JSON string or path (full cert or {summary,detail_ref} envelope)"),
      nodeId: tool.schema.string().optional().describe("UC8 explain node/obligation ID (e.g. accept_tests, d3)"),
    },
    async execute(args) {
      const a = args as any
      const irText = resolveInput(typeof a?.irJson === "string" ? a.irJson : "", root)
      const certText = resolveInput(typeof a?.certJson === "string" ? a.certJson : "", root)
      // detail_ref passthrough: if certJson is a bare digest ref, report parse.
      const maybeRef = typeof a?.certJson === "string" ? (a.certJson as string).trim() : ""
      const refParsed = maybeRef && !certText.startsWith("{") && !certText.startsWith("[") ? parseDigest(maybeRef) : null
      const nodeId = typeof a?.nodeId === "string" ? a.nodeId : ""
      if (refParsed && (!certText || certText === maybeRef)) {
        return {
          title: "Reason Table",
          output: [`Reason table — digest parse:`, `- kind=${refParsed.kind} digest=${refParsed.digest}`, `SLICE: (pass full certJson for UC8 explain)`].join("\n"),
          metadata: { agent: { digest: refParsed } },
        } as any
      }
      const { markdown, agent } = renderReason(irText, certText, nodeId)
      return {
        title: "Reason Table",
        output: markdown,
        metadata: { agent },
      } as any
    },
  })
}

export default async ({ directory, worktree }: { directory: string; worktree?: string }) => {
  const root = worktree ?? directory
  const reason_table = createReasonTableTool(root)
  return {
    tool: { reason_table },
  }
}

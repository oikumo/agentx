// Startup Table — plain-line startup menu for the opencode session open.
// Non-harness on purpose: filename has NO `omt_` prefix so it stays OUTSIDE
// `.meta/META_HARNESS.omt` @var harness_paths (exact/prefix) + e2e receipt guard.
// No registry change, no opencode.jsonc perm change — pure formatter, stdlib only.
//
// Reads WORK.compiled.md (11-line header built by `uv run scripts/omt/workc.py build`)
// + live `omt_net probe` JSON (probeJson arg) and renders, live-first (feature_163):
//   live empty (next:none + other:[]) → lean ≤3-line reply, zero stale letters;
//   else INTRO (1 paragraph) + GLOBAL (<=8 plain lines) + TASKS letter list
//   (A/B/C → live IDs only, drift-filtered) + SUGGESTED (<=5 advisory lines, S=accept).
// Labels hide `proj:`/`unscoped:` prefixes,
// mapping keeps full IDs 1:1 (D19: no invented IDs in TASKS).
// TA: why: `startup_table` (no omt_ prefix) avoids isOmtHarness + TOOL registry churn — new `omt_*` plugin would need @tool row + harnessc build + e2e receipt; template stays usable prompt-side with zero harness edits.

import { Plugin } from "@opencode/plugin"
import { tool, registerTools } from "../lib/v1_compat"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { initOmtShared, repoRoot } from "../lib/omt_shared"

type Parsed = {
  rev: string
  next: string
  other: string
  blocked: string
  resources: string
  pool: string
  lanes: string
  projectsSummary: string
  active: string
  optionsSummary: string
  optionIds: string[]
}

function grab(pattern: RegExp, text: string, fallback = ""): string {
  const m = text.match(pattern)
  return m && m[1] ? m[1].trim() : fallback
}

function parseCompiled(text: string): Parsed {
  const rev = grab(/net_rev:(\d+)/, text, "?")
  const next = grab(/^NEXT:\s*(.+)$/m, text)
  const otherBlockedRes = text.match(/^Other:\s*(.+?)\s*\|\s*Blocked:\s*(.+?)\s*\|\s*Resources:\s*(.+)$/m)
  const pool = grab(/^Pool:\s*(.+)$/m, text)
  const lanes = grab(/^Lanes:\s*(.+)$/m, text)
  const projectsSummary = grab(/^Projects:\s*(.+)$/m, text)
  const active = grab(/^Active:\s*(.+)$/m, text)
  const optionsSummary = grab(/^Options\(\d+\):\s*(.+)$/m, text) || grab(/^Options:\s*(.+)$/m, text)
  const optionIdsRaw = grab(/^OptionIDs:\s*(.+)$/m, text)
  const optionIds = optionIdsRaw ? optionIdsRaw.split(",").map((s) => s.trim()).filter(Boolean) : []
  return {
    rev,
    next,
    other: otherBlockedRes?.[1]?.trim() ?? "",
    blocked: otherBlockedRes?.[2]?.trim() ?? "",
    resources: otherBlockedRes?.[3]?.trim() ?? "",
    pool,
    lanes,
    projectsSummary,
    active,
    optionsSummary,
    optionIds,
  }
}

function groupOf(id: string): string {
  if (id.startsWith("proj:")) return "Projects"
  return "New"
}

function labelOf(id: string): string {
  return id.replace(/^(proj:|unscoped:)/, "")
}

function actionPlanFor(pick: string, rows: { letter: string; label: string; id: string; group: string }[], p: Parsed, probeNext: string | null): string | null {
  const key = (pick || "").trim().toUpperCase()
  if (!key) return null
  if (key === "S") {
    // Live-first: prefer the live probe target, then the file NEXT.
    const cands = [
      probeNext && probeNext !== "none" ? String(probeNext) : "",
      probeNext && probeNext !== "none" && !String(probeNext).includes(":") ? `proj:${probeNext}` : "",
      p.next || "",
    ].filter(Boolean)
    const found = cands.map((c) => rows.find((r) => r.id === c)).find(Boolean) || rows[0]
    if (!found) return null
    return actionPlanFor(found.letter, rows, p, probeNext)
  }
  const row = rows.find((r) => r.letter === key)
  if (!row) return null
  if (row.group === "Projects") {
    const slug = row.label
    return [
      `## ACTION PLAN — ${row.letter}: Resume the ${slug} project`,
      ``,
      `**You picked:** ${slug} (menu shortcut ${row.letter}). Goal: get oriented and start working.`,
      `**Steps (I run these; stop at first block and tell you):**`,
      `1. **Open the project home** — read its purpose and where it left off (runs \`read .projects/meta/${slug}/PROJECT.md\`).`,
      `2. **Recall context** — short resume digest: what was done, what's next (runs \`omt_status{op:"resume"}\`).`,
      `3. **Start working** — declare the phase so edits unlock (runs \`omt_phase{…scope:"Resume ${slug}"}\`; type/scope adjusted to your ask).`,
      ``,
      `> If anything looks stale, I show you the home + digest first.`,
    ].join("\n")
  }
  return [
    `## ACTION PLAN — ${row.letter}: Claim and scope new task ${row.label}`,
    ``,
    `**You picked:** unscoped item \`${row.label}\`. Goal: take ownership, then define it.`,
    `**Steps:**`,
    `1. **Claim it** — reserve the slot so parallel work can't collide (runs \`omt_net{op:"claim"}\`).`,
    `2. **Scope it** — declare analysis and describe what done looks like (runs \`omt_phase{…}\`).`,
  ].join("\n")
}

// Plain-language action per row (abstraction over the tool call).
function actionText(r: { label: string; group: string }): string {
  if (r.group === "Projects") return `Resume — open home, recall context, start`
  return `Claim + scope new work`
}

function renderTables(p: Parsed, probe: any | null, pick?: string): { markdown: string; agent: Record<string, any> } {
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  const probeNext = probe?.menu?.next ?? probe?.next ?? null
  const probeOther: string[] = Array.isArray(probe?.menu?.other_enabled) ? probe.menu.other_enabled.map(String) : []
  const probeTitles: Record<string, string> = (probe?.menu as any)?.titles ?? {}
  const liveEmpty = !!probe && (!probeNext || probeNext === "none") && probeOther.length === 0
  // O1 live-first (feature_162/163): when a probe is present, picks come ONLY
  // from live next/other_enabled — the compiled file is context and never
  // supplies stale letters. Bare ids normalize to unscoped:.
  const normLiveId = (id: string) => (/:/.test(id) ? id : `unscoped:${id}`)
  const liveIds = probe ? [...(probeNext && probeNext !== "none" ? [String(probeNext)] : []), ...probeOther].filter((v, i, a) => v && a.indexOf(v) === i) : null
  const visibleIds = (liveIds ?? p.optionIds).filter((id) => !id.startsWith("drift:"))
  const rows = visibleIds.map((raw, i) => {
    const id = liveIds ? normLiveId(raw) : raw
    return {
      letter: letters[i] ?? `?${i}`,
      label: labelOf(id),
      id,
      group: groupOf(id),
      title: probeTitles[raw] || probeTitles[id] || "",
    }
  })
  const probeObs = probe?.observation?.state ?? probe?.observation ?? ""
  const probeRev = probe?.revision ?? probe?.observation?.revision ?? ""
  const fresh = probe?.freshness
  // TA: why: stale compares file NEXT vs live probe next — probe wins on mismatch (D4)
  const stale = probeNext !== null && probeNext !== undefined && String(probeNext) !== "" && p.next !== "" && String(probeNext) !== p.next
    ? true
    : (probeNext === "none" && p.next !== "none" && p.next !== "" ? true : false)

  const projRows = rows.filter((r) => r.group === "Projects")
  const newRows = rows.filter((r) => r.group === "New")

  const drained = p.pool.includes("pending=0") && p.pool.includes("active=0")
  const suggestedRow = rows.find((r) => r.id === p.next) || rows.find((r) => p.next.includes(r.id)) || projRows[0] || rows[0]
  const suggestedKey = suggestedRow ? suggestedRow.letter : "—"
  const nextFileLabel = suggestedRow?.label || labelOf(p.next || "—")
  const plan = actionPlanFor(pick || "", rows, p, probeNext)

  // AGENT-ONLY payload — full IDs + machine state live ONLY in tool metadata
  // (never in the markdown below). The agent reads `metadata.agent`; the user
  // sees just INTRO + GLOBAL + TASKS + SUGGESTED. D19 holds: letters map 1:1 to
  // stable OptionIDs inside metadata.agent.options.
  const agent = {
    rev: p.rev,
    net: probeObs || "file-only",
    net_rev: probeRev || p.rev,
    pool: p.pool || "",
    lanes: p.lanes || "",
    other: p.other || "",
    blocked: p.blocked || "",
    resources: p.resources || "",
    next_file: p.next || "",
    next_probe: probeNext,
    stale,
    projects_summary: p.projectsSummary || "",
    active: p.active || "",
    options_total: rows.length,
    options: rows.map((r) => ({ letter: r.letter, id: r.id, label: r.label, group: r.group })),
    suggested_pick: suggestedKey,
    suggested_id: suggestedRow?.id || "",
    reply_keys: `A–${rows[rows.length - 1]?.letter || "?"} + S`,
    freshness: fresh || null,
  }

  // INTRO (1 paragraph): what this menu is + where data came from + reply single letter.
  const intro = `This is your task picker from WORK.compiled.md rev ${p.rev}${probeRev ? ` + live probe rev ${probeRev}` : ""} — reply with a single letter.`

  // GLOBAL (<=8 plain lines): status/rev, Pool p/a/d, lanes/workers, Projects a/c/d, STALE wins.
  const globalLines = [
    `GLOBAL:`,
    `- status: ${probeObs || "file-only"} rev ${probeRev || p.rev}`,
    `- Pool: ${p.pool || "unknown"}`,
    `- Lanes: ${p.lanes || "—"}`,
    `- Projects: ${p.projectsSummary || "—"}`,
    `- Resources: ${p.resources || p.other || "—"}`,
    stale ? `- STALE: file NEXT \`${p.next}\` != probe \`${probeNext}\` — probe wins` : `- STALE: OK`,
  ]

  // TASKS (letter-shortcut list, grouped Projects/New, hide prefixes, 1:1 IDs, NEXT first).
  // O2 lean empty-pool: live present but nothing enabled → no stale letters.
  const fmtRow = (r: { letter: string; label: string; group: string; id: string; title?: string }): string => {
    const short = r.label.replace(/^iteration-log:/, "")
    const name = r.title && r.title !== short ? `${short} · ${r.title}` : short
    const nextMark = r.id === suggestedRow?.id ? ` [NEXT]` : ``
    return `${r.letter} - ${name}${nextMark} — ${actionText(r)}`
  }
  const taskLines = liveEmpty
    ? [`TASKS: none live — reply R to reconcile.`]
    : [
        `TASKS — reply a letter (never question-tool):`,
        `Projects:`,
        ...(projRows.length ? projRows.map(fmtRow) : [`- (none)`]),
        `New:`,
        ...(newRows.length ? newRows.map(fmtRow) : [`- (none)`]),
      ]

  // SUGGESTED NEXT (advisory D19-exempt <=5 lines: pool state + S=accept, never auto-applied).
  const suggestedLines = liveEmpty
    ? [
        `SUGGESTED (R=reconcile, never auto-applied):`,
        `- R = reconcile live net before any pick`,
      ]
    : [
        `SUGGESTED NEXT (advisory, S=accept, never auto-applied):`,
        drained
          ? `- pool drained (${p.pool}) — resume ${suggestedKey} (${nextFileLabel})`
          : `- pool ${p.pool} — check probe menu, default resume ${suggestedKey} (${nextFileLabel})`,
        `- S = accept ${suggestedKey} (${nextFileLabel})`,
      ]

  // USER-ONLY markdown — INTRO + GLOBAL + TASKS + SUGGESTED, plain lines, letter shortcuts only.
  const markdown = [
    intro,
    ``,
    ...globalLines,
    ``,
    ...(plan ? [plan, ``, `---`, ``] : []),
    ...taskLines,
    ``,
    ...suggestedLines,
  ].join("\n")
  return { markdown, agent }
}

function createStartupTableTool() {
  return tool({
    description: "Startup menu. OUTPUT (user-only): INTRO + GLOBAL + TASKS + SUGGESTED plain lines, letter shortcuts only. METADATA.agent (agent-only): full state + letter→OptionID map 1:1 (D19). Args: pick (letter/S), probeJson (live probe).",
    args: {
      probeJson: tool.schema.string().optional().describe("Optional live omt_net probe JSON envelope (for STALE + observation/rev)"),
      pick: tool.schema.string().optional().describe('Optional letter (A..H) or S: prepend the ACTION PLAN for that pick'),
    },
    async execute(args) {
      const compiledPath = join(repoRoot(), "WORK.compiled.md")
      if (!existsSync(compiledPath)) {
        return `# Startup — no data\n\n> WORK.compiled.md missing — run \`uv run scripts/omt/workc.py build\`.`
      }
      let text = ""
      try {
        text = readFileSync(compiledPath, "utf8")
      } catch {
        return `# Startup — unreadable\n\n> Could not read WORK.compiled.md.`
      }
      const parsed = parseCompiled(text)
      let probe: any | null = null
      const raw = (args as any)?.probeJson
      if (typeof raw === "string" && raw.trim()) {
        try {
          probe = JSON.parse(raw)
        } catch {
          probe = null
        }
      }
      const pickArg = typeof (args as any)?.pick === "string" ? (args as any).pick : undefined
      const { markdown, agent } = renderTables(parsed, probe, pickArg)
      return {
        title: "Startup Menu",
        output: markdown,
        metadata: {
          rev: parsed.rev,
          options: agent.options_total,
          pick: pickArg || null,
          agent,
        },
      } as any
    },
  })
}

export default Plugin.define({
  id: "startup-table",
  async setup(ctx) {
    initOmtShared(ctx.location.directory)
    const startup_table = createStartupTableTool()
    await registerTools(ctx, { startup_table })
  },
})

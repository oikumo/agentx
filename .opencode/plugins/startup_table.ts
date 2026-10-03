// Startup Table — plain-line startup menu for the opencode session open.
// Non-harness on purpose: filename has NO `omt_` prefix so it stays OUTSIDE
// `.meta/META_HARNESS.omt` @var harness_paths (exact/prefix) + e2e receipt guard.
// No registry change, no opencode.jsonc perm change — pure formatter, stdlib only.
//
// Reads WORK.compiled.md (11-line header built by `uv run scripts/omt/workc.py build`)
// + optional live `omt_net probe` JSON (probeJson arg) and renders:
//   INTRO (1 paragraph) + GLOBAL (<=8 plain lines) + TASKS letter list
//   (A/B/C → stable OptionIDs, drift-filtered) + SUGGESTED (<=5 advisory lines, S=accept).
// Labels hide `proj:`/`unscoped:` prefixes,
// mapping keeps full IDs 1:1 (D19: no invented IDs in TASKS).
// TA: why: `startup_table` (no omt_ prefix) avoids isOmtHarness + TOOL registry churn — new `omt_*` plugin would need @tool row + harnessc build + e2e receipt; template stays usable prompt-side with zero harness edits.

import { tool } from "@opencode-ai/plugin"
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

export function parseCompiled(text: string): Parsed {
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
    const target = p.next && !p.next.startsWith("none") ? p.next : (probeNext && probeNext !== "none" ? `proj:${probeNext}` : rows[0]?.id || "")
    const found = rows.find((r) => r.id === target) || rows[0]
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

// Compact probe digest → full probe-like shape (feature_138, mh16 slice 2).
// Digest schema (JSON string): {"next","obs","rev","fresh","hint"} — the only
// probe fields renderTables reads. ~120B vs ~1.2KB full envelope (~10x smaller
// call turn). Malformed → null (fail-open file-only render, same as bad probeJson).
// Full envelopes pass through untouched (backward compat).
export function normalizeProbe(raw: unknown): any | null {
  let v: any = raw
  if (typeof v === "string") {
    if (!v.trim()) return null
    try {
      v = JSON.parse(v)
    } catch {
      return null
    }
  }
  if (!v || typeof v !== "object") return null
  if (v.menu !== undefined || v.observation !== undefined) return v
  if (v.next === undefined && v.obs === undefined && v.rev === undefined) return null
  return {
    menu: { next: v.next ?? "none" },
    observation: { state: v.obs ?? "file-only", revision: v.rev ?? "?" },
    revision: v.rev ?? "?",
    freshness: { fresh: v.fresh ?? null, hint: v.hint ?? "" },
  }
}

type Resume = { next_task: string; summary: string; rev: string } | null

// Prior-session context → pickup plan (feature_139, mh16 slice 3).
// resumeDigest schema: JSON {"next_task","summary","rev"} (e.g. the
// `omt_status{op:"resume"}` digest, <=2KB) or plain text (= summary, next
// falls back to the suggested default). Empty/malformed → null (fail-open:
// the normal menu renders byte-identically).
export function normalizeResume(raw: unknown): Resume {
  if (raw === null || raw === undefined) return null
  let v: any = raw
  if (typeof v === "string") {
    if (!v.trim()) return null
    try {
      v = JSON.parse(v)
    } catch {
      // Plain text counts as a summary only if substantive (>=16 chars);
      // short garbage fails open to the normal menu.
      const s = v.trim().slice(0, 240)
      return s.length >= 16 ? { next_task: "", summary: s, rev: "" } : null
    }
  }
  if (!v || typeof v !== "object") return null
  const next_task = String(v.next_task ?? v.nextTask ?? v.pickup ?? v.next ?? "").slice(0, 160)
  const summary = String(v.summary ?? v.context ?? v.note ?? "").slice(0, 240)
  const rev = String(v.rev ?? v.revision ?? "")
  if (!next_task && !summary) return null
  return { next_task, summary, rev }
}

export function renderTables(p: Parsed, probe: any | null, pick?: string, resume?: Resume): { markdown: string; agent: Record<string, any> } {
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  const visibleIds = p.optionIds.filter((id) => !id.startsWith("drift:"))
  const rows = visibleIds.map((id, i) => ({
    letter: letters[i] ?? `?${i}`,
    label: labelOf(id),
    id,
    group: groupOf(id),
  }))

  const probeNext = probe?.menu?.next ?? probe?.next ?? null
  const probeObs = probe?.observation?.state ?? probe?.observation ?? ""
  const probeRev = probe?.revision ?? probe?.observation?.revision ?? ""
  const resumeActive = !!resume
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
    resume: resumeActive ? { next_task: resume.next_task, summary: resume.summary, rev: resume.rev } : null,
    reply_keys: `A–${rows[rows.length - 1]?.letter || "?"} + S`,
    freshness: fresh || null,
  }

  // INTRO (1 paragraph): what this menu is + where data came from + reply single letter.
  // Resume mode (feature_139): pickup-first — prior context leads, TASKS map unchanged.
  const intro = resumeActive
    ? `Resume pickup${resume.rev ? ` (prior rev ${resume.rev})` : ""} — ${resume.summary || "prior context held"} — reply with a single letter (S = pick up where you left off).`
    : `This is your task picker from WORK.compiled.md rev ${p.rev}${probeRev ? ` + live probe rev ${probeRev}` : ""} — reply with a single letter.`

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
  const fmtRow = (r: { letter: string; label: string; group: string; id: string }): string => {
    const short = r.label.replace(/^iteration-log:/, "")
    const nextMark = r.id === suggestedRow?.id ? ` [NEXT]` : ``
    return `${r.letter} - ${short}${nextMark} — ${actionText(r)}`
  }
  const taskLines = [
    `TASKS — reply a letter (never question-tool):`,
    `Projects:`,
    ...(projRows.length ? projRows.map(fmtRow) : [`- (none)`]),
    `New:`,
    ...(newRows.length ? newRows.map(fmtRow) : [`- (none)`]),
  ]

  // SUGGESTED NEXT (advisory D19-exempt <=5 lines: pool state + S=accept, never auto-applied).
  // Resume mode: pickup-first line leads; map + S mechanics unchanged.
  const pickup = resumeActive ? (resume.next_task || `${suggestedKey} (${nextFileLabel})`) : ""
  const suggestedLines = [
    `SUGGESTED NEXT (advisory, S=accept, never auto-applied):`,
    resumeActive
      ? `- pick up: ${pickup}`
      : drained
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
      probeDigest: tool.schema.string().optional().describe('Compact probe digest JSON {"next","obs","rev","fresh","hint"} — preferred: ~120B vs ~1.2KB envelope, renders identically. Digest wins when both are passed.'),
      resumeDigest: tool.schema.string().optional().describe('Prior-session context JSON {"next_task","summary","rev"} (e.g. omt_status resume digest, <=2KB) or plain text — renders a pickup-first menu, TASKS map unchanged. Ignored when empty/malformed.'),
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
      // Digest-first (feature_138): compact digest wins when both are passed.
      const digestRaw = (args as any)?.probeDigest
      if (typeof digestRaw === "string" && digestRaw.trim()) {
        probe = normalizeProbe(digestRaw)
      }
      const raw = (args as any)?.probeJson
      if (probe === null && typeof raw === "string" && raw.trim()) {
        try {
          probe = JSON.parse(raw)
        } catch {
          probe = null
        }
      }
      const pickArg = typeof (args as any)?.pick === "string" ? (args as any).pick : undefined
      const resumeRaw = (args as any)?.resumeDigest
      const resume = typeof resumeRaw === "string" || (resumeRaw !== null && typeof resumeRaw === "object")
        ? normalizeResume(resumeRaw)
        : null
      const { markdown, agent } = renderTables(parsed, probe, pickArg, resume)
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

export default async ({ directory, worktree }: { directory: string; worktree?: string }) => {
  initOmtShared(worktree ?? directory)
  const startup_table = createStartupTableTool()
  return {
    tool: { startup_table },
  }
}

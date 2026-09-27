// OMT++ omt_session — Tier-2 session inspector + labeled experiments (feature_131 S5).
// Thin proxy around scripts/session_inspect/service.py via python -m (S6 B1: no script-dir shadow; B2: 120s bounded reads) (stdlib-only core S1–S4 frozen).
// Closed 9-op enum (sessions|capture|query|inspect|trace|profile|compare|experiment|export;
// experiment sub plan|dry_run|run|collect|validate|replay, run gated no_safe_launch).
// Built inside createSessionTool() so description resolves from compiled IR AFTER
// initOmtShared (F2/F17, omt_net.ts R8 pattern).

import { tool } from "@opencode-ai/plugin"
import { execFileSync } from "node:child_process"
import { initOmtShared, repoRoot, irToolDescription } from "../lib/omt_shared"

const OPS = ["sessions", "capture", "query", "inspect", "trace", "profile", "compare", "experiment", "export"]

// Per-op argv whitelist mirroring service.py OP_ARGS
// (cross-source pinned @ tests/scripts/omt/test_omt_session_plugin_args.py).
const OP_ARGS: Record<string, readonly string[]> = {
  sessions: ["db", "directory", "session_ids", "time_from", "time_to", "limit", "expected_revision"],
  capture: ["db", "directory", "session_ids", "time_from", "time_to", "dest", "expected_revision"],
  query: ["db", "query_json", "limit", "cursor", "expected_revision"],
  inspect: ["db", "session_id", "message_id", "part_id", "page", "per_page", "expected_revision"],
  trace: ["db", "session_id", "expected_revision"],
  profile: ["db", "session_id", "top_n", "expected_revision"],
  compare: ["db", "ids_json", "basis", "expected_revision"],
  experiment: ["db", "sub", "manifest", "run", "dest", "expected_revision"],
  export: ["db", "selection_json", "dest", "expected_revision"],
}

function createSessionTool() {
  return tool({
    description: irToolDescription("omt_session", "Session inspector + labeled experiments — SSOT (9 ops, run gated). op=sessions|capture|query|inspect|trace|profile|compare|experiment|export."),
    args: {
      op: tool.schema.string().describe("op enum"),
      db: tool.schema.string().optional().describe("DB path"),
      directory: tool.schema.string().optional().describe("dir filter"),
      session_ids: tool.schema.string().optional().describe("ids filter"),
      time_from: tool.schema.string().optional().describe("from ms"),
      time_to: tool.schema.string().optional().describe("to ms"),
      limit: tool.schema.number().optional().describe("row cap"),
      query_json: tool.schema.string().optional().describe("query doc"),
      cursor: tool.schema.string().optional().describe("page cursor"),
      session_id: tool.schema.string().optional().describe("session id"),
      message_id: tool.schema.string().optional().describe("message id"),
      part_id: tool.schema.string().optional().describe("part id"),
      page: tool.schema.number().optional().describe("page n"),
      per_page: tool.schema.number().optional().describe("page size"),
      top_n: tool.schema.number().optional().describe("top n"),
      ids_json: tool.schema.string().optional().describe("ids doc"),
      basis: tool.schema.string().optional().describe("usage basis"),
      sub: tool.schema.string().optional().describe("exp subop"),
      manifest: tool.schema.string().optional().describe("manifest doc"),
      run: tool.schema.string().optional().describe("run id"),
      dest: tool.schema.string().optional().describe("dest path"),
      selection_json: tool.schema.string().optional().describe("selection doc"),
      expected_revision: tool.schema.number().optional().describe("rev guard"),
    },
    async execute(args, context) {
      const op = String(args?.op ?? "")
      if (!OPS.includes(op)) {
        return JSON.stringify({ ok: false, error: "unknown_op", op, message: `want ${OPS.join("|")}` })
      }
      if (op === "experiment") {
        const sub = String((args as any)?.sub ?? "")
        if (sub === "run") {
          return JSON.stringify({ ok: false, reason: "no_safe_launch", executed: false })
        }
      }
      const argv = ["run", "python", "-m", "session_inspect.service", op]
      for (const k of OP_ARGS[op]) {
        let v: any = (args as any)?.[k]
        if (k === "directory" && (v === undefined || v === null || v === "")) v = undefined
        if (v !== undefined && v !== null && v !== "")
          argv.push(`--${k}`, Array.isArray(v) ? JSON.stringify(v) : String(v))
      }
      try {
        const out = execFileSync("uv", argv, {
          cwd: repoRoot() + "/scripts", encoding: "utf8", timeout: 120000,
          stdio: ["ignore", "pipe", "pipe"],
        })
        return out.trim()
      } catch (e: any) {
        const stdout = String(e?.stdout || "").trim()
        if (stdout) return stdout
        return JSON.stringify({ ok: false, error: "engine_error", op, message: String(e?.message || e) })
      }
    },
  })
}

export default async ({ directory, worktree }: { directory: string; worktree?: string }) => {
  initOmtShared(worktree ?? directory)
  const omt_session = createSessionTool()
  return {
    tool: { omt_session },
  }
}

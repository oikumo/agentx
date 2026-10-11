// OMT++ omt_session — Tier-2 session inspector + labeled experiments (feature_131 S5).
// Thin proxy around scripts/session_inspect/service.py via python -m (S6 B1: no script-dir shadow; B2: 120s bounded reads) (stdlib-only core S1–S4 frozen).
// Closed 9-op enum (sessions|capture|query|inspect|trace|profile|compare|experiment|export;
// experiment sub plan|dry_run|run|collect|validate|replay, run gated no_safe_launch).
// Built inside createSessionTool() so description resolves from compiled IR AFTER
// initOmtShared (F2/F17, omt_net.ts R8 pattern).
//
// V2 (migrate-v1): Plugin.define + ctx.tool.transform with JSON-Schema input,
// {content} results. OP_ARGS/OPS preserved for cross-source pins.

import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { initOmtShared, repoRoot, irToolDescription, argvValue } from "../lib/omt_shared"

const OPS = ["sessions", "capture", "query", "inspect", "trace", "profile", "compare", "experiment", "export"]

// Per-op argv whitelist mirroring service.py OP_ARGS
// (cross-source pinned @ tests/harness_meta/omt/test_omt_session_plugin_args.py).
const OP_ARGS: Record<string, readonly string[]> = {
  sessions: ["db", "directory", "session_ids", "time_from", "time_to", "limit", "expected_revision"],
  capture: ["db", "directory", "session_ids", "time_from", "time_to", "dest", "expected_revision"],
  query: ["db", "query_json", "limit", "cursor", "expected_revision"],
  inspect: ["db", "session_id", "message_id", "part_id", "page", "per_page", "expected_revision"],
  trace: ["db", "session_id", "page", "per_page", "expected_revision"],
  profile: ["db", "session_id", "top_n", "expected_revision"],
  compare: ["db", "ids_json", "basis", "expected_revision"],
  experiment: ["db", "sub", "manifest", "run", "dest", "expected_revision"],
  export: ["db", "selection_json", "dest", "expected_revision"],
}

function createSessionTool() {
  return {
    name: "omt_session",
    description: irToolDescription("omt_session", "Session inspector + labeled experiments — SSOT (9 ops, run gated). op=sessions|capture|query|inspect|trace|profile|compare|experiment|export."),
    input: {
      type: "object",
      properties: {
        op: { type: "string", description: "op enum" },
        db: { type: "string", description: "DB path" },
        directory: { type: "string", description: "dir filter" },
        session_ids: { type: "string", description: "ids filter" },
        time_from: { type: "string", description: "from ms" },
        time_to: { type: "string", description: "to ms" },
        limit: { type: "number", description: "row cap" },
        query_json: { type: "string", description: "query doc" },
        cursor: { type: "string", description: "page cursor" },
        session_id: { type: "string", description: "session id" },
        message_id: { type: "string", description: "message id" },
        part_id: { type: "string", description: "part id" },
        page: { type: "number", description: "page n" },
        per_page: { type: "number", description: "page size" },
        top_n: { type: "number", description: "top n" },
        ids_json: { type: "string", description: "ids doc" },
        basis: { type: "string", description: "usage basis" },
        sub: { type: "string", description: "exp subop" },
        manifest: { type: "string", description: "manifest doc" },
        run: { type: "string", description: "run id" },
        dest: { type: "string", description: "dest path" },
        selection_json: { type: "string", description: "selection doc" },
        expected_revision: { type: "number", description: "rev guard" },
      },
      required: [],
      additionalProperties: false,
    },
    async execute(args: any, _context: any) {
      const op = String(args?.op ?? "")
      if (!OPS.includes(op)) {
        return { content: JSON.stringify({ ok: false, error: "unknown_op", op, message: `want ${OPS.join("|")}` }) }
      }
      if (op === "experiment") {
        const sub = String((args as any)?.sub ?? "")
        if (sub === "run") {
          return { content: JSON.stringify({ ok: false, reason: "no_safe_launch", executed: false }) }
        }
      }
      const argv = ["run", "python", "-m", "session_inspect.service", op]
      for (const k of OP_ARGS[op]) {
        let v: any = (args as any)?.[k]
        if (k === "directory" && (v === undefined || v === null || v === "")) v = undefined
        if (v !== undefined && v !== null && v !== "")
          // feature_136: argvValue re-serializes SDK-coerced arrays/objects —
          // query_json/manifest/selection_json can arrive as JS objects when
          // the emission layer object-parses the JSON string ("[object
          // Object]" class; blocked run001 collect until pinned here).
          argv.push(`--${k}`, argvValue(v))
      }
      try {
        const out = execFileSync("uv", argv, {
          cwd: repoRoot() + "/scripts", encoding: "utf8", timeout: 120000,
          stdio: ["ignore", "pipe", "pipe"],
        })
        return { content: String(out).trim() }
      } catch (e: any) {
        const stdout = String(e?.stdout || "").trim()
        if (stdout) return { content: stdout }
        return { content: JSON.stringify({ ok: false, error: "engine_error", op, message: String(e?.message || e) }) }
      }
    },
  }
}

export default Plugin.define({
  id: "omt-session",
  async setup(ctx) {
    initOmtShared(ctx.location.directory)
    const omt_session = createSessionTool()
    await ctx.tool.transform((editor) => {
      editor.add(omt_session as any)
    })
  },
})

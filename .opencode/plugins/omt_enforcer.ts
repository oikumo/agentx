// OMT++ Process Enforcer — opencode plugin (feature_006).
//
// Turns AGENTS.md's *voluntary* process checkpoints into a *real* gate, tuned for a
// solo-dev learning scaffold: it blocks the edit that would skip a phase, but every block
// is a teaching message that names the OMT++ rule and the exact next command. Internal
// errors fail OPEN (never brick a working session); only genuine process violations block.
//
// meta_harness_dsl R2: this file is the THIN COMPOSITION ROOT — hook
// registration + dispatch only (single default export per Appendix B2). All
// gate logic lives in the lib modules:
//   ../lib/enforcer/session_state.ts  — the 5 process-lifetime containers
//                                       (audit P5/F20) + ledger helpers + OmtBlock
//   ../lib/enforcer/nav_gate.ts       — feature_020 nav gate + R6 S6 session
//                                       bootstrap (nav tip + TA digest, ONE Set)
//   ../lib/enforcer/receipt_guard.ts  — protected files, e2e receipt, tests/ canary
//   ../lib/enforcer/phase_gate.ts     — src/ phase+artifact gate, §12 matrix,
//                                       omt_phase/omt_skip/omt_complete
//   ../lib/enforcer/tdd_hats.ts       — feature_016 two-hats gate + TDD tools
//   ../lib/enforcer/think_gate.ts     — feature_021 think-gate + feature_022 D1
//                                       read-time thought injection
//   ../lib/enforcer/gate_driver.ts    — HDL-2 data-driven before/after gate
//                                       chains (IR @gate records)
//   ../lib/enforcer/mvc_after.ts      — MVC++ lint delta gate + idle sweep
//   ../lib/enforcer/lsp_filter.ts     — feature_090 known-LSP-error allowlist
//                                       (post-edit Pyright noise filter)
//
// Mechanics:
//   • omt_phase  custom tool → agent declares task_type/phase/scope; recorded in the ledger.
//   • omt_skip   custom tool → logged escape hatch that unlocks edits for the session.
//   • tool.execute.before → gate edits to src/ (needs a phase), tests/ (needs approval),
//     and hard-deny README/.env/uv.lock/LICENSE.
//   • tool.execute.after  → data-driven after-chain (IR after-gates in order=: MVC++ delta, TDD revert).
//
// Ledger: .meta/.omt/ledger.jsonl  (gitignored runtime state, one JSON record per line)
//
// V2 (migrate-v1): Plugin.define({id:"omt-enforcer", setup(ctx)}).
// Context mapping: directory→ctx.location.directory, project→ctx.location.project,
// client→console logging (makeSafeLog/makeNotify without client), `$`→node:child_process
// in lib, event→ctx.event.subscribe with AbortController cleanup, tool map→
// ctx.tool.transform(editor.add), tool.execute.before/after→ctx.tool.hook.
//
// API note (V2): before event = {tool, sessionID, input}; after event =
// {tool, sessionID, input, result|error, status}. Synthetic V1 input/output
// objects preserve the gate_driver contract (input={tool,sessionID}, output={args}).

// omt_status is registered by .opencode/plugins/omt_status.ts as its own
// standalone plugin. Keeping it out of this enforcer avoids dynamic-import
// cache/loading failures and duplicate tool registration.

import { Plugin } from "@opencode/plugin"
import { initOmtShared } from "../lib/omt_shared"
import {
  OmtBlock, createSessionState, makeSafeLog, makeNotify, type EnforcerEnv,
} from "../lib/enforcer/session_state"
import { navTrack, sessionBootstrap, kbTrack, trackRead } from "../lib/enforcer/nav_gate"
import { runAfterGates, runBeforeGates } from "../lib/enforcer/gate_driver"
import { createPhaseTools } from "../lib/enforcer/phase_gate"
import { createTddTools } from "../lib/enforcer/tdd_hats"
import { injectThoughtsOnRead } from "../lib/enforcer/think_gate"
import { sessionIdleSweep } from "../lib/enforcer/mvc_after"
import { lspAfterEdit } from "../lib/enforcer/lsp_filter"

// Wrap a lib tool (intermediate string-returning or V2 {content}-returning)
// into a V2 Tool.Info execute returning {content}.
function toV2(name: string, t: any) {
  return {
    name,
    description: t.description,
    input: t.input,
    async execute(input: any, toolCtx: any) {
      const r = await t.execute(input, toolCtx)
      if (typeof r === "string") return { content: r }
      return r
    },
  }
}

export default Plugin.define({
  id: "omt-enforcer",
  async setup(ctx) {
    // V2 location: plugin instance directory (repo root for local plugins).
    const directory = ctx.location.directory
    initOmtShared(directory)

    const safeLog = makeSafeLog()
    const env: EnforcerEnv = {
      directory,
      state: createSessionState(),
      safeLog,
      notify: makeNotify(undefined, safeLog),
    }

    // --- tools ---------------------------------------------------------------
    const phaseTools = createPhaseTools(env) as Record<string, any>
    const tddTools = createTddTools(env) as Record<string, any>
    await ctx.tool.transform((editor) => {
      for (const [name, t] of Object.entries({ ...phaseTools, ...tddTools })) {
        editor.add(toV2(name, t) as any)
      }
    })

    // --- before hook (V1 "tool.execute.before") --------------------------------
    await ctx.tool.hook("execute.before", async (event: any) => {
      const session = event?.sessionID || undefined
      // Synthetic V1 shapes: input={tool,sessionID}, output={args}
      const synthInput = { tool: event.tool, sessionID: event.sessionID }
      const synthOutput = { args: event.input as any }

      // feature_099 S2 (F02): advice may fail open, authority must not.
      try {
        await navTrack(env, session, synthInput)
        await kbTrack(env, session, synthInput)
      } catch (e: any) {
        safeLog("warn", "before-hook instrumentation error (failing open): " + (e?.message || e))
      }

      try {
        // V2: args live on event.input (was output.args in V1 before-hook).
        const rawInput: any = event.input as any
        const raw = rawInput?.filePath ?? rawInput?.path ?? rawInput?.file
        await runBeforeGates(env, session, synthInput, synthOutput,
          typeof raw === "string" && raw ? raw : null)
      } catch (e: any) {
        if (e instanceof OmtBlock) throw e
        throw new OmtBlock(`⛔ OMT++ gate (authority resolution failed closed): ${(e?.message || e)}`)
      }
    })

    // --- after hook (V1 "tool.execute.after") ----------------------------------
    await ctx.tool.hook("execute.after", async (event: any) => {
      // V2 after: {tool, sessionID, input, result|error, status}.
      // Lib expects V1 (input={tool,sessionID,args}, output=result mutable).
      const synthInput = { tool: event.tool, sessionID: event.sessionID, args: event.input as any }
      const synthOutput: any = event.status === "completed" ? (event.result as any) : {}
      // R6 S6: session bootstrap — nav reminder + TA digest, once per session
      await sessionBootstrap(env, synthInput, synthOutput)
      await trackRead(env, (event as any)?.sessionID || undefined, synthInput)
      await injectThoughtsOnRead(env, synthInput, synthOutput)
      // feature_090: LSP allowlist (keys off result metadata, runs before raw guard)
      await lspAfterEdit(env, synthInput, synthOutput)

      const rawInput: any = event.input as any
      const raw = rawInput?.filePath ?? rawInput?.path ?? rawInput?.file
      if (typeof raw !== "string" || !raw) return
      await runAfterGates(env, (event as any)?.sessionID || undefined, synthInput, synthOutput, raw)
    })

    // --- events (V1 `event` hook → V2 subscribe + cleanup) ----------------------
    const controller = new AbortController()
    void (async () => {
      try {
        for await (const ev of ctx.event.subscribe({ signal: controller.signal }) as any) {
          try {
            await sessionIdleSweep(env, ev as any)
          } catch { /* fail-open */ }
        }
      } catch { /* abort on unload */ }
    })()

    return () => controller.abort()
  },
})

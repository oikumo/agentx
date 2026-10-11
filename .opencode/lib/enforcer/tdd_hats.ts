// OMT++ TDD two-hats enforcement (feature_016; meta_harness_dsl R2 module).
//
// Thin wrappers around scripts/omt/tdd_check.py (the state machine lives in
// Python): the namespaced omt_tdd tool (improvement006/OPT-H: five tools
// consolidated into one op= dispatcher), the before-hook two-hats gate
// (tests/ and src/ branches), and the after-hook after-edit check
// (advisories + REFACTOR revert when a refactor edit breaks tests).
// R8 (OMT-HDL-1): tool descriptions resolve from the compiled IR
// (irToolDescription) with the in-source text as fallback seed.
//
// V2 (migrate-v1): V1 `tool()` helper removed — createTddTools returns V2
// Tool.Info definitions ({name, description, input JSON Schema, execute
// returning {content}}) for ctx.tool.transform(editor.add). `$` Bun helper
// replaced by node:child_process.

import { execFileSync } from "node:child_process"
import { writeFileSync } from "node:fs"
import { OmtBlock, getActiveUnlock, type EnforcerEnv } from "./session_state"
import { irToolDescription, gateMsg, argvValue } from "../omt_shared"

// --- TDD tools (thin wrappers delegating to tdd_check.py) -------------------
// improvement006/OPT-H: one registered tool; op dispatches to the subcommands
// (red → the engine's "start" subcommand — the tdd/ package is unchanged).
const TDD_SUBCMD: Record<string, string> = {
  testlist: "testlist", red: "start", green: "green", refactor: "refactor", sync: "sync", done: "done",
}

function runTdd(env: EnforcerEnv, flags: string[]): any {
  const out = execFileSync("uv", ["run", "scripts/omt/tdd_check.py", ...flags], {
    cwd: env.directory, encoding: "utf8", timeout: 60000,
    stdio: ["ignore", "pipe", "pipe"],
  } as any)
  return JSON.parse(String(out || "{}"))
}

export function createTddTools(env: EnforcerEnv) {
  const omt_tdd = {
    name: "omt_tdd",
    description: irToolDescription("omt_tdd", "TDD cycle driver. op=testlist(behaviors,feature; JSON array or prose) | red(test_node,target_src,feature) | green(test_node,feature) | refactor(test_node,feature) | sync(feature) | done(feature). Toolchain-aware: .py→pytest, .ts/.tsx→vitest (GOTCHA_TDD_TOOLCHAIN)."),
    input: {
      type: "object",
      properties: {
        op: { type: "string", description: "testlist|red|green|refactor|sync|done" },
        behaviors: { type: "string", description: "testlist: JSON array of behaviors" },
        feature: { type: "string", description: "feature slug" },
        test_node: { type: "string", description: "red/green/refactor: test node" },
        target_src: { type: "string", description: "red: src file under test" },
      },
      required: [],
      additionalProperties: false,
    },
    async execute(args: any, context: any) {
      const subcmd = TDD_SUBCMD[args?.op ?? ""]
      if (!subcmd) {
        return { content: `⛔ omt_tdd: unknown op '${args?.op}' — want testlist|red|green|refactor|sync|done ` +
          "(testlist(behaviors,feature) red(test_node,target_src,feature) green(test_node,feature) refactor(test_node,feature) sync(feature) done(feature))." }
      }
      const session = context?.sessionID || ""
      const flags = [subcmd]
      for (const k of ["behaviors", "feature", "test_node", "target_src"]) {
        const v = (args as any)?.[k]
        if (v !== undefined && v !== null && v !== "")
          // feature_027 + feature_136: SDK coerces JSON-looking strings fed to a
          // tool string arg into actual JS arrays/objects; argvValue
          // re-serializes them back to valid JSON (behaviors et al.).
          flags.push(`--${k.replace(/_/g, "-")}`, argvValue(v))
      }
      flags.push("--session", session)
      try {
        const data = runTdd(env, flags)
        return { content: data.message || JSON.stringify(data) }
      } catch (e: any) {
        env.safeLog("warn", `tdd_check.py ${subcmd} failed: ${e?.message || e}`)
        return { content: `⚠️ TDD engine error: ${e?.message || e}` }
      }
    },
  }
  return { omt_tdd }
}

// --- before-hook two-hats gate ----------------------------------------------
// Runs tdd_check.py gate for a path and throws when the current TDD state
// (hat) forbids the edit. isTestsDir selects the tests/ branch of the gate.
export async function tddGateCheck(
  env: EnforcerEnv,
  session: string | undefined,
  rel: string,
  isTestsDir: boolean,
): Promise<void> {
  const flags = isTestsDir
    ? ["gate", "--path", rel, "--is-tests", "--session", session || ""]
    : ["gate", "--path", rel, "--session", session || ""]
  let tddData: any = { allowed: true }
  try {
    tddData = runTdd(env, flags)
  } catch (e: any) {
    // Fail-open on engine error? No — gate check failure should fail closed?
    // Preserve V1 semantics: JSON parse of empty stdout → allowed:true default
    // handled above; exec throws (non-zero) → treat as allowed to avoid bricking?
    // V1: JSON.parse(stdout || '{"allowed":true}') — engine error envelope still
    // parsed. Here exec throws without stdout → keep allowed:true.
    env.safeLog("warn", `tdd gate check failed open: ${(e as any)?.message || e}`)
    return
  }
  if (!tddData.allowed) throw new OmtBlock(tddData.reason)
}

// --- after-hook after-edit check (advisory + REFACTOR revert) ---------------
// Runs only when tdd_mode is active. A revert_needed verdict restores the
// pre-edit content captured in the before-hook (refactorSnapshots) and blocks.
// The snapshot slot is always released (finally) so a stale snapshot never
// leaks into the next edit.
export async function tddAfterEdit(
  env: EnforcerEnv,
  input: any,
  abs: string,
  rel: string,
): Promise<void> {
  try {
    const tddSession = input?.sessionID || ""
    const tddUnlock = getActiveUnlock(tddSession)
    if (tddUnlock?.record?.tdd_mode) {
      let tddData: any = {}
      try {
        tddData = runTdd(env, ["after-edit", "--path", rel, "--session", tddSession])
      } catch (e: any) {
        env.safeLog("warn", "TDD after-edit engine failed open: " + ((e as any)?.message || e))
        return
      }
      if (tddData.action === "revert_needed") {
        const content = env.state.refactorSnapshots.get(abs)
        if (content !== undefined) {
          writeFileSync(abs, content, "utf8")
          throw new OmtBlock(tddData.reason || gateMsg("tdd_revert"))
        }
      }
      if (tddData.advisories?.length) {
        await env.notify(tddData.advisories.join("\n"))
      }
    }
  } catch (e: any) {
    if (e instanceof OmtBlock) throw e
    env.safeLog("warn", "TDD after-edit check failed: " + (e?.message || e))
  } finally {
    env.state.refactorSnapshots.delete(abs)
  }
}

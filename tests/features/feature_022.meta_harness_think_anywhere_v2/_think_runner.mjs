// Test fixture: invokes the REAL omt_think plugin tools so Python tests can
// assert on actual tool behavior (not just source-string presence).
//
// feature_022 Tier C extension: omt_think_verify joins the tool map, and a
// "session-start" mode calls the factory's "session.start" hook so tests can
// assert on the real digest (design_003 §3 — C1 stale-count surfacing).
// Tier remainder (design_004): omt_think_suggest + omt_think_reindex join the map.
// feature_023 Tier 1c: "after-hook" mode drives the real "tool.execute.after"
// hook (first-tool-result TA digest) through a BATCH of fake {input, output}
// calls on ONE plugin instance — the per-session digest state is
// process-lifetime, so once-per-session assertions need several calls in one
// process. Prints the mutated outputs.
//
// Usage: node --experimental-strip-types _think_runner.mjs <tool> '<json-args>'
//   <tool>  one of: omt_think | omt_think_list | omt_think_remove |
//           omt_think_verify | omt_think_suggest | omt_think_reindex |
//           session-start | after-hook
// Prints the tool's JSON-encoded result (a plain string) to stdout.
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/plugin/omt_think.ts")

let mod
try {
  mod = await import(pathToFileURL(pluginPath).href)
} catch (e) {
  console.error("PLUGIN_LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(3)
}

// omt_think.ts exports tools via the default plugin factory (opencode's loader
// requires all exports to be functions, so tool objects cannot be named-exported).
const plugin = typeof mod.default === "function" ? await mod.default() : null
const toolMap = plugin?.tool ?? mod
const tools = {
  omt_think: toolMap.omt_think,
  omt_think_list: toolMap.omt_think_list,
  omt_think_remove: toolMap.omt_think_remove,
  omt_think_verify: toolMap.omt_think_verify,
  omt_think_suggest: toolMap.omt_think_suggest,
  omt_think_reindex: toolMap.omt_think_reindex,
}

const name = process.argv[2]
if (name === "session-start") {
  // C1: drive the real session.start hook (thinkDigest) — no args.
  const fn = plugin?.["session.start"]
  if (typeof fn !== "function") {
    console.error("NO_SESSION_START")
    process.exit(2)
  }
  const out = await fn()
  process.stdout.write(JSON.stringify(out))
  process.exit(0)
}
if (name === "after-hook") {
  // feature_023 Tier 1c: drive the real "tool.execute.after" hook through a
  // BATCH of fake {input, output} calls on ONE plugin instance; print the
  // mutated outputs (NO_AFTER_HOOK when the plugin does not register it).
  const fn = plugin?.["tool.execute.after"]
  if (typeof fn !== "function") {
    console.error("NO_AFTER_HOOK")
    process.exit(2)
  }
  const calls = JSON.parse(process.argv[3] || "[]")
  const results = []
  for (const call of calls) {
    await fn(call.input, call.output)
    results.push(call.output)
  }
  process.stdout.write(JSON.stringify(results))
  process.exit(0)
}
const args = process.argv[3] ? JSON.parse(process.argv[3]) : {}
const tool = tools[name]
if (!tool) {
  console.error("UNKNOWN_TOOL: " + name)
  process.exit(2)
}
const exec = tool.execute || tool.run
const out = await exec(args)
process.stdout.write(JSON.stringify(out))

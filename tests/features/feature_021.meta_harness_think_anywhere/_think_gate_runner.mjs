// Test fixture: invokes the REAL thinkGateDecision helper exported from
// .opencode/plugin/omt_enforcer.ts so Python tests can assert on the actual
// think-gate logic (not a reimplementation).
//
// Usage:
//   node --experimental-strip-types _think_gate_runner.mjs decide '<json:opts>'
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/plugin/omt_enforcer.ts")

let mod
try {
  mod = await import(pathToFileURL(pluginPath).href)
} catch (e) {
  console.error("PLUGIN_LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(3)
}

const mode = process.argv[2]
if (mode === "decide") {
  const opts = JSON.parse(process.argv[3])
  process.stdout.write(JSON.stringify({ decision: mod.thinkGateDecision(opts) }))
} else if (mode === "consulted") {
  // Check whether hasConsultedThoughts is exported; report its presence.
  process.stdout.write(JSON.stringify({ exported: typeof mod.hasConsultedThoughts === "function" }))
} else {
  console.error("USAGE: _think_gate_runner.mjs decide '<json>' | consulted")
  process.exit(2)
}

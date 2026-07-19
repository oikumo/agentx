// Test fixture: invokes the REAL navGateDecision / isDocPath helpers exported
// from .opencode/plugin/omt_enforcer.ts so Python tests can assert on the
// actual M1/M2 gate logic (not a reimplementation).
//
// Usage:
//   node --experimental-strip-types _gate_runner.mjs decide '<json:opts>'
//   node --experimental-strip-types _gate_runner.mjs isdoc '<rel>'
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/dist/omt_enforcer.js")

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
  process.stdout.write(JSON.stringify({ decision: mod.navGateDecision(opts) }))
} else if (mode === "isdoc") {
  process.stdout.write(JSON.stringify({ isDoc: mod.isDocPath(process.argv[3]) }))
} else {
  console.error("USAGE: _gate_runner.mjs decide '<json>' | isdoc '<rel>'")
  process.exit(2)
}

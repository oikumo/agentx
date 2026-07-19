// Test fixture: invokes the REAL omt_think plugin tools so Python tests can
// assert on actual tool behavior (not just source-string presence).
//
// Usage: node --experimental-strip-types _think_runner.mjs <tool> '<json-args>'
//   <tool>  one of: omt_think | omt_think_list | omt_think_remove
// Prints the tool's JSON-encoded result (a plain string) to stdout.
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/dist/omt_think.js")

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
}

const name = process.argv[2]
const args = process.argv[3] ? JSON.parse(process.argv[3]) : {}
const tool = tools[name]
if (!tool) {
  console.error("UNKNOWN_TOOL: " + name)
  process.exit(2)
}
const exec = tool.execute || tool.run
const out = await exec(args)
process.stdout.write(JSON.stringify(out))

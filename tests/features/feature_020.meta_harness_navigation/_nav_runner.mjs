// Test fixture: invokes the REAL omt_nav plugin tools so Python tests can
// assert on actual tool behavior (not just source-string presence).
//
// Usage: node --experimental-strip-types _nav_runner.mjs <tool> '<json-args>'
//   <tool>  one of: omt_nav | omt_list_sections | omt_cross_ref | omt_quick_ref
// Prints the tool's JSON result to stdout. Exits non-zero on error.
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/dist/omt_nav.js")

let mod
try {
  mod = await import(pathToFileURL(pluginPath).href)
} catch (e) {
  console.error("PLUGIN_LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(3)
}

// omt_nav.ts exports tools via the default plugin factory (opencode's loader
// requires all exports to be functions, so tool objects cannot be named-exported).
// Call the factory to retrieve the `tool` map.
const plugin = typeof mod.default === "function" ? await mod.default() : null
const toolMap = plugin?.tool ?? mod
const tools = {
  omt_nav: toolMap.omt_nav,
  omt_list_sections: toolMap.omt_list_sections,
  omt_cross_ref: toolMap.omt_cross_ref,
  omt_quick_ref: toolMap.omt_quick_ref,
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

// Test fixture: invokes the REAL omt_nav plugin tools so Python tests can
// assert on actual tool behavior (not just source-string presence).
//
// Usage: node --experimental-strip-types _nav_runner.mjs <tool> '<json-args>'
//   <tool>  one of: omt_nav | omt_list_sections | omt_cross_ref | omt_quick_ref
// Prints the tool's JSON result to stdout. Exits non-zero on error.
import { fileURLToPath, pathToFileURL } from "node:url"
import { dirname, resolve } from "node:path"

const here = dirname(fileURLToPath(import.meta.url))
const pluginPath = resolve(here, "../../../.opencode/plugin/omt_nav.ts")

let mod
try {
  mod = await import(pathToFileURL(pluginPath).href)
} catch (e) {
  console.error("PLUGIN_LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(3)
}

const tools = {
  omt_nav: mod.omt_nav,
  omt_list_sections: mod.omt_list_sections,
  omt_cross_ref: mod.omt_cross_ref,
  omt_quick_ref: mod.omt_quick_ref,
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

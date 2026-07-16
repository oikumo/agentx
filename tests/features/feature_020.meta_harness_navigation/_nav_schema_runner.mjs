// Test fixture: inspects the REAL omt_nav plugin tool objects (via opencode's
// actual `tool()` function) to verify each tool exposes a proper `args` Zod
// schema — the precondition opencode needs to bind incoming tool-call args.
//
// WHY THIS EXISTS (DEFECT C): the function-level runner _nav_runner.mjs calls
// `tool.execute(args)` DIRECTLY, completely bypassing opencode's arg-binding.
// An earlier omt_nav.ts used `input:{type,properties}` (raw JSON schema)
// instead of `args`/`tool.schema`. opencode ignores `input` and registers the
// tool with NO parameters, so real calls passed undefined args and crashed on
// `.startsWith`/`.split`. _nav_runner.mjs never caught this because it never
// went through opencode's schema-binding. This runner inspects the schema
// opencode actually uses (`args`), so a DEFECT-C regression (input: instead of
// args:) is detected directly — no LLM, no HTTP, deterministic.
//
// Usage: node --experimental-strip-types _nav_schema_runner.mjs
// Prints JSON: { <toolName>: { hasArgs, hasInput, loaded, args: {<name>:{isZod,isOptional,typeName}} } }
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

// opencode's loader requires a default plugin function; the tool map lives on
// its `tool` property (see omt_nav.ts default export).
const plugin = typeof mod.default === "function" ? await mod.default() : null
const toolMap = plugin?.tool ?? {}

// Best-effort Zod schema introspection. opencode's tool.schema.*() returns Zod
// schemas carrying a `~standard` vendor marker (Standard Schema spec). We also
// read the type name and optionality for richer assertions.
function describeArg(z) {
  if (!z || typeof z !== "object") return { isZod: false, isOptional: null, typeName: null }
  const std = z["~standard"]
  const isZod = std?.vendor === "zod"
  let isOptional = null
  try { if (typeof z.isOptional === "function") isOptional = z.isOptional() } catch { /* ignore */ }
  let typeName = null
  try { typeName = z._zod?.def?.type || z.def?.type || null } catch { /* ignore */ }
  return { isZod, isOptional, typeName }
}

const out = {}
for (const [name, t] of Object.entries(toolMap)) {
  const hasArgs = !!(t && typeof t.args === "object" && t.args !== null)
  out[name] = {
    loaded: true,
    hasArgs,
    hasInput: !!(t && "input" in t),
    hasExecute: typeof t?.execute === "function",
    argNames: hasArgs ? Object.keys(t.args) : [],
    args: hasArgs
      ? Object.fromEntries(Object.entries(t.args).map(([k, v]) => [k, describeArg(v)]))
      : {},
  }
}
process.stdout.write(JSON.stringify(out))

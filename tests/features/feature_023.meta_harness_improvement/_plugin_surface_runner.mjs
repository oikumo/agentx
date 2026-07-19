// Test fixture (feature_023 Tier 3): inspects the REAL export/hook surface of
// the four OMT plugins so Python tests can pin what opencode's loader sees —
// no opencode server, no reimplementation.
//
// Modes:
//   hooks '<plugin-abs-path>' '<factory:default|OmtEnforcer>' '<tmpdir>'
//     Instantiate the plugin via its real factory and print
//     {"hooks": [...registered hook/tool keys...]} — a renamed/missing hook
//     (e.g. "tool.execute.after" typo'd) fails the wiring assertions.
//   exports '<plugin-abs-path>'
//     Print {"named": [...named exports...], "calls": {name: {ctx, undef, braces}}}
//     — every named FUNCTION export (except the OmtEnforcer factory) invoked
//     with the plugin-context-shaped garbage arg {client:null,$:noop,directory:""}
//     (what opencode's loader actually passes), then undefined, then {}.
//     No-throw is the load-safety property the loader relies on.
//
// Usage:
//   node --experimental-strip-types _plugin_surface_runner.mjs hooks '<abs>' '<factory>' '<tmpdir>'
//   node --experimental-strip-types _plugin_surface_runner.mjs exports '<abs>'
import { pathToFileURL } from "node:url"

const mode = process.argv[2]
const pluginPath = process.argv[3]

let mod
try {
  mod = await import(pathToFileURL(pluginPath).href)
} catch (e) {
  console.error("PLUGIN_LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(3)
}

if (mode === "hooks") {
  const factoryName = process.argv[4]
  const directory = process.argv[5]
  // $ is never exercised at instantiation time (hooks only capture it); a
  // throwing stub makes any unexpected use visible.
  const dollarStub = () => { throw new Error("unexpected $ call at instantiation") }
  const factory = factoryName === "default" ? mod.default : mod[factoryName]
  if (typeof factory !== "function") {
    console.error("NO_FACTORY: " + factoryName)
    process.exit(2)
  }
  const plugin = factoryName === "default"
    ? await factory()
    : await factory({ client: null, $: dollarStub, directory })
  process.stdout.write(JSON.stringify({ hooks: Object.keys(plugin) }))
} else if (mode === "exports") {
  const named = Object.keys(mod).filter((k) => k !== "default")
  const calls = {}
  const garbageCtx = { client: null, $: () => {}, directory: "" }
  for (const name of named) {
    if (name === "OmtEnforcer") continue // the factory — exercised by hooks mode
    const fn = mod[name]
    if (typeof fn !== "function") {
      calls[name] = { ctx: "not-a-function", undef: "not-a-function", braces: "not-a-function" }
      continue
    }
    const attempt = (arg) => {
      try { fn(arg); return "ok" }
      catch (e) { return "ERR: " + (e?.message || String(e)).split("\n")[0] }
    }
    calls[name] = { ctx: attempt(garbageCtx), undef: attempt(undefined), braces: attempt({}) }
  }
  process.stdout.write(JSON.stringify({ named, calls }))
} else {
  console.error("USAGE: _plugin_surface_runner.mjs hooks '<abs>' '<factory>' '<tmpdir>' | exports '<abs>'")
  process.exit(2)
}

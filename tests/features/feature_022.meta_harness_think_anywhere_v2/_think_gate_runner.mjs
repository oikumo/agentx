// Test fixture: invokes the REAL think-gate helpers exported from
// .opencode/plugin/omt_enforcer.ts so Python tests can assert on the actual
// gate logic (not a reimplementation).
//
// feature_022 extension: "file-thoughts" mode exposes fileThoughtsIn(absPath)
// so tests can assert the think-gate sees exactly the anchored TA: lines
// (design_001 §1: the gate must be blind to prose and never blind to what
// omt_think wrote).
//
// feature_022 Tier B1+D1 extension: "after-hook" mode instantiates the REAL
// OmtEnforcer with an isolated directory (tmpdir ledger) and drives the real
// "tool.execute.after" hook through a BATCH of fake {input, output} calls on
// ONE plugin instance — the injectedThisSession Map is process-lifetime
// state, so once-per-session assertions need several calls in one process
// (design_002 §2-§3 — no opencode server needed). Prints the mutated outputs.
//
// feature_022 Tier C extension: "consulted" gains a root-injected JSON form —
// consulted '<json:{session?,rel?,risk?,root?}>' calls the REAL
// hasConsultedThoughts(session, rel, {risk, root}) and prints {consulted}
// (design_003 §2.2; the no-arg form keeps the old exported-check behavior).
// "before-hook" mode drives the REAL OmtEnforcer "tool.execute.before" through
// a BATCH of fake {input, output} calls on ONE plugin instance with an
// isolated directory (tmpdir ledger/index); each call prints {blocked:false}
// or {blocked:true, message} on OmtBlock (design_003 §3 — no opencode server).
//
// feature_023 Tier 1 extension: "after-hook-edit" mode drives the REAL
// tool.execute.after EDIT path (MVC++ post-edit gate) with the throwing
// dollarStub replaced per-batch by a canned-mvc stub returning injected
// findings — no real mvc_check subprocess, deterministic hard-block assertions
// (design_001 §2.3). Each call prints {blocked:false} or {blocked:true,message}
// on OmtBlock.
//
// Usage:
//   node --experimental-strip-types _think_gate_runner.mjs decide '<json:opts>'
//   node --experimental-strip-types _think_gate_runner.mjs consulted ['<json:{session?,rel?,risk?,root?}>']
//   node --experimental-strip-types _think_gate_runner.mjs file-thoughts '<absPath>'
//   node --experimental-strip-types _think_gate_runner.mjs after-hook '<directory>' '<json:[{input,output},...]>'
//   node --experimental-strip-types _think_gate_runner.mjs after-hook-edit '<directory>' '<json:{findings,calls}>'
//   node --experimental-strip-types _think_gate_runner.mjs before-hook '<directory>' '<json:[{input,output},...]>'
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
  const arg = process.argv[3]
  if (!arg) {
    // Back-compat: check whether hasConsultedThoughts is exported; report presence.
    process.stdout.write(JSON.stringify({ exported: typeof mod.hasConsultedThoughts === "function" }))
  } else {
    // Tier C: root-injected real call — hasConsultedThoughts(session, rel, {risk, root}).
    const { session, rel, risk, root } = JSON.parse(arg)
    const consulted = mod.hasConsultedThoughts(session, rel, { risk, root })
    process.stdout.write(JSON.stringify({ consulted }))
  }
} else if (mode === "file-thoughts") {
  const absPath = process.argv[3]
  process.stdout.write(JSON.stringify(mod.fileThoughtsIn(absPath)))
} else if (mode === "after-hook") {
  const directory = process.argv[3]
  const calls = JSON.parse(process.argv[4]) // [{input, output}, ...]
  // $ is never exercised by the read-injection branch (nor by the edit path
  // for non-src files); a throwing stub makes any unexpected use visible.
  const dollarStub = () => { throw new Error("unexpected $ call in after-hook test") }
  const plugin = await mod.OmtEnforcer({ client: null, $: dollarStub, directory })
  const results = []
  for (const call of calls) {
    await plugin["tool.execute.after"](call.input, call.output)
    results.push(call.output)
  }
  process.stdout.write(JSON.stringify(results))
} else if (mode === "after-hook-edit") {
  const directory = process.argv[3]
  const { findings, calls } = JSON.parse(process.argv[4]) // {findings: [...], calls: [{input,output},...]}
  // Canned-mvc stub (feature_023 §2.3): lintFindings' `$`uv run mvc_check …``
  // chain (.cwd().quiet().nothrow()) resolves to the injected findings; the
  // same stub also satisfies the TDD after-edit call (action undefined → no-op).
  const mvcStub = (strings, ...vals) => ({ cwd: () => ({ quiet: () => ({ nothrow: async () =>
    ({ stdout: Buffer.from(JSON.stringify({ findings })) }) }) }) })
  const plugin = await mod.OmtEnforcer({ client: null, $: mvcStub, directory })
  const results = []
  for (const call of calls) {
    try {
      await plugin["tool.execute.after"](call.input, call.output)
      results.push({ blocked: false })
    } catch (e) {
      results.push({ blocked: true, message: String(e?.message || e) })
    }
  }
  process.stdout.write(JSON.stringify(results))
} else if (mode === "before-hook") {
  const directory = process.argv[3]
  const calls = JSON.parse(process.argv[4]) // [{input, output}, ...]
  // $ is never exercised for plain non-src/non-tests files (no tdd/lint path);
  // a throwing stub makes any unexpected use visible.
  const dollarStub = () => { throw new Error("unexpected $ call in before-hook test") }
  const plugin = await mod.OmtEnforcer({ client: null, $: dollarStub, directory })
  const results = []
  for (const call of calls) {
    try {
      await plugin["tool.execute.before"](call.input, call.output)
      results.push({ blocked: false })
    } catch (e) {
      results.push({ blocked: true, message: String(e?.message || e) })
    }
  }
  process.stdout.write(JSON.stringify(results))
} else {
  console.error("USAGE: _think_gate_runner.mjs decide '<json>' | consulted ['<json>'] | file-thoughts '<absPath>' | after-hook '<directory>' '<json:[...]>' | after-hook-edit '<directory>' '<json:{findings,calls}>' | before-hook '<directory>' '<json:[...]>'")
  process.exit(2)
}

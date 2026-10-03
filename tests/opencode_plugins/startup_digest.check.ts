// startup_digest.check.ts — bun behavioral probe for feature_138.
//
// Usage:
//   bun startup_digest.check.ts <compiled.md> <probeJson|-> <digestJson|->
// Prints JSON {md_full, md_digest, agent_full, agent_digest} where a side is
// null when its input is `-`. Exit nonzero with {error} on failure.
// Requires startup_table.ts to export parseCompiled, normalizeProbe,
// renderTables (feature_138 testability seam — additive, runtime-neutral).
import { readFileSync } from "node:fs"
import { createRequire } from "node:module"

const req = createRequire(process.cwd() + "/plugins/startup_table.ts")
const mod = req(process.cwd() + "/plugins/startup_table.ts") as any

const [compiledPath, probeArg, digestArg, resumeArg] = process.argv.slice(2)
try {
  const text = readFileSync(compiledPath, "utf8")
  const parsed = mod.parseCompiled(text)
  const out: any = { md_full: null, md_digest: null, agent_full: null, agent_digest: null, md_resume: null, agent_resume: null }
  let probe: any = null
  if (digestArg && digestArg !== "-") {
    probe = mod.normalizeProbe(digestArg)
  } else if (probeArg && probeArg !== "-") {
    probe = JSON.parse(probeArg)
  }
  if (probeArg && probeArg !== "-") {
    const probeFull = JSON.parse(probeArg)
    const r = mod.renderTables(parsed, probeFull)
    out.md_full = r.markdown
    out.agent_full = r.agent
  }
  if (digestArg && digestArg !== "-") {
    const r = mod.renderTables(parsed, probe)
    out.md_digest = r.markdown
    out.agent_digest = r.agent
  }
  if (resumeArg && resumeArg !== "-") {
    const resume = mod.normalizeResume(resumeArg)
    const r = mod.renderTables(parsed, probe, undefined, resume)
    out.md_resume = r.markdown
    out.agent_resume = r.agent
  }
  console.log(JSON.stringify(out))
} catch (e: any) {
  console.log(JSON.stringify({ error: String(e?.message ?? e) }))
  process.exit(1)
}

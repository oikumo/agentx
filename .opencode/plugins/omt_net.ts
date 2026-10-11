// OMT++ omt_net — meta-harness concurrency net (feature_039.adaptive_net_engine
// + feature_040.net_composition_supervisor + feature_042.goal_net_synthesis
// + feature_044.mined_behavioral_net + feature_050.net_as_gate
// + feature_081.worktree_execution_isolation)
// Thin proxy around scripts/omt/net_check.py (the state machine lives in
// Python, scripts/omt/net/; D2 — no src/ import). One registered tool, closed
// op enum per IDEA-002 v4 §5.0 (probe|fire|splice|sync|synthesize|invariant|gate;
// gate live since feature_050: net permission-to-act for enforcer).
// R8 (OMT-HDL-1): the tool is built inside createNetTool() so its description
// resolves from the compiled IR AFTER initOmtShared ran (module-level tool()
// would read the IR under the pre-init cwd — F2/F17).
//
// V2 (migrate-v1): Plugin.define({id, setup}) + ctx.tool.transform(editor.add)
// with JSON-Schema input and {content} results. Context: directory→
// ctx.location.directory, session→context.sessionID. `$` never used here
// (node:child_process directly).

import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { initOmtShared, repoRoot, irToolDescription, argvValue } from "../lib/omt_shared"

const OPS = ["probe", "fire", "invariant", "splice", "sync", "synthesize", "mine", "gate", "claim", "release", "transfer", "checkpoint"]

// Per-op argv whitelist mirroring the cli.py subparser declarations
// (cross-source pinned @ tests/harness_meta/omt/test_omt_net_plugin_args.py).
const OP_ARGS: Record<string, readonly string[]> = {
  probe: ["expected_revision"],
  fire: ["transition", "reasoning", "session", "expected_revision"],
  splice: ["mode", "mutation", "subnet", "reasoning", "session", "feature", "expected_revision"],
  sync: ["reasoning", "session", "direction", "work_md", "expected_revision"],
  invariant: ["expected_revision"],
  synthesize: ["mutation", "reasoning", "session", "feature", "expected_revision"],
  mine: ["mutation", "reasoning", "session", "feature", "expected_revision"],
  gate: ["path", "session", "expected_revision", "task_id", "owner", "generation"],
  claim: ["task_id", "owner", "reasoning", "session", "expected_revision"],
  release: ["task_id", "owner", "reasoning", "session", "expected_revision"],
  transfer: ["task_id", "owner", "reasoning", "session", "expected_revision"],
  checkpoint: ["task_id", "generation", "mutation", "reasoning", "session", "expected_revision"],
}

function createNetTool() {
  return {
    name: "omt_net",
    description: irToolDescription("omt_net", "Concurrency net + git-plane derived view — SSOT (IDEA-002 v4 §5.0 closed enum, no new op). op=probe(marking+enabled+advice+git_plane) | fire(transition,reasoning,session?) | splice(mode,mutation?,subnet?,reasoning) | sync(bootstrap+proposal, D4) | invariant(invariants+net↔ledger↔git drift) | synthesize(template→splice proposal, D4) | mine(ledger→net draft, D4) | gate(path,session?) | claim(task,owner?,gen-fenced,branch=prefix+task_id)."),
// TA: gotcha: gotcha (feature_050 wrap-up): TS fallback seed must BYTE-match the .omt @tool omt_net payload — currently 1B off: seed says gate(path,session). but .omt payload says gate(path,session?). → harnessc "TS fallback seed drifted" error (358 vs 359 B); add the ? to the seed string
    input: {
      type: "object",
      properties: {
        op: { type: "string", description: "probe|fire|splice|sync|invariant|synthesize|mine|gate|claim|release|transfer|checkpoint" },
        transition: { type: "string", description: "fire: transition name" },
        reasoning: { type: "string", description: "fire/splice: why (audit, D4)" },
        session: { type: "string", description: "session id (default: context)" },
        max_states: { type: "number", description: "probe: analyzer exploration cap (default 1000; 0=startup brief)" },
        mode: { type: "string", description: "splice: add|remove|disable|undo|repair" },
        mutation: { type: "string", description: "splice: JSON mutation string (add_places/add_transitions/add_arcs | remove_places/remove_transitions/token_policy/reroute)" },
        subnet: { type: "string", description: "splice disable: subnet key, e.g. feature_039" },
        feature: { type: "string", description: "splice: owning feature slug (audit)" },
        direction: { type: "string", description: "sync: proposal|net_to_md|md_to_net_propose" },
        dry_run: { type: "boolean", description: "sync: dry-run render/propose without writing" },
        path: { type: "string", description: "gate: target path being edited" },
        expected_revision: { type: "number", description: "all ops: stale-rev guard (feature_050)" },
        task_id: { type: "string", description: "claim: task id" },
        owner: { type: "string", description: "claim: task owner" },
        generation: { type: "number", description: "claim: held generation" },
        work_md: { type: "string", description: "sync: work md" },
        taskId_alias: { type: "string", description: "unused (kept for schema parity)" },
      },
      required: [],
      additionalProperties: false,
    },
    async execute(args: any, context: any) {
      const op = String(args?.op ?? "")
      if (!OPS.includes(op)) {
        return { content: JSON.stringify({
          ok: false, error: "unknown_op", op,
          message: `want ${OPS.join("|")}`,
        }) }
      }
      const argv = ["run", "scripts/omt/net_check.py", op]
      // TA: why: argv is built from the PER-OP OP_ARGS whitelist mirroring cli.py's
      // subparser flags — the pre-feature_046 fixed list appended --session to EVERY
      // op, and probe/invariant/synthesize declare no --session → argparse exit 2
      // (feature_039 latent bug, surfaced by the feature_041 R4 dogfood 2026-08-30).
      // The session fallback stays scoped INSIDE the whitelist loop; max_states is
      // probe-only and gated below. Pinned cross-source @ test_omt_net_plugin_args.py.
      for (const k of OP_ARGS[op]) {
        let v: any = (args as any)?.[k]
        if (k === "session" && (v === undefined || v === null || v === "")) v = context?.sessionID
        if (v !== undefined && v !== null && v !== "")
          // feature_027 + feature_136: the SDK coerces JSON-looking strings fed
          // to a tool string arg into actual JS arrays/objects;
          // argvValue re-serializes them back to valid JSON (mutation et al.).
          argv.push(`--${k}`, argvValue(v))
      }
      if (op === "probe" && args?.max_states !== undefined && args?.max_states !== null)
        argv.push("--max-states", String(args.max_states))
      if (op === "sync" && (args as any)?.dry_run === true) argv.push("--dry-run")
      try {
        const out = execFileSync("uv", argv, {
          cwd: repoRoot(), encoding: "utf8", timeout: 30000,
          stdio: ["ignore", "pipe", "pipe"],
        })
        return { content: String(out).trim() } // the CLI prints exactly one JSON envelope
      } catch (e: any) {
        // non-zero exit: the CLI's error envelope is on stdout — surface it
        const stdout = String(e?.stdout || "").trim()
        if (stdout) return { content: stdout }
        return { content: JSON.stringify({ ok: false, error: "engine_error", op, message: String(e?.message || e) }) }
      }
    },
  }
}

// V2 entrypoint (migrate-v1): stable id + setup registers the tool transform.
// Local discovery loads .opencode/plugins/*.ts automatically (plugins page:
// direct .ts/.js files under every discovered .opencode/plugins/).
export default Plugin.define({
  id: "omt-net",
  async setup(ctx) {
    initOmtShared(ctx.location.directory)
    const omt_net = createNetTool()
    await ctx.tool.transform((editor) => {
      editor.add(omt_net as any)
    })
  },
})

#!/usr/bin/env bun
/** Task-cost benchmark trial runner (feature_093.task_cost_benchmark).
 *
 * ONE process per task = ONE agent session. Replicates the opencode hook bus:
 * shared EnforcerEnv + createSessionState() across gates and tools (the real
 * single-env session model); per step navTrack+kbTrack → runBeforeGatesDry →
 * blocked ⇒ NO effect + NO after-chain; else apply effect →
 * sessionBootstrap/trackRead/injectThoughtsOnRead/lspAfterEdit/runAfterGates.
 *
 * omt_phase/skip/complete/tdd via createPhaseTools/createTddTools(env);
 * omt_status/think/nav/kb/net via plugin defaults rooted at the sandbox.
 * Deny model (opencode.jsonc bash/read) enforced driver-side pre-spawn.
 * Transcript JSON on stdout via console.log(JSON.stringify).
 *
 * Usage: bun probe.ts --sandbox <dir> --spec <spec.json> [--remove <gate-id>]
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs";
import { join, dirname, basename, isAbsolute, resolve } from "node:path";
import { $ } from "bun";
import { initOmtShared, loadIr } from "../../../.opencode/lib/omt_shared";
import {
  createSessionState,
  makeSafeLog,
  makeNotify,
} from "../../../.opencode/lib/enforcer/session_state";
import {
  navTrack,
  kbTrack,
  sessionBootstrap,
  trackRead,
} from "../../../.opencode/lib/enforcer/nav_gate";
import {
  runBeforeGatesDry,
  runAfterGates,
} from "../../../.opencode/lib/enforcer/gate_driver";
import { createPhaseTools } from "../../../.opencode/lib/enforcer/phase_gate";
import { createTddTools } from "../../../.opencode/lib/enforcer/tdd_hats";
import { injectThoughtsOnRead } from "../../../.opencode/lib/enforcer/think_gate";
import { lspAfterEdit } from "../../../.opencode/lib/enforcer/lsp_filter";

function arg(name: string): string | null {
  const i = process.argv.indexOf(name);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : null;
}

// Scrub process-level overrides that beat the injected root (TA:48/TA:126).
for (const k of ["OMT_NET_DIR", "OMT_LEDGER_PATH", "OMT_COORDINATION_ROOT"]) {
  delete process.env[k];
}

const sandbox = arg("--sandbox") || "";
const specPath = arg("--spec") || "";
const removeGate = arg("--remove") || null;
if (!sandbox || !specPath) {
  console.error("usage: probe.ts --sandbox <dir> --spec <spec.json> [--remove <gate>]");
  process.exit(2);
}

initOmtShared(sandbox);

const spec = JSON.parse(readFileSync(specPath, "utf8"));
const task = spec.task;
const deny = spec.deny || { bash_deny: [], read_deny: [] };
const defaultSession: string = task.session || `ses_${task.id}`;

const fakeClient: any = { $ };
const safeLog = makeSafeLog(fakeClient);
const env: any = {
  client: fakeClient,
  $,
  directory: sandbox,
  state: createSessionState(),
  safeLog,
  notify: makeNotify(fakeClient, safeLog),
};

const phaseTools: any = createPhaseTools(env);
const tddTools: any = createTddTools(env);

// Plugin-default tools rooted at the sandbox (each builds its own internal
// env; cross-plugin state flows via ledger + trackers, which the probe calls
// itself — TA:111).
const LIVE = process.cwd();
async function loadPluginTool(rel: string, key: string): Promise<any> {
  const mod = await import(join(LIVE, rel));
  const { tool } = await mod.default({ directory: sandbox, worktree: sandbox });
  return tool[key];
}
const toolStatus = await loadPluginTool(".opencode/plugins/omt_status.ts", "omt_status");
const toolThink = await loadPluginTool(".opencode/plugins/omt_think.ts", "omt_think");
const toolNav = await loadPluginTool(".opencode/plugins/omt_nav.ts", "omt_nav");
const toolKb = await loadPluginTool(".opencode/plugins/omt_kb_nav.ts", "omt_kb_nav");
const toolNet = await loadPluginTool(".opencode/plugins/omt_net.ts", "omt_net");

// Removal experiment: bench-side IR filter (TA:113), zero production changes.
let irOverride: any = undefined;
if (removeGate) {
  const ir = loadIr();
  if (ir && Array.isArray(ir.gates)) {
    irOverride = { ...ir, gates: ir.gates.filter((g: any) => g.id !== removeGate) };
  }
}

function globToReg(pat: string): RegExp {
  // Allow-list patterns use `*` globs (opencode.jsonc). Escape, then * → .*.
  const esc = pat.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
  return new RegExp(`^${esc}$`);
}
function bashDenied(cmd: string): boolean {
  const list: string[] = deny.bash_deny || [];
  return list.some((p: string) => globToReg(p).test(cmd));
}
function readDenied(rel: string): boolean {
  const list: string[] = deny.read_deny || [];
  const base = basename(rel);
  return list.some((p: string) => {
    const re = globToReg(p);
    return re.test(rel) || re.test(base) || re.test(`/${rel}`) || re.test(`./${rel}`);
  });
}
function isRefusalText(s: string): boolean {
  return s.includes("❌") || s.includes("⛔") || s.includes('"ok": false') || s.includes('"ok":false');
}
function absOf(rel: string): string {
  return isAbsolute(rel) ? rel : resolve(sandbox, rel);
}
function readSandbox(rel: string, offset?: number, limit?: number): string {
  const abs = absOf(rel);
  const raw = readFileSync(abs, "utf8");
  const lines = raw.split("\n");
  const off = Math.max(0, (offset ?? 1) - 1);
  const sliced = limit ? lines.slice(off, off + limit) : lines.slice(off);
  const text = sliced.join("\n");
  return text.slice(0, 64 * 1024);
}

type Rec = Record<string, any>;
const records: Rec[] = [];
const byId = new Map<string, Rec>();

function toolNameFor(step: any): string {
  if (step.kind === "omt") return String(step.args?.tool || step.args?.name || "omt_unknown");
  if (step.kind === "edit" || step.kind === "write") return step.kind;
  if (step.kind === "read") return "read";
  if (step.kind === "search") return "search";
  if (step.kind === "bash" || step.kind === "verify") return "bash";
  return step.kind;
}
function relFor(step: any): string | null {
  if (step.kind === "edit" || step.kind === "write" || step.kind === "read") {
    return String(step.args?.path || "") || null;
  }
  if (step.kind === "search") {
    return step.args?.path ? String(step.args.path) : null;
  }
  return null;
}

async function execOmt(toolName: string, args: any, session: string): Promise<string> {
  const ctx = { sessionID: session };
  if (toolName === "omt_phase") return String(await phaseTools.omt_phase.execute(args, ctx));
  if (toolName === "omt_skip") return String(await phaseTools.omt_skip.execute(args, ctx));
  if (toolName === "omt_complete") return String(await phaseTools.omt_complete.execute(args, ctx));
  if (toolName === "omt_tdd") {
    // SDK array-coercion guard lives in tdd_hats; pass behaviors through as-is.
    return String(await tddTools.omt_tdd.execute(args, ctx));
  }
  if (toolName === "omt_status") return JSON.stringify(await toolStatus.execute(args, ctx));
  if (toolName === "omt_think") return JSON.stringify(await toolThink.execute(args, ctx));
  if (toolName === "omt_nav") return JSON.stringify(await toolNav.execute(args, ctx));
  if (toolName === "omt_kb_nav") return JSON.stringify(await toolKb.execute(args, ctx));
  if (toolName === "omt_net") return JSON.stringify(await toolNet.execute(args, ctx));
  if (toolName === "omt_q") {
    const m = await import(join(LIVE, ".opencode/plugins/omt_q.ts"));
    const { tool } = await m.default({ directory: sandbox, worktree: sandbox });
    const r = await tool.omt_q.execute(args, ctx);
    return typeof r === "string" ? r : JSON.stringify(r);
  }
  return `⛔ unknown omt tool ${toolName}`;
}

for (const step of task.steps || []) {
  const session: string = step.session || defaultSession;
  const kind: string = step.kind;
  const tool = toolNameFor(step);
  const rel = relFor(step);
  const abs = rel ? absOf(rel) : null;
  const argsBytes = Buffer.byteLength(JSON.stringify(step.args || {}), "utf8");
  const t0 = Date.now();
  let refused = false;
  let blockedBy: string[] = [];
  let resultText = "";
  let rc: number | null = null;
  let ok: boolean | null = null;

  const runGates = async (inArgs: any, outArgs: any): Promise<{ blocked: boolean; by: string[] }> => {
    const input = { tool, sessionID: session, args: inArgs };
    const output = { args: outArgs };
    try {
      await navTrack(env, session, input);
    } catch { /* trackers fail open */ }
    try {
      await kbTrack(env, session, input);
    } catch { /* trackers fail open */ }
    const ctx: any = { env, session, tool, input, output, rel, abs, memo: new Map() };
    const decisions = await runBeforeGatesDry(ctx, irOverride);
    const blocks = decisions.filter((d: any) => d.blocked);
    return { blocked: blocks.length > 0, by: blocks.map((d: any) => d.gate_id) };
  };
  const runAfter = async (inArgs: any, outText: string, rawPath: string | null) => {
    if (!rawPath) return;
    const input = { tool, sessionID: session, args: inArgs };
    const output: any = { output: outText, metadata: {} };
    try {
      await sessionBootstrap(env, input, output);
    } catch { /* fail open */ }
    try {
      await trackRead(env, session, input);
    } catch { /* fail open */ }
    try {
      await injectThoughtsOnRead(env, input, output);
      const injected = (output as any).injectedThoughts || (output as any).thoughts;
      if (injected) resultText += `\n[thoughts:${JSON.stringify(injected).length}B]`;
    } catch { /* fail open */ }
    try {
      await lspAfterEdit(env, input, output);
    } catch { /* fail open */ }
    try {
      await runAfterGates(env, session, input, output, rawPath);
    } catch (e: any) {
      resultText += `\nafter-chain: ${String(e?.message || e).slice(0, 300)}`;
    }
  };

  if (kind === "assert") {
    const target = byId.get(String(step.args?.step || ""));
    const contains = step.args?.contains;
    const wantRcZero = step.args?.rc_zero;
    const wantRcNonZero = step.args?.rc_nonzero;
    const wantOk = step.args?.ok;
    const wantRefused = step.args?.refused;
    let pass = false;
    if (target) {
      const tText: string = String(target.resultText || "");
      if (contains !== undefined) pass = tText.includes(String(contains));
      else if (wantRcZero !== undefined) pass = (target.rc ?? 1) === 0;
      else if (wantRcNonZero !== undefined) pass = (target.rc ?? 0) !== 0;
      else if (wantOk !== undefined) pass = Boolean(target.ok) === Boolean(wantOk);
      else if (wantRefused !== undefined) pass = Boolean(target.refused) === Boolean(wantRefused);
      else pass = true;
    }
    ok = pass;
    refused = false;
    resultText = pass ? "assert pass" : `assert FAIL on ${step.args?.step}`;
  } else if (kind === "omt") {
    const toolName = tool;
    const oargs = (step.args?.arguments || {}) as any;
    const g = await runGates(oargs, oargs);
    if (g.blocked) {
      refused = true;
      blockedBy = g.by;
      resultText = `blocked by ${g.by.join(",")}`;
    } else {
      try {
        resultText = await execOmt(toolName, oargs, session);
      } catch (e: any) {
        resultText = String(e?.message || e);
      }
      if (isRefusalText(resultText)) refused = true;
      // omt tools are not file edits: still run the session bootstrap once
      // per session (first-result bytes are real hook behavior).
      try {
        await sessionBootstrap(env, { tool, sessionID: session, args: oargs }, { output: resultText });
      } catch { /* fail open */ }
      // omt_think list consults + kb nav consults are tracked via the
      // before-chain trackers already; think consults also write ledger
      // records inside the tool itself (hasConsultedThoughts).
    }
  } else if (kind === "read") {
    const p = String(step.args?.path || "");
    if (readDenied(p)) {
      refused = true;
      blockedBy = ["config_deny:read"];
      resultText = `⛔ read denied by opencode.jsonc: ${p}`;
    } else {
      const g = await runGates({ path: p }, { path: p });
      if (g.blocked) {
        refused = true;
        blockedBy = g.by;
        resultText = `blocked by ${g.by.join(",")}`;
      } else {
        try {
          resultText = readSandbox(p, step.args?.offset, step.args?.limit);
        } catch (e: any) {
          resultText = `read error: ${String(e?.message || e).slice(0, 300)}`;
        }
        await runAfter({ path: p }, resultText, null);
        // trackRead needs input.tool === read shape; runAfter already called it with null raw (skipped) — call explicitly:
        try {
          await trackRead(env, session, { tool: "read", sessionID: session, args: { path: p } });
        } catch { /* fail open */ }
      }
    }
  } else if (kind === "search") {
    const pattern = String(step.args?.pattern || step.args?.query || "");
    const g = await runGates({ pattern }, { query: pattern });
    if (g.blocked) {
      refused = true;
      blockedBy = g.by;
      resultText = `blocked by ${g.by.join(",")}`;
    } else {
      resultText = `search:${pattern}:0 hits (bench stub)`;
    }
  } else if (kind === "bash" || kind === "verify") {
    const cmd = String(step.args?.command || "");
    if (bashDenied(cmd)) {
      refused = true;
      blockedBy = ["config_deny:bash"];
      resultText = `⛔ bash denied by opencode.jsonc: ${cmd}`;
      rc = 1;
    } else {
      const g = await runGates({ command: cmd }, { command: cmd });
      if (g.blocked) {
        refused = true;
        blockedBy = g.by;
        resultText = `blocked by ${g.by.join(",")}`;
      } else {
        try {
          const proc: any = ($ as any)`sh -c ${cmd}`;
          const done = proc.cwd(sandbox).quiet().nothrow();
          const res = await done;
          const out = String(res.stdout?.toString?.() || res.text?.() || "");
          const err = String(res.stderr?.toString?.() || "");
          rc = Number(res.exitCode ?? 0);
          resultText = (out + (err ? `\nSTDERR:\n${err}` : "")).slice(0, 8192);
          if (!resultText) resultText = `(rc=${rc})`;
        } catch (e: any) {
          resultText = `spawn error: ${String(e?.message || e).slice(0, 300)}`;
          rc = 1;
        }
      }
    }
    if (kind === "verify") {
      if (step.expect === "pass") ok = rc === 0;
      else if (step.expect === "fail") ok = rc !== 0 && rc !== null;
    }
  } else if (kind === "edit" || kind === "write") {
    const p = String(step.args?.path || "");
    const outArgs: any = { path: p, filePath: p, file: p };
    const g = await runGates({ path: p }, outArgs);
    if (g.blocked) {
      refused = true;
      blockedBy = g.by;
      resultText = `blocked by ${g.by.join(",")}`;
    } else {
      try {
        const absP = absOf(p);
        if (kind === "edit") {
          if (step.args?.append !== undefined) {
            const cur = existsSync(absP) ? readFileSync(absP, "utf8") : "";
            writeFileSync(absP, cur + String(step.args.append), "utf8");
            resultText = `appended ${String(step.args.append).length}B to ${p}`;
          } else if (step.args?.content !== undefined) {
            mkdirSync(dirname(absP), { recursive: true });
            writeFileSync(absP, String(step.args.content), "utf8");
            resultText = `wrote ${String(step.args.content).length}B to ${p}`;
          } else {
            const oldS = String(step.args?.old ?? "");
            const newS = String(step.args?.new ?? "");
            const cur = readFileSync(absP, "utf8");
            if (!cur.includes(oldS)) {
              resultText = `edit no-op (anchor not found) in ${p}`;
            } else {
              writeFileSync(absP, cur.replace(oldS, newS), "utf8");
              resultText = `edited ${p}`;
            }
          }
        } else {
          if (step.args?.append !== undefined) {
            const cur = existsSync(absP) ? readFileSync(absP, "utf8") : "";
            mkdirSync(dirname(absP), { recursive: true });
            writeFileSync(absP, cur + String(step.args.append), "utf8");
            resultText = `appended ${String(step.args.append).length}B to ${p}`;
          } else {
            mkdirSync(dirname(absP), { recursive: true });
            writeFileSync(absP, String(step.args?.content ?? ""), "utf8");
            resultText = `wrote ${String(step.args?.content ?? "").length}B to ${p}`;
          }
        }
      } catch (e: any) {
        resultText = `effect error: ${String(e?.message || e).slice(0, 300)}`;
      }
      await runAfter({ path: p, filePath: p }, resultText, p);
    }
  } else {
    resultText = `unknown kind ${kind}`;
  }

  const durationMs = Date.now() - t0;
  const resultBytes = Buffer.byteLength(resultText, "utf8");
  const rec: Rec = {
    id: step.id,
    kind,
    role: step.role || "work",
    expect: step.expect || "ok",
    session,
    gate: step.gate ?? null,
    tag: step.tag ?? null,
    args_bytes: argsBytes,
    result_bytes: resultBytes,
    duration_ms: kind === "verify" ? durationMs : 0,
    refused,
    blocked_by: blockedBy,
    rc,
    ok,
    note: step.note || "",
    resultText: resultText.slice(0, 2000),
  };
  records.push(rec);
  byId.set(String(step.id), rec);
  // Keep stat calls honest (mtime use) without affecting the transcript.
  try {
    if (rel && abs) statSync(abs);
  } catch { /* ignore */ }
}

const out = {
  task_id: task.id,
  session: defaultSession,
  sandbox,
  removal: removeGate,
  steps: records.map(({ resultText, ...keep }: any) => keep),
};
console.log(JSON.stringify(out));

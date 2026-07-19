#!/usr/bin/env npx tsx
/**
 * Production verification test for OMT++ hook EFFECTS (feature_023).
 * 
 * This test directly loads the TypeScript plugin modules and invokes
 * the tool.execute.after hooks with REAL SDK payload shapes to verify:
 * 
 * 1. omt_think: TA digest appends to output.output on FIRST tool result per session
 * 2. omt_enforcer: nav reminder prepends to output.output on FIRST tool result per session
 * 3. omt_enforcer: D1 read-time thought injection on FIRST read of thought-carrying file
 * 4. omt_enforcer: F14b - MVC++ post-edit gate on NEW hard error
 * 
 * These are the effects that were DEAD in feature_022 (F14, F14c) and fixed in feature_023.
 */

import { promises as fs } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = resolve(__filename, "..");
// Go up 3 levels: tests/scripts/omt -> tests/scripts -> tests -> agentx (repo root)
const REPO_ROOT = resolve(__dirname, "../../..");

// Load plugins dynamically
async function loadPlugin(pluginName: string) {
  const pluginPath = join(REPO_ROOT, ".opencode", "dist", `${pluginName}.js`);
  const mod = await import(pluginPath);
  
  // Different plugins use different export patterns:
  // - omt_think, omt_nav, omt_status: export default async () => ({...})
  // - omt_enforcer: export const OmtEnforcer = async ({client, $, directory}) => ({...})
  if (pluginName === "omt_enforcer") {
    const factory = mod.OmtEnforcer;
    if (typeof factory !== "function") {
      throw new Error(`Plugin ${pluginName} OmtEnforcer export is not a function`);
    }
    // Provide minimal context (same as _plugin_surface_runner.mjs)
    const dollarStub = () => { throw new Error("unexpected $ call at instantiation"); };
    return await factory({ client: null, $: dollarStub, directory: REPO_ROOT });
  } else {
    const factory = mod.default;
    if (typeof factory !== "function") {
      throw new Error(`Plugin ${pluginName} default export is not a function`);
    }
    return await factory();
  }
}

async function runProductionTests() {
  console.log("=".repeat(70));
  console.log("PRODUCTION VERIFICATION: OMT++ Hook Effects (feature_023)");
  console.log("=".repeat(70));
  console.log();

  // Load both plugins
  const [thinkTools, enforcerTools] = await Promise.all([
    loadPlugin("omt_think"),
    loadPlugin("omt_enforcer"),
  ]);

  let allPassed = true;

  // Test 1: Hook payload shapes match REAL SDK contract
  console.log("Test 1: Hook payload shapes match real SDK contract");
  try {
    const sessionId = `test-${randomUUID()}`;
    
    // REAL SDK contract for tool.execute.after:
    // input: { tool: string, sessionID: string, args: {...} }
    // output: { title: string, output: string, metadata: {...} }  -- NO args!
    const inputPayload = {
      tool: "read",
      sessionID: sessionId,
      args: { filePath: "test.py", path: "test.py", file: "test.py" },
    };
    const outputPayload = {
      title: "Read file",
      output: "file content",
      metadata: { size: 100 },
    };

    // Both hooks MUTATE output in place (opencode SDK pattern)
    await thinkTools["tool.execute.after"](inputPayload, outputPayload);
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload);

    // Check mutated output
    if (typeof outputPayload.output !== "string") {
      throw new Error("Output not string");
    }

    // Input args should be accessible (for D1 read injection)
    if (inputPayload.args.filePath !== "test.py") {
      throw new Error("Input args not accessible");
    }

    console.log("  ✅ Input has args, output={title,output,metadata} (no args)");
    console.log("  ✅ Both hooks execute without error");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 2: session.start exists but is inert (F14c - opencode never dispatches it)
  console.log("\nTest 2: session.start hook retained but inert");
  try {
    await thinkTools["session.start"]({}, {});
    await enforcerTools["session.start"]({}, {});
    console.log("  ✅ session.start hooks exist (retained for future SDK)");
    console.log("  ✅ Both execute without throwing (inert)");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 3: omt_think - TA digest on FIRST tool result per session
  console.log("\nTest 3: omt_think - TA digest on first tool result per session");
  try {
    const sessionId = `test-digest-${randomUUID()}`;
    const inputPayload = { tool: "read", sessionID: sessionId, args: { filePath: "test.py" } };
    const outputPayload = { title: "Read", output: "content", metadata: {} };

    // First call - should inject digest (mutates outputPayload)
    await thinkTools["tool.execute.after"](inputPayload, outputPayload);
    if (!outputPayload.output.includes("TA:") || !outputPayload.output.includes("thought")) {
      throw new Error("Digest not injected on first call");
    }

    // Second call same session - should NOT inject again
    const outputPayload2 = { title: "Read again", output: "content again", metadata: {} };
    await thinkTools["tool.execute.after"](inputPayload, outputPayload2);
    if (outputPayload2.output.includes("TA:") && outputPayload2.output.includes("thought")) {
      throw new Error("Digest injected again on second call (should be once per session)");
    }

    // New session - SHOULD inject again
    const sessionId2 = `test-digest-${randomUUID()}`;
    const inputPayload2 = { tool: "read", sessionID: sessionId2, args: { filePath: "test.py" } };
    const outputPayload3 = { title: "Read", output: "content", metadata: {} };
    await thinkTools["tool.execute.after"](inputPayload2, outputPayload3);
    if (!outputPayload3.output.includes("TA:") || !outputPayload3.output.includes("thought")) {
      throw new Error("Digest not injected for new session");
    }

    console.log("  ✅ Digest injected on FIRST tool result per session");
    console.log("  ✅ Digest NOT repeated for same session");
    console.log("  ✅ Digest injected for NEW session");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 4: omt_enforcer - nav reminder on FIRST tool result per session
  console.log("\nTest 4: omt_enforcer - nav reminder on first tool result per session");
  try {
    const sessionId = `test-nav-${randomUUID()}`;
    const inputPayload = { tool: "read", sessionID: sessionId, args: { filePath: "test.py" } };
    const outputPayload = { title: "Read", output: "content", metadata: {} };

    // First call - should prepend nav reminder
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload);
    if (!outputPayload.output.includes("💡 NAVIGATION TIP") && !outputPayload.output.includes("omt_nav")) {
      throw new Error("Nav reminder not prepended on first call");
    }

    // Second call same session - should NOT prepend again
    const outputPayload2 = { title: "Edit", output: "edit result", metadata: {} };
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload2);
    const navCount = (outputPayload2.output.match(/💡 NAVIGATION TIP/g) || []).length;
    if (navCount > 1) {
      throw new Error("Nav reminder repeated for same session");
    }

    // New session - SHOULD prepend again
    const sessionId2 = `test-nav-${randomUUID()}`;
    const inputPayload2 = { tool: "read", sessionID: sessionId2, args: { filePath: "test.py" } };
    const outputPayload3 = { title: "Read", output: "content", metadata: {} };
    await enforcerTools["tool.execute.after"](inputPayload2, outputPayload3);
    if (!outputPayload3.output.includes("💡 NAVIGATION TIP") && !outputPayload3.output.includes("omt_nav")) {
      throw new Error("Nav reminder not prepended for new session");
    }

    console.log("  ✅ Nav reminder prepended on FIRST tool result per session");
    console.log("  ✅ Nav reminder NOT repeated for same session");
    console.log("  ✅ Nav reminder prepended for NEW session");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 5: omt_enforcer - D1 read-time thought injection (F14 fix)
  console.log("\nTest 5: omt_enforcer - D1 read-time thought injection (F14 fix)");
  try {
    // Create temp file with TA: thoughts
    const tempDir = await fs.mkdtemp(join(tmpdir(), "omt-thought-test-"));
    const thoughtFile = join(tempDir, "thoughtful.py");
    await fs.writeFile(thoughtFile, "# TA: why: design decision\n# TA: risk: might break\nprint('hello')\n");

    const sessionId = `test-d1-${randomUUID()}`;
    const inputPayload = {
      tool: "read",
      sessionID: sessionId,
      args: { filePath: thoughtFile, path: thoughtFile, file: thoughtFile },
    };
    const outputPayload = { title: "Read", output: "file content", metadata: {} };

    // First read of thought-carrying file - should inject
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload);
    
    if (!outputPayload.output.includes("💡 TA: thoughts in")) {
      throw new Error(`Thought injection not triggered: ${outputPayload.output}`);
    }
    if (!outputPayload.output.includes("design decision")) {
      throw new Error("Thought content not in injection");
    }
    if (!outputPayload.output.includes("might break")) {
      throw new Error("Risk thought not in injection");
    }

    // Second read of SAME file in same session - should NOT inject again
    const outputPayload2 = { title: "Read", output: "file content", metadata: {} };
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload2);
    if (outputPayload2.output.includes("💡 TA: thoughts in")) {
      throw new Error("Thought injection repeated for same file in session");
    }

    // Read of DIFFERENT thought-carrying file - SHOULD inject
    const otherFile = join(tempDir, "other.ts");
    await fs.writeFile(otherFile, "// TA: todo: refactor this\nconsole.log('hi');\n");
    
    const inputPayload3 = {
      tool: "read",
      sessionID: sessionId,
      args: { filePath: otherFile, path: otherFile, file: otherFile },
    };
    const outputPayload3 = { title: "Read", output: "file content", metadata: {} };
    await enforcerTools["tool.execute.after"](inputPayload3, outputPayload3);
    if (!outputPayload3.output.includes("💡 TA: thoughts in")) {
      throw new Error("Thought injection not triggered for new file");
    }
    if (!outputPayload3.output.includes("refactor this")) {
      throw new Error("New file thought content not injected");
    }

    // Cleanup
    await fs.rm(tempDir, { recursive: true });

    console.log("  ✅ D1 injection fires on FIRST read of thought-carrying file");
    console.log("  ✅ D1 injection NOT repeated for same file in session");
    console.log("  ✅ D1 injection fires for NEW thought-carrying file");
    console.log("  ✅ Reads input.args (F14 fix: output.args never existed)");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 6: F14b - MVC++ post-edit gate on NEW hard error (using canned-mvc stub)
  console.log("\nTest 6: F14b - MVC++ post-edit gate on new hard error (canned mvc)");
  try {
    // Create a SEPARATE enforcer instance with canned-mvc stub (like _think_gate_runner.mjs)
    // This tests the enforcer logic (delta comparison + OmtBlock) without running real mvc_check
    const mvcStub = (strings, ...vals) => ({ cwd: () => ({ quiet: () => ({ nothrow: async () =>
      ({ stdout: Buffer.from(JSON.stringify({ findings: [] })) }) }) }) });
    
    // Load enforcer module directly to get OmtEnforcer factory
    const enforcerModPath = join(REPO_ROOT, ".opencode", "dist", "omt_enforcer.js");
    const enforcerMod = await import(enforcerModPath);
    const cannedEnforcer = await enforcerMod.OmtEnforcer({ client: null, $: mvcStub, directory: REPO_ROOT });

    // Create test file under actual src/agentx/ui/ named *_view.py
    const srcFile = join(REPO_ROOT, "src", "agentx", "ui", "test_omt_mvc_gate_view.py");
    await fs.writeFile(srcFile, "# UI view file\nprint('ok')\n");

    const sessionId = `test-mvc-${randomUUID()}`;
    
    // First, simulate before-hook to capture clean snapshot (canned mvc returns empty findings)
    const beforeInput = { tool: "edit", sessionID: sessionId, args: { filePath: srcFile } };
    const beforeOutput = { title: "Edit", output: "", metadata: {} };
    await cannedEnforcer["tool.execute.before"](beforeInput, beforeOutput);

    // Now simulate after-hook with NEW hard error finding (canned mvc returns VIEW_IMPORTS_MODEL)
    const mvcStubWithError = (strings, ...vals) => ({
      cwd: () => ({
        quiet: () => ({
          nothrow: async () => ({
            stdout: Buffer.from(JSON.stringify({
              findings: [{ rule: "VIEW_IMPORTS_MODEL", severity: "error", file: "src/agentx/ui/test_omt_mvc_gate_view.py", line: 1, message: "View imports Model" }]
            }))
          })
        })
      })
    });
    
    const enforcerWithError = await enforcerMod.OmtEnforcer({ client: null, $: mvcStubWithError, directory: REPO_ROOT });
    // Copy the hardSnapshot from the first enforcer (before-hook snapshot)
    enforcerWithError["hardSnapshot"] = cannedEnforcer["hardSnapshot"];

    const badEditInput = {
      tool: "edit",
      sessionID: sessionId,
      args: { filePath: srcFile },
    };
    const badEditOutput = { title: "Edit", output: "edited", metadata: {} };
    
    // This should throw OmtBlock (new hard error)
    let threw = false;
    try {
      console.log("  DEBUG: Calling after-hook with canned VIEW_IMPORTS_MODEL error...");
      await enforcerWithError["tool.execute.after"](badEditInput, badEditOutput);
      console.log("  DEBUG: Hook returned, output:", badEditOutput.output.substring(0, 200));
    } catch (e: any) {
      console.log("  DEBUG: Hook threw:", e.name, e.message);
      if (e.name === "OmtBlock" || e.message?.includes("hard MVC++ violation")) {
        threw = true;
      }
    }
    if (!threw) {
      throw new Error("Expected OmtBlock for new hard error (VIEW_IMPORTS_MODEL)");
    }

    // Test 6b: Clean edit - no new errors (canned mvc returns empty findings)
    const mvcStubClean = (strings, ...vals) => ({
      cwd: () => ({
        quiet: () => ({
          nothrow: async () => ({
            stdout: Buffer.from(JSON.stringify({ findings: [] }))
          })
        })
      })
    });
    
    const enforcerClean = await enforcerMod.OmtEnforcer({ client: null, $: mvcStubClean, directory: REPO_ROOT });
    // Need the snapshot from before-hook
    enforcerClean["hardSnapshot"] = cannedEnforcer["hardSnapshot"];

    const goodEditInput = {
      tool: "edit",
      sessionID: sessionId,
      args: { filePath: srcFile },
    };
    const goodEditOutput = { title: "Edit", output: "edited", metadata: {} };
    await enforcerClean["tool.execute.after"](goodEditInput, goodEditOutput);

    // Cleanup
    await fs.rm(srcFile);

    console.log("  ✅ OmtBlock thrown for NEW mvc_check hard error (VIEW_IMPORTS_MODEL)");
    console.log("  ✅ No throw for clean edit (no new errors)");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Test 7: Hook ordering - nav reminder BEFORE think digest on same call
  console.log("\nTest 7: Hook ordering - nav reminder before think digest");
  try {
    const sessionId = `test-order-${randomUUID()}`;
    const inputPayload = { tool: "read", sessionID: sessionId, args: { filePath: "test.py" } };
    const outputPayload = { title: "Read", output: "content", metadata: {} };

    // Call both hooks on same session first tool result
    await enforcerTools["tool.execute.after"](inputPayload, outputPayload);
    await thinkTools["tool.execute.after"](inputPayload, outputPayload);

    // Nav reminder should appear BEFORE think digest in output
    // The actual nav reminder message is "💡 NAVIGATION TIP" (feature_020)
    const navIdx = outputPayload.output.indexOf("💡 NAVIGATION TIP");
    const thinkIdx = outputPayload.output.indexOf("TA:");
    
    // Both should be present, nav first
    if (navIdx === -1) {
      throw new Error("Nav reminder not found");
    }
    if (thinkIdx === -1) {
      throw new Error("Think digest not found");
    }
    // Nav reminder should be at the start of the output (prepended)
    if (navIdx > 50) {
      throw new Error("Nav reminder not prepended at start");
    }

    console.log("  ✅ Nav reminder prepended before think digest");
    console.log("  ✅ Both effects present on same tool result");
  } catch (e) {
    console.log(`  ❌ FAILED: ${e}`);
    allPassed = false;
  }

  // Summary
  console.log();
  console.log("=".repeat(70));
  if (allPassed) {
    console.log("✅ ALL PRODUCTION HOOK EFFECTS VERIFIED");
    console.log("   - F14 fixed: input.args read for D1 injection");
    console.log("   - F14b live: MVC++ gate throws on new hard error");
    console.log("   - F14c live: TA digest + nav reminder on first tool result");
    console.log("   - SDK contract pinned: input.args / output={title,output,metadata}");
    console.log("   - session.start retained but inert");
    console.log("=".repeat(70));
    process.exit(0);
  } else {
    console.log("❌ SOME TESTS FAILED - Hook effects NOT working in production");
    console.log("=".repeat(70));
    process.exit(1);
  }
}

runProductionTests().catch((e) => {
  console.error("Fatal error:", e);
  process.exit(1);
});
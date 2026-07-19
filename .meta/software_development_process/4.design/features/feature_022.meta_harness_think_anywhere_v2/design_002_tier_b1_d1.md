# Design 002: Think Anywhere V2 — Tier B1 + D1 (Anchor Insertion, Read-Time Injection)

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Analysis:** `3.analysis/.../feature_022.meta_harness_think_anywhere_v2/analysis_002_tier_b1_d1.md`

Tooling/enforcement feature (no MVC++ screen) — same idiom as design_001: plugin functions +
pure logic, deterministic node-runner tests. MVC++ self-check N/A (no `src/` business code).
Contracts unchanged: plugin loader (DEFECT-A: no named tool-object exports), plain-string
ToolResult, execFileSync/no-shell, THOUGHT_PATTERN byte-parity (untouched this tier).

## Components / surfaces affected

| Surface | Change | Gated? |
|---|---|---|
| `.opencode/plugin/omt_think.ts` | MODIFY: `omt_think` gains `after`/`symbol` addressing; anchor-aware insertion resolver; index record gains `anchor` field | harness-e2e guard + think-gate (TA: at EOF) |
| `.opencode/plugin/omt_enforcer.ts` | MODIFY: `tool.execute.after` gains D1 read-time thought injection (before the edit-tools early return) | harness-e2e guard |
| `tests/features/feature_022.../` | NEW: `test_omt_think_v2_tier_bd.py`; MODIFY: `_think_gate_runner.mjs` gains `after-hook` mode. `_think_runner.mjs` unchanged (args pass through) | tests via TDD |
| `opencode.jsonc`, `AGENTS.md`, `.meta/META_HARNESS.md` | **unchanged** (no new tools; arg additions on existing tool need no permission entry) | — |

## 1. B1 — Anchor-based insertion (`after:` / `symbol:`)

### 1.1 Arg surface (omt_think)

```
path, thought, category?            (unchanged)
line?: number                        (unchanged — back-compat)
after?: string   — literal substring anchor; insert AFTER the unique matching line
symbol?: string  — definition-regex anchor; insert AFTER the unique definition line
```

**Exactly one** of `line` / `after` / `symbol` may be given; zero → current EOF-append
default. Two or more → denial naming the combination:
`⛔ TA: refused — pass at most one of line, after, symbol (got line+after).`

### 1.2 Resolution (`resolveAnchor`, module-local — NOT exported, DEFECT-A)

```
resolveAnchor(lines: string[], ext: string, args): 
  { ok: true, insertAt: number, anchor: {kind, value} } | { ok: false, err: string }
```

- **`after`:** match = `lines[i].includes(after)` (literal, case-sensitive — no regex path).
- **`symbol`:** name regex-escaped via existing `escapeRegex`; per-family definition pattern:
  - `.py`: `^\s*(?:async\s+def|def|class)\s+NAME\b`
  - `.ts .js .mjs .cjs .tsx .jsx`: `(?:^|\s)(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+NAME\b`
  - any other ext → `{ ok:false }` with:
    `⛔ TA: refused — symbol addressing is not supported for '<ext>'; use after: with a literal anchor.`
- **Match policy (both modes):**
  - 0 matches → `⛔ TA: refused — anchor not found in <rel>: '<preview>'` (preview = anchor,
    whitespace-normalized, truncated at 60 chars).
  - >1 matches → `⛔ TA: refused — anchor matches N lines in <rel> (e.g. lines 12, 47, 88).
    Use a more specific anchor.` (first 5 candidate line numbers listed).
  - 1 match at 0-based `i` → `insertAt = i + 1` (insert AFTER the anchor line — same
    convention as `line`).
- The resolved `insertAt` flows through the **existing** pipeline unchanged: trailing-newline
  adjustment → A3 `inStringContext` guard (anchor inside a triple-quoted string/fence → same
  refusal as line-mode) → splice → EOL-preserving write → dedup already ran earlier.

### 1.3 Index schema extension

`appendIndex` record becomes:
```
{ ts, path, line, category, thought, anchor: {kind:"after"|"symbol", value:string} | null }
```
`null` for line/EOF mode. Stored now, **consumed later** (E1 drift-repair; out of scope).
`reconcileIndex(path, line)` unchanged. No reader added this tier.

### 1.4 Why refuse-on-ambiguous (not first-match)

Line-number fragility (F6) is caused by *silent* retargeting. First-match-on-ambiguous would
reintroduce a quieter version of it (anchor text like `return` matches everywhere). Refusal
with candidate lines makes the caller supply a drift-resistant anchor in one extra step —
same philosophy as A2's deny-unknown-extension.

## 2. D1 — Non-blocking read-time thought injection

### 2.1 Hook placement

Inside `OmtEnforcer`'s returned `"tool.execute.after"` — **before** the
`if (!EDIT_TOOLS.has(input?.tool)) return` early-return (omt_enforcer.ts:958). The edit-path
logic below is untouched; the think-gate before-hook is untouched.

### 2.2 Logic (fail-open; never throws)

```
if (input?.tool === "read") {
  try {
    const raw = output?.args?.filePath ?? output?.args?.path ?? output?.args?.file
    if (typeof raw === "string" && raw) {
      const { abs, rel } = relOf(raw)                       // existing helper (directory-scoped)
      const session = input?.sessionID || ""                // sessionless → shared "" bucket
      if (!injectedThisSession.get(session)?.has(abs)) {
        const hits = fileThoughtsIn(abs)                    // existing anchored grep
        if (hits.length) {
          mark injected (Set per session, created on demand)
          output.output += "\n\n" + injectMsg(rel, hits)    // mutable output — plugin .d.ts:174-180
        }
      }
    }
  } catch (e) { safeLog("warn", "read-injection failed open: " + (e?.message || e)) }
}
```

- **State:** `const injectedThisSession = new Map<string, Set<string>>()` inside the
  `OmtEnforcer` closure (mirrors `sessionNavState`, omt_enforcer.ts:267). Once per
  file per session; a different session injects afresh.
- **Awareness ≠ consult:** NO `think_consult` ledger record is written; the think-gate still
  blocks edits until `omt_think_list` (C2 owns per-file consult — out of scope). The block
  text says so.
- **Cost on thought-free files:** one `fileThoughtsIn` grep per first read per session —
  same call the edit path already makes per edit; negligible.
- **Offset/limit reads:** inject regardless (thoughts are file-scoped).

### 2.3 Message (capped at 10 — `thinkGateMsg` precedent)

```
💡 TA: thoughts in <rel> (N) — review before editing (think-gate applies; omt_think_list{path:"<rel>"} records consult):
  <rel>:<line>: <content>
  … (+M more: omt_think_list{path:"<rel>"})
```

## 3. Test plan (TDD test list; suite `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_bd.py`)

Real-plugin invocation only: B1 via `_think_runner.mjs` (unchanged — args pass through);
D1 via `_think_gate_runner.mjs` new `after-hook` mode: instantiates the REAL `OmtEnforcer`
with `{client:null, $:stub, directory:<tmpdir>}` (isolated ledger), calls
`plugin["tool.execute.after"](input, output)`, prints the mutated `output` as JSON.

**B1 — anchor insertion (omt_think, tmp_path files):**
1. `after` unique match → thought on the line immediately after the anchor line; `✅ … → rel:line`.
2. `after` 0 matches → `anchor not found` denial; file byte-unchanged.
3. `after` 2+ matches → denial naming count + candidate lines; file unchanged.
4. conflicting modes (`line`+`after`, `after`+`symbol`) → `at most one of` denial; unchanged.
5. `symbol` py `def` → inserted after the `def foo(` line.
6. `symbol` py `class` + `async def` → both forms resolve (parametrized).
7. `symbol` ts `export function` / `const` → resolve (parametrized).
8. `symbol` on `.sql` → `not supported` denial pointing to `after:`; unchanged.
9. `symbol` name with regex metachars (`foo.bar`) → literal treatment: matches only a real
   `foo.bar` definition, never `fooXbar` (0-match denial on the latter).
10. `after` anchor whose next line lies inside a triple-quoted string → A3 refusal (guard
    composes with anchor mode); unchanged.
11. index: `after`-mode record carries `anchor:{kind:"after",value}`; `line`-mode record
    carries `anchor:null` (read thoughts.jsonl, filter to the tmp file's records).
12. back-compat: no addressing args → EOF append exactly as Tier A (regression guard).

**D1 — read-time injection (real OmtEnforcer after-hook, tmpdir ledger):**
13. first `read` of a thought-carrying file → `output.output` gains the 💡 block containing
    the thought content + `think-gate applies`; hook does not throw.
14. second `read` same session+file → output NOT re-appended; new sessionID → re-injected.
15. thought-free file → output unchanged; `tool:"edit"` on a thought file → output unchanged
    (D1 does not alter the edit path).
16. injection writes NO `think_consult` record (tmpdir ledger absent/empty after hook).
17. file with 12 thoughts → block shows 10 lines + `+2 more` pointer.

**Regression gates (run, not counted in the 17):** Tier A suite 15/15; feature_021 30/30;
combined harness set green.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Output mutation silently dropped by live opencode 1.18.3 | Type-sanctioned (`plugin/dist/index.d.ts:174-180`, non-readonly); deterministic runner test is primary; manual `opencode serve` spot-check recorded in test report (feature_021 prior art). |
| `output.args` shape differs live (before-hook reads `output.args` at :870 — live-verified there) | Same access pattern as the shipping before-hook; runner mirrors it. |
| Ambiguity refusals annoy | By design (§1.4); message includes candidate lines → one-step fix. |
| Session map growth | Bounded by files-read-with-thoughts per session (tiny); process-lifetime, mirrors sessionNavState. |
| Index pollution from tests | Tests filter index records by their tmp-file path; records are best-effort sidecar (F8 — no reader yet). |

## 5. Token-budget note

B1: zero standing cost (insert-time only). D1: ≤ 11 lines, once per thought-file per session,
strictly earlier than the edit-time gate block that exists today — net-neutral or better.
No new tool descriptions (arg additions only: ~2 lines in `omt_think`'s schema).

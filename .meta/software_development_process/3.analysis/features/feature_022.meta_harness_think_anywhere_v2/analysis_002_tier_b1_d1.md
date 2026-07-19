# Analysis 002: Think Anywhere V2 — Tier B1 + D1 (Anchor Insertion, Read-Time Injection)

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Source:** `2.requirements/.../feature_022.meta_harness_think_anywhere_v2/FEATURE.md` (F5, F6; tiers B1, D1)
> **Prior:** analysis_001 (Tier A hotfixes — shipped 2026-07-18)

## Scope decision (2026-07-18)

**Tier B1 + D1 only**, per FEATURE.md §"Recommended sequencing" ("B1 + D1 (biggest intent-gap
closers)") and the WORK.md task `T-022BD`. B2 (suggest), C1/C2 (verify/per-file consult),
E1/E2 (index consumption/theory doc) are **not** in scope; this tier must not preclude them
(anchor fields added to the index now, consumed later by E1; injection does not usurp C2's
per-file consult semantics).

Rationale for pairing: B1 closes the *placement* half of the paper's intent gap (thoughts
address code, not line numbers); D1 closes the *delivery* half (thoughts arrive at first read,
before generation — not as an edit-time error). Both touch disjoint surfaces (B1: `omt_think.ts`
insert path; D1: `omt_enforcer.ts` after-hook), so one TDD batch is safe.

## Verified evidence (every claim re-checked against source, 2026-07-18)

| Item | Flaw | Verified evidence |
|------|------|-------------------|
| B1 | F6 fragile anchoring | `omt_think.ts:211` — `line` is the ONLY addressing mode (raw 1-based number). `:256-265` clamps+splices by that number; any edit above the thought silently retargets future removes. `:276` index record is `{path,line,category,thought}` — **no anchor stored** → JSONL stale after the first edit above (confirmed F8 write-only). `omt_think_remove:331-357` re-targets by raw line (contains-check only partially mitigates). Production thoughts live at `main_screen.py:77-79` — already shifted from the `:78-79` cited in FEATURE.md F1. |
| B1 | anchor resolution channel | No AST dep available/allowed in plugin (DEFECT-A/C constraints; mirrors A3's rejected-`tokenize` reasoning, analysis_001 §A3). Literal-substring + language-aware definition regex is the mechanical ceiling; `escapeRegex` already exists (`omt_think.ts:46-48`). |
| D1 | F5 reactive-only delivery | `omt_enforcer.ts:944-950` — thoughts surface ONLY as an edit-time think-gate **block** (error UX, one step late). Nothing fires on read. Consult is session-global (`:946 hasConsultedThoughts`) — one consult clears all files (C2's target, not this tier's). |
| D1 | mutation channel exists | `tool.execute.after` hook signature `(input, output)` with `output: {title: string; output: string; metadata: any}` — **mutable, non-readonly** (`@opencode-ai/plugin/dist/index.d.ts:174-180`, opencode 1.18.3). Appending to `output.output` is the documented post-processing pattern. |
| D1 | reusable machinery | `fileThoughtsIn(abs)` already exported + cheap single-file grep (`omt_enforcer.ts:236-250`); `thinkGateMsg` 10-line cap (`:255`) is the token-discipline precedent; `sessionNavState` Map (`:267`) is the per-session state pattern; after-hook already handles non-edit tools by early return (`:958`) — read-injection slots before that return. |

**Runner/instantiation fact (test design):** `OmtEnforcer` is a named FUNCTION export
(`omt_enforcer.ts:262`) — importable by node test runners today (loader-safe per feature_020
DEFECT-A rule: every export is a function). A runner can call
`OmtEnforcer({client:null, $:stub, directory})` and drive `"tool.execute.after"` with a fake
`{input, output}` — no opencode server needed for deterministic tests.

## Problem analysis per item

### B1 — Anchor-based insertion (`after:` / `symbol:`)

New optional args on `omt_think`; **exactly one** of `line` / `after` / `symbol` (none → current
EOF-append default, back-compat).

- **`after` (literal substring):** `lines[i].includes(after)` — case-sensitive, no regex
  (deterministic; `escapeRegex` not even needed on the match path).
  - 0 matches → error (`anchor not found`).
  - >1 matches → **refuse**, listing candidate line numbers (forces specific, drift-resistant
    anchors; keeps tests deterministic; ambiguity is resolved by the caller picking a longer
    anchor — same philosophy as A2's deny-unknown).
  - 1 match → insert AFTER that line (same "insert after" semantics as `line`).
- **`symbol` (definition-regex, escaped name via `escapeRegex`):**
  - `.py`: `^\s*(?:async\s+def|def|class)\s+NAME\b`
  - JS/TS family (`.ts .js .mjs .cjs .tsx .jsx`): `(?:^|\s)(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+NAME\b`
  - other extensions → refuse with pointer to `after` (no silent substring fallback).
  - same 0/1/N match policy as `after`.
- **A3 guard still applies** to the resolved insertion point (anchor inside a triple-quoted
  string / fence → refuse, identical message path as line-mode).
- **Index:** `appendIndex` record gains `anchor: {kind: "after"|"symbol", value} | null`
  (`null` for line/EOF mode) — stored now for E1's drift-repair; `reconcileIndex(path, line)`
  on remove unchanged this tier.
- **No new named exports** from `omt_think.ts` (DEFECT-A); helpers stay module-local.
- **Non-goal:** `omt_think_remove` by anchor — stays line-based; anchor-aware reconcile is E1.

### D1 — Non-blocking read-time injection

On `"tool.execute.after"` where `input.tool === "read"`:

1. Extract path from `output.args.filePath ?? output.args.path ?? output.args.file` (mirrors
   before-hook `:870`); non-string/missing → return.
2. `hits = fileThoughtsIn(abs)`; empty → return (zero cost on thought-free files).
3. **Once per file per session:** `Map<sessionID, Set<abs>>` (session key `input.sessionID || ""`
   — sessionless calls share one bucket, still once-per-process). Already-injected → return.
4. Append a capped block to `output.output`:
   ```
   💡 TA: thoughts in <rel> (N) — review before editing (think-gate applies):
     <rel>:<line>: <content>   (max 10, then "… (+M more: omt_think_list{path})")
   ```
5. **Non-blocking:** never throws from this path; internal errors fail-open via the existing
   `safeLog` style. Injection is **awareness, not consult** — it does NOT write a
   `think_consult` record and does NOT clear the think-gate (C2 owns per-file consult
   semantics; the block text says the gate still applies).
6. Offset/limit reads: inject regardless (thoughts are file-scoped, not window-scoped).

**Token budget:** ≤ 10 thought lines + 1 header, once per file per session — bounded, and
strictly earlier than the gate block that would fire anyway at edit time.

## Risks / open questions → Design

| # | Risk/question | Design must decide |
|---|---------------|--------------------|
| R1 | Output mutation is type-sanctioned but unverified in the live server (1.18.3) | Deterministic runner test is primary; add a manual live-verify step to the test report (spawn `opencode serve`, read a thought-carrying file, observe block) — mirrors feature_021's serve spot-check. |
| R2 | `read` on huge thought files (hypothetical 100s of tags) | 10-line cap + "+M more" pointer (mirrors thinkGateMsg). |
| R3 | B1 ambiguity refusal could frustrate legit anchors (e.g. `return`) | By design — refuse-with-candidates is the drift-safety mechanism; message must list candidate lines so the next call is one step. |
| R4 | Sessionless `tool.execute.after` (sessionID undefined) | Shared `""` bucket — once-per-process; deterministic for tests. |
| R5 | Editing `omt_think.ts` itself (carries TA: at :388) during Programming | `omt_think_list` consult first; harness-e2e receipt refresh before each plugin edit (Tier A gotcha — batch each plugin's changes into ONE write). |
| R6 | Interaction with `experimental.chat.system.transform` as alternate channel | Rejected: system-prompt injection is session-wide, not file-point-of-use; after-hook output mutation is exactly file-scoped. |

## Test strategy (feeds design §5)

Mirror Tier A: new module `test_omt_think_v2_tier_bd.py` in the existing
`tests/features/feature_022.meta_harness_think_anywhere_v2/` dir; `_think_runner.mjs` unchanged
(passes args through — `after`/`symbol` just work); extend `_think_gate_runner.mjs` with an
`after-hook` mode instantiating the real `OmtEnforcer`. Tier A suite (15 tests) stays untouched
as regression; feature_021 suite (30 tests) is the second regression gate.

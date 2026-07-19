# Implementation Notes: feature_022.meta_harness_think_anywhere_v2 — Tier B1 + D1

> **Feature:** Think Anywhere V2 — Tier B1 (anchor insertion) + D1 (read-time injection)
> **Type:** major_feature | **Phase:** Implementation | **Status:** Complete
> **Design:** `4.design/.../design_002_tier_b1_d1.md` (+ `operation_spec_tier_b1_d1.md`)
> **Prior:** implementation_notes.md (Tier A — shipped 2026-07-18)

---

## 1. What was built

Two disjoint-surface changes closing the paper's *placement* (B1) and *delivery* (D1) intent
gaps. No new tools, no permission/config changes (arg additions on an existing tool need no
opencode.jsonc entry; the D1 branch rides the existing after-hook).

| Item | Surface | Change |
|---|---|---|
| B1 arg surface | `omt_think.ts` | `omt_think` gains optional `after` (literal substring anchor) and `symbol` (definition-name anchor). **At most one** of `line`/`after`/`symbol`; two or more → `⛔ … pass at most one of line, after, symbol (got line+after).` naming the combination. Zero → EOF append (back-compat, Tier A behavior byte-identical). |
| B1 resolver | `omt_think.ts` | `resolveAnchor(lines, ext, rel, after, symbol)` — **module-local** (DEFECT-A: not exported). `after`: `lines[i].includes(after)` (case-sensitive, no regex). `symbol`: name `escapeRegex`'d, per-family definition regex — `.py`: `^\s*(?:async\s+def|def|class)\s+NAME\b`; `.ts .js .mjs .cjs .tsx .jsx`: `(?:^|\s)(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+NAME\b`; other exts → refusal pointing at `after:`. Match policy both modes: 0 → `anchor not found` (preview whitespace-normalized, ≤60 chars); >1 → refusal naming count + up to 5 candidate lines (refuse-on-ambiguous per design §1.4 — first-match would silently retarget, reintroducing F6); 1 → `insertAt = i + 1` (same "insert after" convention as `line`). |
| B1 pipeline | `omt_think.ts` | Resolved `insertAt` flows through the **unchanged** Tier A pipeline: trailing-newline adjustment → A3 `inStringContext` guard (anchor mode composes: inserting right after a line inside a triple-quoted string/fence is refused exactly as line-mode) → splice → EOL-preserving write. Dedup still runs earlier. |
| B1 index | `omt_think.ts` | `appendIndex` record gains `anchor: {kind:"after"\|"symbol", value} \| null` (`null` for line/EOF). Stored now, consumed later by E1 drift-repair (out of scope). `reconcileIndex` unchanged. |
| D1 state | `omt_enforcer.ts` | `injectedThisSession = new Map<string, Set<string>>()` inside the `OmtEnforcer` closure, next to `sessionNavState` (the per-session state pattern it mirrors). Session key `input?.sessionID \|\| ""` (sessionless → shared bucket). |
| D1 hook | `omt_enforcer.ts` | Read branch at the **top** of `"tool.execute.after"`, before the `EDIT_TOOLS` early-return: on `input.tool === "read"`, extract path from `output.args.filePath ?? path ?? file` (typeof-guarded, mirroring the live-verified before-hook access), `relOf` → once-per-session-per-file check → `fileThoughtsIn(abs)` → append capped 💡 block to `output.output` (mutable per plugin `.d.ts:174-180`). **Fail-open** (`try/catch` → `safeLog`), never throws; marks injected only when thoughts exist (a file that later gains thoughts still injects on next read). Edit-path logic below untouched. |
| D1 message | `omt_enforcer.ts` | `💡 TA: thoughts in <rel> (N) — review before editing (think-gate applies; omt_think_list{path:"<rel>"} records consult):` + ≤10 `  <rel>:<line>: <content>` lines + `… (+M more: omt_think_list{path:"<rel>"})` when truncated (cap 10 = `thinkGateMsg` precedent). |

## 2. Contracts preserved (regression surface)

- **DEFECT-A**: no new named exports from `omt_think.ts` (`resolveAnchor` module-local); enforcer
  keeps its all-function named exports (`OmtEnforcer` stays runner-instantiable).
- **THOUGHT_PATTERN byte-parity**: untouched this tier; the Tier A structural guard still pins it.
- **Awareness ≠ consult**: the D1 branch writes **no** `think_consult` ledger record; the
  edit-time think-gate still blocks until `omt_think_list` (C2 owns per-file consult — out of
  scope). Block text says so.
- Plain-string ToolResult, `execFileSync` no-shell, EOL preservation, dedup, protected denylist,
  never-creates-files — all unchanged (Tier A suite green as the regression gate).

## 3. TDD execution

17-behavior test list (design §3) recorded as a JSON array (tdd_check.py:403 `json.loads`
gotcha). Suite `test_omt_think_v2_tier_bd.py` (19 cases: 2 parametrized pairs) verified
**true-RED** on Tier-A code — 17 failed / 2 passed (passers: B1.12 EOF back-compat guard,
D1.15 thought-free/edit control — both assert preserved old behavior). `omt_red` batch-N
warning acknowledged (hotfix batch, Tier A prior art). Single GREEN pass: 19/19.
Regression: Tier A 15/15, feature_021 30/30, combined harness set 208/208.
`omt_refactor` no-op (design-exact implementation).

**Test-infra refinement (vs design §3 literal text):** `_think_gate_runner.mjs after-hook`
mode drives a **batch** of `{input, output}` calls through ONE `OmtEnforcer` instance —
`injectedThisSession` is process-lifetime state, so the once-per-session assertion (§3.14)
requires several calls in one process. Single-call design text is the batch-of-1 case.
Runner: `{client:null, $:throwing-stub, directory:tmpdir}` (isolated ledger; `$` is never
reached by the read branch or by the edit path for non-src files).

## 4. Operational gotchas hit (process)

- **harness-e2e receipt rule** (Tier A known): each plugin's changes were batched into ONE
  write; `tests/scripts/omt/test_omt_harness_e2e.py` re-run between plugins to refresh the
  receipt (the enforcer needed two regions → receipt refresh between its two edits).
- **think-gate**: `omt_think.ts` carries TA: lines (:84 prose-comment residual, :388 xref) →
  `omt_think_list` consult recorded before editing. `omt_enforcer.ts` carries none.
- **tests/ bootstrap**: `omt_skip{scope:tests}` used before RED (TESTLIST two-hats blocks
  tests/ — chicken-and-egg; ledger-audited, Tier A prior art).

## 5. Known limitations (accepted per design/analysis)

- Symbol family covers only `.py` + JS/TS per design; other mapped comment families (`.go`,
  `.rs`, `.css`, …) get the `not supported … use after:` refusal by design (no silent fallback).
- B1 does not address `omt_think_remove` by anchor (stays line-based; anchor-aware reconcile
  is E1). Index `anchor` field is written but has no reader yet (E1).
- D1 injects regardless of read offset/limit (thoughts are file-scoped — design §2.2).
- Session map is process-lifetime (bounded by thought-files read per session — design §4).
- `omt_done` strict full-suite remains unreachable (pre-existing feature_018 react_screen ×3
  + 2 live-ledger-sensitive tdd_check subprocess tests) → phase exit via `omt_complete`
  (Tier A / feature_021 prior art); the state-sensitive pair verified green post-advance.

## 6. Verification

- 19/19 Tier B1+D1 tests; Tier A 15/15; feature_021 30/30; combined harness set 208/208.
- Live `opencode serve` spot-check (1.18.3): bootstrap OK, **zero plugin-load failures** with
  both modified plugins (deterministic runner is primary; serve check guards the loader
  contract — feature_021 prior art).
- MVC++ lint baseline unchanged (no `src/` business code).

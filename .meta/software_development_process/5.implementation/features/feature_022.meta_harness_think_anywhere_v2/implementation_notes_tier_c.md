# Implementation Notes: feature_022.meta_harness_think_anywhere_v2 — Tier C

> **Feature:** Think Anywhere V2 — Tier C (verify lifecycle C1 + per-file consult C2)
> **Type:** major_feature | **Phase:** Implementation | **Status:** Complete
> **Design:** `4.design/.../design_003_tier_c.md` (+ `operation_spec_tier_c.md`)
> **Prior:** implementation_notes_tier_b1_d1.md (Tier B1+D1 — shipped 2026-07-18)

---

## 1. What was built

Two changes closing the paper's *feedback-loop* intent gap: C1 gives thoughts a
verified/stale lifecycle (structural placement-integrity, the RLVR-analogue drift
signal); C2 makes the think-gate consult per-file and drops the cross-session
window for `risk:`-carrying files.

| Item | Surface | Change |
|---|---|---|
| C1 tool | `omt_think.ts` | New `omt_think_verify{path, line}` — **structural** re-check (never semantic): line in range → anchored `THOUGHT_PATTERN` test → `parseThoughtLine` → index lookup (latest ADD-record at `(path,line)`, drift fallback latest `(path, thought-text)`, latest wins) → if the record carries a B1 anchor, re-`resolveAnchor`: `ok && insertAt+1 === line` → `verified`, else `stale` (reasons: `anchor moved (thought at N, anchor resolves to M)` / resolver-refusal text); no record or `anchor:null` → `verified`, `basis: exists` (message says placement-only). Appends `{ts, kind:"verify", path, line, category, thought, status, basis}` (append-only; latest per slot wins). Refusals mirror `omt_think_remove` (protected / missing file / out-of-range naming length / not-a-TA-comment). |
| C1 index read | `omt_think.ts` | `readThoughtsIndex(): any[]` — first read-consumer of `thoughts.jsonl` (partial F8 progress; full strategy is E1). Skips corrupt lines, fail-open `[]`. `latestVerifyStatus(recs)` → `Map<"path:line", status>`. Both module-local (DEFECT-A). |
| C1 digest | `omt_think.ts` | `thinkDigest` header gains ` ⚠️ N stale — re-check with omt_think_verify{path, line}.` when current grep hits include thoughts whose latest verify record is stale. Index unreadable → 0 stale (fail-open; digest never breaks session.start). |
| C1 gate weighting | `omt_enforcer.ts` | `thinkGateMsg(rel, thoughts, opts?: { staleLines?: Set<number> })` — **stable sort** risk-first (category read via `/TA:\s*risk:/i` at category position only — a `gotcha:` thought mentioning "risk:" in text does not match); line suffix `  ⚠️ STALE` when `opts.staleLines` has the line. 10-cap + `+M more` pointer unchanged. New module-local `staleLinesFor(root, rel)` — latest verify records for `path === rel` → stale line numbers; fail-open empty. |
| C1 wiring | `omt_enforcer.ts` | Think-gate call site: `risk = thinkHits.some(t => /TA:\s*risk:/i.test(t.content))`; `thinkGateMsg(rel, thinkHits, { staleLines: staleLinesFor(directory, rel) })`. D1 read-injection message deliberately unchanged (scope discipline). |
| C2 consult record | `omt_think.ts` | `recordConsult(session, files)` — record gains `files: files.slice(0,200)` (+ `files_truncated: true` beyond; truncated records cover only listed files — safe direction). `omt_think_list` computes `files = [...new Set(hits.map(h => h.file))]` (what the agent was shown); empty result → `files: []` (covers nothing, still records — v1 always-records behavior preserved). |
| C2 gate check | `omt_enforcer.ts` | `hasConsultedThoughts(session, rel?, opts?: { risk?, root? })` — ledger at `join(opts?.root ?? process.cwd(), ".meta/.omt/ledger.jsonl")` (production passes `directory`; root injection = hermetic tests). `covered(r)`: `rel === undefined` → true (v1 back-compat); record without `files` (legacy) → true (grandfathered, ages out with the window); else `r.files.includes(rel)`. Exact-session covering consult → true; cross-session within `UNLOCK_WINDOW_MS` covering → true **only if not** `opts.risk`. |
| C2 wiring | `omt_enforcer.ts` | Call site passes `(session, rel, { risk, root: directory })`. `thinkGateDecision` untouched (feature_021 decide-mode regression surface). |
| Permission | `opencode.jsonc` | `"omt_think_verify": "allow"` (permissions are explicit per-tool). |

## 2. Contracts preserved (regression surface)

- **DEFECT-A**: `omt_think.ts` still exports only the default factory; `omt_think_verify`
  joins the tool map only. The feature_021 structural guard
  (`test_no_named_exports_except_default`) stays green; its three-tool literal assert was
  updated to the four-tool map (intentional surface change, tracked in the same file).
- **THOUGHT_PATTERN byte-parity**: untouched this tier; Tier A structural guard still pins it.
- **Awareness ≠ consult**: D1 branch untouched (no consult record on read injection).
- **v1 consult semantics**: `hasConsultedThoughts(session)` with no rel/opts is
  byte-equivalent in behavior to v1 (exact-session → window fallback); legacy no-`files`
  records grandfather any rel.
- Plain-string ToolResult, `execFileSync` no-shell, protected denylist, never-creates-files —
  unchanged. `reconcileIndex` already dropped kind-agnostic records per slot: removed thoughts
  leave no zombie verify state (asserted by design, no change needed).

## 3. TDD execution

22-behavior test list (design §3) recorded as a JSON array (tdd_check.py:403 `json.loads`
gotcha — Tier B1+D1 prior art). Suite `test_omt_think_v2_tier_c.py` (22 cases, 1:1 with the
design items) verified **true-RED** on Tier-B1+D1 code — **20 failed / 2 passed** (passers:
C2.18 legacy-grandfather + C2.19 cross-session-window-no-risk — both pin v1 behaviors the
design explicitly preserves). `omt_red` batch-N warning acknowledged (hotfix batch, Tier
A/B1+D1 prior art). Single GREEN pass: **22/22**. Regression: Tier A 15/15, Tier B1+D1
19/19, feature_021 30/30, rest of combined harness set 144/144 (**230/230** total).
`omt_refactor` no-op (design-exact implementation).

**Test-infra additions (per design §3):** `_think_runner.mjs` gained `omt_think_verify` in
the tool map + a `session-start` mode (drives the factory's real `"session.start"` hook);
`_think_gate_runner.mjs` gained `consulted '<json:{session?,rel?,risk?,root?}>'` (root-
injected real call; no-arg form keeps the old exported-check behavior) and
`before-hook '<directory>' '<json:[{input,output},...]>'` (ONE `OmtEnforcer` instance per
batch, tmpdir-isolated ledger/index, throwing `$` stub, `OmtBlock → {blocked:true,message}`).

## 4. Operational gotchas hit (process)

- **harness-e2e receipt rule** (Tier A/B1+D1 known): three guarded files this tier
  (`omt_think.ts`, `omt_enforcer.ts`, `opencode.jsonc`). `omt_think.ts` batched into ONE
  write; the enforcer needed two regions (helpers/message block + call site) → receipt
  refreshed between them; receipt refreshed before each guarded edit. The e2e's own
  tool-map literal assert (`test_omt_harness_e2e.py:190`) had to track the new four-tool
  map **before** the first post-write receipt refresh (else the refresh run fails).
- **think-gate**: `omt_think.ts` carries TA: (:480 xref) and `omt_enforcer.ts` carries an
  accidental anchored one (:965 `// TA: thoughts to the read result…` — prose comment that
  matches the anchored pattern) → whole-repo `omt_think_list` consult recorded before
  editing (legacy no-`files` record; governs this session under pre-C2 loaded code).
- **tests/ bootstrap**: `omt_skip{scope:tests}` used before RED (TESTLIST two-hats blocks
  tests/ — chicken-and-egg; ledger-audited, Tier A/B1+D1 prior art).
- **feature_021 source assert**: `test_omt_think.py:88` pinned the three-tool map literal;
  updated to four tools (intentional surface change; assert renamed
  `..._with_four_tools`).

## 5. Known limitations (accepted per design/analysis)

- Verify is **structural only** — it never judges whether a thought's claim is still true
  (design §1.1: the agent's job at consult/read time).
- Verify can bind the wrong add-record when two thoughts share text (R1; match order pinned
  `(path,line)` before `(path,text)`, latest wins — documented design §1.2 step 7).
- `basis: exists` is deliberately weak (existence only) for line-mode/hand-written thoughts;
  the message says so.
- Consult `files` capped at 200 (R6); truncated records cover only listed files (safe
  direction: re-consult with a narrower path).
- Legacy no-`files` records weaken the per-file gate until they age out of the 8h window
  (R7 — accepted grandfather).
- `omt_done` strict full-suite remains unreachable (pre-existing feature_018 react_screen ×3
  + 2 live-ledger-sensitive tdd_check subprocess tests) → phase exit via `omt_complete`
  (Tier A/B1+D1 prior art).

## 6. Verification

- 22/22 Tier C tests; Tier A 15/15; Tier B1+D1 19/19; feature_021 30/30; combined harness
  set **230/230** (feature_022+021+020+016+scripts/omt).
- `tests/scripts/omt/test_omt_harness_e2e.py` green after every guarded-file edit (receipt
  refreshed 5× this session; final receipt covers all three modified harness files).
- MVC++ lint baseline unchanged (no `src/` business code).

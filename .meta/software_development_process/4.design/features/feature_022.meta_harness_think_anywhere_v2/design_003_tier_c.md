# Design 003: Think Anywhere V2 — Tier C (Verify Lifecycle C1 + Per-File Consult C2)

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Analysis:** `3.analysis/.../feature_022.meta_harness_think_anywhere_v2/analysis_003_tier_c.md`

Tooling/enforcement feature (no MVC++ screen) — same idiom as design_001/002: plugin functions +
pure logic, deterministic node-runner tests. MVC++ self-check N/A (no `src/` business code).
Contracts unchanged: plugin loader (DEFECT-A: no named tool-object exports — `omt_think_verify`
joins the default factory's tool map only), plain-string ToolResult, execFileSync/no-shell,
THOUGHT_PATTERN byte-parity (untouched this tier).

## Components / surfaces affected

| Surface | Change | Gated? |
|---|---|---|
| `.opencode/plugin/omt_think.ts` | MODIFY: new `omt_think_verify` tool; `recordConsult` gains `files`; `omt_think_list` records consulted files; `thinkDigest` reports stale count; index read helper | harness-e2e guard + think-gate (TA: at EOF) |
| `.opencode/plugin/omt_enforcer.ts` | MODIFY: `hasConsultedThoughts` gains `(rel, {risk, root})`; gate call site passes rel+risk+directory; `thinkGateMsg` risk-first + ⚠️ STALE weighting; index read helper | harness-e2e guard |
| `tests/features/feature_022.../` | NEW: `test_omt_think_v2_tier_c.py`; MODIFY: `_think_runner.mjs` gains `omt_think_verify` + `session-start` mode; `_think_gate_runner.mjs` gains `consulted <json>` (root-injected) + `before-hook` mode | tests via TDD |
| `opencode.jsonc` | MODIFY: add `"omt_think_verify": "allow"` — permissions are explicit per-tool (`omt_think`/`_list`/`_remove` each listed at opencode.jsonc:65-67, verified 2026-07-18) | harness-e2e guard (`opencode.jsonc` ∈ isOmtHarness) |
| `AGENTS.md`, `.meta/META_HARNESS.md` | **unchanged** (tool docs update is a docs-phase nicety, not required by this tier) | — |

## 1. C1 — `omt_think_verify{path, line}` + stale surfacing

### 1.1 Semantics (pinned from analysis)

Verification is **structural**, not semantic: it re-checks *placement integrity* (thought
exists where expected; its B1 anchor still resolves to it). It never judges whether the
thought's claim is still true — that remains the agent's job at consult/read time. This is the
RLVR-analogue feedback signal: drifted/detached thoughts are flagged `stale` instead of
silently persisting as trustworthy.

### 1.2 Tool logic (omt_think.ts; helpers module-local — DEFECT-A)

```
omt_think_verify(path, line):
  1. path required; line required (mirror omt_think_remove validation)
  2. rel = relOf(path); protected → refuse (symmetric with remove)
  3. file must exist; read lines (split /\r?\n/)
  4. line in range → else "out of range (file has N lines)"
  5. lines[line-1] must match THOUGHT_PATTERN → else "not a TA: comment" refusal
  6. {cat, text} = parseThoughtLine(lines[line-1])
  7. rec = latest ADD-record (no `kind` field) in thoughts.jsonl with (path==rel && line==line)
     → if none: latest ADD-record with (path==rel && thought==text)   # drift fallback
  8. if rec?.anchor:
       r = resolveAnchor(lines, ext, rel, kind=="after"?value:null, kind=="symbol"?value:null)
       status = (r.ok && r.insertAt + 1 === line) ? "verified" : "stale"
       basis = "anchor"; reason = r.ok ? `anchor moved (thought at ${line}, anchor resolves to ${r.insertAt+1})`
                                       : r.err-derived short reason
     else:
       status = "verified"; basis = "exists"   # weaker: existence only, message says so
  9. appendIndex({kind:"verify", path:rel, line, category:cat||null, thought:text, status, basis})
 10. return "✅ TA: verified — rel:line (basis: anchor)" 
     |      "✅ TA: verified — rel:line (basis: exists — placement only, no anchor recorded)"
     |      "⚠️ TA: STALE — rel:line — <reason>. Re-place with omt_think or remove with omt_think_remove."
```

- **Index read helper** `readThoughtsIndex(): any[]` — parses `thoughts.jsonl`, skips corrupt
  lines, fail-open `[]`. First read-consumer of the index (partial F8 progress; full strategy
  is E1). Used by verify lookup (7) and the digest (1.3).
- **`reconcileIndex(path, line)` already drops verify records** for that slot (its filter is
  kind-agnostic, omt_think.ts:101) — removed thoughts leave no zombie verify state; a re-added
  thought at the same slot starts unverified. No change needed.
- Verify records are additive (append-only); the **latest** record per `(path, line)` wins.
- No phase/canary gate impact: custom tools are not EDIT_TOOLS; verify only appends to the
  gitignored index (annotation, like omt_think).

### 1.3 Digest stale count (thinkDigest)

```
const verify = latestVerifyStatus(readThoughtsIndex())   // Map<"path:line", status>
const stale = hits.filter(h => verify.get(`${h.file}:${h.line}`) === "stale")
if (stale.length) header gains:  " ⚠️ N stale — re-check with omt_think_verify{path, line}."
```

Index unreadable/corrupt → 0 stale (fail-open; digest never breaks session.start).

### 1.4 Gate weighting (enforcer thinkGateMsg)

- `thinkGateMsg(rel, thoughts, opts?: { staleLines?: Set<number> })` — stays module-local
  (observed via before-hook block message in tests).
- **risk-first:** stable sort so `risk:`-category thoughts render before others; category read
  from content via `/TA:\s*([a-z0-9_-]+):/i` (A4 lowercases at insert; `i` covers pre-A4 tags).
- **stale marker:** line suffix `  ⚠️ STALE` when `opts.staleLines` contains the thought's line.
- Enforcer-side helper `staleLinesFor(root, rel): Set<number>` — reads
  `join(root, ".meta/.omt/thoughts.jsonl")`, latest verify record per `(path,line)`, returns
  stale line numbers for `path === rel`; fail-open empty set. Call site passes `directory`.
- D1 read-injection message is **unchanged** this tier (scope discipline; awareness block).

## 2. C2 — Per-file consult granularity

### 2.1 Consult record (omt_think.ts)

```
recordConsult(session, files: string[]):
  { ts, kind:"think_consult", session, files: files.slice(0,200),
    ...(files.length > 200 ? { files_truncated: true } : {}) }
```

`omt_think_list` computes `files = [...new Set(hits.map(h => h.file))]` (rel paths — the files
the listing actually matched, i.e. what the agent was shown) and records consult with them.
Empty result → `files: []` (covers nothing; preserves the v1 always-records behavior without
granting clearance). A truncated record covers only listed files (safe direction: re-consult
with a narrower path).

### 2.2 Gate check (enforcer)

```
export function hasConsultedThoughts(
  session: string | undefined,
  rel?: string,
  opts?: { risk?: boolean; root?: string },
): boolean
```

- Ledger path: `join(opts?.root ?? process.cwd(), ".meta/.omt/ledger.jsonl")` — root injection
  enables hermetic tests; the production call site passes `directory` (identical in real
  opencode). Existing no-rel/no-opts callers behave exactly as today (back-compat).
- `covered(r)`: `rel === undefined` → true; record without `files` (legacy, pre-C2) → true
  (grandfathered — ages out with the window); else `r.files.includes(rel)`.
- exact-session: any consult with `r.session === session && covered(r)` → consulted.
- cross-session (no exact-session match): **if `opts?.risk` → not consulted** (FEATURE.md C2:
  drop the window for `risk:` — a risk thought demands this session looked); else any consult
  within `UNLOCK_WINDOW_MS` with `covered(r)` → consulted.
- `thinkGateDecision` stays pure/unchanged (feature_021 `decide`-mode regression surface).

### 2.3 Call site (tool.execute.before, think-gate block)

```
const thinkHits = fileThoughtsIn(abs)
if (thinkHits.length) {
  const risk = thinkHits.some(t => /TA:\s*risk:/i.test(t.content))
  const consulted = hasConsultedThoughts(session, rel, { risk, root: directory })
  if (thinkGateDecision({ hasThoughts: true, consulted }) === "block") {
    throw new OmtBlock(thinkGateMsg(rel, thinkHits, { staleLines: staleLinesFor(directory, rel) }))
  }
}
```

`risk` detection anchors at category position (`TA:\s*risk:`) — a `gotcha:` thought mentioning
"risk:" later in its text does not match.

## 3. Test plan (TDD test list; suite `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_c.py`)

Real-plugin invocation only. Runner extensions (tests/ files): `_think_runner.mjs` adds
`omt_think_verify` to the tool map + a `session-start` mode (calls the factory's
`"session.start"`); `_think_gate_runner.mjs` adds `consulted '<json:{session?,rel?,risk?,
root?}>'` (no-arg form keeps old exported-check behavior) and `before-hook '<directory>'
'<json:[{input,output},...]>'` (ONE OmtEnforcer instance per batch; each call →
`{blocked:false}` or `{blocked:true, message}` on OmtBlock).

**C1 — omt_think_verify (runner; tmp_path files; index records filtered by tmp path):**
1. anchor intact → `verified` + `basis: anchor`; index gains `kind:"verify"` record
   `{status:"verified", basis:"anchor"}` for (path,line).
2. anchor line deleted after insert → `STALE`; verify record `{status:"stale"}`.
3. anchor text duplicated after insert (2 matches) → `STALE` (ambiguous).
4. line inserted between anchor and thought (thought drifted down) → `STALE`
   (`anchor moved`) — also exercises the (path,text) index fallback.
5. line-mode thought (anchor:null record) → `verified`, `basis:"exists"`.
6. hand-written TA: line, no index record at all → `verified`, `basis:"exists"`.
7. verify at a non-thought line → `not a TA: comment` refusal.
8. line out of range → refusal naming file length.
9. missing file → refusal.
10. protected path (`.env`) → refusal.

**C1 — digest (runner `session-start`; unique temp file INSIDE repo root, `finally` cleanup
via omt_think_remove + unlink):**
11. one current thought marked stale → digest contains `stale` + `omt_think_verify` pointer.

**C1 — gate weighting (before-hook mode; tmpdir directory; no consult → gate blocks):**
12. file with `gotcha:` (line 1) + `risk:` (line 2) thoughts → block message renders the
    `risk:` thought before the `gotcha:` one.
13. tmpdir index seeded with a stale verify record for the line-2 thought → its block-message
    line carries `⚠️ STALE`; a verified-record line does not.
14. no index file at all → block message renders normally, no `STALE` (fail-open control).

**C2 — consult record (real ledger; capture size before, assert only new records):**
15. `omt_think_list` on a tmp file with a thought → new `think_consult` record has `files`
    containing the tmp file's rel path.
16. `omt_think_list` with 0 hits → new record has `files: []`.

**C2 — hasConsultedThoughts (runner `consulted` mode; tmpdir ledger root):**
17. exact-session record `files:["a.py"]` → consulted("a.py")=true, consulted("b.py")=false.
18. legacy record (no `files`) same session → consulted(any rel)=true (grandfather).
19. cross-session within-window record `files:["a.py"]`, no risk → consulted=true.
20. same as 19 with `risk:true` → consulted=false (window dropped for risk:).

**C2 — before-hook integration (tmpdir; files A/B/R each carry one thought):**
21. ledger has exact-session consult `files:[A]` → edit A allowed, edit B blocked.
22. R carries a `risk:` thought; ledger has only a cross-session within-window consult
    covering R → edit R **blocked**; after adding an exact-session consult for R → allowed.

**Regression gates (run, not counted in the 22):** Tier A suite 15/15; Tier B1+D1 suite 19/19;
feature_021 30/30; combined harness set green.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Verify binds the wrong add-record when two thoughts share text (R1) | Match order pinned: `(path,line)` before `(path,text)`; latest wins; documented limitation (§1.2 step 7). |
| `risk:` regex false-positive from thought text (R2) | Anchored at category position only; tests 12/22 include non-risk controls. |
| Real-ledger/index pollution from runner tests (R4) | Accepted precedent (feature_021/Tier A/B1+D1); hermeticism where decisions happen (root-injected consult check, tmpdir before-hook, tmpdir index). |
| Digest test file inside REPO_ROOT (R5) | Unique name, `finally` cleanup (remove thought + unlink); never in grep-excluded dirs. |
| Consult `files` unbounded (R6) | 200-cap + `files_truncated`; truncated records cover only listed files (safe direction). |
| Legacy no-`files` records weaken per-file gate (R7) | Grandfather explicitly; they age out of the 8h window / with sessions. |
| Editing omt_think.ts (TA: at EOF) during Programming (R3) | `omt_think_list` consult first; harness-e2e receipt refresh between plugin edits; ONE batched write per plugin (Tier A/B1+D1 gotcha). |

## 5. Token-budget note

C1: verify is on-demand only (zero standing cost); digest gains ≤ 1 line when stale > 0; gate
block same cap (10 lines) with at most a sort + short suffix. C2: zero standing cost (one
extra field on an already-written ledger record; gate does one extra regex over ≤ fetched
hits). New tool description ~4 lines.

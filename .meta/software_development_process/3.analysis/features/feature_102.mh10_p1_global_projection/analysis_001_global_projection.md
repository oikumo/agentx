# Analysis 001 — MH10 P1 global read-only projection + divergence log

> Feature: `feature_102.mh10_p1_global_projection` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Profile: **advisory only** — projection never grants/authorizes/mutates policy; no new gates/tools/budgets (net-zero 10/12 holds); sidecar-first.

---

## 1. Overlap gate (D3 — cite mh9 §2 rows; re-implementation refused)

| Reused part | mh9 §2 row / source | P1 use (no redo) |
|---|---|---|
| Net engine as fact source | 039–050 (net engine, rev 57 `drained_complete`) | `omt_net{op:probe}` marking + WORK.md Tasks menu as facts only, never authority |
| Typed evaluator + prep slice | 072 + 073 | Substrate for the projection schema (candidate/decision normalization) |
| Digest + ≤2KB cap + continuation | 092 + S3 contract (feature_100) | Global view shape: ≤2KB default, required-continuation, unknown stays unknown |
| Paired advisory experiment | S4 frontier (feature_101, MERGE) | 2-task demo pattern (routine + interrupted/resumed orient-from-projection) |
| Benchmark proxies labeled | 093/S1 (feature_098) | Any cost field labeled proxy (`tokens_est`/`io_bytes`/delivered-bytes), oracle pinned before any economy sentence |

Nothing from 070–075/079–096 is rebuilt; P1 cites and reuses.

## 2. Frozen advisory profile

- Enforcement untouched; projection is a **read** over live state (net probe + WORK.md + `.projects/meta/META.md` + feature ledger).
- Candidate domain: MH project / workflow / feature / task moves. Revision + generation + owner carried as facts; stale revision/generation cannot commit — **refuse + preserve + diagnose** (no silent drops).
- Omitted-count/continuation contract honored; dry/live parity gap (F10) recorded as UNKNOWN, not papered over.

## 3. Projection schema (one bounded global view)

```text
global_state (rev <net_rev> @ <HEAD>, ≤2KB default)
├── projects: draft / active / complete (+ linked features)
├── workflows: subject → loop/one-shot → last round + resume pointer
├── features: lifecycle Analysis→Done + tdd_position + stranded_red
└── tasks: pool pending/active/done + resources + workers/verification/integration + NEXT menu
```

Missing/inconsistent fields labeled; stale-or-unknown facts listed, never interpolated.

**R3/R5 contract (analysis_002, PROJECT.md v0.3 — binding on Programming):** explicit join keys across WORK.md tasks / ledger features / net bindings / project slugs (C4 residual named, never interpolated — without keys the view is four juxtaposed lists, which earns no "global"); per-section as-of (`rev/HEAD/ts`; no global as-of exists); sync-generated rows labeled **derived**; workflow section = catalog position + last `.sandbox/` round pointer only; doc→token loss labeled.

## 4. Divergence instrumentation (C6/C1 named, not claimed)

- Per managed op, log `projection(B) vs marking(M)`: counts that agree with **no fired transition** are OMISSIONS (known paths: `claim_task`/recovery/lane/integration via `_move_pool_token` `state.py:819-834,896`; absent-lane binding-only occupancy `:296-300` vs `fire()` `:763-768`).
- Crash window carried: clear-before-record `:730-742` vs WAL `:672-675` — P1 never depends on replay surviving that window.
- Output: `.sandbox/global_state/divergence.md` (machine-readable rows: op, B, M, transition-fired?, omission-class, file:line).

## 5. Sidecar + demo

- Sidecar: `.sandbox/global_state/` (projection snapshots + divergence log + 2-task demo notes). Runs in sidecar/worktree; never the live checkout.
- Demo tasks: (a) routine fix, (b) interrupted/resumed — each orients + resumes from the projection alone (paired order, frozen criteria/pins).
- **R4 blind protocol (binding on Testing):** resume performed by a fresh session working **blind** (projection + acceptance checklist only, no source peeking); pass = all checklist items satisfiable from ≤2KB alone. Borrowed from the S1 oracle-qualification pattern.
- Metrics (all labeled proxy until S1-full oracle): first-useful-action, avoided attempts (seeded defects for detection only; economic return needs natural wins too), recovery accuracy, acceptance, all-agent tokens + query cost.

## 6. Exit criteria (Analysis → Programming → Testing → Done)

- Analysis: this doc signed + FEATURE.md scope/traceability filled (this step).
- Programming: sidecar projection builder (imports S3 contract, no second engine) + 2 snapshots + divergence log — live surfaces untouched.
- Testing: `test_report.md` PASS — `check` 0 + `build` OK before AND after + demo orients from projection alone + budget sheets unchanged (tool_args 2455/2464, schemas 1840/1856, agents_md 2918/2944, nav 64990/65536, gates 10/12).
- Done: `omt_complete` feature_102 → PROJECT.md Status P1 row checked; P2 stays parked unless ALL (a–e) re-entry evidence exists.

## 7. Payback gate

- Expected benefit: one global resume point killing "where is MH work?" scans. Minimum meaningful effect: fresh session orients a real task from ≤2KB alone. Expansion rule + resource budget frozen before any corpus/scope growth. Stop when realistic use cannot repay build + eval + maintenance.

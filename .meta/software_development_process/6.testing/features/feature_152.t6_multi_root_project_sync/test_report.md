# Test Report — feature_152.t6_multi_root_project_sync (T6)

Date: 2026-10-11/12 (session bridged UTC midnight) · HEAD at close: post-T5 `ac54d04` + this feature.

## TDD cycle (same-node)

- testlist 9 behaviors → RED declared at
  `TestMultiRootSync::test_union_writes_both_roots_and_idempotent`
  (exit 1, TRUE-RED, inferred target `scripts/omt/project_state.py`).
  Batch-of-10 warning acknowledged (151 precedent: golden contract, single cycle).
- RED shape: 9 failed / 1 passed (`env_compat` regression guard — correctly
  green at RED, pins today's single-root env semantics).
- GOLD 10/10; REFACTOR clean (no further src churn needed); DONE recorded
  (checklist verified; 12 pre-existing failures tolerated as repo drift,
  byte-identical to the feature baseline captured at Programming declare).

## Suites

| Gate | Result |
|---|---|
| feature_152 goldens (`test_multi_root_meta.py`, 5 classes) | **10 passed** |
| 030 contract (`omt/test_project_lifecycle.py` + feature_030 sentinel) | **43 passed, ZERO edits** |
| Boundary e2e (`test_omt_harness_e2e.py`) | 1 passed (batch receipt; mid-batch mint during the round) |
| Lanes `tests/agentx tests/harness_meta` | **12F / 2154P / 5S** — same-12 pre-existing, +10 new goldens, zero-new |
| `prove --lane product` | clean 268+37, exempted 8 |
| `prove --lane harness` | clean 268+37, exempted 8 |
| `verify` ×2 | STALE-valid (ledger-grew only), certs rm'd, zero root-strays |
| `harnessc check` | **282 records, 0 errors** |
| WORK.md budget | 10874/11264 at peak (DONE row + 147 rotation lands ~10604) |

## Live relocations proof (post-impl)

- 4× `project.py move … --to-root agentx`: dirs relocated, states preserved
  (3 active + 1 draft), WORK.md `## Projects` rows byte-identical before/after,
  per-root manifests re-split 21 meta / 5 agentx, `harnessc check` re-run 282/0.

## Test-side corrections during RED→GREEN (honesty notes)

- Convention-line assertion: the manifest's backtick closes AFTER `/{…}` —
  asserted substring with a trailing backtick after `<slug>` can never match;
  fixed to `` `.projects/<root>/<slug>/ `` prefix form.
- dest-exists scenario re-designed (see implementation_001 §corrections 1–2):
  archived-guard order + non-dir-straggler reachability are DESIGNED semantics
  discovered by the goldens, not impl concessions.

## D8 revision on record

`harness_wrapper_split` backfill moved from "deferred" to "executed with this
unit": the root-aware status check (this feature's own surface) demands
lifecycle records for every home; Options drift resolved surgically (no
net_to_md — the rev60-vs-live STALE item in the program close tail still owns
net reconciliation).

# Test Report: MH10 P2 slice B — evidence-carrying claim path (feature_104)

> **Phase:** Testing | **Feature:** feature_104.mh10_p2_rewire_claims_through_fire (`minor_feature`, project `meta_harness_10`)
> ONE `state.py` round (helper + 2 wirings + 2 ledger dicts, 53+/2-); no further `state.py` touches (receipt discipline).

## Stage 1 — Unit (new goldens, 5/5)

| Check | Result |
|---|---|
| First claim fires `work_start` (`fired=true`, `fire_fallback=null`), pool 2/0→1/1, attention/feature_ready refunded (1/1, no leak) | [x] pass |
| Attention-held claim falls back `transition_not_enabled`, legacy acceptance preserved (2-worker model untouched) | [x] pass |
| Release names missing back-edge (`transition=work_release`, `fired=false`, `no_transition`), counts 1/1→2/0 | [x] pass |
| `task_not_pending` on double claim + `task_not_found` on unknown preserved | [x] pass |

## Stage 2 — Integration (receipt, 76/76)

- `test_net_task_claim_generation` + `test_net_pool` + `test_net_two_worker_capacity_scope` + `test_net_recovery_journal` + `test_net_verification_integration_lane` + `test_net_worktree_isolation` + slice-A `test_managed_ops` + `test_net_conformance` + `test_net_state` — [x] 76 passed

## Stage 3 — System (gates)

```
$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections

$ uv run pytest -q
1749 passed, 7 warnings in ~206s (0 failures)  # 1744 baseline + 5 new
```

## Verdict

Slice B **PASS**: claim path prefers a real template firing with shape-check + resource refund; every claim/release record carries `transition/fired/fire_fallback`. C6 narrows to two named residuals: (i) attention-vs-workers template conflict (fallback, never refusal), (ii) missing `work_release` back-edge. No guard/code/revision/workspace behavior changed — `fired=false` paths run the exact legacy mutation. Lane/integration rewiring (B3), template fix (B2), crash reorder (C), matrix/payback (D) stay parked.

# Test Report: MH10 P2 slice B3b — cap-safe lane template landing (feature_107)

> **Phase:** Testing | **Feature:** feature_107.mh10_p2b3b_lane_template_landing (`minor_feature`, project `meta_harness_10`)
> ONE `state.py` round (catalog retire + slot aliases + slot-adopting `_fire_lane_move` + 4 call-site wirings + `ensure_pool_b3b`), ONE `managed_ops.py` round (6 lane rows → `yes-B3b-template`), catalog fixture updates (sync/resources/103-test), 10 new goldens. No further live-surface touches.

## Stage 1 — Unit (new goldens, 10/10)

B3b bundle (migrated 15/15 net: retire-one + reuse-two + add-three): migration retires `e2e_receipt` (reroute → `archive_pool`) and lands 3 lane states + 6 transitions + 19 arcs · rerun noop · full pass walk fires all 6 with slot accounting (submit takes test / frees worker; verify frees test; start takes integration; finish frees integration) · verify_fail/integrate_fail back-edges fire and free their slots, `work_done` untouched on fail · 2 concurrent claims still fire (B2 preserved) + release fires · slot exhaustion refuses (`verification_busy`/`integration_busy`) · attention/ready/goal/archive/round/token untouched across walks · `managed_ops` lane rows read `yes-B3b-template`, ledger-evidence `ok` with 5 fired / 0 fallback · legacy bundle keeps `not_lane_net` fallbacks with code-managed alias slots · old `test_slots`/`integration_slot` names still honored — [x] 10/10 pass.

## Stage 2 — Integration (receipt, 141/141)

- `test_net_task_claim_generation` + `test_net_pool` + `test_net_two_worker_capacity_scope` + `test_net_recovery_journal` + `test_net_verification_integration_lane` + `test_net_worktree_isolation` + slice-A `test_managed_ops` (B3b-updated: 6 lane rows `yes-B3b-template`) + `test_net_conformance` + `test_net_state` + slice-B `test_rewire` (untouched) + B2 `test_b2_template` (untouched) + B3 `test_b3_lane` (untouched) + B3b `test_b3b_template` + `test_net_sync` + `test_net_resources` (B3b-updated 4-resource catalog) — [x] 141 passed

## Stage 3 — System (gates + live migration)

```
$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections

$ uv run pytest -q
1782 passed, 7 warnings in ~128s (0 failures)  # 1772 slice-B3 baseline + 10 new B3b

$ live migration (snapshot-guarded, .meta/.omt gitignored)
before: rev 58 places 13 → migrate rev 60 places 15 (conformance 9/9 ok) → rerun noop
probe rev 60: drained_complete (done=7, no pending/active), resources 4/4 free,
  workers 0/2, verification/integration free, bindings valid, archive_pool 40
$ sync net_to_md → WORK.md Tasks re-rendered (net_rev:60, places 15/15, 4/4 free)
$ uv run scripts/omt/net_snapshot.py → dashboard snapshot.json rev 60 (sentinel green)
```

## Verdict

Slice B3b **PASS**: the lane template is landed within the 15-place cap — every lane record on the migrated net carries `transition/fired=true` with template-enforced slot accounting; legacy bundles keep labeled fallbacks; catalog + fixtures + map + docs agree. C6 lane residual CLOSED (template landed); remaining P2: crash reorder (C), matrix/payback (D), or close the program.

# Test Report: MH10 P2 slice B2 — additive template fix (feature_105)

> **Phase:** Testing | **Feature:** feature_105.mh10_p2b2_template_fix_work_release (`minor_feature`, project `meta_harness_10`)
> TWO `state.py` rounds (helper v2 + callers + catalog + migration helper; compat default for direct callers), ONE `managed_ops.py` round (release_task row + ledger-evidence reader), 103-test B2 update, dashboard snapshot regen. No further live-surface touches.

## Stage 1 — Unit (new goldens, 12/12)

B2 bundle (slots + `work_release`, attention arcs kept + refunded): claim fires with slot adopted (2→1, attention 1, `fired=true`) · **2-concurrent both fire** (slots 2→0) · 3rd claim refused `worker_capacity_exhausted` (code fence authoritative) · release fires back-edge (`work_release`, slots→2) · release→reclaim fires · old release still `no_transition` · old attention-held still `transition_not_enabled` · slot-place-without-arcs → `transition_shape_mismatch` with legacy slot move · migration migrates-then-noops (rev+1, slots M0=2, arcs land; rerun same rev, no ledger row) · migration M0 accounts active (1 active → slots=1) · ledger reader counts fired/fallbacks + flags key-missing rows — [x] 12/12 pass.

## Stage 2 — Integration (receipt, 95/95)

- `test_net_task_claim_generation` + `test_net_pool` + `test_net_two_worker_capacity_scope` + `test_net_recovery_journal` + `test_net_verification_integration_lane` + `test_net_worktree_isolation` + slice-A `test_managed_ops` (B2-updated: `release_task` row, happy-path list) + `test_net_conformance` + `test_net_state` + slice-B `test_rewire` (untouched — compat default) + B2 `test_b2_template` — [x] 95 passed

## Stage 3 — System (gates)

```
$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors   # work_md 8214/8704 after deliberate 8192→8704 bump

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections

$ uv run pytest -q
1763 passed, 7 warnings in ~155s (0 failures)  # 1749 slice-B baseline + 2 pause-housekeeping goldens + 12 new B2

$ omt_net probe → rev 58 drained_complete (13 places, worker_slots=2, bounded)
$ omt_net sync net_to_md → WORK.md Tasks re-rendered (net_rev 58, places 13/15)
```

Live migration (local-only, gitignored bundle): snapshot → `.sandbox/b2_mig_snapshot/` → `ensure_pool_b2` (rev 57→58, additive only) → probe green → rerun noop → dashboard `snapshot.json` regen'd via sanctioned `net_snapshot.py` (sentinel green).

## Verdict

Slice B2 **PASS**: claim/release fire literally on the B2 template with slot adoption and attention refund — 2-worker concurrency holds with zero fallbacks on the happy path; every record still carries `transition/fired/fire_fallback`; old-shape bundles keep exactly their slice-B rows. C6 narrows to lane/integration rewiring (B3: `submit/verify/integrate` still counter-move + code slots); crash reorder (C), matrix/payback (D) stay parked.

# Test Report: MH10 P2 slice A — managed-op transition map (feature_103)

> **Phase:** Testing | **Feature:** feature_103.mh10_p2_global_gate (`minor_feature`, project `meta_harness_10`)
> Read-only evidence harness; no live authority change (gate flip stays parked).

## Stage 1 — Unit (map + classifier)

| Check | Result |
|---|---|
| `MANAGED_OPS` covers all 7 ops (fire/claim_task/release_complete/absent_lane/project_sync/session_menu/crash_window), only `fire` fires today | [x] pass |
| `classify`: agree+fired=FIRED, agree+unfired=OMISSION, disagree=DIVERGENCE | [x] pass |
| `check_counts` on P1 shape (0/0/7 vs 0/0/7) → 3× OMISSION | [x] pass |
| Seeded claim-without-fire detected as omission; seeded count mismatch as DIVERGENCE | [x] pass |

## Stage 2 — Integration (live bundle)

- `check_live(.meta/.omt)` rev 57: pool 0/0/7 vs marking 0/0/7 → 3× OMISSION, managed-ops table attached — [x] pass
- `tests/scripts/omt/test_net_conformance.py + test_net_state.py` 18/18 green (no regression on the existing conformance surface) — [x] pass

## Stage 3 — System (gates)

```
$ uv run scripts/omt/harnessc.py check
harnessc: check OK — 265 records, 0 errors

$ uv run scripts/omt/harnessc.py build
harnessc: build OK — 265 records → 5 projections

$ uv run pytest -q
1744 passed, 7 warnings in ~165s (0 failures)  # 1739 baseline + 5 new
```

## Verdict

Slice A **PASS**: every managed op is named in one template map with a falsifiable B-vs-M check; live agrees-as-omission (C6 carried, not claimed); seeded bypasses are detected. No `state.py`/`.opencode/` edits; net-zero holds. Re-entry row (b) partial earned; rows (a,c,d,e) + rewiring (slice B) + crash reorder (slice C) + matrix/payback (slice D) remain parked.

# Analysis 001 — Slice B3: evidence-carrying lane path (fire preferred, fallback labeled)

> Feature: `feature_106.mh10_p2b3_lane_integration_rewire` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.

---

## 1. Why literal rewire is refused (blocker, head-verified)

Lane moves today are **binding-only + code slot tokens** — no template edge exists:

* `submit_result` (`state.py:1358`): `_move_pool_token(st, "work_active", "work_verifying")` is a **no-op on pool nets** (`_move_pool_token:825-826` returns when src/dst not in `live_marking`). Live bundle rev 58 has 13 places (probe): `work_pending/active/done + worker_slots + 8 resources` — **no** `work_verifying`, `work_integration_ready`, `work_integrating`, `test_slots`, `integration_slot`. The real move is binding `work_active→work_verifying` + `worker_slots+1` (free) + `test_slots-1` (occupy, code-managed `:1354-1357`).
* `verify_result` (`:1443`, `:1448`): `work_verifying→work_integration_ready` (pass) / `→work_pending` (fail) — both binding-only, plus `test_slots+1` free.
* `integrate_start` (`:1518`): `work_integration_ready→work_integrating` binding-only + `integration_slot-1`.
* `integrate_finish` (`:1590`, `:1604`): `work_integrating→work_done` (pass) / `→work_pending` (fail) binding-only + `integration_slot+1`.
* Lane capacity fences are **binding counts** (`_lane_task_count` vs `TEST_SLOTS_CAPACITY=1` `:1342`, `INTEGRATION_SLOT_CAPACITY=1` `:1504`), authoritative without the place — same pattern as pre-B2 `worker_slots` (feature_082).

Template landing would need **+5 places** (`work_verifying`, `work_integration_ready`, `work_integrating`, `test_slots`, `integration_slot`) + 6 transitions + ~12 arcs on the 13-place rev-58 net → **18 places > 15-place cap** (`MAX_PLACES:89`, `_check_place_cap:327-334`). Forcing it now breaks D20 or forces a place-cap exception — refused per non-interference (D5). Slice B3 is therefore **evidence-carrying only** (same staged rule as slice B §2): call sites take the one-template shape today, land literally when a B3b template migration solves the cap (reuse vs retire vs cap raise — separate slice with e2e).

Further: `verify_fail → work_pending` and `integrate_fail → work_pending` are back-edges with no natural single forward transition (like pre-B2 `work_release`); they need named transitions even in the future template.

## 2. Staged rule (what slice B3 implements)

New helper `_fire_lane_move(st, transition, src, dst) -> (fired, fallback_reason)`:

1. If `transition` exists in `st.net.transitions` AND `src+dst` both in `st.live_marking` AND `fire_marking` succeeds with lane-shape check (src −1, dst +1, other lane places unchanged) → adopt successor marking (pool places untouched), return `True`.
2. Else → legacy behavior exactly (binding move by caller + existing slot-token code moves stay in the caller), return `False` with reason `no_transition` | `transition_not_enabled` | `not_lane_net` (src/dst not in marking — today's pool-net case) | `transition_shape_mismatch`.

Wiring (ONE `state.py` round, receipt discipline — 4 functions, 6 edges):

* `submit_result`: `_fire_lane_move(st, "work_submit", "work_active", "work_verifying")`; ledger `net_submit` gains `"transition": "work_submit", "fired": <bool>, "fire_fallback": <reason?>`.
* `verify_result` pass: `_fire_lane_move(st, "work_verify_pass", "work_verifying", "work_integration_ready")`; fail: `_fire_lane_move(st, "work_verify_fail", "work_verifying", "work_pending")`; ledger `net_verify_pass` / `net_verify_fail` gain the 3 keys.
* `integrate_start`: `_fire_lane_move(st, "work_integrate_start", "work_integration_ready", "work_integrating")`; ledger `net_integrate_start` gains the 3 keys.
* `integrate_finish` pass: `_fire_lane_move(st, "work_integrate_pass", "work_integrating", "work_done")`; fail: `_fire_lane_move(st, "work_integrate_fail", "work_integrating", "work_pending")`; ledger `net_integrate_pass` / `net_integrate_fail` gain the 3 keys.

Ledger stays append-only compatible (new optional keys only); no guard, capacity, generation, workspace, or revision behavior changes — `fired=false` paths execute the exact legacy mutation. Today's pool nets deterministically take `not_lane_net` (src/dst absent) or `no_transition` — never silent, never refused.

`managed_ops.py` (ONE round): `release_complete` row splits into the 6 lane rows (transition names above, `fired_today: no-B3-fallback`); `check_ledger_evidence` extends from claim/release to the 7 lane kinds (`net_submit`, `net_verify_pass/fail`, `net_integrate_start/pass/fail`) — offenders are rows missing the 3 keys. `check_live` unchanged (counts-only).

## 3. What this earns / leaves

Earns: every lane record names its future template transition + whether it fired — `managed_ops.check_live` + extended ledger-evidence reader assert the shape instead of trusting prose. C6 narrows to one named residual: lane/integration template landing (B3b: cap-safe place/transition design + migration + e2e).

Leaves parked: B3b template landing (lane places + 6 transitions + slot arcs within the 15-place cap — needs splice design + migration + e2e, separate slice); crash reorder (C); matrix/payback (D). No `POOL_PLACES` / `is_pool_net` / `pool_counts` changes in B3 (lane places stay binding-only; marking move only when template already has them).

## 4. Exit

Programming: ONE `state.py` round (helper + 4 function wirings + 7 ledger dicts) + ONE `managed_ops.py` round (lane rows + extended reader) + tests (existing lane/pool/worker/recovery/worktree/slice-A/B/B2 suites must stay green; new tests assert `not_lane_net`/`no_transition` fallback-labeled on pool fixtures + binding/slot behavior preserved + ledger keys present). Testing: `test_report.md` + `check`/`build`/suite green.

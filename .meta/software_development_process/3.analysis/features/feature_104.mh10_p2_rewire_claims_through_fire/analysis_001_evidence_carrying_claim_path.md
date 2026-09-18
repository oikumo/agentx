# Analysis 001 — Slice B: evidence-carrying claim path (fire preferred, fallback labeled)

> Feature: `feature_104.mh10_p2_rewire_claims_through_fire` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.

---

## 1. Why literal rewire is refused (blocker, head-verified)

Template pool transitions (pool-net shape, cf. `tests/scripts/omt/test_net_pool.py:74-84`):

* `work_start`: consumes `agent_attention + feature_ready + work_pending`, produces `feature_ready + work_active` — **holds `agent_attention` while active** (cap 1, IDEA-002 §2.3 serial-mirror).
* `work_complete`: consumes `work_active`, produces `agent_attention + goal_satisfied + work_done`.

Task model (`state.py:91-98`, feature_082): `worker_slots=2` + active-binding count fence — **2 concurrent claims allowed**.

Conflict: forcing `claim_task` through `fire_marking("work_start")` would serialize claims on `agent_attention` (cap 1) and refuse the 2nd concurrent worker the task model allows. It would also couple task claims to `feature_ready` (a harness-surface resource). Behavior change on the live bundle — refused per non-interference (D5).

Further: `release_task` (active→pending back-edge) has **no template transition at all** (`work_complete` goes active→done). A literal fire does not exist for it.

## 2. Staged rule (what slice B implements)

New helper `_fire_pool_move(st, transition, src, dst) -> bool fired`:

1. If `transition` exists in `st.net.transitions` AND `fire_marking` succeeds on the live tuple → adopt the successor marking, return `True`.
2. Else → legacy `_move_pool_token` counter move, return `False` with a reason code (`no_transition` | `transition_not_enabled` | `not_pool_net`).

Wiring (ONE `state.py` edit, receipt discipline):

* `claim_task`: guards unchanged (place/capacity/scope/worker_slots); pool move via `_fire_pool_move(st, "work_start", "work_pending", "work_active")`; ledger `net_claim` gains `"transition": "work_start", "fired": <bool>, "fire_fallback": <reason?>`.
* `release_task`: pool move via `_fire_pool_move(st, "work_release", "work_active", "work_pending")` — `work_release` does not exist in the template, so this deterministically takes the labeled `no_transition` fallback today while the call site is already on the one-template shape for the day the transition lands.

Ledger stays append-only compatible (new optional keys only); no guard, code, revision, or workspace behavior changes — `fired=false` paths execute the exact legacy mutation.

## 3. What this earns / leaves

Earns: every claim/release record names its template transition + whether it fired — `managed_ops.check_live` + a new ledger-evidence test can assert the shape instead of trusting prose. C6 narrows to two named residuals: (i) attention-vs-workers template conflict, (ii) missing `work_release` back-edge transition.

Leaves parked: template fix for (i) — worker_slots arcs or per-worker attention (needs splice migration + e2e, slice B2); `work_release` transition landing (slice B2); lane/integration rewiring (slice B3); crash reorder (C); matrix/payback (D).

## 4. Exit

Programming: ONE `state.py` edit + `managed_ops` ledger-evidence reader + tests (existing claim/release/lane suites must stay green; new tests assert fired-preferred on pool fixture + fallback-labeled where template lacks the edge). Testing: `test_report.md` + `check`/`build`/suite green.

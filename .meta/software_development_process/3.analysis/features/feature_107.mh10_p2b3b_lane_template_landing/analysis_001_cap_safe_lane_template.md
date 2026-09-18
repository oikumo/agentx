# Analysis 001 — Slice B3b: cap-safe lane template landing (reuse + retire, within 15)

> Feature: `feature_107.mh10_p2b3b_lane_template_landing` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Resumes: feature_106 analysis_001 §1 (blocker) + test_report verdict (C6 narrows to B3b).

---

## 1. Cap math (head-verified 2026-09-18)

- Live bundle rev 58 (`omt_net{op:probe}`): **13 places** (`agent_attention, archive_pool, e2e_receipt, feature_ready, goal_satisfied, harness_surface_round, resource_token, src_edit_capacity, tests_capacity, work_active, work_done, work_pending, worker_slots`), 3 transitions, 14 arcs. Cap `MAX_PLACES=15` (`state.py:92`, `_check_place_cap:330-337`). **2 free.**
- Naive lane landing (feature_106 §1): +5 places (`work_verifying, work_integration_ready, work_integrating, test_slots, integration_slot`) + 6 transitions + ~12 arcs → **18 > 15**. Refused without a cap-safe design (this slice).
- Dead weight in the pool template (zero arcs — verified against `META_NET.petri.json` arcs list, which touches only `agent_attention, feature_ready, work_*, worker_slots, goal_satisfied`): `resource_token, src_edit_capacity, tests_capacity, harness_surface_round, e2e_receipt` — all M0=1, never consumed/produced by `work_start/release/complete`. Enforcement for the receipt/round concepts lives in TS enforcer guards, not in these net tokens.

## 2. Options (reuse vs retire vs raise)

| Option | Shape | Verdict |
|---|---|---|
| **A. Raise cap 15→18**, add 5+6 | 1-line `MAX_PLACES` change, additive-only (B2 pattern) | REFUSED for B3b: weakens D20 WIP guard; lane is pool lifecycle so a raise is arguable, but CURRENT_STATE iter 13 + PROJECT.md Quick Start explicitly scope B3b as **within-cap** — a raise is a D20 amendment, separate slice if ever. |
| **B. Retire 3, add 5** (drop 3 dead, land all incl. new slot places) | 13−3+5=15 | REFUSED: retires more catalog than needed; larger fixture blast for zero gain over C. |
| **C. REUSE 2 slots + RETIRE 1 + ADD 3 states (adopted)** | 13−1+3=**15 exactly**, transitions 3+6=9 | Minimal catalog change, keeps every live contract that matters. |

### Adopted design C

- **REUSE (keep names, add arcs, extend code):** `tests_capacity` (M0=1) ≡ test lane slot (`TEST_SLOTS_CAPACITY=1`); `src_edit_capacity` (M0=1) ≡ integration slot (`INTEGRATION_SLOT_CAPACITY=1`). No new `test_slots`/`integration_slot` places — the 082 pattern (place tokens honored when present; binding counts remain the authoritative fence so legacy bundles without wiring still arbitrate). Code honors **both** names (alias): live bundle wires `tests_capacity`/`src_edit_capacity`; existing test fixtures using `test_slots`/`integration_slot` keep passing.
- **RETIRE 1:** `e2e_receipt` (drain its 1 token with an explicit retirement ledger record). Rationale: the e2e receipt discipline is already evidenced in the ledger (`net_*` rows + receipt 104/104) and enforced by the TS enforcer — the net token is redundant. `resource_token` (boundary anchor, `BOUNDARY_PORTS`/history) and `harness_surface_round` (round-state placeholder) stay; `RESOURCE_PLACES` shrinks 5→4 with a D-entry (041 R1 amendment, this slice).
- **ADD 3 state places** (M0=0 — no live tasks in lane today): `work_verifying, work_integration_ready, work_integrating` + 6 `LANE_TRANSITIONS` (already named in `state.py:90-91`, B3 wired call sites to these names).

## 3. Transition/arc table (19 new arcs, slot-adopting firings)

Refund rule (B2 precedent): each firing adopts lane-state + slot deltas, refunds every other place (attention/ready/goal/archive stay put — verified §4: no leak because refund, not because hold).

| Transition | Inputs | Outputs |
|---|---|---|
| `work_submit` | `work_active`, `tests_capacity` | `work_verifying`, `worker_slots` (free worker at submit, §10.5) |
| `work_verify_pass` | `work_verifying` | `work_integration_ready`, `tests_capacity` (free test) |
| `work_verify_fail` | `work_verifying` | `work_pending`, `tests_capacity` (free test; re-claim consumes `worker_slots`) |
| `work_integrate_start` | `work_integration_ready`, `src_edit_capacity` | `work_integrating` (occupy integration) |
| `work_integrate_pass` | `work_integrating` | `work_done`, `src_edit_capacity` (free integration) |
| `work_integrate_fail` | `work_integrating` | `work_pending`, `src_edit_capacity` (free integration) |

- `_fire_lane_move` gains `slot_deltas: dict[str,int] | None = None` (default `None` keeps all B3 callers green — B2 `slot_delta` precedent): submit `{tests_capacity:-1, worker_slots:+1}` (+ `test_slots` alias when present), verify `{tests_capacity:+1}`, start `{src_edit_capacity:-1}`, finish `{src_edit_capacity:+1}`. Shape check extends to listed slots (template must move each by its delta); unlisted places refunded.
- Verify-fail / integrate-fail back-edges keep their named transitions (feature_106 §1: no natural forward transition) — they free their lane slot and return to `work_pending`, exactly as today but template-fired.

## 4. Attention/goal safety (why the template does NOT touch them)

- `agent_attention` is **refunded, never held**, in pool mode (`_fire_pool_move:897-899`, `_fire_lane_move:951-953`; probe: attention=1 with 0 active). `work_complete` (the only attention-releasing template edge) has no code path — lane pass/fail must not invent attention/goal arcs or they will shape-mismatch on every firing. B3b keeps attention/ready/goal/archive out of all 6 lane transitions; a future slice can reconcile attention with 2-worker concurrency explicitly (the slice-B TA risk, `state.py:843`).
- `goal_satisfied` accumulation path is unchanged (historic `f{N}_complete`; lane does not produce it — same as today).

## 5. Migration (idempotent, remove-first, snapshot-guarded)

- `ensure_pool_b3b(base, reasoning, session, feature)` (mirrors `ensure_pool_b2:958-1014`): (1) `splice(remove, {remove_places:[e2e_receipt], token_policy:drain})`; (2) `splice(add, {add_places:[3 lane states M0=0], add_transitions:[6], add_arcs:[19]})`. Each leg is conformance-gated + `net_splice` ledger-recorded + rev-bumped; reruns noop. Live bundle (`.meta/.omt/`, gitignored): snapshot before running; expected rev 58→60, places 13→15. `RESOURCE_PLACES` − `e2e_receipt` + `sync()` bootstrap/missing-resources update ride in the same `state.py` round (one round, receipt discipline — B/B2/B3 precedent).
- Test-bundle migrations use the same helper (hermetic `tmp_path`, never live).

## 6. Blast radius (explicit)

- `state.py` ONE round: `RESOURCE_PLACES`, `_fire_lane_move` + 4 call-site slot-delta wirings, `ensure_pool_b3b`, `managed_ops.py` ONE round (6 lane rows `fired_today: no-B3-fallback` → `yes-B3b-template`; `check_ledger_evidence` unchanged — keys already asserted in B3).
- Fixtures asserting exact place sets / catalog membership update: `test_net_pool`, `test_net_sync` (skeleton + missing-resources), `test_net_resources` (catalog), `test_net_mine/synthesize/menu` fixtures, slice-A `test_managed_ops` (B3b-updated lane rows), B3 `test_b3_lane` (migrated-net firings flip `not_lane_net` → `fired=true` where template lands; legacy-bundle fallback tests stay).
- Parked: crash reorder (C), matrix/payback (D), attention-vs-workers reconciliation, cap-raise amendment.

## 7. Exit

- Programming: ONE `state.py` round + ONE `managed_ops.py` round + `ensure_pool_b3b` + slot-alias code + fixture updates (receipt discipline: one edit per file per e2e receipt).
- Testing: new `test_b3b_template` goldens (migration idempotent + noop rerun; cap 15 held; full lane walk claim→submit→verify→start→finish fires all 6 with slot accounting; legacy bundle keeps labeled fallbacks; alias both slot names; Goals/attention/archive untouched) + full receipt (`claim/pool/workers/recovery/lane/worktree/slice-A/conformance/state` + B/B2/B3 suites green) + `check` 265/0 + `build` OK + suite green + live rev 58→60 snapshot-guarded migration + `test_report.md` → `omt_complete`.

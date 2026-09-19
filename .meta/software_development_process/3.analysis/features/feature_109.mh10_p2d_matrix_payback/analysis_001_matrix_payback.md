# Analysis 001 — Slice D: allow/deny matrix + payback + net-zero retirement (spec for approval)

> Feature: `feature_109.mh10_p2d_matrix_payback` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-19.
> Resumes: PROJECT.md §Plan P2 (d)+(e)+(a) + CURRENT_STATE iter15 Next (Slice D) + slices A/B/B2/B3/B3b/C shipped (rev 60, suite 1788, check 265/0).

---

## 1. What D must prove (P2 re-entry rows)

P2 §Plan needs ALL of (a–e). Status after C:

- (b) one-template map — PARTIAL EARNED: `managed_ops.py` MANAGED_OPS + `claim/release/submit/verify/integrate` all `yes-B2/B3b-template` (fire-carried); `absent_lane_occupancy` + `project_sync`/`session_menu` stay `no`/`derived-read` by design; `crash_window` CLOSED by C (record-before-clear + backfill).
- (c) crash reorder — EARNED (feature_108, 6 goldens, C1 CLOSED, rev stays 60).
- (d) allow/deny matrix — ABSENT: no matrix run on real edits (seeded invalids rejected + valid controls accepted).
- (e) net-zero retirement + diet — ABSENT: gates 10/12 held throughout, but no D-time retirement/diet math yet.
- (a) measured wins + payback — ABSENT: P1 shipped 2026-09-18, zero wild sessions, only seeded blind-demo numbers (7/7, 8/8, 13/13). No natural-use data, no payback math.

D earns (d)+(e) and defines the (a) measurement protocol. D does NOT flip any live gate (advisory stays until a future complete a–e bundle + separate approval).

## 2. Allow/deny matrix (proposed, approval-gated)

Authority: `scripts/omt/net/gate.py::check_edit_allowed` codes (`ERR_NET_NOT_ENABLED / ERR_NET_STALE_REV / ERR_NET_DRIFT_CONFLICT / ERR_NET_DOWN / OK + break_glass`) + TS enforcer `g.net` + `phase_gate`/`gate_driver` dry/live paths. Harness: differential `managed_ops.check_counts` (FIRED/OMISSION/DIVERGENCE) + `check_ledger_evidence` (fired vs fallback-by-reason, offenders never silent).

### 2a. Valid controls (must ALLOW)

| # | Class | Setup | Oracle |
|---|-------|-------|--------|
| V1 | `fire(work_start)` → `src/` edit in same 8h window | fresh fire receipt (`net_fire transition=*_start`) | `OK`, edit proceeds, ledger `transition/fired=true` |
| V2 | derived reads (`project_sync`, `session_menu`, `check_live`) without fire | no receipt | allowed as `sync_render (derived read)`, never counted as firing |
| V3 | solo path (`command_id=None`) | no index expected | unchanged, no marker, no index (D8 frozen) |
| V4 | reconcile-committed retry replays (post-C backfill) | W1/W2 planted then reconciled | replays, exactly 1 rev bump, `recovered_committed[_backfilled]` |
| V5 | e2e receipt refresh after one `state.py` round | one edit per file per receipt | receipt N/N, `check` 265/0 |

### 2b. Seeded invalids (must DENY fail-closed)

| # | Class | Setup | Oracle |
|---|-------|-------|--------|
| I1 | `src/` edit with no fire receipt, no break-glass | clean ledger window | DENY `ERR_NET_NOT_ENABLED` (or enforcer block), no state change |
| I2 | stale rev (`expected_revision != live`) | bump live after probe | DENY `ERR_NET_STALE_REV`, retry re-probes |
| I3 | drift/conflict (marking vs bundle, overlay mismatch) | plant divergent marking | DENY `ERR_NET_DRIFT_CONFLICT`, diagnosis names the divergence |
| I4 | net-down without break-glass | bundle unreadable / engine unavailable | DENY `ERR_NET_DOWN`, `_unknown` stays unknown (never interpolated) |
| I5 | expired break-glass (`scope:all` older than 8h) | aged skip record | DENY (no silent pass), must re-issue |
| I6 | generation/owner mismatch on claim | foreign `generation`/`owner` | DENY, no token adopted, refund path taken (B-pattern) |
| I7 | lane move without slot / over workers cap | 2 active + 3rd submit | DENY or labeled `fire_fallback` (never silent double-adopt) |
| I8 | resultless-commit retry as fresh fire | old-shape marker, no index, `live==to` | DENY-synthesize: `txn_unindexed_commit` diagnosis, marker left (C-rule) |

Execution substrate: worktree/sidecar real edits (never live harness until matrix green), stage discipline (snapshot → allow → single e2e → clear), `uv` only. Every row records `transition/fired/fire_fallback` ledger keys so `check_ledger_evidence` closes its loop (no offenders).

Refused: auto-retry inside `_transact` (feature_084 lock); synthesizing results (generation ownership); raising the 15-place cap or 12-gate ceiling inside D.

## 3. Payback math (measurement protocol, not a claim)

Setup cost (per session): `fire` + preflight + receipt refresh + `check`/`build`/suite time. Support cost: template/bundle migrations (B2 57→58, B3b 58→60 pattern) + diet trims + goldens maintenance.

Win classes (natural only — seeded matrix rows do NOT count): avoided double-fires (W1/W2 hits in the wild), stale-rev blocks that would have clobbered, drift diagnoses that named a real divergence, crash-backfill recoveries with same-txid replay.

Protocol: run P1-advisory + A–C enforcement in natural sessions; log every win with ledger pointer + would-have-cost (rework hours). Payback = `Σ(avoided_rework) − Σ(setup+support)` over N≥10 wild sessions. Gate-flip needs payback > 0 surviving support (migrations + diet + goldens), otherwise verdict stays keep-advisory (D7 pattern).

## 4. Net-zero + diet math (binding on Programming)

- Gates: 10/12 today. D adds ZERO live gates (matrix harness is tests-only). If a future flip proposes +1 gate, the same edit retires −1 in the same `.omt` edit (retirement candidates: advisory fallback rows already superseded by B3b-template `yes` rows; `archive_pool` consolidation; a named `OMISSION` class after its bypass is rewired). No retire → no flip.
- Budgets (head 2026-09-19, `check` green): `tool_args` 2455/2464 (9B headroom), `schemas` 1840/1856 (16B), `agents_md` 2918/2944 (26B), `nav` 64990/65536, `work_md` 8457/8704. Any new tool arg/schema/nav record in D pays its bytes in the same edit (diet the longest arg — `omt_net` describes 657B — or grow the cap deliberately in the same `.omt` edit per budget-diet warnings). Matrix goldens live in `tests/features/feature_109*/`, never in live tool schemas.
- Places: 15/15 exact (B3b). D adds no places/transitions/arcs (no template change, no migration, rev stays 60) — matrix exercises the existing template only.

## 5. Blast radius (explicit)

- Analysis (this doc) + FEATURE.md/PLAN.md scope fill — docs only, non-gated.
- Programming (on approval): tests-only — new `tests/features/feature_109.mh10_p2d_matrix_payback/test_d_matrix.py` (V1–V5 + I1–I8 goldens) + optional `managed_ops.py` reader extension for matrix rows (same-file round discipline, e2e receipt exempt for the test file). NO `state.py` behavior change (C-rule frozen); NO template/bundle change; NO live gate registration.
- Testing: matrix goldens RED-then-GREEN (invalids deny on old code paths where applicable) → `test_net_transaction_authority` + `test_net_recovery_journal` 17/17 → `tests/scripts/omt/` 637 → e2e receipt → full suite green → `check` 265/0 + `build` OK → `test_report.md` → `omt_complete`.

## 6. Exit (approval gate)

- This spec needs explicit user approval before Programming (no auto-fix, no silent scope growth).
- On approval: `omt_phase{phase:Programming}` → tests-only matrix → Testing (matrix + regressions + receipt + suite + check/build) → `test_report.md` → `omt_complete` feature_109 → PROJECT.md/CURRENT_STATE D-row checked.
- Residual after D: (a) natural-use payback accumulation (needs wild sessions) — then P2 close-or-flip decision with full (a–e) bundle.

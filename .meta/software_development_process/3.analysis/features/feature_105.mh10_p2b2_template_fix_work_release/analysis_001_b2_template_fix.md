# Analysis 001 — Slice B2: additive template fix (worker_slots + work_release, attention refunded)

> Feature: `feature_105.mh10_p2b2_template_fix_work_release` (`minor_feature`, project `meta_harness_10`) · Phase: Analysis · Date: 2026-09-18.
> Parent: slice-B evidence path (`feature_104`, `_fire_pool_move` + `transition/fired/fire_fallback` ledger keys, suite 1749 green, `check` 265/0).

---

## 1. Residuals being closed (slice-B §3 leaves)

(i) **attention-vs-workers conflict** — template `work_start` holds `agent_attention` (cap 1, IDEA-002 §2.3 serial-mirror) while the task model allows 2 concurrent workers (`WORKER_SLOTS_CAPACITY=2`, `state.py:98`). Slice B kept legacy acceptance via `transition_not_enabled` fallback. (ii) **missing `work_release` back-edge** — `release_task` (active→pending) has no template transition (`work_complete` goes active→done), so slice B deterministically records `no_transition`.

Live template at rev 57 (head-verified via `state.load(.meta/.omt)`): places 12 incl. `agent_attention=1/feature_ready=1/work_pending=0/work_active=0/work_done=7`; transitions (`work_complete`,`work_start`); `work_start` in {attention, feature_ready, pending} → out {feature_ready, active} (holds attention); `work_complete` in {active} → out {attention, goal_satisfied, done}.

## 2. Why additive-only (no arc removal)

Splice removal rebuilds the net copying survivors (`_rebuild_without`, `state.py:1840`) — it removes whole places/transitions, **not single arcs**. Decoupling attention from the pool path (deleting `attention→work_start` + `work_complete→attention`) would require removing the `agent_attention` place or the pool transitions themselves: refused per non-interference (D5). Pre-pool subnet template (`_subnet_mutation`, `state.py:2257`) keeps its attention claim/release untouched; pool-vs-subnet attention use is a **named divergence** (pool = concurrency via slots, subnets = serial-mirror), not a contradiction.

Concurrency is recovered **without removing arcs**: slice-B `_fire_pool_move` already refunds non-pool places (attention/feature_ready) to pre-fire values inside the lock-held transaction. Refund makes attention non-blocking on pool nets (every pool transaction starts with attention=1, fires, refunds to 1 — the second concurrent claim still sees attention=1), while the firing itself stays a real `fire_marking` successor for the pool deltas. B2 extends the adopted set from pool-only to **pool + worker_slots**.

## 3. B2 template delta (one splice-add migration, 12→13 places, cap 15 held)

- `add_places`: `worker_slots` tokens = `max(0, 2 − active_bindings)` (2 on drained rev 57; formula covers non-drained reruns — idempotent).
- `add_transitions`: `work_release` (the missing back-edge).
- `add_arcs` (5): `worker_slots→work_start` (claim consumes a slot) · `work_complete→worker_slots` (finish releases; wired by B3, harmless now — hermetic bundles without the arc are unaffected) · `work_active→work_release` (input) · `work_release→work_pending` + `work_release→worker_slots` (release restores pending + slot; no attention/feature_ready touch — matches today's code behavior).
- `POOL_TRANSITIONS` grows to `("work_start", "work_release", "work_complete")` (informational; sole in-repo definition).

## 4. Helper v2 (`_fire_pool_move` + `slot_delta`, ONE `state.py` round with callers)

New signature `_fire_pool_move(st, transition, src, dst, *, slot_delta: int)` (`-1` claim, `+1` release); direct `worker_slots ∓1` lines leave the callers (single ownership — no double decrement):

1. Non-pool bundle → `(False, "not_pool_net")`, no mutation (unchanged).
2. Transition missing → legacy `_move_pool_token` + code slot `+= slot_delta` (if place present) → `no_transition` (release on pre-B2 bundles keeps today's row).
3. `fire_marking` raises → legacy + code slot → `transition_not_enabled` (attention-held pre-B2 shape keeps slice-B row).
4. Shape-check: pool deltas exactly `src−1/dst+1`, other `POOL_PLACES` unchanged (existing) **plus** `worker_slots` delta `== slot_delta` whenever the place exists in live marking. Template-without-slot-arcs on a slot bundle (delta 0 ≠ ±1) → legacy + code slot → `transition_shape_mismatch` (never silent, never half-managed).
5. Fire path: adopt successor for `src/dst/worker_slots`, **refund every other place** (attention, feature_ready, …) to pre-fire values; return `(True, None)`. Slot conservation: start −1 balanced by complete/release +1; code fence (`_active_task_count` + capacity guard) stays authoritative — template slot is the checkable mirror, never the gate.

Back-compat: hermetic old-shape bundles (attention arcs, no slots/release — all of `test_net_pool`, `test_net_two_worker_capacity_scope`, feature_104 goldens) take the labeled fallbacks exactly as today; **zero existing tests change shape**.

## 5. `managed_ops.py` ledger-evidence reader (closes TA todo `:122`)

`MANAGED_OPS` rows for `claim_task`/`release_task` flip to fired-on-happy-path with the B2 note; new `check_ledger_evidence(records)` asserts every `net_claim`/`net_release` row carries `transition/fired/fire_fallback` keys and returns `{fired, fallback:{reason: n}}` — the machine-checkable form of analysis_001 §4's "new ledger-evidence test". B2 goldens assert it; `check_live` stays counts-only (no behavior change).

## 6. Live migration (local-only, ignored files, snapshot-guarded)

`.meta/.omt/` bundle files are gitignored — B2 ships an idempotent `ensure_pool_b2(base)` helper (additive only, reruns are no-ops) plus a snapshot-first local run (`cp` bundle → `.sandbox/b2_mig_snapshot/` → migrate → `probe` → e2e). Drained rev 57 makes it safe (0 active ⇒ slots M0=2, no in-flight claims); non-drained reruns use the §3 formula. Live rev bumps 57→58; no committed files change.

## 7. Exit

Programming: ONE `state.py` round (helper v2 + 2 callers + constant + migration helper) + `managed_ops` rows/reader + new goldens (B2 happy-path claim/release fire, **2-concurrent both fire**, slot-exhaustion guard preserved, old-shape fallbacks unchanged, migration idempotent, ledger-evidence green); existing suites stay green. Testing: `test_report.md` + `check`/`build`/suite green + e2e receipt refresh per harness-surface round + deliberate `work_md` budget growth 8192→8704 (8214 over today from scaffold linkage) with `WORK_BUDGET` pin sync. Lane/integration rewiring (B3), crash reorder (C), matrix/payback (D) stay parked.

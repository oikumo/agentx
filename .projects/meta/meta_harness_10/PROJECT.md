# PROJECT: meta_harness_10 — Petri Net as Global State for MH Development

> Status: **complete** · **v0.3 (2026-09-18)** — staged hybrid (user-picked 2026-09-18): Phase 1 read-only global projection (MH9-compliant, advisory) with R1–R6 locked; Phase 2 enforced gate only on measured wins + C6 map + payback. Created by `project.py new --slug meta_harness_10`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_10`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: MH10 unifies projects/workflows/features/tasks under one Petri-backed global state view — advisory first (P1), enforced only if earned (P2).

**Next:** P1 SHIPPED 2026-09-18 (`omt_complete` feature_102 → Done; blind demo 13/13 from 1994B md alone + `test_report.md`; `check` 265/0 + `build` OK + suite 1739 green before AND after). P2 stays parked (no (a–e) evidence yet). Next program step: M1 (P2 verdict: gate or keep-advisory, written with evidence).

---

## Summary (one line)

**One Petri-backed global state for all MH development — read-only projection first (reuse net rev 57 as facts, never as authority), enforcement only after measured avoided-failures + full transition map + crash-ordering + payback.**

---

## Purpose

### What this project is

- The **sole execution home** for Petri-as-global-state after mh9-close (mh8/mh9 read-only; nothing lands there).
- A **two-phase program**: P1 advisory projection over projects + workflows + features + tasks with divergence instrumentation → P2 gate (every managed move = checked fired transition) only if P1 earns it. "Global state" in MH10 means reading 1 (**view**) now; readings 2–4 (**store** / **authority** / **model**) only via P2 re-entry (analysis_002 §2).
- The **non-interference guarantor**: live harness pinned/green throughout; experiments in sidecars/worktrees; slice violation → slice reverts, never the harness.

### What this project is **not**

- NOT executable closure by default. P2 re-opens parked mh9-S5 (C6) and needs ALL P2 re-entry evidence — no authority claim until then.
- NOT re-shipping mh8/mh9 (039–050 net engine, 072/073/092, S3 contract, S4 frontier stand) or weakening locks (think/protect, two-hats + genuine-RED + auto-revert, net-zero 10/12, KNOWN empty, Tier-3 excludes net, stage discipline, `uv` only).
- NOT a date plan: each slice estimated only after reproducer + support boundary + oracle + resource budget are concrete.

---

## Plan — P1 then gated P2 (one bounded queue; max 1 active, 2 only as 1 correctness + 1 measurement on disjoint files)

### P1 — Global read-only projection + divergence instrumentation (advisory; no src/authority change)

- Goal: one bounded global view a fresh session can orient + resume from, with the C6 gap measured instead of claimed.
- Shape: `projects (draft/active/complete) / workflows (subject→loop→round) / features (Analysis→Done + tdd_position) / tasks (WORK.md pool pending/active/done + net rev marking + resources/workers/verification/integration)` — ≤2KB default with required-continuation (never mid-sentence cuts). Missing/inconsistent/stale labeled; unknown stays unknown.
- Steps: (1) reuse net rev 57 probe + WORK.md Tasks + `.projects/meta/META.md` + feature ledger as fact sources (projection, no store, no writer migration — designate the future one-writer per action in a migration log); (2) reuse 072 evaluator + 073 prep + 092 digest + S3 contract schema as substrate; S4 paired-projection pattern for the P1 demo; (3) divergence log: `projection(B) vs marking(M)` per managed op incl. known direct-counter paths (`claim_task`/recovery/lane via `_move_pool_token`, absent-lane binding-only occupancy) — counted as OMISSIONS, never as firings; (4) 2-task demo (routine fix + interrupted/resumed) orients from the projection alone.
- Exit: demo passes + divergence log published + `check`/`build`/suite green before AND after. Size: `minor_feature`. Depends: none (reads live state only).

### P2 — Enforced global gate (PARKED until all re-entry evidence exists)

- Goal: every MH project/workflow/feature/task movement = a checked fired transition; stale rev/generation/owner cannot commit.
- Re-entry needs (ALL): (a) P1 measured wins — naturally occurring avoided failures (not only seeded) + payback math surviving setup/support; (b) one-template transition map with differential conformance (every managed op incl. `claim_task`/recovery/lane/integration = fired transition; `projection(B)=M` invariants across pass/fail/cancel/recovery; identity-sensitive resume); (c) record-before-clear reorder + crash-injection suite (mh9-C1 residual); (d) allow/deny matrix on real edits incl. seeded invalid classes rejected + valid controls accepted; (e) net-zero retirement + diet math for any new gate/tool/nav record in the same edit.
- Exit: gate live under stage discipline (snapshot → allow → single e2e → clear) with the matrix green; any red → revert before further work. Size: `minor_feature` ×1–2 (split only if file sets disjoint). Depends: P1-green + all of (a–e).

Milestones: **M0** (P1: one global view + honest divergence log) → **M1** (P2 verdict: gate or keep-advisory, written with evidence). No M2 scheduled.

---

## Scope & success criteria

**Scope:** P1 now (derived view + divergence log; **no new store** — any durable global record is reading 2 = S6a territory, not P1); P2 parked pending §Plan re-entry evidence.

**P1 schema contract (analysis_002 R3/R5):** explicit join keys across WORK.md tasks / ledger features / net bindings / project slugs (C4 residual named, never interpolated); per-section as-of (`rev/HEAD/ts` — there is no global as-of); sync-generated rows (WORK.md/META.md via `project.py sync`) labeled **derived**, never source; workflow section shows catalog position + last `.sandbox/` round pointer only; loss from doc→token projection labeled.

**Success:**

1. P1: a **blind** fresh session orients + resumes one real task per demo class (routine fix, interrupted/resumed) from the global projection alone against an acceptance checklist (R4 falsifiable protocol); divergence omissions named with file:line; no silent drops.
2. Live harness green throughout (`check` 0 + `build` OK + e2e + suite + KNOWN empty; budgets never regress without diet; net-zero holds; Tier-3 excludes net).
3. Docs section-retrievable: snapshot + queue here; narrative in CURRENT_STATE.md + history. Roadmap/projection out of startup context (section retrieval + stable refs).

**Out of scope:** P2 enforcement before re-entry; any new durable store in P1; mh8/mh9 re-implementation; gate removals; `src/agentx/` product work — MH10 never imports `src/agentx/*` (harness↔product non-dependence, R2); `feature_001.session_user_objectives_driven_by_Petri_Net` + `feature_002` explicitly out (separate product consumers, not MH10 territory); second adapter/SDK/remote/distributed/timed/colored/self-modification (real user need + measured local limitation first); any Git/publication allowance (each policy change ships separately under current authority).

---

## Status

- [x] v0.1 (2026-09-18): created (`project.py new`, state: draft).
- [x] v0.2 (2026-09-18): refined per user pick — staged hybrid (P1 advisory now, P2 parked with re-entry); MH9-conflict named (S4 MERGE ≠ KEEP, C6/C1 residuals carried, not re-litigated).
- [x] P1 `feature_102.mh10_p1_global_projection` Analysis signed (2026-09-18: `analysis_001_global_projection.md` + FEATURE.md scope/traceability; overlap gate cites mh9 rows, advisory profile frozen, sidecar `.sandbox/global_state/` designated).
- [x] v0.3 scope deep-think (2026-09-18, user-approved all): `analysis_002_scope_deep_think.md` → R1–R6 folded into Scope (4-readings lock, harness↔product non-dependence, join keys + per-section as-of, blind demo protocol, derived-row marking, no-new-store non-goal).
- [x] P1 Programming (2026-09-18: sidecar `.sandbox/global_state/build.py` + projection.md ≤2KB + projection.json + divergence.md + snapshots/; `check` 265/0 + `build` OK; no live tool registration per net-zero).
- [x] P1 Testing SHIPPED 2026-09-18 (blind demo per R4: routine 7/7 + interrupted 8/8 full-render + honest probe 7/11 → R4 reorder fix → retest 13/13 from 1994B md alone; `test_report.md`; `check` 265/0 + `build` OK + suite 1739 green before AND after) → `omt_complete` feature_102 → Done.
- [x] M1 verdict (2026-09-18): **keep-advisory** — see D7. P2 stays parked; project ready to close.

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — mh10 is the sole Petri-global-state home (2026-09-18):** mh8/mh9 CLOSED read-only; global-state work lands here. Forced closes reserved for tombstones/short-slug gaps.
- **D2 — staged hybrid, P1 first (2026-09-18, user-picked):** read-only projection + divergence log before any enforcement; P2 needs all §Plan (a–e) evidence.
- **D3 — MH9 verdict stands (MERGE, analysis-only):** S4-keep re-entry NOT met; C6 (lifecycle ops bypass transition relation: `state.py` `_move_pool_token`/`claim_task`/recovery/lane vs `fire()`; absent-lane binding-only occupancy) and C1-residual (clear-before-record crash window) carried as scoped unknowns, fixed only inside a declared P2 slice with approval.
- **D4 — inherited locks stand:** net solo-only, Tier-3 excludes net, KNOWN empty, gates net-zero 10/12, clean-close-over-force, stage discipline + `uv` only + `src/` needs `omt_phase` (this doc non-gated).
- **D5 — non-interference is mechanical:** default surfaces `.projects/meta/meta_harness_10/` + `.sandbox/` + declared sidecars; live surfaces change only inside a declared slice with approval via stage + `check`/`build` + suite green before AND after; slice violation → slice reverts.
- **D6 — scope deep-think adopted (2026-09-18, user-approved R1–R6):** "global state" = reading 1 (view) now, readings 2–4 only via P2 re-entry; MH10 never imports `src/agentx/*`, feature_001/002 out; join keys + per-section as-of + derived-row marking are P1 schema contract; demo is blind with acceptance checklist; no new store in P1 (reading 2 = S6a territory).
- **D7 — M1 verdict: keep-advisory (2026-09-18):** P2 re-entry evidence assessed against §Plan (a–e), all absent: (a) no natural-use data — P1 shipped today, only seeded blind-demo numbers exist (7/7, 8/8, 13/13), zero wild sessions, no payback math possible; (b) no one-template transition map — C6 bypasses (`_move_pool_token`/`claim_task`/recovery/lane, absent-lane occupancy) still outside `fire()`; (c) crash window still clear-before-record (`:730-742` vs WAL `:672-675`), no injection suite; (d) no allow/deny matrix run on real edits; (e) nothing to retire — no new gate/tool was added (net-zero 10/12 intact). Therefore no enforcement change is earned: projection remains advisory sidecar, P2 stays parked under unchanged re-entry terms. A future complete (a–e) bundle re-opens the question via a new declared slice; this verdict does not pre-judge it.

---

## References

- Prior home (read-only): `.projects/meta/meta_harness_9/PROJECT.md` (v1.0 complete, S0–S4, verdict MERGE, S5+ parked) + `CURRENT_STATE.md`.
- Roadmap: `sandbox/META_HARNESS_ROADMAP.md` (baseline `81b3aa1`; mh9 §1 re-verified at HEAD).
- Live pins (2026-09-18, HEAD `f66d268`, `check` 265/0 green): net rev 57 `drained_complete` (done=7, pending=0/active=0, resources 5/5, workers 0/2 used, verification 0/1 used, integration 0/1 used); `omt_q{op:state}` global phase Unknown + `feature_102` Analysis dangling (feature-scoped record — global Unknown and feature-Analysis coexist, not a conflict).
- Head-verified residuals: `scripts/omt/net/state.py` C6 (`_move_pool_token` `:819-834`, `claim_task` `:896`, absent-lane `:296-300` vs `fire()` `:763-768`) + C1 (`_transact` `:730-742` vs WAL `:672-675`); `.opencode/lib/omt_shared.ts:154-159` (F09) · `.opencode/plugins/omt_enforcer.ts:100-103` (F02) · `.opencode/lib/enforcer/phase_gate.ts:455` vs `:512` (F05-caller) · `.opencode/lib/enforcer/gate_driver.ts:219-221/:366-410` (F03 + dry/live divergence).
- SSOT: `.meta/META_HARNESS.omt` · WORK.md Tasks · `.projects/meta/META.md` · `.workflows/meta_harness/loops/meta_harness_project.md`.

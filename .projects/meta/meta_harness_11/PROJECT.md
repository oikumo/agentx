# PROJECT: meta_harness_11 — Session Use-Case Closure (Whole-Project Menu → Multi-Pick → Concurrent Doing)

> Status: **complete** · **v0.1 (2026-09-19)** — user-picked FULL O1–O6 (2026-09-19). Created by `project.py new --slug meta_harness_11`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_11`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: MH11 closes the session use-case gaps — selectable whole-project menu with atomic multi-pick apply, then concurrent dispatch.

**Next:** MH11 COMPLETE (closed 2026-09-20) — 117 + 118 Done, O6a/O6b DEFERRED (D5: tokens 0% structural + wall median 11% below 15%/10% bars, D1 stays locked); take WORK.md NEXT `proj:agentx_concurrent_development`.

---

## Summary (one line)

**Cold-start → whole-project menu → multi-pick + directives → atomic net adapt → concurrent doing with safety → WORK.md re-render + audit.**

---

## Purpose

### What this project is

- The **sole execution home** for session use-case closure after mh10-close (mh10 complete, rev 60 `drained_complete`; mh8/mh9 read-only).
- A **full O1–O6 program** from `.sandbox/meta_harness_session_usecase_gaps.md` (2026-09-19, G1–G16):
  - **O1** Whole-project menu composer (net counts + Projects + drift/hygiene + unscoped 001/002 → single NEXT/Other/Blocked/Resources with stable IDs) — closes G1, G2, G3, G7.
  - **O2** Multi-select + directive protocol (`pick {id,…} + per-id directive` grammar, `question`-tool binding, batch rev-checked apply/rollback) — closes G5, G6, G8, G9.
  - **O3** Identity-aware pool (overlay ID map → claimable menu handles, de-anonymize coverage) — closes G10, G11.
  - **O4** Concurrent dispatch runtime (enabled[] → N worktrees/sub-agents → join → work_complete; WIP/capacity enforced; wires 080–083) — closes G12, G13.
  - **O5** Live progress projection (menu-time freshness via pre-present `probe`; re-render push after each fire; minimal live view) — closes G4, G14.
  - **O6** Bridge harness-pool ↔ agentx adaptive net (scope feature_001; USER_OBJECTIVES ↔ net fragment contract; directive→fragment via 042 templates) — closes G15 (+ G16 measurement via wild-session payback N≥10).
- The **non-interference guarantor**: live harness pinned/green throughout; experiments in sidecars/worktrees; slice violation → slice reverts, never the harness.

### What this project is **not**

- NOT re-shipping mh10 (P1 projection, P2 A/B/B2/B3/B3b/C/D gate, 8 features, suite 1801) or weakening locks (think/protect, two-hats + genuine-RED + auto-revert, net-zero 10/12, KNOWN empty, Tier-3 excludes net, stage discipline, `uv` only).
- NOT executable concurrency by default without decisions: O4 needs explicit reversal of F7 (`agent_attention=1` serial) for this lane; O6 needs explicit revisit of D1 (`src/agentx/` out-of-scope) — both ship only with new decisions + evidence.
- NOT a date plan: each slice estimated only after reproducer + support boundary + oracle + resource budget are concrete.

---

## Plan — O1→O6 (one bounded queue; max 1 active, 2 only as 1 correctness + 1 measurement on disjoint files)

- **O1 — Whole-project menu composer:** extend `sync_md` render: pool counts + `project.py sync` rows + `omt_q{drift}` hygiene + PENDING 001/002 as selectable proposals; stable IDs; keep D19 ordering + rev-stamp. Size: `minor_feature`. Depends: none.
- **O2 — Multi-select + directive protocol:** selection grammar; one `apply_selection` transaction (claims+fires+splices, atomic, ledger `net_*`, re-render); directive attach as overlay annotation. Size: `minor_feature` ×1–2. Depends: O1 IDs.
- **O3 — Identity-aware pool:** overlay `task_id→holder` map; `probe.menu` emits claim handles; `claim` reserves on select; `fire --expected-revision` per handle; coverage de-anonymized. Size: `minor_feature`. Depends: O1/O2.
- **O4 — Concurrent dispatch runtime:** wire 080–083: worktree per claim, 2-worker arbitration, verification/integration lanes, progress fires; explicit F7 reversal decision. Size: `major_feature`. Depends: O2/O3 green.
- **O5 — Live progress projection:** menu-time freshness (`probe` before present); re-render push after each fire; minimal live view reusing studio projection. Size: `minor_feature`. Depends: O1.
- **O6 — Harness↔agentx bridge:** scope feature_001; define which net owns execution vs harness state; directive→fragment via 042 templates; payback metric (wild N≥10). Size: `major_feature`. Depends: D1 revisit + O2/O4.

Milestones: **M0** (O1+O2+O3: selectable menu with atomic apply, still serial) → **M1** (O4+O5: true concurrency + live view) → **M2** (O6: bridge + payback). Minimal use-case slice = M0 before M1 (gaps doc §4).

---

## Scope & success criteria

**Scope:** Full O1–O6 per user pick 2026-09-19; M0 first, M1/M2 only after M0 green + F7/D1 decisions recorded.

**Success:**

1. M0: cold start renders whole-project menu (pool + 3 active / 3 draft projects + 001/002 + hygiene) with stable IDs; multi-pick `{id,…}` + directives applies atomically (claims+fires+splices, ledger `net_*`, re-render); stale rev refuses with re-render; coverage de-anonymized.
2. M1: `enabled[]/parallel[]` → N worktrees/sub-agents → join → `work_complete` with WIP/capacity enforced; menu-time freshness; live view during execution.
3. Live harness green throughout (`check` 0 + `build` OK + e2e + suite + KNOWN empty; budgets never regress without diet; net-zero holds; Tier-3 excludes net).
4. Docs section-retrievable: snapshot + queue here; narrative in CURRENT_STATE.md + history.

**Out of scope:** P2-style enforcement before O1–O3 evidence; second adapter/SDK/remote/distributed/timed/colored/self-modification (real need + measured limitation first); any Git/publication allowance (each policy change ships separately).

---

## Status

- [x] v0.1 (2026-09-19): created (`project.py new --slug meta_harness_11`, state: draft).
- [x] v0.1 scope (2026-09-19, user-approved full): O1–O6 from gaps doc adopted; M0→M1→M2 order; F7/D1 reversals deferred to O4/O6 slices.
- [x] O1 shipped to Testing (2026-09-19): `feature_110.whole_project_menu_composer` (minor_feature, Testing; 14 goldens, live menu rev 60 in WORK.md, trim+grow budget 9728, test report).
- [x] M0 COMPLETE (2026-09-19, user-approved close): O1 (110) + O2 (111) + O3 (112) Done + O5-slice (113) Done; suites 1817→1830→1840→1847; `check 265/0`; tree clean. O4/O6 unspawned (need F7/D1 decisions).
- [x] M1 SHIPPED (2026-09-20, user-approved close): O4 `feature_114.concurrent_dispatch_runtime` Done (major_feature, TDD GREEN; 23 canonical + 2 pointer goldens, targeted 56/56, suite 1872 + 2 deselected, `check 265/0`, test report); F7 lane-only reversal locked (fan-out ≤2, `src/` serialism unchanged). O6 unspawned (needs D1 revisit).
- [x] O5-follow-up SHIPPED (2026-09-20, user-approved close): `feature_115.live_progress_full_push_join_view` Done (minor_feature; 8 goldens, targeted 78/78, suite 1880 + 2 deselected, `check 265/0`, test report; D4 proposal-only + Tier-3 held). Next = O6 (needs D1 revisit) or WORK.md NEXT `proj:agentx_concurrent_development`.
- [x] 117 SHIPPED (2026-09-20, user-approved implement-now): `feature_117.dispatch_lane_exploitation_for_harness_verifies` Done (minor_feature; pure `verify_dispatch.py` batch composer + report join, 8 goldens `test_net_verify_dispatch_117.py`, neighbors 68/68, suite 1899 + 2 deselected with 2 pre-existing improvement003 budget-pin failures, `check 274/0`, test report; F7 lane-only, D1 locked, no new places/ledger kinds).
- [x] 118 Done CONFIRMED (2026-09-20): `feature_118.mh11_worktree_lifecycle` Done (major_feature, TDD closed; 11 goldens + 2 pointer smokes, suite 1887 baseline, `check 274/0`; `omt_complete{advance_to:Done}` green — already Done, no-op confirmed).
- [x] O6a/O6b DEFERRED (2026-09-20, user-approved defer-with-evidence, D5): harness↔agentx bridge not spawned — dispatch median N=3 wall 11.0% / tokens 0.0% structural below pre-registered bars (O6a ≥15%/10%, O6b ≥25%/15%); tokens 0% forces defer under AND-threshold; D1 (`src/agentx/` out-of-scope) stays locked. Revisit only with new decision + N≥10 dispatch median or wall-only threshold revision. MH11 closes as M0+M1+verify-exploitation complete, bridge deferred.

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — mh11 is the session use-case home (2026-09-19):** mh10 CLOSED complete (rev 60); use-case work lands here. Inherits D4 locks (net solo-only, Tier-3 excludes net, KNOWN empty, net-zero 10/12, stage + `uv` only + `src/` needs `omt_phase`; this doc non-gated).
- **D2 — full O1–O6, M0 first (2026-09-19, user-picked):** all improvements in scope, but M1 (concurrency) only after M0 (selectable atomic menu) green; F7 serial vs dispatch and D1 harness↔product boundary revisited only inside O4/O6 slices with approval.
- **D3 — gaps doc is proposal baseline, not authority (2026-09-19):** `.sandbox/meta_harness_session_usecase_gaps.md` G1–G16/O1–O6 are inputs; each O slice needs reproducer + oracle + resource budget before estimate.
- **D4 — O5-follow-up stays proposal-only + read-only (2026-09-20, feature_115):** full-text `push.tasks_block` is a dry-run `sync net_to_md` compose the caller still applies (no auto-commit); batch/join projection is pure read-only over `plan_to_dict` (no daemon/socket/TS import). No F7 reversal (no new fan-out) and no D1 revisit (`src/agentx/` untouched).
- **D5 — O6a/O6b deferred, D1 stays locked (2026-09-20, user-approved):** dispatch pilots d1–d3 median wall 11.0% / tokens 0.0% structural (N=3; serial N=10 baselines green) below pre-registered bars (O6a ≥15%/10%, O6b ≥25%/15%); tokens 0% is structural (same work, parallelism saves wall never tokens) so the AND-threshold forces defer regardless of wall. D1 (`src/agentx/` out-of-scope) NOT revisited; F7 lane-only (fan-out ≤2) NOT reversed. 117 banks the harness-internal wall saving instead (d2 51% reference, pure composer, no live mutation). Revisit O6 only with new decision + evidence (N≥10 dispatch median or wall-only threshold revision).

---

## References

- Gaps baseline: `.sandbox/meta_harness_session_usecase_gaps.md` (2026-09-19, rev 60, commit `d282a4c5eba555f81a6baca90e7d349a88218858`).
- Prior home (read-only): `.projects/meta/meta_harness_10/PROJECT.md` (v0.3 complete, P1+P2 A–D, 8 features, suite 1801, rev 60).
- Live pins (2026-09-19): net rev 60 `drained_complete` (done=7, pending=0/active=0, resources 4/4 free, workers 0/2, verification 0/1, integration 0/1); WORK.md Pool `pending=0 active=0 done=7 (places 15/15)`; 3 active / 3 draft projects; PENDING 001/002 scope unset.
- SSOT: `.meta/META_HARNESS.omt` · WORK.md Tasks · `.projects/meta/META.md` · `.workflows/meta_harness/loops/meta_harness_project.md`.

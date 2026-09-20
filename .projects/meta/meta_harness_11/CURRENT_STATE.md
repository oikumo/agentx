# CURRENT_STATE: meta_harness_11

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-20 (pilots: O6c template validated, 2 fixture runs)

### run p1 — fixture_bugfix — 2026-09-20

- rev: live HEAD · mode: fixture (hermetic) · workers: 1 · lanes: n/a
- serial: wall n/a · tokens 646 · harness_calls 2 · tool_calls 10 · verify 0.042s · success true · regressions 0 · blocks_tp 2 · missed 0
- dispatch: n/a (template validation, not same-pair comparison)
- payback: n/a · green: held (no live change)
- evidence: `uv run scripts/omt/bench/cli.py run --task fixture_bugfix --mode fixture` transcript above

### run p2 — fixture_nophase — 2026-09-20

- rev: live HEAD · mode: fixture (hermetic) · workers: 1 · lanes: n/a
- serial: wall n/a · tokens 559 · harness_calls 2 · tool_calls 7 · verify 0.022s · success true · regressions 0 · blocks_tp 2 · missed 0
- dispatch: n/a (template validation)
- payback: n/a · green: held
- evidence: `uv run scripts/omt/bench/cli.py run --task fixture_nophase --mode fixture` transcript above

### Outcome

- Template columns map 1:1 (wall/tokens/io/verify/success/check/build/suite/payback; `tokens_est=io_bytes//4` confirmed 2586→646, 2238→559).
- Same-pair serial-vs-dispatch N≥10 still pending real sidecars (deferred: tree dirty 115+116, `check` red work_md 9758>9728). Threshold decision O6a/O6b/defer pending wild.

---

## 2026-09-20 (auto — feature_116.mh11_o6c_wild_payback_measurement Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_116.mh11_o6c_wild_payback_measurement/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

### Close (continue — O6c design Done, user-approved)

- `omt_complete{advance_to:Done}` green — O6c metric + template + thresholds Done; no `src/`/`tests/` edits (docs-only).
- Evidence held at close: Analysis 001 + Design 001 + impl notes (template dry-run vs rev 60 / suite 1880) + test report (check red pre-existing work_md 9758>9728 noted, drift 0, suite baseline held).
- PROJECT.md unchanged (Next = pilots/wild N≥10 → O6a/O6b/defer, or WORK.md NEXT `proj:agentx_concurrent_development`).
- Non-interference held: no places/transitions; no ledger kinds; `src/agentx/` untouched; `uv` only. Tree still dirty (115 + 116 WIP, user commit).

---


## 2026-09-20 (resume: MH11 O6c spawned as feature_116)

### Done

- Spawned `feature_116.mh11_o6c_wild_payback_measurement` (`minor_feature`, linked to `meta_harness_11`); declared `omt_phase{Analysis}`.
- Filled FEATURE.md Summary/Scope/task-type + PLAN.md Objective (payback metric + N≥10 protocol, O6a/O6b/defer threshold, D1 locked).
- Wrote Analysis 001 (`analysis_001_payback_metric.md`) + Design 001 (`design_001_metric_template.md`) + impl notes (docs-only Programming); test report; `omt_complete{advance_to:Testing}` green.

### In progress / Blocked

- feature_116 in Testing (needs user close/ship call). `harnessc check` red pre-existing (work_md 9758>9728 from feature_115 WIP row, no new surface edit; grow deferred to 115 commit).

### Next

- User close/ship feature_116 → run 2 pilots then N≥10 wild → threshold decision O6a/O6b/defer; or WORK.md NEXT.

### Notes / context

- Non-interference: docs only so far; `src/agentx/` untouched (D1); `uv` only; feature_115 WIP still uncommitted (user commit).

---

## 2026-09-20 (resume: MH11 O6c measure-first scoping approved)

### Done

- Resumed MH11 at O5-follow-up SHIPPED (feature_115 Done 01:31, suite 1880 + 2 deselected, `check 265/0`, tree dirty WIP uncommitted) via `meta_harness_project` loop (root → subject → loop file; approval gates honored).
- User picked O6 bridge scope → refined to O6c measure-first (wild sessions N≥10 payback before bridge) over O6a contract-only / O6b full prototype; approved scoping draft (no `src/`/`tests/` edits).
- O6c scope drafted here: reproducer + oracle + budget (D3 gate) for payback measurement; D1 still locked (`src/agentx/` untouched), F7 lane-only locked (fan-out ≤2).

### Reproducer (G15/G16 gap)

- G15: harness WIP-pool (rev 60 `drained_complete`, pool 0/0/7) vs agentx adaptive net (feature_001 scope unset, D1 forbids `src/agentx/`) — selection like "do rag_v2 + studio fix concurrently" has no net spanning harness + execution state.
- G16: no metric proves M0/M1 concurrency pays back — feature_093 + feature_098 exist, but wild-session payback N≥10 residual open (WORK.md Paused + PROJECT.md O6). Suite 1880 + `check 265/0` is the green baseline before measurement.

### Oracle (what passes)

- Payback metric defined before N runs: wall-time + agent tokens + `check`/`build`/suite cost per wild session vs serial baseline; honest-cost method (feature_098) reused; ledger `net_*` + CURRENT_STATE logs as evidence.
- Wild protocol: N≥10 sidecar/worktree sessions, disjoint files, harness green throughout (`check 0` + `build` OK + suite + KNOWN empty; net-zero holds; Tier-3 excludes net); each run logs reproducer/oracle/budget + outcome.
- Decision threshold pre-registered: payback → O6a (contract-only, read-only D1 exception) or O6b (full prototype, D1 reversal + `major_feature` TDD); no payback → defer O6, take WORK.md NEXT `proj:agentx_concurrent_development`.

### Budget

- Scoping: 0 receipt rounds (this doc only, non-gated; `uv` only; no places/transitions; no ledger kinds).
- Measurement (when spawned): sidecars/worktrees only, slice reverts on violation, never the harness; spawn via `new_feature.py` only with new decisions + evidence.

### Next

- Spawn measurement slice via `new_feature.py "<name>" --type <tt> --project meta_harness_11` with D5 (O6c threshold) decision + evidence; or run wild sessions ad-hoc and log here.
- Then O6a/O6b revisit (needs D1 decision) or WORK.md NEXT `proj:agentx_concurrent_development`. Tree still dirty (feature_115 WIP) — commit is user call.

### Notes / context

- Non-interference held: no `src/`/`tests/` edits in this resume; `src/agentx/` untouched (D1); `uv` only.
- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

---

## 2026-09-20 (auto — feature_115.live_progress_full_push_join_view Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_115.live_progress_full_push_join_view/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-20 (feature_115 Programming → Testing)

### Done

- Implemented O5a+b per Design 001 (receipt-disciplined): `freshness.batch_projection_lines` pure + `state._render_push_text`/`join_projection_for_state` + dispatch-join threading + `cli.py` 4-site bash-transform (probe/fire/apply-selection/task envelopes).
- Goldens `tests/scripts/omt/test_net_followup_o5.py` 8/8 (canary-approved via `omt_skip{scope:tests}`); targeted 78/78; full suite **1880 passed** + 2 deselected; `check 265/0`; live probe rev 60 shows full `push.tasks_block` (`fresh:true`).
- Wrote impl notes + test report; `omt_complete{advance_to:Testing}` green.

### In progress / Blocked

- feature_115 in Testing (needs user close/ship call).

### Next

- User close/ship feature_115 → MH11 O5-follow-up Done; then O6 (needs D1 revisit) or WORK.md NEXT `proj:agentx_concurrent_development`.

### Notes / context

- Non-interference held: no places/transitions added; no new ledger kinds; `src/agentx/` untouched; live rev 60; `uv` only.

---

## 2026-09-20 (resume: MH11 O5-follow-up spawned as feature_115)

### Done

- Resumed MH11 at M1 SHIPPED (O4 Done, suite 1872, `check 265/0`, F7 lane-only locked) via `meta_harness_project` loop (root → subject → loop file; approval gates honored).
- User picked O5-follow-up then O5a+b combined (full-text push + join progress view) over O6/WORK.md-NEXT/verify-only.
- Spawned `feature_115.live_progress_full_push_join_view` (`minor_feature`, linked to `meta_harness_11`); declared `omt_phase{Analysis}`.
- Wrote Analysis 001 (`analysis_001_full_push_join.md`): reproducer (`push.tasks_block==""` at `cli.py:356/377/408/442` + text-only `projection_lines` vs `plan_to_dict`) + oracle (D19 round-tripping push text D4 proposal-only; deterministic batch/join view) + budget (3 receipt rounds, canary-gated goldens, work_md budget watch).
- Locked PROJECT.md D4 (proposal-only + read-only; no F7/D1 reversal); think-gate + KB consults recorded (no KB hits).
- Filled FEATURE.md Summary/Scope/task-type + PLAN.md Objective.

### In progress / Blocked

- feature_115 in Analysis (needs Design approval before Programming; tests/ canary required for new goldens).

### Next

- `omt_phase{minor_feature, Design}` → push-text threading points + batch projection shape + golden list → Programming (receipt-disciplined) → `omt_complete{advance_to:Testing}` + test report.

### Notes / context

- Non-interference: no places/transitions added; no `src/` edits yet (docs only); `src/agentx/` untouched (D1); `uv` only.

---

## 2026-09-20 (auto — feature_114.concurrent_dispatch_runtime Done)

- shipped: major_feature · test report @ 6.testing/features/feature_114.concurrent_dispatch_runtime/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

### Close (iter 9 — O4 Done, user-approved)

- `omt_tdd done` + `omt_complete{advance_to:Done}` green — O4 Done; TDD closed.
- Evidence held at close: 23 canonical + 2 pointer goldens (25/25 + e2e 1/1), targeted 56/56, suite 1872 + 2 deselected, `check 265/0`, `omt_tdd sync` clean.
- PROJECT.md updated: M1 SHIPPED (O4 Done, F7 lane-only reversal locked); Next = O5-follow-up / O6 (D1 revisit) or WORK.md NEXT `proj:agentx_concurrent_development`.
- Non-interference held throughout: no places/transitions added; `src/agentx/` untouched; `uv` only.

---


## 2026-09-20 (iter 8 — resume: O4 test report → Testing)

### Done

- Wrote feature_114 test report @ `6.testing/features/feature_114.concurrent_dispatch_runtime/test_report.md` (23/23 canonical goldens breakdown + 56 targeted + full suite + `check 265/0` + e2e + TDD sync clean + contract-fix + hermetic-hardening notes).
- Scaffolded + filled `5.implementation/features/feature_114.concurrent_dispatch_runtime/impl_notes.md` (`new_feature.py implementation`; dispatch_runtime/state/cli/test sites).
- Canary-approved (user) §12 pointer `tests/features/feature_114.concurrent_dispatch_runtime/test_dispatch_o4.py` 2/2 smoke (empty-refuses + single-claim composes; `omt_skip{scope:tests, purpose:canary}`); canonical 23 remain at `tests/scripts/omt/test_net_dispatch_o4.py` (combined 25/25 + e2e 1/1).
- `omt_complete{advance_to:Testing}` green — O4 in Testing (needs user close/ship call).
- Verified 2026-09-20: full suite **1872 passed** + 2 deselected; `check 265/0`; `omt_tdd sync` clean.

### In progress / Blocked

- O4 in Testing (major_feature needs user close/ship call).

### Next

- User close/ship O4 → O5-follow-up / O6 (need F7/D1 decisions) or WORK.md NEXT `proj:agentx_concurrent_development` per iter 6.

### Notes / context

- Non-interference held: no places/transitions added (Tier-3 excludes net); helpers fail-open; `src/agentx/` untouched (D1); `uv` only.
- CLI `dispatch --expected-revision` commit subcommand deferred (probe `plan[]` preview only); O2 bound lifted only in dispatch lane with atomic join.

---

## 2026-09-20 (iter 7 — resume: O4 goldens + 6-failure triage)

### Done

- Closed stranded RED `test_net_dispatch_o4.py::TestPlanEmpty::test_empty_refuses` green (cycle 1; implementation predates tests per prior session's user-directed override skip).
- Triaged 6 pre-existing suite failures (5× feature_109 P2D deny-matrix i1–i5 + 1× feature_073 task_prep blocker): single root cause — prior session's `scope=all` override skip (21:49Z, 8h window) alive in the live ledger; the goldens read it (test-isolation violation). Fixed tests-only: hermetic `OMT_LEDGER_PATH` seeding (d_matrix autouse fixture + task_prep bun subprocess env). Suite 1848 green.
- O4 goldens `tests/scripts/omt/test_net_dispatch_o4.py`: 23/23 — planner (compose/refusals/determinism/shape) + preview (bind-resolution/fail-open/stale) + join (one-revision commit, ledger batch carrier, stale/unknown/not-pending/scope/slots-token refusals all atomic).
- Contract fix (src, code-hat + think-consulted): `dispatch_claims` accepts the preview shape (`plan.get("tasks") or plan.get("plan")`) per operation_spec_001 §dispatch_claims ("plan from preview"); probe `plan[]` contract untouched.
- Verified 2026-09-20: 23 O4 goldens green; full suite **1870 passed** + 2 deselected; `check 265/0`; `omt_tdd sync` clean.

### In progress / Blocked

- O4 in Programming (test report + `omt_complete{advance_to:Testing}` pending; needs user close/ship call). TDD ledger: cycle 1 closed; remaining goldens pin existing implementation directly (directed scope).
- Live `scope=all` skip expires ~05:49Z (by design; ledger untouched).

### Next

- Write feature_114 test report @ `6.testing/features/feature_114.concurrent_dispatch_runtime/test_report.md` → `omt_complete{advance_to:Testing}` → user close/ship call. Then O5-follow-up / O6 or WORK.md NEXT per iter 6.

### Notes / context

- Non-interference held: no places/transitions added (Tier-3 excludes net); helpers fail-open; `src/agentx/` untouched (D1); `uv` only.
- Receipt discipline: 1 edit per file per e2e receipt (state.py contract fix ×1, d_matrix ×1, task_prep ×2 with refresh, dispatch_o4 goldens ×3 rounds with refresh); `uv` only.

---

## 2026-09-19 (iter 6 — M0 COMPLETE, user-approved close)

### Done

- M0 closed: O1 `feature_110.whole_project_menu_composer` + O2 `feature_111.multi_select_directive_protocol` + O3 `feature_112.identity_aware_pool` all Done (reports: 14/43 + 12/54 + 12/58 goldens/targeted; suites 1817→1830→1840; `check 265/0` each).
- O5 slice `feature_113.live_progress_projection` Done (7 goldens `test_net_fresh_o5.py`, targeted 62/62, suite 1847 + 2 deselected, `check 265/0`; live probe rev 60 `fresh:true`, `push {net_revision:60}` honest).
- Verified 2026-09-19: all 4 test reports on disk under `.meta/software_development_process/6.testing/features/feature_{110,111,112,113}*/test_report.md`; tree clean; `check 265/0`; budgets OK (work_md 9623/9728).

### In progress / Blocked

- _(nothing — M0 complete, O4/O6 unspawned per user pick)_

### Next

- O4 `concurrent dispatch runtime` (major_feature, needs F7 reversal decision + reproducer/oracle/budget) or O5-follow-up (full text push, slider/join) or O6 bridge (needs D1 revisit) — spawn via `new_feature.py` only with new decisions + evidence.
- Or leave MH11 active and do WORK.md NEXT `proj:agentx_concurrent_development`.

### Notes / context

- Non-interference held throughout M0: no places/transitions added (Tier-3 excludes net); helpers fail-open; `src/agentx/` untouched (D1); `uv` only.
- Residuals: O2 multi-mutate → `multi_mutate_deferred_o4`; O3 live `menu.claims:[]` honest (no pending bindings); O5 `push.tasks_block` empty (caller-applied per D4), text-only projection.

---

## 2026-09-19 (auto — feature_113.live_progress_projection Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_113.live_progress_projection/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-19 (auto — feature_112.identity_aware_pool Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_112.identity_aware_pool/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-19 (iter 5 — O3 identity-aware pool to Testing)

### Done

- O3 `feature_112.identity_aware_pool` (minor_feature, Analysis→Design→Programming→Testing): `claim_handles.py` pure map + `state.apply_selection` handles view + `cli._task_menu` additive `claims[]`; 12/12 new goldens `test_net_claim_o3.py` (canary-approved); targeted 58/58; full suite 1840 passed + 2 deselected; `check 265/0`; test report @ `6.testing/features/feature_112.identity_aware_pool/test_report.md`.
- Receipt discipline: 1 new-module round + 1 state.py bash-transform round + 1 cli.py round, e2e refreshed per round; P10-clean derived view (sidecar SSOT, overlay untouched); `uv` only.

### In progress / Blocked

- O3 in Testing (needs user close/ship call); M0 closes when O3 ships (O1+O2 Done, O3 Testing).

### Next

- Close/ship O3 from Testing (user call), then M0 complete → spawn O4 `concurrent dispatch runtime` (needs F7 reversal decision) or O5 live view.

### Notes / context

- Live rev 60 still `drained_complete`, `menu.claims:[]` honest (no pending bindings); de-anonymization proven hermetically.
- Non-interference held: no places/transitions added (Tier-3 excludes net); helpers fail-open.

---

## 2026-09-19 (auto — feature_111.multi_select_directive_protocol Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_111.multi_select_directive_protocol/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-19 (auto — feature_110.whole_project_menu_composer Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_110.whole_project_menu_composer/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-19 (iter 4 — O1 goldens + budget trim/grow + live menu + Testing)

### Done

- O1 goldens `tests/scripts/omt/test_net_menu_o1.py` (canary-approved): 14 tests — compose_menu_options IDs, lanes_line, render_tasks_block/menu_lines fallback (G2), state helpers, sync dry-run threading; targeted 43/43 green (14 new + 28 existing + 1 e2e); `check 265/0`.
- Budget fix (both user-approved): persisted Tasks keeps `Options:` IDs + `Lanes:` lines only (30 checklist rows dropped; 11562→9507 B) + `.omt @budget work_md` 8704→9728 with test pin + `build` (5 projections).
- Live `sync net_to_md` applied rev 60: `NEXT: proj:agentx_concurrent_development (recommended)` + 19 proj + 9 drift + 2 unscoped + Lanes; WORK.md is the whole-project menu.
- Full suite 1817 passed + 1 live-smoke infra flake (TimeoutExpired, unrelated); test report @ `.meta/software_development_process/6.testing/features/feature_110.whole_project_menu_composer/test_report.md`; `omt_complete{advance_to:Testing}`.
- Receipt discipline: 1 edit per file per e2e receipt (sync_md trim → e2e → goldens fix → e2e → .omt grow → build → pin fix); `uv` only.

### In progress / Blocked

- O1 in Testing (minor_feature needs no TDD); O2 `multi-select + directive protocol` not yet spawned.

### Next

- Close or ship O1 from Testing (user call), then spawn O2 via `new_feature.py` (depends on O1 IDs).

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Non-interference held: no places/transitions added (Tier-3 excludes net); helpers fail-open.

---

## 2026-09-19 (iter 3 — O1 threading: state.sync supplies whole-project menu)

### Done

- Threaded `state.sync net_to_md` → `render_tasks_block` with live menu inputs (all in `scripts/omt/net/state.py`, pure render untouched):
  - `_menu_projects_from_work()` — WORK.md `## Projects` rows → `proj:<slug>` (19 live rows).
  - `_menu_hygiene()` — `aging-draft` (>21d ledger age-gate) + `unlinked-project-backed` (full ledger fold archives+hot) + `iteration-log` (git fail-open); live: 2 + 2 + 5.
  - `_menu_unscoped()` — PENDING FEATURES block only → `unscoped:001/002`.
  - `_menu_lanes()` — bindings-preferred, live-marking fallback, None when no lane places (backward compat).
  - `record/info["menu"]` counts (projects/hygiene/unscoped/lanes) for audit.
- Evidence: live dry-run rev 60 renders `NEXT: proj:agentx_concurrent_development (recommended)` + 19 proj + 9 drift + 2 unscoped + `Lanes:` line; hermetic suites 29/29 green (`sync_md`/`menu`/`sync`/`state`/e2e); `check 265/0`.
- Receipt discipline: 4 single-edit rounds on `state.py` (helpers → call-site → ledger-fold/age-gate → annotation), e2e refreshed per round; 3 remaining LSP notes pre-existing downstream.

### In progress / Blocked

- O1 goldens: no new `tests/` yet (needs canary approval) — existing 28 cover compat + dry-run only.
- Live `sync net_to_md` (non-dry-run) not yet applied to WORK.md — awaiting goldens + `omt_complete{advance_to:Testing}`.

### Next

- O1 goldens (canary) → real `sync net_to_md` → `omt_complete{advance_to:Testing}` + test report; then O2 spawn.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Non-interference held: no places/transitions added (Tier-3 excludes net); helpers fail-open; hermetic env overrides respected.

---

## 2026-09-19 (iter 2 — O1 spawned + pure render shipped)

### Done

- Spawned O1 `feature_110.whole_project_menu_composer` (`minor_feature`, linked to `meta_harness_11`; state now `active`).
- Analysis 001 (`analysis_001_menu_composer.md`): reproducer rev60 empty-menu vs 3 active projects + oracle (stable IDs, D19, rev-stamp) + budget.
- Design→Programming: `sync_md.py` pure extensions (additive optional args, old callers unchanged):
  - `compose_menu_options(projects/hygiene/unscoped)` → `proj:/drift:/unscoped:` IDs, sorted deterministic.
  - `lanes_line(lanes, conflicts)` → verification/integration + deadlocks_complete one-liner (G3).
  - `render_tasks_block(..., projects/hygiene/unscoped/lanes)` + `menu_lines(..., same)`; empty enabled + options → NEXT is first option (G2); Options + Lanes appended after Pool.
- Evidence: `test_net_sync_md + test_net_menu` 12/12 green; e2e 1/1 green (receipt round-robin: 5 edits, refresh per round); manual `compose/lanes` check green.

### In progress / Blocked

- O1 threading: `state.sync net_to_md` still calls `render_tasks_block` with slugs only (no projects/drift/unscoped/lanes yet) — next slice.
- O1 goldens: no new `tests/` yet (needs canary approval) — existing 12 cover backward compat only.

### Next

- Thread `state.sync` (projects from `project.py sync` + drift + PENDING 001/002 + lanes) + O1 goldens (canary) → `omt_complete{advance_to:Testing}` + test report.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Non-interference held: net rev still 60, `check` 265/0, no places/transitions added (Tier-3 excludes net).

---

## 2026-09-19 (iter 1 — scope v0.1 full O1–O6 approved)

### Done

- Scoped PROJECT.md v0.1 full O1–O6 (user pick: Full over Minimal/Staged); M0→M1→M2 order; F7/D1 reversals deferred to O4/O6.
- Baseline linked: `.sandbox/meta_harness_session_usecase_gaps.md` (G1–G16/O1–O6, rev 60).

### In progress / Blocked

- _(nothing — awaiting O1 spawn)_

### Next

- Spawn O1 `whole-project menu composer` via `new_feature.py "<name>" --type minor_feature --project meta_harness_11`.

### Notes / context

- MH10 closed complete (rev 60 drained_complete, suite 1801); mh11 is sole use-case home (D1). Non-interference: sidecars/worktrees only until slice approval.
- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

---

## 2026-09-19 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft).

### In progress / Blocked

- _(nothing)_

### Next

- <!-- the single next action -->

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

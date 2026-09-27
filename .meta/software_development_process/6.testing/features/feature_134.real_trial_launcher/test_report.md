# Test Report — feature_134.real_trial_launcher (fake-executor launcher core)

> Task type: major_feature · 2026-09-27 · RED `test_fake_plans_12_in_order` → GREEN (`launcher.py` NEW) → REFACTOR → SYNC (validate-exit ok, no stranded REDs). No launches, no tokens, fakes only.

## Verdict

**PASS (fake slice).** Slice+bridge battery **72 passed, 2 skipped** (`tests/scripts/session_inspect/` 66 + `test_bridge_134.py` 2 + 132/133 bridges + `test_run_gate` — live-DB tests stay opt-in gated). Full minus inspect **2012 passed, 2 deselected, 5 failed — all 5 pre-existing baseline drift, zero NEW failures** (R4 guard). `harnessc check`: **1 pre-existing error** (`work_md` budget 9758 B > 9728 B, 30 B over — introduced by the feature_134 allocation growing the WORK.md Projects row at iter 11, before this slice; see Repo drift).

## What was verified

| Behavior | Test | Result |
|---|---|---|
| plan expands 12 trials, in-order, unique | test_fake_launcher.py::test_fake_plans_12_in_order | PASS — 2×2×3 matrix via `manifest.expand_matrix`, `rep01` first, 12 unique IDs |
| dispatch sequential, once each, concurrency 1 | test_fake_dispatch_sequential_once_each | PASS — call order == result order, injected fake executor |
| timeout strict-once, no retry | test_timeout_strict_once_no_retry | PASS — 999 s > 300 s → `timeout_failed`, `attempt:1` |
| run_fake refuses without gate | test_run_fake_refuses_without_gate | PASS — `allowed False`, `executed False` |
| run_fake allow path stays un-executed | test_bridge_134.py::test_run_fake_gated_no_execute | PASS — allowed → `n_trials 12, fake_n 12, executed False` |
| 132/133 contracts preserved | test_run_gate.py, test_bridge_132.py, test_bridge_133.py | PASS — gate + dispatcher wiring unchanged |
| closed failure vocabulary | launcher.py (executor exception → `trial_incomplete`; manifest → `manifest_invalid`) | PASS — no new Finding names; timeout is an outcome string |

## Repo drift (pre-existing, NOT introduced by this slice)

- Full-suite failures (5, all at Programming-declare baseline): `test_budget_diet.py::test_live_check_emits_diet_warnings` · `test_harnessc.py::test_repo_omt_check_has_zero_errors` · `test_harnessc.py::test_repo_projections_are_fresh` · `test_omt_docs_drift_pins.py::test_work_md_within_budget` · `test_run_metering.py::test_run_all_seeds_ok`.
- `work_md` budget 9758 B > 9728 B: WORK.md grew when feature_134 was allocated (iter 11, rev 60, 17:58) — before any code this slice. Remediation (deliberate, separate task): grow the `work_md` budget in the same `.omt` edit + `harnessc build` + pin re-pins (harness-surface ceremony), or run the budget diet bot. Not done inside this feature's Testing pass.

## Boundary

- No subprocess, no threads, no sleeps, no `/tmp` creation (isolation paths are stubs; real per-trial worktree is the future live slice).
- `service.py`/`run_gate.py`/`manifest.py`/`.ts`/`.omt` untouched — zero harness-surface edits, no pin churn.
- `feature_129/130/131/132/133` untouched; synthetic fixtures only; `executed` stays `False` everywhere in this slice.

## Next

- Live `executed:true` remains gated: needs real executor path + 12 held claims + budgets + explicit `p` invocation (design_001 §4 decisions). Fake wiring proven end to end: manifest → gate → dispatch → timeout → collect.

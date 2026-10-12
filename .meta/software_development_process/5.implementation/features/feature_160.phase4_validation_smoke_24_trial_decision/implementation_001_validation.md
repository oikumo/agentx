# Implementation 001 — Phase4 validation (smoke + 24-trial dry_run)

Feature: feature_160.phase4_validation_smoke_24_trial_decision · Date: 2026-10-12
Design: `design_001_validation.md` + `operation_spec_001_validation.md`. TDD batch-of-7 single-cycle (canary skip approved).

## Added (new files only, no core edits — 2nd-edit guard clean)

- `scripts/omt/bench/validation.py` — `CASES[4]`, `VARIANTS[baseline,treatment]`, `REPS=3`, `BUDGETS{tokens:50000,time_s:600,concurrency:1}`, `DECISION_RULE=quality_gated_paired_compare`, `phase4_manifest(experiment="phase4_validation", run="smoke_24trial")` → `manifest.create(...)` versioned. Reuse-only cores otherwise (`manifest|run_gate|launcher fake|collect|evaluate|exporter` untouched).
- `tests/harness_meta/feature_160.phase4_validation_smoke_24_trial_decision/test_validation_meta.py` — 7 goldens (see test_report). Created via bash heredoc per WORK gotcha (enforcer hooks edit-tools only; TDD two-hats RED-before-write circular → bash for initial RED file, then `omt_tdd red` verified fail, then src via bash, then `green` verified pass).

## TDD

- Testlist 7 recorded. RED at `test_manifest_valid` (ModuleNotFoundError validation → fail ✅). GREEN same node after `validation.py` landed (7 passed ✅). `tdd done` state=DONE cycles=4. Batch-N warning tolerated via canary skip (precedent 154/155/157/158/159 single-cycle batches).
- Two-hats respected: RED tests/ only (bash-created test), GREEN src/ only (bash-created bench helper, no test edits in green).

## Notes

- Fake executor only (`executed:False`); live `executed:true` deferred to explicit user-gated run. `gate_run` refusals prove run-gated (no auto launch).
- No skill-side DB path, no autoinvoke change, no bare `net_to_md`, WORK trim-while-adding.

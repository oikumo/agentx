# Feature 125: Harness Reason Stage 3 Paired Experiment

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Stage-3 paired experiment for harness_reason: three arms (current harness, enhanced typed planner, categorical kernel) sharing S0 catalog/adapters/fragments, S1 12 cases + held-out reuse tasks, common snapshot + varied order, per-case outcomes + variability on correctness/staleness/cost, sandbox-only design + probe.

## Scope (one sentence — what "done" looks like)

Done = stage3 analysis (arms/tasks/oracle/metrics/keep-conditions) + design (experiment ops + run_experiment outline + cert envelope) + `run_experiment.py` sandbox probe passing validity checks (shared-inputs parity, snapshot/order discipline, per-case report + 15%-threshold rule as decision rule not prediction) with no src/net/toolbox change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_125.harness_reason_stage_3_paired_experiment/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_125.harness_reason_stage_3_paired_experiment/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_125.harness_reason_stage_3_paired_experiment/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_125.harness_reason_stage_3_paired_experiment/` | [ ] |
| Testing | Test report | `6.testing/features/feature_125.harness_reason_stage_3_paired_experiment/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

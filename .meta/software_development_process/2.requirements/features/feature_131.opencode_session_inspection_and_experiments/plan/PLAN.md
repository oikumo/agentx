# PLAN — feature_131: Opencode Session Inspection And Experiments

> Task type: **major_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

Deliver the meta_harness_13 Tier-2 `omt_session` capability per its PROJECT.md milestones M1–M6; this feature implements it in TDD slices (M1 contracts → M2 capture/inspection → M3 usage/diagnosis → M4 experiments → M5 registration → M6 acceptance).

## Steps

- [x] Analysis — `analysis_001_real_log_inventory.md` (real DB + legacy labeled captures mapped field by field; ambiguity register A1–A10)
- [x] Design — `design_001_core_architecture.md` (module architecture, normalized records, adapter/usage/label contracts, TDD behavior list)
- [ ] Implementation — TDD slices (omt_tdd testlist → red → green → refactor → done)
- [ ] Testing — regression + slice test reports

## Artifacts produced

- Requirements: `feature_131.opencode_session_inspection_and_experiments/FEATURE.md`
- Analysis: `3.analysis/features/feature_131.opencode_session_inspection_and_experiments/analysis_001_*.md`
- Design: `4.design/features/feature_131.opencode_session_inspection_and_experiments/design_001_*.md`
- Testing: `6.testing/features/feature_131.opencode_session_inspection_and_experiments/test_report.md`

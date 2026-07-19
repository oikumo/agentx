# PLAN — feature_023: Meta Harness Improvement

> Task type: **major_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

D1 read-injection fires in production (F14 + F14b edit-path sibling + F14c session.start
dead-hook — all three fixed via the real `input.args` contract / first-`tool.execute.after`
live path), runner fixtures pinned against the installed SDK contract, named-export guard
extended to all 4 plugins, accidental `TA:` prose reworded, runner index pollution isolated.

## Steps

- [x] Analysis — `analysis_001_f14_contract_pinning.md` (+F14c addendum, 2026-07-19)
- [x] Design — `design_001_contract_pinning.md` (13 TDD behaviors, sequencing §7, 2026-07-19)
- [ ] Implementation — resume in new session: design_001 §7 steps 1–9
- [ ] Testing

## Artifacts produced

- Requirements: `feature_023.meta_harness_improvement/FEATURE.md`
- Analysis: `3.analysis/features/feature_023.meta_harness_improvement/analysis_001_f14_contract_pinning.md`
- Design: `4.design/features/feature_023.meta_harness_improvement/design_001_contract_pinning.md`
- Testing: `6.testing/features/feature_023.meta_harness_improvement/test_report.md`

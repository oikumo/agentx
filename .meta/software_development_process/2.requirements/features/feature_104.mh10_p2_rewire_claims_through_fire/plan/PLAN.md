# PLAN — feature_104: Mh10 P2 Rewire Claims Through Fire

> Task type: **minor_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

Slice B: claim/release pool moves prefer template fire with transition/fired ledger evidence; labeled fallback where template cannot express the move.

## Steps

- [x] Analysis (attention-vs-workers conflict + staged rule)
- [ ] Programming (ONE state.py edit: `_fire_pool_move` + claim/release wiring + ledger fields)
- [ ] Testing (existing claim/release/lane suites + new fired-vs-fallback tests + check/build/suite)

## Artifacts produced

- Requirements: `feature_104.mh10_p2_rewire_claims_through_fire/FEATURE.md`
- Analysis: `3.analysis/features/feature_104.mh10_p2_rewire_claims_through_fire/analysis_001_*.md`
- Design: `4.design/features/feature_104.mh10_p2_rewire_claims_through_fire/design_001_*.md`
- Testing: `6.testing/features/feature_104.mh10_p2_rewire_claims_through_fire/test_report.md`

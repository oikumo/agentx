# PLAN — feature_130: Real Token Discharge

> Task type: **minor_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

Real-token gate item (1) discharged: 6 labeled opencode sessions (H1/H3 × harness/planner/kernel) → harvested ledger → `run_real_tokens.py --ledger` 8/8 with threshold verdict on measured medians + full sandbox regression green.

## Steps

- [x] Analysis (discharge_analysis.md: protocol, task specs, measurement mapping, fairness disclosures)
- [x] Design (discharge_design.md: label spec, session prompts, harvest query, ledger schema)
- [x] Implementation (harvest_ledger.py + 6 labeled sessions + ledger + --ledger run) — 6/6 harvested, `REAL_TOKENS_OK 96ba44edc7968ca0` stable ×2
- [x] Testing (8/8 ×2 digest stable + S0 7/7 + checker 12/12 + composer 7/7 + experiment 7/7 + tier0/tier1 + reason tests 14) — threshold MISSED on measured medians (kernel −246% vs harness) → `shrink-tier0-or-keep-planner`

## Artifacts produced

- Requirements: `feature_130.real_token_discharge/FEATURE.md`
- Analysis: `3.analysis/features/feature_130.real_token_discharge/analysis_001_*.md`
- Design: `4.design/features/feature_130.real_token_discharge/design_001_*.md`
- Testing: `6.testing/features/feature_130.real_token_discharge/test_report.md`

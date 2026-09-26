# Feature 130: Real Token Discharge

> **Status:** [x] Done (Testing complete — item (1) discharged, threshold MISSED on measured medians: `shrink-tier0-or-keep-planner`)
> **Created:** 2026-09-26
> **WORK.md task:** proj:harness_reason → feature_130.real_token_discharge

---

## Summary

Discharge of the Tier-2 gate item (1) left "ready-not-discharged" by feature_129: capture REAL token usage for the reuse-sensitive cases H1/H3 across the three arms (harness/planner/kernel) by running labeled, dedicated opencode subagent sessions (label in prompt first line + task description), harvesting the sessions' cumulative token columns from the opencode session DB into `stage_real_tokens_ledger.json`, and re-running `run_real_tokens.py --ledger` so the ≥15% threshold rule is read on measured medians instead of `inconclusive_host_usage_unavailable` — data discharge only, no measurement-design change (the seam/ledger/threshold mechanics are feature_129's, byte-stable).

## Scope (one sentence — what "done" looks like)

Done is 6 labeled real sessions (H1/H3 × 3 arms), a sandbox harvester + hand-captured-shape ledger with per-session provenance, `run_real_tokens.py --ledger` 8/8 with a threshold verdict on measured medians (proxy stays honestly `mixed` — T-cases unmeasured), full S0–S3/tier regression green, and PROJECT.md/CURRENT_STATE.md updated — sandbox only, no src/net/toolbox change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_130.real_token_discharge/` | [x] |
| Analysis | Analysis doc | `.sandbox/harness_reason/discharge_analysis.md` | [x] |
| Design | Design doc | `.sandbox/harness_reason/discharge_design.md` | [x] |
| Implementation | Impl notes | `.sandbox/harness_reason/harvest_ledger.py` + `stage_real_tokens_ledger.json` (impl decisions in test report + ledger provenance) | [x] |
| Testing | Test report | `6.testing/features/feature_130.real_token_discharge/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

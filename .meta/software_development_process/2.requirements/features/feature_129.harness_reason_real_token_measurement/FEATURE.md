# Feature 129: Harness Reason Real Token Measurement

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Real-token paired measurement for harness_reason Stage-3: replace synthetic proxy-byte cost ledgers with actual host token accounting across the same three arms (harness/planner/kernel) on T01–T12+H1–H3, so the Tier-2 promotion gate can evaluate the ≥15% median cost-reduction rule on measured tokens instead of `proxy:true` bytes.

## Scope (one sentence — what "done" looks like)

Done is sandbox-only `run_real_tokens.py` + analysis/design docs that define the token-measurement harness, report real-token medians with variability on fixtures, and state the Tier-2 promotion reading without any src/net/toolbox change.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_129.harness_reason_real_token_measurement/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_129.harness_reason_real_token_measurement/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_129.harness_reason_real_token_measurement/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_129.harness_reason_real_token_measurement/` | [ ] |
| Testing | Test report | `6.testing/features/feature_129.harness_reason_real_token_measurement/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

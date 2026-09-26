# Feature 128: Harness Reason Tier 1 Advisory Pilot

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Tier-1 advisory pilot `reason_check.ts` (no `omt_` prefix, closed `check|explain|compare|concretize` enum, `plan` withheld) as thin proxy to Python SSOT `scripts/reason/check.py` with per-op argv whitelist plus pinned arg tests, TS advisory guard, §5 envelope output (≤2KB summaries + detail_ref), one `reason_check: allow` line outside harnessc blocks, no @tool row/build/receipt.

## Scope (one sentence — what "done" looks like)

`reason_check.ts` carries S0 7/7 + S1 12/12 replays via SSOT with whitelist pins and §5 envelopes, zero net/ledger writes, no src imports, no plan op.

## Task type

<!-- bug_fix | minor_feature | major_feature | new_screen | refactor -->

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_128.harness_reason_tier_1_advisory_pilot/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_128.harness_reason_tier_1_advisory_pilot/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_128.harness_reason_tier_1_advisory_pilot/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_128.harness_reason_tier_1_advisory_pilot/` | [ ] |
| Testing | Test report | `6.testing/features/feature_128.harness_reason_tier_1_advisory_pilot/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

# Feature 131: Opencode Session Inspection And Experiments

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Tier-2 session inspector + labeled-experiment evaluator for the META HARNESS: a read-only OpenCode SQLite adapter that normalizes real session/message/part/event records (session trees, traces, usage, failures), a `[mh13.experiment]` label protocol binding trials to real message logs, and an experiment lifecycle (manifest → dry run → run → collect → validate → compare → replay). Project home: `.projects/meta/meta_harness_13/` (proposal = its PROJECT.md; milestones M1–M6).

## Scope (one sentence — what "done" looks like)

A `scripts/session_inspect/` core (adapters, normalized schema, queries, attribution, labels, experiment evaluation) that satisfies the project's AC1–AC12 via TDD, registered as the Tier-2 `omt_session` tool with budget/e2e checks green (M5/M6 may land as later slices of this feature).

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_131.opencode_session_inspection_and_experiments/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_131.opencode_session_inspection_and_experiments/analysis_001_real_log_inventory.md` | [x] |
| Design | Design doc + operation spec | `4.design/features/feature_131.opencode_session_inspection_and_experiments/{design_001_core_architecture.md,operation_spec_001_slice1_contracts.md}` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_131.opencode_session_inspection_and_experiments/` | [ ] |
| Testing | Test report | `6.testing/features/feature_131.opencode_session_inspection_and_experiments/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

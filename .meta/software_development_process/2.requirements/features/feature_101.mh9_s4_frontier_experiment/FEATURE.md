# Feature 101: Mh9 S4 Frontier Experiment

> **Status:** [~] In progress (S4 verify green, verdict MERGE — ready for Done)
> **Created:** 2026-09-14
> **WORK.md task:** mh9 S4 frontier experiment — project meta_harness_9 (active)
> **Project:** `meta_harness_9` (origin: scaffold)

---

## Summary

mh9 S4: paired read-only frontier-vs-preflight experiment (arms A/B/C, 2 task classes, identical facts + 2KB budget) over the S3 thin contract — advisory frontier schema only, no authority change; ends in a written keep/merge/drop verdict that gates everything parked.

## Scope (one sentence — what "done" looks like)

Done = sidecar schema + paired harness in `.sandbox/frontier/` with paired results on both task classes + keep/merge/drop verdict, per `analysis_001_frontier_experiment.md`, with check/build/suite green.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_101.mh9_s4_frontier_experiment/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_101.mh9_s4_frontier_experiment/analysis_001_frontier_experiment.md` | [x] |
| Design | Design doc | `4.design/features/feature_101.mh9_s4_frontier_experiment/design_001_frontier_schema.md` (short note only) | [x] |
| Implementation | Sidecar | `.sandbox/frontier/` (frontier.py + 2 pairs × 3 arms + verdict.md MERGE) | [x] |
| Testing | Test report | `6.testing/features/feature_101.mh9_s4_frontier_experiment/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

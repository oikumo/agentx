# Feature 098: Mh9 S1 Benchmark Follow-Up Honest Cost Picture

> **Status:** [~] In progress (S1 smoke green at HEAD)
> **Created:** 2026-09-14
> **WORK.md task:** mh9 S1 — project meta_harness_9 (paired with S2)
> **Project:** `meta_harness_9` (origin: scaffold)

---

## Summary

S1 measurement: honest cost picture at HEAD `f1be918` — fixture re-baseline green, g.phase/g.tests removal deltas published, proxies labeled, corpus frozen, no policy change.

## Scope (one sentence — what "done" looks like)

Done = repeatable traces with honest usage fields + waste ranking + expansion rule + budget per `analysis_001_oracle_proxies_corpus.md` + `test_report.md`.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture/analysis_001_oracle_proxies_corpus.md` | [x] |
| Design | Design doc | `4.design/features/feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture/` | [ ] |
| Testing | Test report | `6.testing/features/feature_098.mh9_s1_benchmark_follow_up_honest_cost_picture/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

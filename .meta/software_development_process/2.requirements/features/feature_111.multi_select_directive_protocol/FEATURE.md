# Feature 111: Multi-Select + Directive Protocol

> **Status:** [ ] Not started
> **Created:** 2026-09-19
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

O2 of meta_harness_11 (closes G5/G6/G8/G9): a `pick {id,…} + per-id directive` grammar over the O1 whole-project menu IDs with one atomic rev-checked `apply_selection` batch (at most one net-mutating op, M0 serial) and directive capture in the ledger envelope.

## Scope (one sentence — what "done" looks like)

`pick {O1 IDs} + directives` parses, validates, and applies as one atomic rev-checked batch (single mutate max + annotations/proposals) with stable refuse codes and goldens green.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_111.multi_select_directive_protocol/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_111.multi_select_directive_protocol/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_111.multi_select_directive_protocol/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_111.multi_select_directive_protocol/` | [ ] |
| Testing | Test report | `6.testing/features/feature_111.multi_select_directive_protocol/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

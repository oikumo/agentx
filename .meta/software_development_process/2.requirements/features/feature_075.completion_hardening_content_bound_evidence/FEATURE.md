# Feature 075: Completion Hardening Content Bound Evidence

> **Status:** [x] Done (Testing green; omt_complete)
> **Created:** 2026-09-12
> **WORK.md task:** meta_harness_8 T4-3 (no pool task; project-linked minor_feature)
> **Project:** meta_harness_8 (origin: scaffold, D5 overlap-clear vs Improvement002 D-part + 074 T4-2)

---

## Summary

T4-3 strengthens completion beyond public-method call-coverage (Improvement002
D-part): `validate-exit` runs the feature's own tests
(`tests/features/<feature>/`) and fails completion when they fail — seeded
broken behavior can no longer ride a call-reference to "done". The e2e receipt
carries a `results` block alongside digests / `policy_ver` / `toolchain`, and
the guard treats a non-passing recorded run as stale.

## Scope (one sentence — what "done" looks like)

T4-3 done = behavioral validate-exit + results-bound receipt shipped with 5
golden tests green (incl. the seeded-fault golden), boundary e2e green,
`harnessc check` 0 errors, full suite 2063/2064 (pre-existing budget-pin
failure unrelated).

## Task type

minor_feature (decl-only per §12; no design doc)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_075.completion_hardening_content_bound_evidence/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_075.completion_hardening_content_bound_evidence/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_075.completion_hardening_content_bound_evidence/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_075.completion_hardening_content_bound_evidence/` | [ ] |
| Testing | Test report | `6.testing/features/feature_075.completion_hardening_content_bound_evidence/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

# Feature 105: Mh10 P2B2 Template Fix Work Release

> **Status:** [x] Analysis signed
> **Created:** 2026-09-18
> **WORK.md task:** P2 re-entry slice B2 (additive template fix: worker_slots + work_release)

---

## Summary

Slice B2 closes the two slice-B residuals without removing any arc: a splice-add migration lands `worker_slots` (M0 = 2 − active) + the `work_release` back-edge (active→pending+slot) on the pool template (12→13 places), while `_fire_pool_move` grows a `slot_delta` parameter that adopts the template's pool+slot deltas and keeps refunding attention/feature_ready — so two concurrent claims both record `fired=true` instead of serializing on `agent_attention` (cap 1). Old-shape bundles keep today's labeled fallbacks; `managed_ops` gains the ledger-evidence reader its TA todo promised.

## Scope (one sentence — what "done" looks like)

Claim/release fire literally on the B2 template (incl. 2-concurrent both `fired=true`) with `transition/fired/fire_fallback` ledger evidence, old-shape fallbacks unchanged, all existing suites green plus new B2 goldens, `check`/`build`/suite green.

## Task type

<!-- bug_fix | minor_feature | major_feature | new_screen | refactor -->

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_105.mh10_p2b2_template_fix_work_release/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_105.mh10_p2b2_template_fix_work_release/analysis_001_b2_template_fix.md` | [x] |
| Design | Design doc | `4.design/features/feature_105.mh10_p2b2_template_fix_work_release/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_105.mh10_p2b2_template_fix_work_release/` | [ ] |
| Testing | Test report | `6.testing/features/feature_105.mh10_p2b2_template_fix_work_release/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

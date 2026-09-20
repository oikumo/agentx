# Feature 116: Mh11 O6C Wild Payback Measurement

> **Status:** [ ] Not started
> **Created:** 2026-09-19
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

O6c measure-first for MH11 O6 bridge: define the wild-session payback metric and N≥10 protocol that decides O6a contract-only vs O6b full prototype vs defer to WORK.md NEXT, keeping D1 locked (no `src/agentx/` edits).

## Scope (one sentence — what "done" looks like)

Define wild-session payback metric plus N≥10 protocol with pre-registered O6a/O6b/defer threshold, D1 locked with no src/agentx edits.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_116.mh11_o6c_wild_payback_measurement/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_116.mh11_o6c_wild_payback_measurement/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_116.mh11_o6c_wild_payback_measurement/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_116.mh11_o6c_wild_payback_measurement/` | [ ] |
| Testing | Test report | `6.testing/features/feature_116.mh11_o6c_wild_payback_measurement/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

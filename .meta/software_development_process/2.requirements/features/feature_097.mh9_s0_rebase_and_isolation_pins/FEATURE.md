# Feature 097: Mh9 S0 Rebase And Isolation Pins

> **Status:** [~] In progress (S0 Analysis signed)
> **Created:** 2026-09-14
> **WORK.md task:** mh9 S0 rebase — project meta_harness_9 (active)
> **Project:** `meta_harness_9` (origin: scaffold)

---

## Summary

mh9 S0: rebase the roadmap onto post-mh8 reality at HEAD `f1be918` — re-verify §1 findings file:line, sign the §2 table, freeze budget/retirement sheet + toolchain/policy/net pins + bench corpus + sidecar surface. Hygiene only, no src/authority change.

## Scope (one sentence — what "done" looks like)

Done = signed §2 table + pins + sheet at HEAD with check/build green and corpus/sidecar frozen per `analysis_001_s0_rebase.md`.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_097.mh9_s0_rebase_and_isolation_pins/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_097.mh9_s0_rebase_and_isolation_pins/analysis_001_s0_rebase.md` | [x] |
| Design | Design doc | `4.design/features/feature_097.mh9_s0_rebase_and_isolation_pins/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_097.mh9_s0_rebase_and_isolation_pins/` | [ ] |
| Testing | Test report | `6.testing/features/feature_097.mh9_s0_rebase_and_isolation_pins/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

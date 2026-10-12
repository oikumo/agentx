# Feature 153: Ci Base Green

> **Status:** [ ] Not started
> **Created:** 2026-10-11
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

CI base-green for skills rollout: make `uv sync --frozen` reproducible from clean checkout, run critical pytest in PR (not nightly-only), add dep/security checks. Unblocks all later skill contracts/pilots.

## Scope (one sentence — what "done" looks like)

Clean checkout installs with `--frozen`, PR runs split-proofs + critical pytest + audit, `uv.lock` tracked.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_153.ci_base_green/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_153.ci_base_green/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_153.ci_base_green/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_153.ci_base_green/` | [ ] |
| Testing | Test report | `6.testing/features/feature_153.ci_base_green/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

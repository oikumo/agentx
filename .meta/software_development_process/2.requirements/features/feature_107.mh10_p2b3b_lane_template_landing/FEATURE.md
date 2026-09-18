# Feature 107: Mh10_P2B3B_Lane_Template_Landing

> **Status:** [ ] Not started
> **Created:** 2026-09-18
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

MH10 P2 slice B3b lands the lane template within the 15-place cap by reusing `tests_capacity`/`src_edit_capacity` as the test/integration slot tokens, retiring the redundant `e2e_receipt` net token, and adding the 3 lane state places + 6 lane transitions (19 arcs), so every lane move becomes a checked template firing with slot accounting.

## Scope (one sentence — what "done" looks like)

Full lane walk claim→submit→verify→start→finish fires all 6 template transitions on the migrated 15-place net with receipt + `check`/`build`/suite green.

## Task type

minor_feature (declaration only per §12; Analysis signed in `analysis_001_cap_safe_lane_template.md`)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_107.mh10_p2b3b_lane_template_landing/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_107.mh10_p2b3b_lane_template_landing/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_107.mh10_p2b3b_lane_template_landing/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_107.mh10_p2b3b_lane_template_landing/` | [ ] |
| Testing | Test report | `6.testing/features/feature_107.mh10_p2b3b_lane_template_landing/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

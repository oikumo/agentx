# Feature 147: T3_Overlay_Lane_Proofs

> **Status:** [~] In progress (Analysis; renamed from scaffold `feature_139.feature_147_t3_overlay` 2026-10-11 to align phase slug `feature_147` — untracked scaffold, no history lost)

> **Status:** [ ] Not started
> **Created:** 2026-10-11
> **WORK.md task:** `## Paused` — **harness_wrapper_split — T3 overlay lane proofs (feature_147) PAUSED 2026-10-11**

---

## Summary

T3 overlay lane proofs: run each lane suite in an ephemeral overlay with the other
side renamed away (`prove --lane` worktree/tmpfs copy), wire split + nightly CI,
and close the TS TA-strip gap (`tsc --noEmit`). First harness-surface change since R3.

## Scope (one sentence — what "done" looks like)

`prove --lane both --overlay tmpfs` green with byte-identical/STALE-valid `verify`, split + nightly CI green, `tsc --noEmit` clean, lanes 2112+12+9 baseline held.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_147.t3_overlay_lane_proofs/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_147.t3_overlay_lane_proofs/analysis_001_t3_overlay.md` | [x] |
| Design | Design doc | `4.design/features/feature_147.t3_overlay_lane_proofs/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_147.t3_overlay_lane_proofs/` | [ ] |
| Testing | Test report | `6.testing/features/feature_147.t3_overlay_lane_proofs/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

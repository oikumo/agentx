# Feature 127: Harness Reason Tier 0 Renderer

> **Status:** [ ] Not started
> **Created:** 2026-09-26
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Tier-0 prompt-side renderer `reason_table.ts` (no `omt_` prefix, stdlib only, same pattern as `startup_table.ts`): formats §2 programs + §5 certificates/summaries + UC8 explain slices as plain text, parses digests and `detail_ref`s, zero harness cost.

## Scope (one sentence — what "done" looks like)

`reason_table.ts` renders stage0_ir + §5 cert + UC8 slice as plain lines with digest/detail_ref parsing, stdlib only, no registry/perm/receipt change, sandbox demo passes.

## Task type

<!-- bug_fix | minor_feature | major_feature | new_screen | refactor -->

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_127.harness_reason_tier_0_renderer/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_127.harness_reason_tier_0_renderer/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_127.harness_reason_tier_0_renderer/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_127.harness_reason_tier_0_renderer/` | [ ] |
| Testing | Test report | `6.testing/features/feature_127.harness_reason_tier_0_renderer/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

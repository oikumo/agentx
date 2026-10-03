# Feature 138: Startup Compact Digest Render-Once

> **Status:** [x] Shipped 2026-09-28 (minor_feature: TDD RED→GREEN→REFACTOR→DONE; `startup_table` probeDigest + verbatim-relay STARTUP; 4 tests + e2e receipt; test report @ 6.testing)
> **Created:** 2026-09-28
> **WORK.md task:** mh16 slice 2 (linked: meta_harness_16, origin scaffold)

---

## Summary

`startup_table` accepts a compact `probeDigest` (~81B vs ~583B envelope, 7.2×) rendering byte-identically, and the STARTUP protocol goes digest-first with verbatim relay (render-once: one canonical renderer, identical D19 map, zero hand-render variance). Budgets grown deliberately with dated rationale (agents_md 3584→3648, nav_index 67584→67648, NAV_INDEX_CEIL re-pin).

## Scope (one sentence — what "done" looks like)

Digest renders byte-identical menu to the full envelope with legacy path intact, STARTUP pins digest-first + verbatim relay, call-turn bytes measured, budgets green, full suite green.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_138.startup_compact_digest_render_once/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_138.startup_compact_digest_render_once/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_138.startup_compact_digest_render_once/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_138.startup_compact_digest_render_once/` | [ ] |
| Testing | Test report | `6.testing/features/feature_138.startup_compact_digest_render_once/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

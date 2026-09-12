# Feature 071: Delegate Advisory Fold

> **Status:** [ ] Not started
> **Created:** 2026-09-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

T3-2 delegate-advisory fold + fanout recipe (mh2 U16 + mh7 P2-2): op:state
resume / op:plan research-shaped path returns advisory
delegate_hint {subagent_type, suggested_prompt}, never enforced; one loop
recipe explore(read-only) → propose → approval → execute with
ledger-session scoping so parallel probes don't shadow canary.

## Scope (one sentence — what "done" looks like)

Research-heavy resume (session with ≥1 complete re-deriving KB/nav, or fresh
feature resume) and research-shaped op:plan (grep|glob|rg|find) emit advisory
delegate_hint; advisory-only, agent still free to ignore.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_071.delegate_advisory_fold/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_071.delegate_advisory_fold/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_071.delegate_advisory_fold/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_071.delegate_advisory_fold/` | [ ] |
| Testing | Test report | `6.testing/features/feature_071.delegate_advisory_fold/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

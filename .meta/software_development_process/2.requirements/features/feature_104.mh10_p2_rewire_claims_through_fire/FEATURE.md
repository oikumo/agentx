# Feature 104: Mh10 P2 Rewire Claims Through Fire

> **Status:** [x] Analysis signed
> **Created:** 2026-09-18
> **WORK.md task:** P2 re-entry slice B (evidence-carrying claim path)

---

## Summary

Slice B narrows C6 on the claim path: `claim_task`/`release_task` route their pool-token move through a shared `_fire_pool_move()` helper that fires the template transition (`work_start`/`work_complete`) when enabled and records `transition + fired` evidence in every ledger record — with a labeled fallback (reason-coded) where the template cannot express the move (attention-vs-workers conflict, back-edges). Behavior preserved; every claim/release becomes checkable via `managed_ops`.

## Scope (one sentence — what "done" looks like)

Claim/release carry `transition/fired` ledger evidence with template fire preferred and labeled fallback, all existing claim/release/lane tests green plus new fired-vs-fallback tests, `check`/`build`/suite green.

## Task type

<!-- bug_fix | minor_feature | major_feature | new_screen | refactor -->

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_104.mh10_p2_rewire_claims_through_fire/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_104.mh10_p2_rewire_claims_through_fire/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_104.mh10_p2_rewire_claims_through_fire/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_104.mh10_p2_rewire_claims_through_fire/` | [ ] |
| Testing | Test report | `6.testing/features/feature_104.mh10_p2_rewire_claims_through_fire/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

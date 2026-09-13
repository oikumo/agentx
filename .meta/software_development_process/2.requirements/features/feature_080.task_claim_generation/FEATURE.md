# Feature 080: Task Claim Generation

> **Status:** [ ] Not started
> **Created:** 2026-09-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

T5-2 (slice 2B, NEXT_STEP §6, mh8 D9/D10/D14): convert slice-1 named bindings
(feature_064, observation-only, generation recorded-not-enforced) into
enforceable ownership — a task-aware claim transaction under the T5-1
`CoordinationLock` + `_transact` authority with owner/session/generation
capability, atomic marking+binding update, explicit release/transfer, and
generation-fenced checkpoint/result mutation. Strict T5 slice order: builds on
079, gates 2C–3C.

## Scope (one sentence — what "done" looks like)

Done = `claim_task`/`release_task`/`transfer_task`/`checkpoint_task` in
`scripts/omt/net/state.py` (all via `_transact`: lock + `expected_revision` +
`command_id`) + `claim|release|transfer|checkpoint` CLI ops (+ plugin
whitelist) + goldens proving same-task race = 1 winner, unrelated rev bump
keeps generation, stale generation cannot submit.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_080.task_claim_generation/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_080.task_claim_generation/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_080.task_claim_generation/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_080.task_claim_generation/` | [ ] |
| Testing | Test report | `6.testing/features/feature_080.task_claim_generation/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

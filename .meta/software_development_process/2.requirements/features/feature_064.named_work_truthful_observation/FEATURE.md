# Feature 064: Named Work Truthful Observation

> **Status:** [x] Done (2026-09-12 — suite 2015+1-flake-cleared, e2e #23, harnessc 0 errors)
> **Created:** 2026-09-12
> **WORK.md task:** meta_harness_7 focus track slice 1 (D4) — `AGENTX_CONCURRENT_WORK.md` §First slice step 1

---

## Summary

Slice 1 of the focused AgentX concurrent-coordination track (meta_harness_7 D4):
named task bindings over the existing pool engine plus a truthful, revisioned
probe observation/menu. No live-net restructure (15-place cap held), no new
`omt_net` op (closed enum untouched), no WORK.md renderer change. Bindings live
in the sidecar (revision-coupled, atomic with the bundle); the probe reports
per-place bindings-vs-tokens (anonymous remainder explicit), a single
observation state with reason, task-bound menu actions in NEXT/Other/Blocked/
Resources order, and labeled analysis basis (live marking vs initial-marking
analysis). Atomic claims + integration/evidence (slices 2–3) are explicitly
deferred — see design note.

## Scope (one sentence — what "done" looks like)

Probe answers the agent-facing contract's observation questions from a
revisioned bundle with validated named bindings, explicit idle/active/blocked/
complete/inconsistent meanings, and no false claim about analysis basis, pinned
by hermetic tests + e2e check #23 with suite green.

## Task type

minor_feature (+ short design note for binding semantics; no §12 major gate)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_064.named_work_truthful_observation/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_064.named_work_truthful_observation/analysis_001_*.md` | [ ] skipped (minor decl-only; design note covers) |
| Design | Design doc | `4.design/features/feature_064.named_work_truthful_observation/design_001_*.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_064.named_work_truthful_observation/` | [x] (state.py bindings + cli.py probe; detail @ design_001) |
| Testing | Test report | `6.testing/features/feature_064.named_work_truthful_observation/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

# Feature 118: Mh11 Worktree Lifecycle

> **Status:** [ ] Not started
> **Created:** 2026-09-19
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

Worktree-per-claim runtime on the improvement003 git-plane: `claim(task_id)` creates a sidecar worktree+branch under `@var.git_worktree_root`, the agent works there only, `fire(work_complete)` requires a sidecar-local commit plus green suite, and a local join merges and cleans up with `main` protected. It turns MH11's manual d1–d3 sidecar discipline into a net-enforced lifecycle with `net↔ledger↔git` triple drift.

## Scope (one sentence — what "done" looks like)

`claim` → sidecar worktree+branch `feat/{task_id}` exists and is bound gen-fenced; `fire(work_complete)` refuses without sidecar commit + green suite + `expected_revision` match; local join merges and removes the worktree with `main` protected and every step ledger-audited.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_118.mh11_worktree_lifecycle/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_118.mh11_worktree_lifecycle/analysis_001_*.md` | [x] |
| Design | Design doc | `4.design/features/feature_118.mh11_worktree_lifecycle/design_001_*.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_118.mh11_worktree_lifecycle/` | [x] |
| Testing | Test report | `6.testing/features/feature_118.mh11_worktree_lifecycle/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

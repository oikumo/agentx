# Feature 015: AgentX Security & Quality Hardening

> **Status:** [~] In progress
> **Created:** 2026-07-11
> **WORK.md task:** T-015-hardening

---

## Summary

Feature_007 (agentx intelligent agent behaviour) has a solid MVC++ architecture (0
violations, 169/169 tests pass) but a line-by-line re-review found **3 critical security
defects**, **7 high-severity logic/concurrency bugs**, **14 medium issues**, **18 low
issues**, and **8 incomplete stubs**. This feature fixes all of them in four priority
phases: Critical (security + broken DSL) → High (data consistency + concurrency) → Medium
(batch polish) → Low + Stubs (code quality roadmap). The goal is to make feature_007 safe
for production autonomous deployment.

## Scope (one sentence — what "done" looks like)

All 50 issues from `FEATURE_007_IMPLEMENTATION_REVIEW.md` are fixed with regression tests,
the full suite passes with zero regressions, and MVC++ remains at 0 errors.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_015.../FEATURE.md` | [x] |
| Analysis | Issue verification | `3.analysis/features/feature_015.../analysis_001_issue_verification.md` | [x] |
| Analysis | Use cases & operations | `3.analysis/features/feature_015.../analysis_002_use_cases_and_operations.md` | [x] |
| Design | Fix design | `4.design/features/feature_015.../design_001_fix_design.md` | [ ] |
| Design | Operation spec | `4.design/features/feature_015.../operation_spec_001_changed_operations.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_015.../impl_notes.md` | [ ] |
| Testing | Test report | `6.testing/features/feature_015.../test_report.md` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

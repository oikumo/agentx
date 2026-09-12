# Feature 068: Schema Audit Autolink

> **Status:** [ ] Not started
> **Created:** 2026-09-12
> **WORK.md task:** <!-- link the matching line in WORK.md -->

---

## Summary

T1-2 adds a read-only `op:audit` to `omt_q` that joins `4.design/features/<slug>` vs `6.testing/features/<slug>/test_report.md` to flag schema gaps, and extends `op:drift` project_drift detail to emit an exact runnable `project.py link --infer` / `check_projects` fix-it. Source: mh2 U14 + mh7 P1-3; D5 overlap-clear (current ops are state|plan|drift only).

## Scope (one sentence — what "done" looks like)

`omt_q{op:audit}` flags the known design-vs-testing gaps and `op:drift` lines contain a runnable link command, verified by golden tests.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_068.schema_audit_autolink/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_068.schema_audit_autolink/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_068.schema_audit_autolink/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_068.schema_audit_autolink/` | [ ] |
| Testing | Test report | `6.testing/features/feature_068.schema_audit_autolink/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

# Feature 016: Tdd Enforcement

> **Status:** [x] Done
> **Created:** 2026-07-11
> **WORK.md task:** `<!-- id:T-016-prio-high agent:true -->`

---

## Summary

A TDD enforcement engine (`scripts/omt/tdd_check.py`) that implements Kent Beck's
TDD spec (`.meta/doc/tdd/tdd-agent-spec.md`) as a stdlib-only Python script, integrated
with the existing `omt_enforcer.ts` gate via the same pattern as `mvc_check.py`. The
engine provides AST-based test→target inference, true-RED verification, coverage gap
analysis, anti-pattern detection, and a two-hats gate (RED→tests only, GREEN/REFACTOR→src
only). Five thin wrapper tools (`omt_testlist`, `omt_red`, `omt_green`, `omt_refactor`,
`omt_done`) delegate to the Python script, while the enforcer's `tool.execute.before` hook
enforces the two-hats gate on every `src/` and `tests/` edit, and the `tool.execute.after`
hook reverts REFACTOR edits that break tests.

## Scope (one sentence — what "done" looks like)

A Python TDD engine (`tdd_check.py`) with 9 subcommands is integrated into the
`omt_enforcer.ts` gate, enforcing the Red→Green→Refactor cycle via AST analysis and
the two-hats principle, with 52 tests passing and zero regressions.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_016.tdd_enforcement/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_016.tdd_enforcement/analysis_001_tdd_enforcement.md` | [x] |
| Design | Design doc | `4.design/features/feature_016.tdd_enforcement/design_001_tdd_enforcement.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_016.tdd_enforcement/impl_notes.md` | [x] |
| Testing | Test report | `6.testing/features/feature_016.tdd_enforcement/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

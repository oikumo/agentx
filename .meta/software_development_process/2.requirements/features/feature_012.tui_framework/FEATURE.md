# Feature 012: TUI Framework

> **Status:** [x] Done (zero regressions; 578/579, 1 pre-existing; MVC++ 0/6)
> **Created:** 2026-07-05
> **WORK.md task:** Implement feature_012.tui_framework

---

## Summary

AgentX's Textual TUI is spread across `ui/tui/` and `agent/view/tui/` with no
shared base classes: ~830 LOC of copy-paste boilerplate (controller wiring,
quit/back actions, defensive notify, navigation glue, adapter skeletons,
embedded widgets) is duplicated across 9 screens/adapters. This feature extracts
a reusable base-class library under `src/agentx/ui/tui/framework/` — base screen,
base modal screen, base app, base adapter, navigation mixin, reusable widgets,
and a metaclass-safe partner-registration helper — and refactors the 9 existing
screens/adapters to inherit from it, centralising TUI implementation and making
new TUI implementations cheap to build.

## Scope (one sentence — what "done" looks like)

A reusable `ui/tui/framework/` base-class library exists, the 9 existing TUI
screens/adapters inherit from it, the existing 516-test suite stays green (1
pre-existing failure allowed), and MVC++ reports 0/0.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_012.tui_framework/FEATURE.md` | [x] |
| Analysis | Overview & current-state | `3.analysis/features/feature_012.tui_framework/analysis_001_overview.md` | [x] |
| Analysis | Use cases | `3.analysis/features/feature_012.tui_framework/analysis_002_use_cases.md` | [x] |
| Analysis | Analysis class diagram | `3.analysis/features/feature_012.tui_framework/analysis_003_class_diagram.md` | [x] |
| Design | Design doc | `4.design/features/feature_012.tui_framework/design_001_tui_framework.md` | [x] |
| Design | Operation spec | `4.design/features/feature_012.tui_framework/operation_spec_001_tui_framework.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_012.tui_framework/impl_notes.md` | [x] |
| Testing | Test report | `6.testing/features/feature_012.tui_framework/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

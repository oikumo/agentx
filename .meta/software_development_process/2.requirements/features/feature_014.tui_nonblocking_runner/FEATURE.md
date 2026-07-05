# Feature 014: TUI Nonblocking Runner

> **Status:** [x] Done
> **Created:** 2026-07-05
> **WORK.md task:** `Implement feature_014.tui_nonblocking_runner`

---

## Summary

The TUI framework (feature_012) provides reusable base classes for screens, modals,
adapters, and widgets — but it has **no mechanism for running blocking operations off
the Textual UI thread**. Three screens call blocking operations synchronously on the
event loop, freezing the entire UI:

- `AgentTUIScreen.action_run_cycle()` — `controller.run_cycle()` → `llm.invoke()` HTTP
- `AgentDemoScreen.action_run_cycle()` — same blocking call
- `AgentTUIScreen.action_save()` — `controller.save_snapshot()` (sqlite I/O)

The Fast Agent's `RunningModal` already solved this with a daemon worker thread +
`queue.Queue` + `threading.Event` + `set_timer` poll loop — but that ~100 LOC of
threading logic is **hardcoded inline** in the modal, not reusable by other screens.

This feature adds a reusable **`BlockingTaskRunner`** to the TUI framework that any
screen inherits via `BaseAgentXScreen.run_blocking()`. It runs blocking callables on a
daemon worker thread, delivers results/errors to the UI thread via a queue + `set_timer`
poller, supports cancellation, and cleans up on unmount. The three freeze-affected
screens are refactored to use it, and `RunningModal`'s threading is optionally migrated
to reduce duplication.

## Scope (one sentence — what "done" looks like)

A `BlockingTaskRunner` in `src/agentx/ui/tui/framework/` that any `BaseAgentXScreen`
subclass uses via `run_blocking()` to execute blocking callables off-thread with
result/error callbacks, cancellation, and unmount cleanup — with the Agent/Demo screen
freezes eliminated, the existing `RunningModal` freeze-fix tests still green, and the
full suite passing with MVC++ 0 errors.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | FEATURE.md | `2.requirements/.../feature_014.tui_nonblocking_runner/FEATURE.md` | [x] |
| Analysis | Overview | `3.analysis/.../analysis_001_overview.md` | [x] |
| Analysis | Use cases | `3.analysis/.../analysis_002_use_cases.md` | [x] |
| Analysis | Class diagram | `3.analysis/.../analysis_003_class_diagram.md` | [x] |
| Design | Design doc | `4.design/.../design_001_nonblocking_runner.md` | [x] |
| Design | Operation spec | `4.design/.../operation_spec_001_nonblocking_runner.md` | [x] |
| Implementation | Impl notes | `5.implementation/.../impl_notes.md` | [x] |
| Testing | Test report | `6.testing/.../test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

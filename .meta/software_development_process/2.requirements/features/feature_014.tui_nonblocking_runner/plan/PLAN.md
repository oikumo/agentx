# PLAN — feature_014: TUI Nonblocking Runner

> Task type: **major_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

A reusable `BlockingTaskRunner` in `src/agentx/ui/tui/framework/` that any
`BaseAgentXScreen` subclass uses via `run_blocking()` to execute blocking callables
off the UI thread — eliminating the agent-screen freezes, with the existing
`RunningModal` freeze-fix tests still green and the full suite passing.

## Steps

- [x] Analysis (3 artifacts: overview, use cases, class diagram)
- [x] Design (design_001 + operation_spec_001)
- [x] Implementation (BlockingTaskRunner + framework integration + screen refactors)
- [x] Testing (38 tests: 23 unit + 7 freeze regression + 8 MVC++ compliance; full suite 678 pass)

## Artifacts produced

- Requirements: `feature_014.tui_nonblocking_runner/FEATURE.md`
- Analysis: `3.analysis/features/feature_014.tui_nonblocking_runner/analysis_001_overview.md`
- Analysis: `3.analysis/features/feature_014.tui_nonblocking_runner/analysis_002_use_cases.md`
- Analysis: `3.analysis/features/feature_014.tui_nonblocking_runner/analysis_003_class_diagram.md`
- Design: `4.design/features/feature_014.tui_nonblocking_runner/design_001_nonblocking_runner.md`
- Design: `4.design/features/feature_014.tui_nonblocking_runner/operation_spec_001_nonblocking_runner.md`
- Testing: `6.testing/features/feature_014.tui_nonblocking_runner/test_report.md`

## Key decisions

1. **Framework-level fix** — the runner lives in `ui/tui/framework/`, not per-screen.
2. **Preserve the RunningModal freeze-fix** — its 4 regression tests must stay green.
3. **Queue + set_timer poll pattern** — proven in RunningModal; reuse the approach.
4. **Daemon threads** — workers don't outlive the process; unmount sets a stop event.
5. **MVC++ pure View** — the runner imports no Model; controllers are duck-typed `Any`.

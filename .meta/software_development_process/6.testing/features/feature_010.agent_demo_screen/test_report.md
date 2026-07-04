# Test Report — feature_010.agent_demo_screen

> **Phase:** Testing → Done | **Feature:** feature_010.agent_demo_screen
> **Date:** 2026-07-04

## Summary

| Metric | Result |
|--------|--------|
| feature_010 tests | **34/34 pass** |
| feature_007 regression | **169/169 pass** |
| Full suite | **468/469 pass** (1 pre-existing failure, unrelated) |
| MVC++ lint | **0 errors, 6 warnings** (baseline unchanged) |

**Verdict:** PASS — no regressions introduced.

## Pre-existing failure (not caused by this feature)

`tests/tui/test_chat_rag_screens.py::TestChatTUIScreenConstruction::test_llm_initialization_attempted`
fails because `ChatTUIScreen` no longer exposes an `llm` attribute. This is the
same pre-existing failure recorded in `WORK.md` (the baseline was 434/435 before
this feature; now 468/469 with 34 new tests added). feature_010 does not touch
chat/rag screens.

## Test inventory (tests/features/feature_010.agent_demo_screen/)

### Unit — `test_demo_scenarios.py` (10 tests)
- Scenario registry: 2 scenarios, case-insensitive lookup, unknown→None.
- Scenario A shape: goal/rule/file contract.
- Scenario B shape: two rules, memory_contains + NOT condition, create action.
- `seed_sandbox_files`: writes files, idempotent overwrite, parent dirs, path
  escape rejected, scenario B notes seeded.

### Unit — `test_demo_controller.py` (16 tests)
- `GoalManager.clear()`: empties tree, idempotent.
- `MemoryManager.clear_volatile()`: empties cache.
- `Agent.clear_state()`: clears goals/rules/memory, resets state→PERCEIVING.
- `AgentController.reset_state()`: clears via controller.
- `load_demo_scenario_by_name`: loads A/B, unknown→False, clears prior state,
  scenario A completes in one cycle, scenario B two-cycle flow, reset re-seeds.
- `get_demo_scenario_info`: returns display dict, unknown→None.

### Integration — `test_demo_screen.py` (8 tests, Textual pilot)
- `AgentDemoScreen` is an `IAgentViewPartner` virtual subclass.
- Bindings: r/x/escape present; buttons btn-run/btn-reset/btn-back present.
- Pilot mount: auto-loads scenario A, auto-runs one cycle, goal COMPLETED.
- Run Cycle button (r): steps a cycle without crashing.
- Reset button (x): clears memory + re-seeds the scenario goal.
- `AgentTUIScreen` demo wiring: `d` binding, `action_open_demo`/`_cmd_demo`
  exist, `demo b` dispatches with "b", `demo` defaults to "a".

## MVC++ compliance

- `AgentDemoScreen` (View) imports no Model module.
- `scenarios.py` is pure data (Model); controller translates specs.
- `uv run scripts/omt/mvc_check.py src/agentx/agent/` → 0 errors, 0 warnings.

## Bug fix verification

The feature_007 tool dispatch bug (tools reading `command.parameters` instead of
`command.action`) was fixed. All 169 feature_007 tests pass — the fix is safe
and backward-compatible (existing tests set `action=` on the command, so reading
`command.action` works for both test and runtime paths).

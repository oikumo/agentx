# Test Report — feature_011.fast_agent

> **Phase:** Testing | **Date:** 2026-07-04 | **Feature:** feature_011.fast_agent

## Summary

The Fast Agent feature (modal-dialog-driven agent UX) was tested with 44 new
tests across 4 test files, plus 5 updated existing tests. All pass. Zero
regressions in the full suite.

## Test files

| File | Tests | Type |
|------|-------|------|
| `tests/features/feature_011.fast_agent/test_fast_agent_unit.py` | 9 | Unit |
| `tests/features/feature_011.fast_agent/test_fast_agent_modals.py` | 18 | Unit (Textual pilot) |
| `tests/features/feature_011.fast_agent/test_fast_agent_flow.py` | 7 | Integration (Textual pilot) |
| `tests/features/feature_011.fast_agent/test_mvc_fast_agent.py` | 10 | MVC++ compliance |
| `tests/tui/test_main_screen.py` (updated) | 5 updated | Regression (menu structure) |

## Results

```
feature_011 tests:  44/44 pass
Full suite:        512/513 pass (1 pre-existing failure in test_chat_rag_screens.py)
MVC++ check:        0 errors, 6 warnings (all pre-existing, unchanged baseline)
```

## Coverage

### Unit tests (`test_fast_agent_unit.py`)
- `FastAgentTUIView` — virtual subclass of `IAgentViewPartner`, all 6 methods are no-ops
- `AgentController.get_cycle_summary()` — before any cycle (defaults), after one cycle (incremented), after multiple cycles (counter)
- `AgentAdapter.create_fast()` — returns `(Agent, AgentController, FastAgentTUIScreen)` triad, wires no-op view, screen holds controller

### Modal tests (`test_fast_agent_modals.py`)
- `GoalModal` — bindings, compose (Input + Start/Cancel buttons), cancel dismisses with None, start dismisses with dict
- `ResultModal` — bindings, compose (Save/New/Back buttons), parametrized dismiss values (save/new/back)
- `ReflectionModal` — bindings, compose (Approve/Dismiss/Stop buttons), parametrized dismiss values (approve/dismiss/stop)
- `RunningModal` — MAX_CYCLES constant (50), bindings, `__init__` state, `action_stop` logic

### Integration tests (`test_fast_agent_flow.py`)
- `FastAgentTUIScreen` bindings + controller
- Mount pushes GoalModal
- Cancel returns to host
- Start dismisses GoalModal (RunningModal pushes)
- Full flow: Start → (auto-run) → exit
- Full flow: Start → New goal

### MVC++ compliance tests (`test_mvc_fast_agent.py`)
- `mvc_check.py` 0 errors on all 7 touched files
- View files import no `agentx.agent.model` or `agentx.agent.types`
- `FastAgentTUIView` is virtual subclass of `IAgentViewPartner`
- `MainTUIScreen` has `f` binding + "Advanced Agent" label + `btn-fast-agent` button + `grid-size: 3 2`
- `AgentController` has `get_cycle_summary`
- `AgentAdapter` has `create_fast`
- `MainController` has `show_fast_agent` + `get_fast_agent_controller`

## Known limitations

1. **RunningModal pilot tests** — The auto-run loop (`call_after_refresh`
   chain) is incompatible with Textual pilot's `_wait_for_screen()` timeout.
   RunningModal compose and stop are tested via `__init__` state verification
   instead of full pilot mount. The full flow is covered by the integration
   flow tests (which push FastAgentTUIScreen → GoalModal → Start).

2. **Advanced constraints** — The `GoalModal`'s constraints input is captured
   but unused in v1 (displayed with "(optional, not used yet)" hint). This is
   by design — a future iteration can parse constraints into policy rules.

3. **Textual 8.x `app.query` vs `app.screen.query`** — Discovered during
   testing that `app.query()` does not search screen widget trees in Textual
   8.x; must use `app.screen.query()` instead. All tests updated accordingly.

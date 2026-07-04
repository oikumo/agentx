# Implementation Notes — feature_011.fast_agent

> **Phase:** Programming → Testing | **Date:** 2026-07-04

## Summary

Implemented the **Fast Agent** — a new `⚡ Fast Agent` main-menu option (`f`
key) that drives the existing feature_007 `Agent` via a stack of Textual
`ModalScreen` dialogs (Goal → Running → Reflection → Result). The existing
`🤖 Agent` button was relabeled `⚙️ Advanced Agent`. Zero Model-layer changes.

## Files created (3 new View files)

| File | Purpose |
|------|---------|
| `src/agentx/agent/view/tui/fast_agent_screen.py` | `FastAgentTUIScreen(Screen)` — modal-stack host; owns controller + modal callbacks |
| `src/agentx/agent/view/tui/fast_agent_modals.py` | 4 `ModalScreen` subclasses: `GoalModal`, `RunningModal`, `ReflectionModal`, `ResultModal` |
| `src/agentx/agent/view/tui/fast_agent_view.py` | `FastAgentTUIView` — no-op `IAgentViewPartner` (virtual-subclass registered) |

## Files edited (4 existing files)

| File | Change |
|------|--------|
| `src/agentx/agent/controller/agent_controller.py` | `+ get_cycle_summary()`, `+ _cycle_count` counter, `+ _last_result` tracking in `run_cycle()` |
| `src/agentx/agent/adapter.py` | `+ AgentAdapter.create_fast()` factory (lazy imports, no-op view wiring) |
| `src/agentx/ui/screens/main/main_controller.py` | `+ show_fast_agent()`, `+ get_fast_agent_controller()`, `+ _fast_agent_controller` field |
| `src/agentx/ui/tui/screens/main_screen.py` | `+ Binding("f", "open_fast_agent")`, `+ btn-fast-agent` button, `+ action_open_fast_agent()`, relabel `btn-agent` → `⚙️ Advanced Agent`, grid `4 1` → `3 2`, help text updated |

## Tests created (4 test files, 44 tests)

| File | Tests | Coverage |
|------|-------|----------|
| `tests/features/feature_011.fast_agent/test_fast_agent_unit.py` | 9 | `get_cycle_summary()` before/after cycles, `FastAgentTUIView` virtual subclass + no-ops, `AgentAdapter.create_fast()` triad |
| `tests/features/feature_011.fast_agent/test_fast_agent_modals.py` | 18 | GoalModal/ResultModal/ReflectionModal/RunningModal bindings, compose, dismiss values (parametrized) |
| `tests/features/feature_011.fast_agent/test_fast_agent_flow.py` | 7 | Textual pilot e2e: mount → GoalModal, Cancel, Start, full flow |
| `tests/features/feature_011.fast_agent/test_mvc_fast_agent.py` | 10 | mvc_check.py 0 errors, no Model imports in View, virtual subclass, bindings/buttons/grid assertions |

## Existing tests updated (1 file, 5 tests)

| File | Changes |
|------|---------|
| `tests/tui/test_main_screen.py` | Updated `TestMenuGrid` (4→5 buttons, new IDs/variants, grid 3×2), `TestMainTUIScreenBindings` (6→7 bindings) |

## Test results

- **feature_011 tests:** 44/44 pass
- **Full suite:** 512/513 pass (1 pre-existing failure in `test_chat_rag_screens.py`, unrelated)
- **MVC++ check:** 0 errors, 6 warnings (all pre-existing, unchanged baseline)

## Design decisions implemented

1. **No Model changes** — Fast Agent is View-only; `Agent` facade + `AgentController` reused as-is.
2. **Auto-run via `call_after_refresh`** — cooperative chain, UI stays responsive.
3. **Manual success criteria** — goal never auto-completes; user presses Stop when done.
4. **No-op `FastAgentTUIView`** — swallows controller UI callbacks during `run_cycle()`.
5. **50-cycle safety cap** — prevents infinite loops.
6. **First `ModalScreen` use** in the codebase.
7. **Grid `3 2`** layout for 5 buttons (3+2 arrangement).

## Known limitations

- RunningModal's auto-run loop is incompatible with Textual pilot's
  `_wait_for_screen()` timeout in direct unit tests — the RunningModal compose
  and stop tests verify `__init__` state and `action_stop` logic without a
  full pilot mount. The full flow is tested via the integration flow tests.
- The "Advanced" constraints input in `GoalModal` is captured but unused in v1
  (displayed with an "(optional, not used yet)" hint).

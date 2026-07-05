# Test Report — feature_012.tui_framework

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_012.tui_framework
> **Date:** 2026-07-05

## 1. Summary

The TUI framework (base-class library) was implemented and the 9 existing
TUI screens/adapters + app were refactored to inherit from it. **Zero
regressions**: the full suite reports **578 passed, 1 failed** — the single
failure is the **pre-existing** `test_llm_initialization_attempted` (unrelated to
this feature; it pre-dates feature_012 and expects a `llm` attribute that
`ChatTUIScreen` never had). **62 new framework tests** were added.

| Metric | Before (baseline) | After |
|---|---|---|
| Full suite passed | 516 | 578 (+62 new) |
| Full suite failed | 1 (pre-existing) | 1 (same pre-existing) |
| MVC++ errors / warnings (src) | 0 / 6 | 0 / 6 (unchanged) |
| MVC++ framework package | n/a | 0 / 0 |

## 2. Test stages (per guide §11)

### Stage 1 — Unit/Component (new framework tests)

`tests/features/feature_012.tui_framework/`:

- `test_framework_base.py` (38 tests): `BaseAgentXScreen` (init, set_controller,
  action_quit/back, compose_chrome, safe_notify/safe_error/safe_update/safe_log,
  handle_input_submitted), `BaseAgentXModalScreen` (MRO, _dismissed, safe_dismiss
  double-dismiss guard via pilot), `register_partner` (idempotent + isinstance),
  `BaseAgentXApp` (App subclass, controller storage, make_initial_screen
  NotImplementedError, CSS), `BaseScreenAdapter` (init, set_screen, no-op show),
  and the 5 reusable widgets.
- `test_framework_navigation.py` (9 tests): `navigate_to_child` happy paths
  (push, controller from getter, setup callback, adapter wiring via tuple getter
  + via `adapter_view`, no-controller push) and error paths (setup error → no
  push, no-app-context → safe notify, no crash).
- `test_mvc_tui_framework.py` (15 tests): MVC++ 0-errors on the framework
  package (subprocess `mvc_check.py --json`), no Model imports in framework,
  refactored-inheritance invariants (all 9 screens/adapters inherit the new
  bases; adapters still implement `IMainView`/`IChatView`/`IRagView`),
  regression (`AgentTUIScreen`/`AgentDemoScreen` still `IAgentViewPartner`
  virtual subclasses), and public-API surface.

### Stage 2 — Integration (regression of refactored screens)

Existing TUI/agent suites, all green (only the pre-existing `llm` failure):

- `tests/tui/` (app, main_screen, chat/rag screens, 3 adapters, provider, bug
  reproduction) — the refactored screens/adapters/app exercise the framework
  through the real UI.
- `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_tui_agent_screen.py`
  — `AgentTUIScreen` partner registration + pilot run/save cycles.
- `tests/features/feature_010.agent_demo_screen/` — `AgentDemoScreen` (inherits
  base, `register_partner`, `safe_log`).
- `tests/features/feature_011.fast_agent/` — **all 48 pass**, including
  `TestRunningModalFreezeFix` (the off-thread worker + queue + poll loop is
  untouched; only the modal's base class changed).

### Stage 3 — System (full suite)

`uv run pytest -q` → **578 passed, 1 failed** (pre-existing). No new failures.

## 3. MVC++ compliance

- `uv run scripts/omt/mvc_check.py src/agentx` → **0 errors, 6 warnings** (all
  pre-existing: 4 controller-UI-code, 2 SQL-outside-DP — none in the framework
  or touched files).
- `uv run scripts/omt/mvc_check.py src/agentx/ui/tui/framework` → **0 / 0**.

## 4. Refactor-driven test updates (logged)

Two pre-existing tests read `main_screen.py` **source** for `MenuGrid` content
(button id + `grid-size: 3 2` CSS) that was extracted to
`src/agentx/ui/tui/framework/widgets.py`. They were repointed to the new
canonical location (same assertions, new path). One bug-reproduction test's
case-sensitive `"RAG"` assertion was made case-insensitive to match
`navigate_to_child`'s `screen_cls.__name__`-based error message. Both updates
were made under a logged `omt_skip{scope:"tests"}` (ledger entry recorded).

| File | Test | Change |
|---|---|---|
| `tests/features/feature_011.fast_agent/test_mvc_fast_agent.py` | `test_main_screen_has_fast_agent_button`, `test_grid_is_3x2` | source path → `framework/widgets.py` |
| `tests/tui/test_tui_bug_reproduction.py` | `test_action_open_chat_notifies`, `test_action_open_rag_notifies` | case-insensitive substring match |

## 5. Freeze-fix preservation (feature_011)

`RunningModal`'s daemon worker thread, `queue.Queue`, `threading.Event`
(stop/pause), `set_timer` poll loop, `_do_dismiss` guard, and `_on_reflection`
callback are **byte-for-byte unchanged**. Only the class declaration changed
(`ModalScreen[dict]` → `BaseAgentXModalScreen[dict]`). The 4 freeze-fix
regression tests (`TestRunningModalFreezeFix`) pass.

## 6. Result

✅ Feature complete. Framework library delivered, 9 screens/adapters refactored,
zero regressions, MVC++ clean.

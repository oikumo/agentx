# Implementation Notes — feature_012.tui_framework

> **Phase:** Programming → Testing | **Feature:** feature_012.tui_framework
> **Date:** 2026-07-05
> **Design:** `4.design/features/feature_012.tui_framework/design_001_tui_framework.md`

## 1. What was built

A reusable TUI base-class library at `src/agentx/ui/tui/framework/` (7 files)
plus a refactor of the 9 existing TUI screens/adapters + app to inherit from it.

### New package — `src/agentx/ui/tui/framework/`

| File | Contents |
|---|---|
| `partner.py` | `register_partner(abc_cls, screen_cls)` — idempotent, metaclass-safe ABC registration. |
| `base_screen.py` | `BaseAgentXScreen(Screen, NavigationMixin)` + `NavigationMixin`. Absorbs controller storage, `set_controller`, `action_quit`/`action_back`, `compose_chrome`, `safe_notify`/`safe_error`/`safe_update`/`safe_log`, `handle_input_submitted`, and `navigate_to_child`. |
| `base_modal.py` | `BaseAgentXModalScreen[T](BaseAgentXScreen, ModalScreen[T])` — `_dismissed` guard + `safe_dismiss(value)`. |
| `base_app.py` | `BaseAgentXApp(App)` — default CSS, TTY check on mount, `make_initial_screen()` hook. |
| `base_adapter.py` | `BaseScreenAdapter` — `controller`/`_screen` storage, `set_screen`, no-op `show`. |
| `widgets.py` | `SessionStatusBar`, `WelcomePanel`, `MenuGrid`, `CommandInput`, `ChatMessage` (extracted verbatim with their `DEFAULT_CSS`). |
| `__init__.py` | Public API re-exports + `__all__`. |

### Refactored files (inherit the bases)

- `ui/tui/app.py` — `TUIApplication(BaseAgentXApp)` (overrides `make_initial_screen`); minimal `MainTUIScreen(BaseAgentXScreen)`.
- `ui/tui/screens/main_screen.py` — `MainTUIScreen(BaseAgentXScreen)`; 4 navigation methods → `navigate_to_child`; widgets imported + re-exported.
- `ui/tui/screens/chat_screen.py` — `ChatTUIScreen(BaseAgentXScreen)`; `ChatMessage` imported from framework.
- `ui/tui/screens/rag_screen.py` — `RagTUIScreen(BaseAgentXScreen)`; `action_quit`/`action_back` removed (inherited).
- `ui/tui/adapters/{main,chat,rag}_adapter.py` — all `BaseScreenAdapter` + `IXxxView`.
- `agent/view/tui/agent_screen.py` — `AgentTUIScreen(BaseAgentXScreen)`; `register_partner`; `_log` → `safe_log`.
- `agent/view/tui/demo_screen.py` — `AgentDemoScreen(BaseAgentXScreen)`; `register_partner`; `_log` → `safe_log`; `action_back` removed.
- `agent/view/tui/fast_agent_screen.py` — `FastAgentTUIScreen(BaseAgentXScreen)`.
- `agent/view/tui/fast_agent_modals.py` — 4 modals → `BaseAgentXModalScreen[T]`.

## 2. Key design decisions & deviations from the design doc

### 2.1 Modal MRO (corrected)

The design doc §3.3 sketched `BaseAgentXModalScreen(ModalScreen[T], BaseAgentXScreen)`
and claimed `super().__init__(controller)` chains correctly. **That ordering is
wrong**: `super()` from the modal would hit `ModalScreen.__init__` first, which
(= `Screen.__init__`) does **not** accept a `controller` arg → `TypeError`.

Implemented as `BaseAgentXModalScreen(BaseAgentXScreen, ModalScreen[T])` so the
cooperative `super().__init__(controller)` consumes `controller` in
`BaseAgentXScreen.__init__` first, then chains to `ModalScreen`→`Screen` with no
positional arg. Verified MRO:

```
BaseAgentXModalScreen → BaseAgentXScreen → ModalScreen → Screen → … → NavigationMixin → object
```

Smoke-tested instantiation + `issubclass(..., ModalScreen/BaseAgentXScreen/Screen)`.

### 2.2 `_controller` typed `Any` (not `Any | None`)

`BaseAgentXScreen._controller` is typed `Any` (not `Any | None`) to match the
codebase's duck-typed controller convention and avoid per-access None-narrowing
in subclasses (e.g. `RunningModal`'s worker calls `self._controller.run_cycle()`
without a None guard). `Any` is falsy when `None`, so `if self._controller:`
guards still work.

### 2.3 Main adapter is app-delegating, not screen-delegating

The design doc's "adapter trio shares one skeleton" was slightly off: the
**main** adapter (`TUIAdapter`) delegates to the running **app** (`_app.notify`),
not a pushed screen, and its `show()` runs the app. Only the chat/rag adapters
fit the screen-delegation skeleton. `TUIAdapter` therefore inherits
`BaseScreenAdapter` for `_controller` storage but overrides `__init__` (adds
`_app`) and `show()` (runs `TUIApplication`). The inherited `_screen`/`set_screen`
are unused on the main adapter (harmless).

### 2.4 `_screen` typed `Any` in `BaseScreenAdapter`

Concrete adapters call screen-specific methods (`show_message`, `_update_repository_ui`)
on `self._screen`. Typing it `Any` (rather than `Screen | None`) mirrors the
duck-typed style and avoids `# type: ignore` on every delegation.

### 2.5 Simple modals keep direct `dismiss()`

`GoalModal`/`ReflectionModal`/`ResultModal` inherit `safe_dismiss` but retain
their direct `self.dismiss(value)` calls (single-dismiss by design). Only
`RunningModal` uses a dismiss guard (`_do_dismiss`) — kept verbatim. Switching
the simple modals to `safe_dismiss` was judged not worth the risk on the
freeze-fix-adjacent code; the guard is available for future use.

### 2.6 `navigate_to_child` behaviour vs. original navigation

The original `action_open_*` methods continued to push a screen even if
`controller.show_X()` raised. `navigate_to_child` instead treats a setup error
as fatal (safe_error + return, no push). This is a deliberate, safer behaviour
change. No test exercised the "push despite setup failure" path, so no
regression; it is noted here for traceability.

## 3. Threading-safety (feature_011 freeze fix)

`RunningModal`'s daemon worker thread + `queue.Queue` + `threading.Event`
(stop/pause) + `set_timer(0.05, _poll)` loop + `_do_dismiss` guard +
`_on_reflection` callback are **unchanged**. Only the class base changed. The
`_dismissed` attribute is set by both the base `__init__` and `RunningModal`'s
own `__init__` (redundant, same value — harmless). `TestRunningModalFreezeFix`
(4 tests) passes.

## 4. Backward compatibility

- All public class names + constructors preserved: `TUIApplication`, `TUIProvider`,
  `TUIAdapter`, `TUIChatAdapter`, `TUIRagAdapter`, `MainTUIScreen`, `ChatTUIScreen`,
  `RagTUIScreen`, `AgentTUIScreen`, `AgentDemoScreen`, `FastAgentTUIScreen`,
  `GoalModal`, `RunningModal`, `ReflectionModal`, `ResultModal`.
- Widgets re-exported from their original modules (`from agentx.ui.tui.screens.main_screen import MenuGrid` still works).
- `IAgentViewPartner` virtual-subclass registration preserved (via `register_partner`).
- `IMainView`/`IChatView`/`IRagView` interfaces unchanged; adapters still implement them.

## 5. Verification

- `uv run pytest -q` → **578 passed, 1 failed** (pre-existing `test_llm_initialization_attempted`).
- `uv run scripts/omt/mvc_check.py src/agentx` → **0 errors, 6 warnings** (baseline, all pre-existing).
- `uv run scripts/omt/mvc_check.py src/agentx/ui/tui/framework` → **0 / 0**.
- Feature_011 (fast agent + freeze fix): 48/48 pass.
- Feature_012 framework tests: 62/62 pass.

## 6. Duplication removed

~830 LOC of duplicated boilerplate (controller storage, quit/back, defensive
notify/update, navigation glue, adapter skeletons, embedded widgets, metaclass
hack, input boilerplate, `_log` helper) is now absorbed by the framework. The 4
`MainTUIScreen` navigation methods collapsed from ~240 LOC to ~40 LOC of
`navigate_to_child` calls.

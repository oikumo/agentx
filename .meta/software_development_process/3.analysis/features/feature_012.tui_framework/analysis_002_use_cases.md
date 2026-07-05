# Analysis 002 — TUI Framework: Use Cases

> **Phase:** Analysis — `omt_agent_guide.md §2, §11` | **Feature:** feature_012.tui_framework

The framework is an internal library; its "actors" are (a) the **TUI developer**
building a new screen/variant, and (b) the **end user** who must see no
behavioural change after the refactor. Use cases are therefore written from the
developer's perspective, with a regression use case for the end user.

## UC-1 — Build a new TUI screen from the base library

**Actor:** TUI developer
**Goal:** Create a new Textual screen with minimal boilerplate.

**Main flow:**
1. Developer subclasses `BaseAgentXScreen` (or `BaseAgentXModalScreen` for a modal).
2. The base class already provides: controller storage, `set_controller()`,
   `action_quit()`/`action_back()`, a `compose_chrome()` helper yielding
   Header/Footer, safe-notify helpers (`safe_notify`, `safe_error`), and a
   `handle_input_submitted()` template hook.
3. Developer implements only `compose()` (screen-specific widgets) and the
   screen-specific input/command handlers.
4. Developer registers the screen against its ABC partner via
   `register_partner(IScreenPartner, MyScreen)` (metaclass-safe).

**Alternative flows:**
- 2a. If the screen needs a reusable widget, developer imports it from
  `framework.widgets` instead of re-implementing it.

**Success condition:** screen compiles, mounts, shows Header/Footer, responds to
`q`/`escape`, and notifies without crashing in a no-app-context test.

## UC-2 — Navigate from one screen to another (reusable navigation)

**Actor:** TUI developer (writing a menu/host screen)
**Goal:** Push a child screen and wire its adapter with one call.

**Main flow:**
1. Developer calls `self.navigate_to_child(ScreenClass, controller, adapter_view)`
   provided by the navigation helper (mixed into `BaseAgentXScreen`).
2. The helper: calls `controller.show_X()` if a setup callback is supplied,
   fetches the child controller via an optional getter, constructs the screen,
   connects the adapter via `set_screen()` when an adapter view is supplied,
   and `push_screen()`s it — all with centralised error handling.
3. Developer writes one line instead of ~60.

**Success condition:** child screen mounts; adapter (if any) delegates to it;
errors surface as a single safe notification instead of a crash.

## UC-3 — Implement a new TUI variant (alternate provider)

**Actor:** TUI developer
**Goal:** Ship a second TUI look-and-feel reusing the same base classes.

**Main flow:**
1. Developer subclasses `BaseAgentXApp` with a different initial-screen factory
   and/or CSS theme.
2. Developer reuses `BaseAgentXScreen`, `BaseScreenAdapter`, and the
  `framework.widgets` for the new variant's screens.
3. Developer registers the new provider via `ProviderRegistry.register(...)`.

**Success condition:** the new variant runs side-by-side with the existing TUI
provider; both share the base classes; no duplicated boilerplate.

## UC-4 — Reuse a widget across screens

**Actor:** TUI developer
**Goal:** Use `SessionStatusBar` / `CommandInput` / `ChatMessage` in a new screen.

**Main flow:**
1. Developer imports the widget from `agentx.ui.tui.framework.widgets`.
2. Developer `yield`s it in `compose()`; the widget's `DEFAULT_CSS` travels with it.

**Success condition:** widget renders identically in the new screen; no CSS
collision; no copy-paste.

## UC-5 — Regression: end user sees no behavioural change

**Actor:** End user
**Goal:** After the refactor, the TUI behaves exactly as before.

**Main flow (per existing screen):**
1. User opens Main → presses `c`/`r`/`f`/`a` → child screen opens and works.
2. User chats / runs RAG / runs agent cycles / fast-agent modal flow.
3. `q` quits; `escape` pops back; notifications still appear.

**Success condition:** all 516 existing tests pass (1 pre-existing failure
allowed); MVC++ 0/0; no new console errors.

## Operation list (extracted from use cases)

These become framework/public API methods (detailed specs in Design phase):

| # | Operation | Owner | Source UC |
|---|---|---|---|
| O1 | `BaseAgentXScreen.__init__(controller)` | base screen | UC-1 |
| O2 | `BaseAgentXScreen.set_controller(controller)` | base screen | UC-1 |
| O3 | `BaseAgentXScreen.action_quit()` / `action_back()` | base screen | UC-1, UC-5 |
| O4 | `BaseAgentXScreen.compose_chrome(show_clock, footer)` | base screen | UC-1 |
| O5 | `BaseAgentXScreen.safe_notify(msg, severity, timeout)` | base screen | UC-1, UC-2 |
| O6 | `BaseAgentXScreen.safe_update(widget_id, text)` | base screen | UC-1 |
| O7 | `BaseAgentXScreen.handle_input_submitted(value, input_widget)` | base screen | UC-1 |
| O8 | `BaseAgentXModalScreen.__init__(...)` + dismiss guard | base modal | UC-1 |
| O9 | `register_partner(abc, screen_cls)` | framework helper | UC-1 |
| O10 | `navigate_to_child(screen_cls, controller, adapter_view, setup, getter)` | navigation mixin | UC-2 |
| O11 | `BaseAgentXApp.__init__(controller)` + `on_mount` (TTY check + initial screen) | base app | UC-3 |
| O12 | `BaseAgentXApp.make_initial_screen()` (override hook) | base app | UC-3 |
| O13 | `BaseScreenAdapter.__init__(controller)` + `set_screen(screen)` + `show()` | base adapter | UC-2 |
| O14 | `safe_log(widget_id, message)` | base screen / log mixin | UC-1 |

## Test mapping (UC → tests, executed in Testing phase)

| UC | Test class | Stage |
|---|---|---|
| UC-1 | `TestBaseAgentXScreen` (init, quit/back, safe_notify no crash, compose_chrome) | Unit |
| UC-2 | `TestNavigation` (navigate_to_child pushes screen + wires adapter + handles error) | Unit+Integration |
| UC-3 | `TestBaseAgentXApp` (TTY check path, initial-screen factory) | Unit |
| UC-4 | `TestWidgets` (each widget mounts + renders) | Unit |
| UC-5 | Existing `tests/tui/*` + `tests/features/feature_011.fast_agent/*` unchanged & green | System (regression) |

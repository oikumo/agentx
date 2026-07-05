# Operation Spec 001 — TUI Framework

> **Phase:** Design — `omt_agent_guide.md §10` | **Feature:** feature_012.tui_framework
> **Design:** `design_001_tui_framework.md`

Operation specifications for every public operation introduced by the framework.
Format: `Operation / Preconditions / Exceptions / Postconditions`.

---

## O1 — `BaseAgentXScreen.__init__(self, controller=None)`

**Operation:** Construct a base screen, storing the optional controller.

**Preconditions:**
- Called on a Textual `Screen` subclass instance (Textual owns lifecycle).

**Exceptions:**
- None expected. `super().__init__()` is Textual `Screen.__init__` (no required args).

**Postconditions:**
- `self._controller == controller`.
- Screen is constructed but not mounted.

---

## O2 — `BaseAgentXScreen.set_controller(self, controller)`

**Operation:** Late-bind or replace the controller after construction.

**Preconditions:** none.

**Exceptions:** none.

**Postconditions:** `self._controller == controller`.

---

## O3 — `BaseAgentXScreen.action_quit(self)` / `action_back(self)`

**Operation:** Standard quit (exit app) / back (pop screen) actions.

**Preconditions:**
- Screen is mounted and has an app context (Textual guarantees during bindings).

**Exceptions:**
- `action_back`: `app.pop_screen()` may raise if stack is empty → swallowed (try/except).

**Postconditions:**
- `action_quit`: app exit requested.
- `action_back`: current screen popped, or no-op if stack empty.

---

## O4 — `BaseAgentXScreen.compose_chrome(self, *, show_clock=True, footer=True)`

**Operation:** Yield `Header` (+ optional `Footer`) for use inside a subclass `compose()`.

**Preconditions:** called inside a `compose()` generator.

**Exceptions:** none (yields widgets; Textual handles mount).

**Postconditions:** a `Header` (and `Footer` if `footer`) is part of the compose result.

---

## O5 — `BaseAgentXScreen.safe_notify(self, message, severity="information", timeout=3)`

**Operation:** Show a Textual notification without crashing when no app context is active.

**Preconditions:** none.

**Exceptions:**
- `self.notify(...)` raises if no app context / not mounted → **swallowed**.

**Postconditions:**
- If app context present: notification shown.
- If not: silent no-op. No exception propagates.

---

## O6 — `BaseAgentXScreen.safe_update(self, widget_id, text, widget_cls=Static) -> bool`

**Operation:** Update a widget's content by id; never crash if widget not mounted.

**Preconditions:** none.

**Exceptions:**
- `query_one` raises `NoMatches`/`WrongType` if widget absent → **swallowed**.

**Postconditions:**
- Returns `True` if the widget was found and updated.
- Returns `False` if widget missing or update failed. No exception propagates.

---

## O7 — `BaseAgentXScreen.safe_log(self, widget_id, message)`

**Operation:** Append a line to a `RichLog` widget by id; never crash.

**Preconditions:** none.

**Exceptions:** `query_one`/`write` failures → **swallowed**.

**Postconditions:** line written if widget present; else silent no-op.

---

## O8 — `BaseAgentXScreen.handle_input_submitted(self, value, input_widget) -> bool`

**Operation:** Shared input-submission template: strip, reject empty, clear input.

**Preconditions:** `input_widget` is a Textual `Input`.

**Exceptions:** none.

**Postconditions:**
- If `value` blank after strip: returns `False`, input unchanged.
- Else: `input_widget.value == ""`; returns `True`. Caller then dispatches.

---

## O9 — `BaseAgentXModalScreen.__init__(self, controller=None)` + `safe_dismiss(self, value)`

**Operation:** Construct a modal with a dismiss guard; dismiss exactly once.

**Preconditions:**
- `safe_dismiss` called on a mounted modal (Textual `dismiss` requires mount).

**Exceptions:**
- `dismiss()` called before mount → Textual raises → **NOT swallowed** (caller bug;
  treat as programming error). The guard only prevents double-dismiss.

**Postconditions:**
- `self._dismissed == True` after first `safe_dismiss`.
- Subsequent `safe_dismiss` calls are no-ops.
- Host `push_screen(..., callback=...)` callback fires exactly once with `value`.

---

## O10 — `register_partner(abc_cls, screen_cls)`

**Operation:** Register `screen_cls` as a virtual subclass of `abc_cls` (ABC), idempotently.

**Preconditions:**
- `abc_cls` is an `ABC` subclass.
- `screen_cls` is a Textual `Screen` subclass (cannot inherit ABC directly due to metaclass).

**Exceptions:** none.

**Postconditions:**
- `issubclass(screen_cls, abc_cls)` is `True` (virtual).
- `isinstance(screen_instance, abc_cls)` is `True`.
- Re-calling is a no-op.

---

## O11 — `NavigationMixin.navigate_to_child(self, screen_cls, controller=None, *, adapter_view=None, setup=None, getter=None)`

**Operation:** Push a child screen, optionally running a setup callback, fetching the
child controller via a getter, and wiring an adapter view. Centralises the 4
navigation-glue copies in `MainTUIScreen`.

**Preconditions:**
- `self` is a mounted screen with an app context.
- `screen_cls(controller)` is a valid constructor for the child screen.
- `setup` (if given) takes the host controller.
- `getter` (if given) takes the host controller and returns either `child_controller`
  or `(child_controller, view)`.

**Exceptions:**
- `setup` raises → `safe_error(str(e))`; return (no push).
- `getter` raises → `safe_error(str(e))`; return.
- `screen_cls(...)` raises → `safe_error(str(e))`; return.
- `app.push_screen` raises (no app context) → `safe_error(str(e))`; return.
- All exceptions are caught so the host screen never crashes.

**Postconditions:**
- On success: child screen is pushed; if a `view` returned by `getter` is a
  `BaseScreenAdapter`, `view.set_screen(child_screen)` was called before push.
- On failure: a single error notification shown; host screen remains.

---

## O12 — `BaseAgentXApp.__init__(self, controller=None)` + `make_initial_screen(self)` + `on_mount(self)`

**Operation:** Construct the app, and on mount perform TTY check + push the initial screen.

**Preconditions:**
- Subclass overrides `make_initial_screen()` to return a `Screen`.

**Exceptions:**
- `sys.stdin.isatty()` may raise on closed stdin → guarded (treated as non-TTY).
- `make_initial_screen` not overridden → `NotImplementedError` on mount.

**Postconditions:**
- If non-TTY: a warning notification scheduled.
- `make_initial_screen()` result pushed as the active screen.

---

## O13 — `BaseScreenAdapter.__init__(self, controller)` + `set_screen(self, screen)` + `show(self)`

**Operation:** Adapter skeleton: store controller + optional screen; `show` is a no-op
(screen already pushed by host).

**Preconditions:** none.

**Exceptions:** none.

**Postconditions:**
- `self._controller == controller`, `self._screen == None` initially.
- After `set_screen(s)`: `self._screen == s`.
- `show()` is a no-op.

---

## O14 — Widget constructors (`SessionStatusBar`, `WelcomePanel`, `MenuGrid`, `CommandInput`, `ChatMessage`)

**Operation:** Construct a reusable widget (extracted verbatim from screen files).

**Preconditions:** none.

**Exceptions:** none.

**Postconditions:**
- Widget instance created with its `DEFAULT_CSS` active (Textual scopes CSS by class name).
- `SessionStatusBar.update_context(...)` / `ChatMessage(role=...)` APIs unchanged.

---

## Cross-cutting: regression invariants (must hold after refactor)

| Invariant | How verified |
|---|---|
| `issubclass(AgentTUIScreen, IAgentViewPartner)` still True | unit test |
| `issubclass(AgentDemoScreen, IAgentViewPartner)` still True | unit test |
| `MainTUIScreen` still pushes Chat/RAG/Agent/FastAgent | existing `tests/tui/test_main_screen.py` |
| `RunningModal` worker thread + queue unchanged | `TestRunningModalFreezeFix` (feature_011) |
| `TUIProvider` creates same adapter types | `tests/tui/test_provider.py` |
| Adapters delegate to screen via `set_screen` | `tests/tui/test_*_adapter.py` |

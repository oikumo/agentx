# Design 001 — TUI Framework

> **Phase:** Design — `omt_agent_guide.md §2, §5–§10` | **Feature:** feature_012.tui_framework
> **Analysis:** `3.analysis/features/feature_012.tui_framework/analysis_001..003_*.md`

## 1. Components / screens affected

This feature is **View-only**. No Model layer is touched. No controller public
API changes. The `IUIProvider`/`IMainView`/`IChatView`/`IRagView` interfaces are
unchanged — adapters still implement them.

**New (the library):** `src/agentx/ui/tui/framework/` package (7 files).
**Edited (refactor to inherit):** 9 screens + 3 adapters + app + provider.

| Component | Layer | Change |
|---|---|---|
| `ui/tui/framework/` (new) | View | Base classes + widgets + helpers |
| `ui/tui/app.py` | View | `TUIApplication` → `BaseAgentXApp` |
| `ui/tui/provider.py` | View | unchanged (uses adapters) |
| `ui/tui/screens/main_screen.py` | View | `MainTUIScreen` → `BaseAgentXScreen` + `NavigationMixin`; extract 4 widgets |
| `ui/tui/screens/chat_screen.py` | View | `ChatTUIScreen` → `BaseAgentXScreen`; extract `ChatMessage` |
| `ui/tui/screens/rag_screen.py` | View | `RagTUIScreen` → `BaseAgentXScreen` |
| `ui/tui/adapters/main_adapter.py` | View | `TUIAdapter` → `BaseScreenAdapter` |
| `ui/tui/adapters/chat_adapter.py` | View | `TUIChatAdapter` → `BaseScreenAdapter` |
| `ui/tui/adapters/rag_adapter.py` | View | `TUIRagAdapter` → `BaseScreenAdapter` |
| `agent/view/tui/agent_screen.py` | View | `AgentTUIScreen` → `BaseAgentXScreen` |
| `agent/view/tui/demo_screen.py` | View | `AgentDemoScreen` → `BaseAgentXScreen` |
| `agent/view/tui/fast_agent_screen.py` | View | `FastAgentTUIScreen` → `BaseAgentXScreen` |
| `agent/view/tui/fast_agent_modals.py` | View | 4 modals → `BaseAgentXModalScreen` (skeleton only; `RunningModal` keeps worker/queue) |

## 2. Static structure (classes & files)

```
src/agentx/ui/tui/framework/
├── __init__.py          # public API re-exports
├── partner.py           # register_partner() — metaclass-safe ABC registration
├── base_screen.py       # BaseAgentXScreen(Screen) + NavigationMixin
├── base_modal.py        # BaseAgentXModalScreen[T](ModalScreen[T], BaseAgentXScreen)
├── base_app.py          # BaseAgentXApp(App)
├── base_adapter.py      # BaseScreenAdapter
└── widgets.py           # SessionStatusBar, WelcomePanel, MenuGrid, CommandInput, ChatMessage
```

| File | Layer | Responsibility |
|------|-------|----------------|
| `framework/partner.py` | View | `register_partner(abc, screen_cls)` — wraps `abc.register()` for the Textual/ABCMeta conflict. |
| `framework/base_screen.py` | View | `BaseAgentXScreen`: controller storage, `set_controller`, `action_quit`/`action_back`, `compose_chrome`, `safe_notify`/`safe_update`/`safe_log`, `handle_input_submitted` hook. `NavigationMixin`: `navigate_to_child`. |
| `framework/base_modal.py` | View | `BaseAgentXModalScreen[T]`: `dismissed` guard + `safe_dismiss(value)`. |
| `framework/base_app.py` | View | `BaseAgentXApp`: TTY check, `make_initial_screen()` hook, default CSS. |
| `framework/base_adapter.py` | View | `BaseScreenAdapter`: `controller`, `_screen`, `set_screen`, no-op `show`. |
| `framework/widgets.py` | View | Reusable widgets extracted from screen files. |

## 3. Detailed class designs

### 3.1 `partner.py`

```python
def register_partner(abc_cls: type, screen_cls: type) -> None:
    """Register screen_cls as a virtual subclass of abc_cls (ABC).

    Works around the metaclass conflict between Textual's _MessagePumpMeta and
    abc.ABCMeta — Textual screens cannot inherit ABC, so they register virtually.
    Idempotent: re-registering is a no-op.
    """
    if not issubclass(screen_cls, abc_cls):   # virtual check
        abc_cls.register(screen_cls)
```

### 3.2 `base_screen.py`

```python
from typing import Any, Callable, ClassVar
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input

class NavigationMixin:
    """Provides navigate_to_child() to any Screen subclass."""

    def navigate_to_child(
        self,
        screen_cls: type,
        controller: Any | None = None,
        *,
        adapter_view: Any | None = None,
        setup: Callable[[Any], None] | None = None,
        getter: Callable[[Any], Any] | None = None,
    ) -> None:
        """Push a child screen, optionally wiring an adapter.

        setup:    called with self._controller first (e.g. controller.show_chat)
        getter:   called with self._controller to obtain (child_controller[, view])
        adapter_view: if given AND isinstance(adapter_view, BaseScreenAdapter),
                  call adapter_view.set_screen(screen) before push.
        All steps are wrapped in safe error handling (one safe_notify on failure).
        """
        ...


class BaseAgentXScreen(Screen, NavigationMixin):
    """Base for all AgentX full (non-modal) TUI screens.

    Absorbs: controller storage, quit/back, chrome compose, safe notify/update/log,
    input-submission boilerplate.
    """

    BINDINGS: ClassVar[list] = []  # subclasses extend

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__()
        self._controller: Any | None = controller

    # --- controller wiring ---
    def set_controller(self, controller: Any) -> None:
        self._controller = controller

    # --- standard actions (overridable) ---
    def action_quit(self) -> None:
        self.app.exit()

    def action_back(self) -> None:
        try:
            self.app.pop_screen()
        except Exception:
            pass

    # --- chrome helper ---
    def compose_chrome(self, *, show_clock: bool = True, footer: bool = True) -> ComposeResult:
        """Yield Header(+Footer). Call inside a subclass compose()."""
        yield Header(show_clock=show_clock)
        if footer:
            yield Footer()

    # --- safe UI helpers (never crash without app context / before mount) ---
    def safe_notify(self, message: str, severity: str = "information",
                    timeout: float | None = 3) -> None:
        try:
            self.notify(message, severity=severity, timeout=timeout)
        except Exception:
            pass

    def safe_error(self, message: str) -> None:
        self.safe_notify(message, severity="error", timeout=None)

    def safe_update(self, widget_id: str, text: str, widget_cls: type = Static) -> bool:
        """Update a widget by id. Returns True on success."""
        try:
            self.query_one(f"#{widget_id}", widget_cls).update(text)
            return True
        except Exception:
            return False

    def safe_log(self, widget_id: str, message: str) -> None:
        """Append a line to a RichLog widget by id."""
        try:
            self.query_one(f"#{widget_id}", RichLog).write(message)
        except Exception:
            pass

    # --- input hook (template method) ---
    def handle_input_submitted(self, value: str, input_widget: Input) -> bool:
        """Shared input handling. Returns True if value was non-empty (and input cleared).

        Subclasses call this from on_input_submitted, then dispatch.
        """
        text = value.strip()
        if not text:
            return False
        input_widget.value = ""
        return True
```

### 3.3 `base_modal.py`

```python
from typing import Generic, TypeVar
from textual.screen import ModalScreen
from agentx.ui.tui.framework.base_screen import BaseAgentXScreen

T = TypeVar("T")

class BaseAgentXModalScreen(ModalScreen[T], BaseAgentXScreen):
    """Base for modal dialogs: centered-box + dismiss-guard pattern.

    Subclasses MUST call safe_dismiss() instead of dismiss() to be double-dismiss-safe.
    NOTE: RunningModal keeps its worker/queue/poll logic intact; only the skeleton
    (init, dismissed guard) is inherited.
    """

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__(controller)
        self._dismissed: bool = False

    def safe_dismiss(self, value: Any) -> None:
        """Dismiss exactly once."""
        if self._dismissed:
            return
        self._dismissed = True
        self.dismiss(value)
```

> **MRO note:** `ModalScreen[T]` and `BaseAgentXScreen(Screen)` share `Screen`,
> so the cooperative MRO is `BaseAgentXModalScreen → ModalScreen →
> BaseAgentXScreen → Screen → ...`. `__init__` calls `super().__init__(controller)`
> which chains correctly because `BaseAgentXScreen.__init__` calls
> `super().__init__()` (Screen). Verified: Textual `Screen.__init__` takes no
> required args.

### 3.4 `base_app.py`

```python
import sys
from textual.app import App
from textual.screen import Screen

class BaseAgentXApp(App):
    """Base TUI app: TTY detection + initial-screen push + default CSS."""

    CSS = """
    Screen { background: $surface; }
    Header { background: $primary; color: white; }
    Footer { dock: bottom; }
    """

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__()
        self._controller: Any | None = controller

    def make_initial_screen(self) -> Screen:
        """Override hook: return the first screen to push. Abstract by convention."""
        raise NotImplementedError

    def on_mount(self) -> None:
        if not sys.stdin.isatty():
            self.notify("⚠️ Non-TTY environment. Keyboard input may not work.",
                        severity="warning", timeout=10)
        self.push_screen(self.make_initial_screen())
```

### 3.5 `base_adapter.py`

```python
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from textual.screen import Screen

class BaseScreenAdapter:
    """Base for TUI adapters that delegate to a pushed Screen.

    Concrete adapters implement an IXxxView by delegating to self._screen,
    guarding each call with `if self._screen:`.
    """

    def __init__(self, controller: Any) -> None:
        self._controller: Any = controller
        self._screen: "Screen | None" = None

    def set_screen(self, screen: "Screen") -> None:
        self._screen = screen

    def show(self) -> None:
        """No-op: the screen is already pushed by the host screen."""
        pass
```

### 3.6 `widgets.py`

Extract these classes verbatim (with their `DEFAULT_CSS`) from their current
locations into `framework/widgets.py`, then import them back where used:

- `SessionStatusBar(Static)` ← from `main_screen.py`
- `WelcomePanel(Static)` ← from `main_screen.py`
- `MenuGrid(Grid)` ← from `main_screen.py`
- `CommandInput(Vertical)` ← from `main_screen.py`
- `ChatMessage(Static)` ← from `chat_screen.py`

No API change — only file location. CSS stays class-scoped (`DEFAULT_CSS`), so no
collision.

### 3.7 `__init__.py` (public API)

```python
from agentx.ui.tui.framework.partner import register_partner
from agentx.ui.tui.framework.base_screen import BaseAgentXScreen, NavigationMixin
from agentx.ui.tui.framework.base_modal import BaseAgentXModalScreen
from agentx.ui.tui.framework.base_app import BaseAgentXApp
from agentx.ui.tui.framework.base_adapter import BaseScreenAdapter
from agentx.ui.tui.framework.widgets import (
    SessionStatusBar, WelcomePanel, MenuGrid, CommandInput, ChatMessage,
)

__all__ = [
    "register_partner", "BaseAgentXScreen", "NavigationMixin",
    "BaseAgentXModalScreen", "BaseAgentXApp", "BaseScreenAdapter",
    "SessionStatusBar", "WelcomePanel", "MenuGrid", "CommandInput", "ChatMessage",
]
```

## 4. Refactor mapping (before → after)

| Existing code | After |
|---|---|
| `def __init__(self, controller=None): super().__init__(); self._controller = controller` | deleted — inherited |
| `def action_quit(self): self.app.exit()` | deleted — inherited (override only if custom) |
| `def action_back(self): self.app.pop_screen()` | deleted — inherited |
| `try: self.notify(...)\nexcept Exception: pass` | `self.safe_notify(...)` |
| `try: self.query_one("#x", Static).update(...)\nexcept Exception: pass` | `self.safe_update("x", ...)` |
| `try: self.query_one("#x-log", RichLog).write(...)\nexcept Exception: pass` | `self.safe_log("x-log", ...)` |
| 4× navigation glue in `MainTUIScreen` | 4× `self.navigate_to_child(...)` |
| adapter `__init__`/`set_screen`/`show` | inherited from `BaseScreenAdapter` |
| `IAgentViewPartner.register(AgentTUIScreen)` | `register_partner(IAgentViewPartner, AgentTUIScreen)` |
| `yield Header(show_clock=True) ... yield Footer()` | `yield from self.compose_chrome()` (when contiguous) |

### `MainTUIScreen.action_open_chat` before (~30 LOC) → after

```python
def action_open_chat(self) -> None:
    self.navigate_to_child(
        ChatTUIScreen,
        controller=self._controller,
        setup=lambda c: c.show_chat(),
        getter=lambda c: c.get_chat_controller() if hasattr(c, "get_chat_controller") else (None, None),
        adapter_view=None,  # set below: needs the view from getter
    )
```
(The chat/rag variant needs the adapter-view from the getter's second return;
`navigate_to_child`'s `getter` may return `(controller, view)` and the helper
auto-wires `view.set_screen(screen)` when `view` is a `BaseScreenAdapter`. So the
call collapses to one `navigate_to_child` with `getter=get_chat_controller`.)

## 5. Functional flow (sequence)

### 5.1 Building a new screen (UC-1)

```
Developer: class MyScreen(BaseAgentXScreen):
Developer:   def compose(self): yield from self.compose_chrome(); yield ...
User mounts screen → BaseAgentXScreen.__init__ stores controller
  → Textual calls compose() → developer widgets + compose_chrome() Header/Footer
User presses 'q' → BaseAgentXScreen.action_quit → app.exit()
User presses 'escape' → BaseAgentXScreen.action_back → app.pop_screen()
Screen calls safe_notify → BaseAgentXScreen.safe_notify → try notify / except pass
```

### 5.2 Navigation (UC-2) — `navigate_to_child`

```
HostScreen.navigate_to_child(ScreenCls, controller, setup=fn, getter=fn, adapter_view=av):
  1. if setup and controller: try setup(controller) except E: safe_error(E); return
  2. child = None; view = None
     if getter and controller: 
        res = getter(controller); unpack (child[, view]) 
  3. if app context: screen = ScreenCls(child)
     if view isinstance BaseScreenAdapter: view.set_screen(screen)
     app.push_screen(screen)
     else if no app: safe_notify("no app context")
  except E: safe_error(E)
```

### 5.3 Modal dismiss (UC-1 modal) — `safe_dismiss`

```
User clicks button → MyModal.action_xxx → self.safe_dismiss(value)
  → if self._dismissed: return (guard)
  → self._dismissed = True; self.dismiss(value)
Host callback fires once with value.
```

### 5.4 Regression flow (UC-5) — unchanged

```
User 'c' → MainTUIScreen.action_open_chat → navigate_to_child(ChatTUIScreen, ...)
  → controller.show_chat() → ChatController + TUIChatAdapter created
  → getter returns (chat_controller, chat_view)
  → ChatTUIScreen(chat_controller) pushed; chat_view.set_screen(screen)
  → user types → on_input_submitted → handle_input_submitted + process_user_message
  → 'escape' → action_back (inherited) → pop_screen → back to Main
```

## 6. MVC++ self-check

- [x] Framework classes import **no** `agentx.model.*` and **no** concrete controller.
      Controllers are duck-typed `Any`. (View-only)
- [x] Adapters still implement `IMainView`/`IChatView`/`IRagView` (interfaces unchanged).
- [x] No SQL anywhere in the framework (View layer).
- [x] No `*Controller` under `model/` (no model change).
- [x] `register_partner` keeps the ABC pattern without forcing screens to inherit ABC.
- [x] `uv run scripts/omt/mvc_check.py src/agentx/ui/tui` will be run after each edit.

## 7. Threading-safety note (fast-agent freeze-fix preservation)

`RunningModal` (feature_011) runs `run_cycle()` on a daemon worker thread,
communicating via `queue.Queue` + `threading.Event`, polled by `set_timer`. The
refactor **only** lifts its `__init__` controller-storage and adds
`safe_dismiss`/`_dismissed` (it already had `_dismissed`). The worker loop,
`_poll`, `_on_reflection`, `action_pause_resume`, `action_stop` stay **verbatim**
in `RunningModal`. The freeze-fix regression tests
(`TestRunningModalFreezeFix`) must stay green.

## 8. Backward compatibility

- Public symbols `TUIApplication`, `TUIProvider`, `TUIAdapter`, `TUIChatAdapter`,
  `TUIRagAdapter`, `MainTUIScreen`, `ChatTUIScreen`, `RagTUIScreen`,
  `AgentTUIScreen`, `AgentDemoScreen`, `FastAgentTUIScreen`, `GoalModal`,
  `RunningModal`, `ReflectionModal`, `ResultModal` keep their names + constructors.
- `IAgentViewPartner.register(...)` calls are replaced by `register_partner(...)`
  but the virtual-subclass relationship is identical.
- Widget classes (`SessionStatusBar`, etc.) keep their names + CSS; only their
  import path changes from `main_screen`/`chat_screen` to `framework.widgets`.

# Analysis 001 — TUI Framework: Overview & Current-State

> **Phase:** Analysis — `omt_agent_guide.md §2, §4` | **Feature:** feature_012.tui_framework
> **Task type:** major_feature

## 1. Problem statement

AgentX has a working Textual-based TUI, but its implementation is **spread across
two locations** with heavy copy-paste duplication and no shared base classes:

- `src/agentx/ui/tui/` — `app.py`, `provider.py`, `adapters/` (3), `screens/` (4 files)
- `src/agentx/agent/view/tui/` — `agent_screen.py`, `demo_screen.py`,
  `fast_agent_screen.py`, `fast_agent_modals.py`, `fast_agent_view.py`

Adding a new TUI screen today means re-implementing the same boilerplate from
scratch (init/controller wiring, Header/Footer compose, quit/back actions,
defensive notify, navigation glue). There is **no library layer** a new screen or
a new TUI variant can inherit from. The request is to extract that library:
*"a module that contains base classes of the current implementation of tui, that
allow the reuse of tui views, with base classes, in order to facilitate new TUI
implementations, centralizing the implementation, improving the reuse of views.
like a library for agentx tui development."*

## 2. Scope (what "done" looks like)

A reusable base-class library under `src/agentx/ui/tui/framework/` plus a
refactor of the **9 existing TUI screens/adapters** to inherit from it, with
**zero regressions** in the existing 516-test suite (1 pre-existing failure
allowed) and MVC++ 0/0.

## 3. Current-state analysis — duplication inventory

Every finding below is copy-pasted across multiple files. Each is a candidate
for a base class / shared helper.

### 3.1 Screen `__init__` + controller storage (9 screens)

Every screen stores an optional controller the same way:

```python
def __init__(self, controller: Any | None = None) -> None:
    super().__init__()
    self._controller = controller
```

Found in: `MainTUIScreen`, `ChatTUIScreen`, `RagTUIScreen`, `AgentTUIScreen`,
`AgentDemoScreen`, `FastAgentTUIScreen`, `GoalModal`, `RunningModal`,
`ReflectionModal`, `ResultModal`. `AgentTUIScreen`/`AgentDemoScreen` even add a
`set_controller()` for late wiring.

### 3.2 Quit / Back actions (9 screens)

Identical pair repeated everywhere:

```python
def action_quit(self) -> None:
    self.app.exit()

def action_back(self) -> None:
    self.app.pop_screen()
```

`AgentDemoScreen.action_back` wraps `pop_screen()` in try/except; others don't.
Inconsistent.

### 3.3 Header + Footer compose (every Screen, not ModalScreen)

```python
yield Header(show_clock=True)   # or Header()
...
yield Footer()
```

Modal screens (`GoalModal`, `RunningModal`, …) skip Footer and use a centered
`Vertical` box — a second recurring layout.

### 3.4 Defensive `try/except` around `self.notify(...)` (~25 sites)

Because `notify()` crashes when no app context is active (e.g. unit tests that
construct a screen without running the app), every screen wraps it:

```python
try:
    self.notify(msg, severity="error", timeout=None)
except Exception:
    pass
```

This appears ~25 times across `main_screen.py`, `rag_screen.py`,
`agent_screen.py`, `demo_screen.py`, `fast_agent_modals.py`. It is noise that
hides real bugs and bloats every action method.

### 3.5 Defensive `try/except` around `query_one(...).update(...)` (~10 sites)

Same pattern for widget updates that may run before mount:

```python
try:
    self.query_one("#status", Static).update(...)
except Exception:
    pass
```

### 3.6 Navigation glue in `MainTUIScreen` (4 copies)

`action_open_chat`, `action_open_rag`, `action_open_agent`,
`action_open_fast_agent` are structurally identical:

```python
if self._controller:
    try:
        self._controller.show_X()                      # set up triad
    except Exception as e:
        try: self.notify(...)
        except Exception: pass
X_controller = None
X_view = None
if self._controller and hasattr(self._controller, 'get_X_controller'):
    X_controller, X_view = self._controller.get_X_controller()
try:
    from agentx.ui.tui.screens.X_screen import XTUIScreen
    from agentx.ui.tui.adapters.X_adapter import TUIXAdapter
    if hasattr(self, 'app') and self.app is not None:
        screen = XTUIScreen(X_controller)
        if X_view and isinstance(X_view, TUIXAdapter):
            X_view.set_screen(screen)
        self.app.push_screen(screen)
except Exception as e:
    try: self.notify(...)
    except Exception: pass
```

~60 lines of near-identical boilerplate. The two variants (chat/rag use the
adapter+set_screen dance; agent/fast_agent skip it) should collapse to one
configurable helper.

### 3.7 Adapter trio (3 adapters, identical skeleton)

`TUIAdapter`, `TUIChatAdapter`, `TUIRagAdapter` all share:

```python
def __init__(self, controller) -> None:
    self._controller = controller
    self._screen = None

def set_screen(self, screen) -> None:
    self._screen = screen

def show(self) -> None:        # no-op — screen already pushed
    pass
# ... delegating methods each guarded by `if self._screen:`
```

Only the delegated method set differs (dictated by the `IXxxView` interface each
implements). A `BaseScreenAdapter` removes the repeated skeleton.

### 3.8 Reusable widgets embedded in screen files (not importable)

`SessionStatusBar`, `WelcomePanel`, `MenuGrid`, `CommandInput` live inside
`main_screen.py`; `ChatMessage` lives inside `chat_screen.py`. They cannot be
reused by another screen or TUI variant without copy-paste.

### 3.9 `IXxxViewPartner.register(Screen)` metaclass hack (2 sites)

```python
IAgentViewPartner.register(AgentTUIScreen)
IAgentViewPartner.register(AgentDemoScreen)
```

Textual's `_MessagePumpMeta` conflicts with `abc.ABCMeta`, so screens can't
inherit `ABC`. The virtual-subclass registration is copy-pasted and easy to
forget. The framework should provide a helper.

### 3.10 `on_input_submitted` boilerplate (5 screens)

`MainTUIScreen`, `ChatTUIScreen`, `RagTUIScreen`, `AgentTUIScreen`,
`AgentDemoScreen`(via run) all: read `event.value`, strip, early-return on
empty, clear `event.input.value`, dispatch to controller. Only the dispatch
target differs.

### 3.11 `_log(message)` helper (2 screens, identical)

`AgentTUIScreen._log` and `AgentDemoScreen._log` are byte-for-byte identical:

```python
def _log(self, message: str) -> None:
    try:
        self.query_one("#X-log", RichLog).write(message)
    except Exception:
        pass
```

### 3.12 TTY-detection + initial-screen push (1 site, but app-coupled)

`TUIApplication.on_mount` does `sys.stdin.isatty()` check + `push_screen(...)`.
Worth promoting into a base app with an overridable "initial screen factory".

## 4. Quantified duplication

| Pattern | Sites | Approx LOC duplicated |
|---|---|---|
| `__init__` + controller storage | 10 | 30 |
| `action_quit` / `action_back` | 9 | 36 |
| Header/Footer compose | 6 | 12 |
| defensive `notify` try/except | ~25 | 100 |
| defensive `query_one` try/except | ~10 | 40 |
| MainTUIScreen navigation glue | 4 | 240 |
| adapter skeleton | 3 | 60 |
| embedded reusable widgets | 5 | 220 |
| metaclass `register` hack | 2 | 4 |
| `on_input_submitted` boilerplate | 5 | 75 |
| `_log` helper | 2 | 12 |
| **Total** | **~80** | **~830 LOC** |

Roughly **~830 LOC** of the current TUI is duplicated boilerplate that a base
library can absorb.

## 5. Goals of the framework (derived from analysis)

1. **One base screen** absorbing init/controller storage, quit/back, Header/Footer
   compose, safe-notify, safe-widget-update, input-submission boilerplate.
2. **One base modal screen** for the centered-box layout + dismiss-guard pattern.
3. **One base app** absorbing TTY detection + initial-screen push + default CSS.
4. **One base adapter** absorbing the controller/screen/delegate skeleton.
5. **A navigation helper** collapsing the 4 navigation-glue copies into one
   parameterised call.
6. **A reusable widgets package** (`SessionStatusBar`, `WelcomePanel`,
   `MenuGrid`, `CommandInput`, `ChatMessage`) importable by any screen.
7. **A metaclass-safe partner-registration helper** so screens register against
   an ABC partner without copy-paste.
8. **Refactor** the 9 existing screens/adapters to inherit from the above,
   proving reuse and removing ~830 LOC of duplication.

## 6. Non-goals

- No new screens, no new features, no controller/model changes.
- No change to the public `IUIProvider` / `IMainView` / `IChatView` / `IRagView`
  interfaces (the adapters still implement them).
- No change to Textual version or dependencies.

## 7. Risk assessment

| Risk | Level | Mitigation |
|---|---|---|
| Refactor breaks the 516-test suite | High | Run full suite after each screen refactor; MVC++ check after each edit. |
| Textual metaclass conflict resurfaces | Medium | Keep the `register()` helper; verify `AgentTUIScreen`/`AgentDemoScreen` still register against `IAgentViewPartner`. |
| Fast-agent threading freeze regresses | High | Do **not** move `RunningModal` worker/queue logic into the base; only its skeleton (init/dismiss-guard) is lifted. Keep freeze-fix tests green. |
| CSS regressions from extracting widgets | Medium | Keep `DEFAULT_CSS` on each widget class (Textual scopes CSS by class name). |
| MVC++ View↔Model leak introduced | Low | Framework is View-only; `mvc_check.py` after each edit. |

## 8. Feasibility statement

- **Phase:** Analysis → Design (clear feature, major size).
- **Files affected:** new `src/agentx/ui/tui/framework/` package (≈7 files); edit
  9 existing screen/adapter files + `app.py` + `provider.py`.
- **Risk:** High (touches working TUI + fast-agent threading) — mitigated by the
  existing test suite and incremental refactor.
- **Effort estimate:** Design ~30 min, Implementation ~90 min, Testing ~45 min.

"""Base classes for AgentX TUI full (non-modal) screens.

This module absorbs the boilerplate duplicated across every existing TUI screen
(``__init__`` controller storage, ``action_quit``/``action_back``, Header/Footer
compose, defensive ``notify``/``query_one`` wrappers, input-submission
template) into :class:`BaseAgentXScreen`, and provides :class:`NavigationMixin`
which collapses the navigation glue repeated 4× in ``MainTUIScreen``.

Design: ``design_001_tui_framework.md`` §3.2, §4, §5.
Operation spec: ``operation_spec_001_tui_framework.md`` O1–O8, O11.

MVC++: pure View — no ``agentx.model.*`` import, controllers duck-typed ``Any``.
"""

from __future__ import annotations

from typing import Any, Callable, Literal

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, RichLog, Static

# Textual's notify() accepts a literal severity.  We type the parameter as a
# Literal so the call site type-checks, while still accepting plain strings at
# runtime (Textual tolerates them).
SeverityLevel = Literal["information", "warning", "error"]


class NavigationMixin:
    """Mixin providing :meth:`navigate_to_child` to any ``Screen`` subclass.

    Centralises the 4 navigation-glue copies in ``MainTUIScreen``
    (chat/rag/agent/fast-agent): ``controller.show_X()`` → ``get_X_controller()``
    → construct screen → wire adapter → ``push_screen``, all with centralised
    error handling.
    """

    def navigate_to_child(  # noqa: C901 — readable as one flow
        self,
        screen_cls: type,
        controller: Any | None = None,
        *,
        adapter_view: Any | None = None,
        setup: Callable[[Any], None] | None = None,
        getter: Callable[[Any], Any] | None = None,
    ) -> None:
        """Push a child ``screen_cls`` screen, optionally wiring an adapter.

        Args:
            screen_cls:   The child ``Screen`` subclass to construct + push.
            controller:   The host controller (stored as ``self._controller``
                          if ``None``, this method reads ``self._controller``).
            adapter_view: Optional pre-existing adapter view.  If it is a
                          :class:`BaseScreenAdapter`, ``set_screen`` is called
                          automatically.  (Use this OR let ``getter`` return one.)
            setup:        Optional callback run with the controller first
                          (e.g. ``lambda c: c.show_chat()``).
            getter:       Optional callback run with the controller to obtain
                          the child controller.  May return either
                          ``child_controller`` or ``(child_controller, view)``;
                          if a ``view`` is returned and is a
                          ``BaseScreenAdapter``, it is wired via ``set_screen``.

        All steps are wrapped so the host screen never crashes on a navigation
        error — a single ``safe_error`` notification is shown instead.
        """
        host_controller = controller if controller is not None else getattr(
            self, "_controller", None
        )

        # 1. setup callback (e.g. controller.show_chat())
        if setup is not None and host_controller is not None:
            try:
                setup(host_controller)
            except Exception as exc:  # noqa: BLE001 — never crash on nav
                _safe_error(self, f"Controller error: {exc}")
                return

        # 2. getter → child controller (+ optional view)
        child_controller: Any | None = None
        view: Any | None = adapter_view
        if getter is not None and host_controller is not None:
            try:
                result = getter(host_controller)
            except Exception as exc:  # noqa: BLE001
                _safe_error(self, f"Controller error: {exc}")
                return
            if isinstance(result, tuple):
                # (controller[, view])
                child_controller = result[0] if len(result) > 0 else None
                if len(result) > 1 and result[1] is not None:
                    view = result[1]
            else:
                child_controller = result

        # 3. construct + wire + push
        try:
            app = getattr(self, "app", None)
            if app is None:
                _safe_notify(self, "No app context — cannot navigate.")
                return
            screen = screen_cls(child_controller)
            # Wire the adapter view (either the one passed in or the one from getter).
            from agentx.ui.tui.framework.base_adapter import BaseScreenAdapter

            if view is not None and isinstance(view, BaseScreenAdapter):
                view.set_screen(screen)
            app.push_screen(screen)
        except Exception as exc:  # noqa: BLE001 — never crash on nav
            _safe_error(self, f"Error opening {screen_cls.__name__}: {exc}")


class BaseAgentXScreen(Screen, NavigationMixin):
    """Base for all AgentX full (non-modal) TUI screens.

    Absorbs the boilerplate duplicated across every existing screen:
      - controller storage (``__init__(controller=None)``) + ``set_controller``
      - standard ``action_quit`` / ``action_back``
      - ``compose_chrome`` (Header/Footer) helper
      - ``safe_notify`` / ``safe_error`` / ``safe_update`` / ``safe_log``
      - ``handle_input_submitted`` template hook
      - ``navigate_to_child`` (via :class:`NavigationMixin`)

    Subclasses typically only implement ``compose()`` (calling
    ``compose_chrome``) and their screen-specific input/command handlers.
    """

    # Subclasses extend BINDINGS; the base provides none so existing bindings
    # are preserved exactly.
    BINDINGS: list = []

    def __init__(self, controller: Any | None = None) -> None:
        """Construct the screen and store the optional controller.

        Args:
            controller: Optional controller (duck-typed; the View never imports
                        a concrete controller class).
        """
        super().__init__()
        # Duck-typed ``Any`` (mirrors the codebase convention) so subclasses can
        # call controller methods without per-access None-narrowing.
        self._controller: Any = controller
        # Active blocking-task handles (feature_014).  Each entry is a
        # :class:`~agentx.ui.tui.framework.async_runner.TaskHandle` returned by
        # :meth:`run_blocking`.  All are cancelled on unmount so no callback
        # fires on a gone screen and no zombie thread lingers.
        self._task_handles: list[Any] = []

    # ----------------------------------------------------------- controller wiring

    def set_controller(self, controller: Any) -> None:
        """Late-bind or replace the controller after construction."""
        self._controller = controller

    # ----------------------------------------------------------- standard actions

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_back(self) -> None:
        """Pop back to the previous screen (no-op if the stack is empty)."""
        try:
            self.app.pop_screen()
        except Exception:
            pass

    # ----------------------------------------------------------- chrome helper

    def compose_chrome(
        self, *, show_clock: bool = True, footer: bool = True
    ) -> ComposeResult:
        """Yield ``Header`` (+ optional ``Footer``) for a subclass ``compose()``.

        Args:
            show_clock: pass to ``Header(show_clock=...)``.
            footer:     if ``True`` (default), also yield a ``Footer``.
        """
        yield Header(show_clock=show_clock)
        if footer:
            yield Footer()

    # ----------------------------------------------------------- safe UI helpers

    def safe_notify(
        self,
        message: str,
        severity: SeverityLevel = "information",
        timeout: float | None = 3,
    ) -> None:
        """Show a Textual notification without crashing when no app context is active.

        Textual's ``notify`` raises if the screen is not mounted / has no app
        context (common in unit tests).  This wrapper swallows that so action
        methods stay readable.
        """
        try:
            self.notify(message, severity=severity, timeout=timeout)
        except Exception:
            pass

    def safe_error(self, message: str) -> None:
        """Show an error notification (no timeout) without crashing."""
        self.safe_notify(message, severity="error", timeout=None)

    def safe_update(
        self, widget_id: str, text: str, widget_cls: type = Static
    ) -> bool:
        """Update a widget's content by id; never crash if not mounted.

        Returns:
            ``True`` if the widget was found and updated, ``False`` otherwise.
        """
        try:
            self.query_one(f"#{widget_id}", widget_cls).update(text)
            return True
        except Exception:
            return False

    def safe_log(self, widget_id: str, message: str) -> None:
        """Append a line to a ``RichLog`` widget by id; never crash."""
        try:
            self.query_one(f"#{widget_id}", RichLog).write(message)
        except Exception:
            pass

    # ----------------------------------------------------------- input hook

    def handle_input_submitted(self, value: str, input_widget: Input) -> bool:
        """Shared input-submission template.

        Strips ``value``; rejects empty input (returns ``False``); otherwise
        clears ``input_widget`` and returns ``True`` so the caller can dispatch.

        Args:
            value:         the raw input value.
            input_widget:  the ``Input`` widget to clear.

        Returns:
            ``True`` if the value was non-empty (and input cleared),
            ``False`` if it was blank (input left untouched).
        """
        text = value.strip()
        if not text:
            return False
        input_widget.value = ""
        return True

    # ----------------------------------------------------------- non-blocking work

    def run_blocking(
        self,
        func: Callable[[], Any],
        *,
        on_result: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> Any:
        """Run a blocking callable on a daemon worker thread (feature_014).

        The UI thread stays free — timers fire, keys are accepted, Stop/Escape
        work mid-call.  When ``func`` returns (or raises), ``on_result`` (or
        ``on_error``) is invoked **on the UI thread** (safe to touch widgets).

        This is the framework-level fix for the agent-screen freeze: calling
        ``controller.run_cycle()`` synchronously on the UI thread blocks on
        ``llm.invoke()`` (a 1–30s HTTP call), freezing the entire TUI.  Routing
        it through ``run_blocking`` moves the blocking call to a worker thread.

        Args:
            func:       The blocking callable (takes no args, returns ``Any``).
            on_result:  Callback invoked on the UI thread with the return value.
                        May be ``None`` (result silently discarded).
            on_error:   Callback invoked on the UI thread with the exception.
                        May be ``None`` (error silently discarded).

        Returns:
            A :class:`~agentx.ui.tui.framework.async_runner.TaskHandle` with
            ``cancel()`` and ``is_done``.  The handle is tracked internally and
            cancelled automatically on unmount.

        Operation spec: ``operation_spec_001_nonblocking_runner.md`` O1.
        """
        from agentx.ui.tui.framework.async_runner import (
            BlockingTaskRunner,
            TaskHandle,
        )

        runner = BlockingTaskRunner(func, on_result, on_error, screen=self)
        handle = TaskHandle(runner)
        self._task_handles.append(handle)
        runner.start()
        return handle

    def on_unmount(self) -> None:
        """Cancel all active blocking tasks when the screen is popped.

        Ensures no callback fires on the now-unmounted screen (which would
        crash — no widget context) and no zombie worker thread lingers.  Each
        handle's stop event is set and its runner is marked unmounted so the
        poller exits without invoking callbacks.

        Subclasses that override ``on_unmount`` MUST call ``super().on_unmount()``
        first (or cancel their own handles manually).

        Operation spec: ``operation_spec_001_nonblocking_runner.md`` O4.
        """
        for handle in self._task_handles:
            try:
                handle._runner._unmounted = True  # type: ignore[attr-defined]
                handle.cancel()
            except Exception:  # noqa: BLE001 — never crash on cleanup
                pass
        self._task_handles.clear()


# ---------------------------------------------------------------------------
# Module-level helpers used by NavigationMixin (kept here so the mixin can call
# them on ``self`` without forcing every screen to inherit the full base — e.g.
# a plain ``Screen`` that only mixes in ``NavigationMixin``).
# ---------------------------------------------------------------------------


def _safe_notify(screen: Any, message: str, **kwargs: Any) -> None:
    try:
        screen.notify(message, **kwargs)
    except Exception:
        pass


def _safe_error(screen: Any, message: str) -> None:
    _safe_notify(screen, message, severity="error", timeout=None)

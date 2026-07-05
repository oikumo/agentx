"""Base class for AgentX TUI modal dialogs.

Modal dialogs (``GoalModal``, ``RunningModal``, ``ReflectionModal``,
``ResultModal``) share two things with full screens — controller storage and the
safe-UI helpers — plus a dismiss-guard pattern (dismiss exactly once).  This
module provides :class:`BaseAgentXModalScreen` to absorb that.

Design: ``design_001_tui_framework.md`` §3.3, §7.
Operation spec: ``operation_spec_001_tui_framework.md`` O9.

MVC++: pure View — no Model import.

Threading note: ``RunningModal`` (feature_011) keeps its daemon worker thread +
``queue.Queue`` + ``threading.Event`` + ``set_timer`` poll loop **verbatim**.
Only the skeleton (``__init__`` controller storage + the ``_dismissed`` guard)
is lifted here; the freeze-fix logic is untouched.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from textual.screen import ModalScreen

from agentx.ui.tui.framework.base_screen import BaseAgentXScreen

T = TypeVar("T")


class BaseAgentXModalScreen(BaseAgentXScreen, ModalScreen[T], Generic[T]):
    """Base for AgentX modal dialogs: controller storage + dismiss guard.

    Inherits :class:`BaseAgentXScreen` (so it gets ``set_controller``,
    ``safe_notify``/``safe_update``/``safe_log``, ``handle_input_submitted``,
    ``navigate_to_child``, ``action_quit``/``action_back``) **and** Textual's
    :class:`~textual.screen.ModalScreen` (so it gets ``dismiss`` + modal
    message-pump behaviour).

    Base ordering is ``(BaseAgentXScreen, ModalScreen)`` so cooperative
    ``super().__init__(controller)`` consumes ``controller`` in
    :meth:`BaseAgentXScreen.__init__` first, then chains to
    ``ModalScreen``→``Screen`` with no positional arg (Textual's
    ``Screen.__init__`` does not accept a controller).

    Subclasses **must** call :meth:`safe_dismiss` instead of ``dismiss`` to be
    double-dismiss-safe.
    """

    def __init__(self, controller: Any | None = None) -> None:
        """Construct a modal screen with a dismiss guard.

        Args:
            controller: Optional controller (duck-typed ``Any``).
        """
        super().__init__(controller)
        # Double-dismiss guard.  Subclasses use safe_dismiss() instead of dismiss().
        self._dismissed: bool = False

    def safe_dismiss(self, value: Any) -> None:
        """Dismiss the modal exactly once.

        Subsequent calls are no-ops.  Use this instead of ``self.dismiss(...)``
        so a worker thread / repeated button press cannot dismiss twice.

        Args:
            value: The dismiss value passed to the host's push-screen callback.
        """
        if self._dismissed:
            return
        self._dismissed = True
        self.dismiss(value)

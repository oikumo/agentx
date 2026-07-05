"""Base class for TUI screen adapters.

The existing adapters (``TUIAdapter``, ``TUIChatAdapter``, ``TUIRagAdapter``)
each implement an ``IXxxView`` interface by delegating to a ``Screen`` that the
host screen already pushed.  They all share the same skeleton: store the
controller, hold an optional screen reference, ``set_screen``, and a no-op
``show``.  :class:`BaseScreenAdapter` absorbs that skeleton.

Design: ``design_001_tui_framework.md`` §3.5.
Operation spec: ``operation_spec_001_tui_framework.md`` O13.

MVC++: pure View — no Model import.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.screen import Screen


class BaseScreenAdapter:
    """Base for TUI adapters that delegate to a pushed :class:`Screen`.

    Concrete adapters implement an ``IXxxView`` interface (e.g. ``IMainView``,
    ``IChatView``, ``IRagView``) by delegating to ``self._screen``, guarding
    each delegated call with ``if self._screen:``.

    The adapter does **not** push the screen itself — that is the host screen's
    job (via ``navigate_to_child`` or ``push_screen``).  ``show`` is therefore a
    no-op, matching the existing adapter behaviour.
    """

    def __init__(self, controller: Any) -> None:
        """Construct the adapter with its controller.

        Args:
            controller: The controller that owns this view (duck-typed ``Any``;
                        the View never imports a concrete controller class).
        """
        self._controller: Any = controller
        # Duck-typed: concrete adapters call screen-specific methods on this,
        # so it is typed ``Any`` (mirrors the duck-typed controller style).
        self._screen: Any = None

    def set_screen(self, screen: "Screen") -> None:
        """Set the ``Screen`` instance to delegate view calls to.

        Args:
            screen: The mounted ``Screen`` instance.
        """
        self._screen = screen

    def show(self) -> None:
        """Display the screen — no-op.

        The screen is already pushed by the host screen, so the adapter has
        nothing to do here.  Kept for ``IXxxView.show()`` interface compliance.
        """
        pass

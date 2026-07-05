"""Base class for AgentX TUI applications.

The existing :class:`TUIApplication` does two things on mount: a TTY check
(non-TTY warning) and pushing the initial screen.  :class:`BaseAgentXApp`
absorbs that, plus the default CSS, and exposes a ``make_initial_screen()``
override hook so a new TUI variant can plug in a different first screen without
rewriting the app.

Design: ``design_001_tui_framework.md`` §3.4.
Operation spec: ``operation_spec_001_tui_framework.md`` O12.

MVC++: pure View — no Model import.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from textual.app import App

if TYPE_CHECKING:
    from textual.screen import Screen


class BaseAgentXApp(App):
    """Base Textual application for AgentX TUI variants.

    Provides:
      - default CSS (Screen / Header / Footer base styles),
      - TTY detection on mount (non-TTY warning notification),
      - an overridable :meth:`make_initial_screen` hook pushed on mount.
    """

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: white;
    }

    Footer {
        dock: bottom;
    }
    """

    def __init__(self, controller: Any | None = None) -> None:
        """Construct the app, storing the optional controller.

        Args:
            controller: Optional controller (duck-typed ``Any``).  Stored so
                        :meth:`make_initial_screen` can pass it to the first screen.
        """
        super().__init__()
        self._controller: Any | None = controller

    def make_initial_screen(self) -> "Screen":
        """Return the first screen to push on mount.

        Subclasses **must** override this.  Raising ``NotImplementedError`` is
        the base behaviour so a misconfigured variant fails loudly on mount
        rather than silently showing a blank screen.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must override make_initial_screen()"
        )

    def on_mount(self) -> None:
        """Called when the app is mounted: TTY check + push initial screen."""
        # Non-TTY environments (CI, piped stdin) break keyboard input — warn.
        try:
            is_tty = sys.stdin.isatty()
        except Exception:
            is_tty = False
        if not is_tty:
            try:
                self.notify(
                    "⚠️  Non-TTY environment detected. Keyboard input may not work.\n"
                    "Run in a proper terminal for full interactivity.",
                    severity="warning",
                    timeout=10,
                )
            except Exception:
                pass

        # Push the initial screen (provided by the subclass).
        self.push_screen(self.make_initial_screen())

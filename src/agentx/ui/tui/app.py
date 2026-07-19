"""TUI Application — Base Textual app for AgentX.

Refactored (feature_012.tui_framework):
  - :class:`TUIApplication` now inherits :class:`BaseAgentXApp`, which absorbs
    the TTY check, the default CSS, and the on-mount screen push.  The app only
    overrides :meth:`make_initial_screen` to supply the full
    :class:`~agentx.ui.tui.screens.main_screen.MainTUIScreen`.
  - The minimal fallback :class:`MainTUIScreen` (kept here for app-infrastructure
    tests) now inherits :class:`BaseAgentXScreen`, dropping its duplicated
    ``__init__``/``action_quit`` boilerplate.

``sys`` is imported (and kept) so the test-suite can patch
``agentx.ui.tui.app.sys.stdin.isatty``; the inherited ``on_mount`` lives in
``base_app`` but reads the same shared ``sys.stdin``.
"""

from __future__ import annotations

import sys  # noqa: F401  — kept for test patching of sys.stdin.isatty
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label

from agentx.ui.tui.framework import BaseAgentXApp, BaseAgentXScreen

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner


class TUIApplication(BaseAgentXApp):
    """Main Textual application for AgentX.

    Inherits TTY detection, default CSS, and the on-mount initial-screen push
    from :class:`BaseAgentXApp`.  Only :meth:`make_initial_screen` is overridden
    to supply the full main screen.
    """

    def make_initial_screen(self):  # type: ignore[override]
        """Return the full MainTUIScreen (from ``screens.main_screen``)."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        return MainTUIScreen(self._controller)


class MainTUIScreen(BaseAgentXScreen):
    """Minimal main screen — a lightweight fallback used by app-infrastructure tests.

    The full main screen lives in ``agentx.ui.tui.screens.main_screen``; this
    minimal version is retained here so the app can be exercised without the
    full menu/command-input layout.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "open_chat", "Chat"),
        ("r", "open_rag", "RAG"),
    ]

    # __init__ and action_quit are inherited from BaseAgentXScreen.

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=True)
        yield Label("Welcome to AgentX TUI", id="welcome")
        yield Label("Press 'c' for Chat, 'r' for RAG, 'q' to quit", id="instructions")
        yield Footer()

    def action_open_chat(self) -> None:
        """Open chat screen (placeholder)."""
        self.safe_notify("Chat screen - coming soon!")

    def action_open_rag(self) -> None:
        """Open RAG screen (placeholder)."""
        self.safe_notify("RAG screen - coming soon!")
# TA: analysis: Need to implement dark mode / theme improvement for the TUI module. Textual has built-in dark themes (textual-dark is default). Need to add theme selection / dark mode toggle. Feature request mentions 'code main tui module interface improvement, set to dark mode' - so this is a UI improvement feature. Need to declare phase first via omt_phase.

"""TUI Application - Base Textual app for AgentX.

This is the main Textual application that hosts all screens.
It is completely isolated from the existing UI module.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner


class TUIApplication(App):
    """Main Textual application for AgentX.
    
    This application hosts all TUI screens and manages navigation.
    It is completely isolated from the existing console-based UI.
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

    def __init__(self, controller: IMainViewPartner | None = None) -> None:
        """Initialize TUI application.
        
        Args:
            controller: Optional main controller for command handling
        """
        super().__init__()
        self._controller = controller

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Check if running in a proper terminal
        if not sys.stdin.isatty():
            self.notify(
                "⚠️  Non-TTY environment detected. Keyboard input may not work.\n"
                "Run in a proper terminal for full interactivity.",
                severity="warning",
                timeout=10
            )
        
        # Push the main screen
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        self.push_screen(MainTUIScreen(self._controller))


class MainTUIScreen(Screen):
    """Main screen with welcome message and navigation.
    
    This is a minimal implementation to test the TUI infrastructure.
    Full implementation will include menu buttons and command input.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "open_chat", "Chat"),
        ("r", "open_rag", "RAG"),
    ]

    def __init__(self, controller: IMainViewPartner | None = None) -> None:
        """Initialize main screen.
        
        Args:
            controller: Optional main controller
        """
        super().__init__()
        self._controller = controller

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=True)
        yield Label("Welcome to AgentX TUI", id="welcome")
        yield Label("Press 'c' for Chat, 'r' for RAG, 'q' to quit", id="instructions")
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_open_chat(self) -> None:
        """Open chat screen."""
        # Placeholder - will navigate to chat screen
        self.notify("Chat screen - coming soon!", severity="information")

    def action_open_rag(self) -> None:
        """Open RAG screen."""
        # Placeholder - will navigate to RAG screen
        self.notify("RAG screen - coming soon!", severity="information")
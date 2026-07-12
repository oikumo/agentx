"""Reusable TUI widgets for AgentX.

These widgets were previously embedded inside individual screen files
(``SessionStatusBar``/``WelcomePanel``/``MenuGrid``/``CommandInput`` in
``main_screen.py``; ``ChatMessage`` in ``chat_screen.py``) and could not be
imported by other screens.  Centralising them here makes any screen — existing
or a new TUI variant — able to ``yield`` them directly.

Each widget keeps its own ``DEFAULT_CSS`` (Textual scopes CSS by class name), so
extraction causes no style collision.

Design: ``design_001_tui_framework.md`` §3.6.
Operation spec: ``operation_spec_001_tui_framework.md`` O14.

MVC++: pure View — no Model import.
"""

from __future__ import annotations

from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Button, Input, Label, Static


class SessionStatusBar(Static):
    """Status bar showing session context (session name · directory · screen)."""

    DEFAULT_CSS = """
    SessionStatusBar {
        dock: bottom;
        background: $primary-darken-2;
        color: white;
        padding: 0 2;
        height: 1;
    }

    SessionStatusBar #session-name {
        text-style: bold;
    }

    SessionStatusBar #directory {
        color: $text-muted;
    }

    SessionStatusBar #screen-name {
        text-style: italic;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.session_name = "default"
        self.working_directory = "/workspace"
        self.current_screen = "Main"

    def compose(self) -> ComposeResult:
        """Compose status bar content."""
        yield Static(
            f"Session: [#{self.session_name}] | Dir: {self.working_directory} | Screen: {self.current_screen}",
            id="status-text",
        )

    def update_context(
        self,
        session_name: str | None = None,
        directory: str | None = None,
        screen: str | None = None,
    ) -> None:
        """Update session context display."""
        if session_name:
            self.session_name = session_name
        if directory:
            self.working_directory = directory
        if screen:
            self.current_screen = screen

        self.query_one("#status-text", Static).update(
            f"Session: {self.session_name} | Dir: {self.working_directory} | Screen: {self.current_screen}"
        )


class WelcomePanel(Static):
    """Welcome panel with AgentX branding."""

    DEFAULT_CSS = """
    WelcomePanel {
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
        height: auto;
    }

    WelcomePanel #title {
        text-style: bold;
        color: $primary;
        text-align: center;
    }

    WelcomePanel #subtitle {
        color: $text-muted;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose welcome panel."""
        yield Static("🤖 AgentX", id="title")
        yield Static(
            "Your AI-powered development assistant", id="subtitle"
        )


class MenuGrid(Grid):
    """Grid layout for the main menu buttons."""

    DEFAULT_CSS = """
    MenuGrid {
        grid-size: 3 3;
        grid-gutter: 1 1;
        margin: 1 0;
        height: auto;
    }

    MenuGrid Button {
        width: 100%;
        height: 5;
    }

    MenuGrid Button:hover {
        background: $primary-lighten-2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose menu buttons."""
        yield Button("💬 Chat", id="btn-chat", variant="primary")
        yield Button("📚 RAG", id="btn-rag", variant="primary")
        yield Button("⚡ Fast Agent", id="btn-fast-agent", variant="warning")
        yield Button("⚙️ Advanced Agent", id="btn-agent", variant="success")
        yield Button("🎛️ Models", id="btn-models", variant="primary")
        yield Button("🧠 ReAct", id="btn-react", variant="primary")
        yield Button("💻 Coding", id="btn-coding", variant="success")
        yield Button("❓ Help", id="btn-help", variant="default")


class CommandInput(Vertical):
    """Command input section (label + Input)."""

    DEFAULT_CSS = """
    CommandInput {
        height: auto;
        margin: 1 0;
        padding: 1;
        background: $surface;
    }

    CommandInput Label {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    CommandInput Input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose command input."""
        yield Label("Command:")
        yield Input(
            placeholder="(agentx) > Type command or '/' for help...",
            id="command-input",
        )


class ChatMessage(Static):
    """A single chat message widget (user or assistant role).
    
    Visual design:
    - User messages: right-aligned, distinct background, white text, "You:" prefix
    - Assistant messages: left-aligned, transparent background, "Assistant:" prefix
    - No timestamps for cleaner, simpler display
    """

    DEFAULT_CSS = """
    ChatMessage {
        width: 100%;
        padding: 1 2;
        margin: 0 0 1 0;
    }

    ChatMessage.user {
        background: $primary-darken-2;
        color: white;
        text-align: right;
    }

    ChatMessage.assistant {
        background: transparent;
        color: $text;
        text-align: left;
    }
    """

    def __init__(
        self,
        message: str,
        role: str = "user",
    ) -> None:
        """Initialize chat message.

        Args:
            message:   Message content.
            role:      'user' or 'assistant'.
        """
        self.role = role
        # Format the display with role prefix for clarity
        prefix = "You:" if role == "user" else "Assistant:"
        display = f"{prefix} {message}"
        super().__init__(display)
        self.add_class(role)

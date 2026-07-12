"""Main TUI Screen — Full implementation with menu, input, and status bar.

Refactored (feature_012.tui_framework) to inherit from
:class:`BaseAgentXScreen` and use :meth:`navigate_to_child`, removing the
duplicated boilerplate (controller storage, quit/back, navigation glue,
defensive notify).  The reusable widgets (``SessionStatusBar`` etc.) now live in
``agentx.ui.tui.framework.widgets`` and are **re-exported** here for backward
compatibility with existing imports.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label

from agentx.ui.tui.framework import (
    BaseAgentXScreen,
    CommandInput,
    MenuGrid,
    SessionStatusBar,
    WelcomePanel,
)

__all__ = [
    "MainTUIScreen",
    "SessionStatusBar",
    "WelcomePanel",
    "MenuGrid",
    "CommandInput",
]


class MainTUIScreen(BaseAgentXScreen):
    """Main screen with full UI layout.

    Features:
    - Header with clock
    - Welcome panel
    - Menu buttons (Chat, RAG, Fast Agent, Advanced Agent, Models, ReAct, Help)
    - Command input field
    - Session status bar
    - Footer with key bindings
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("c", "open_chat", "Chat", show=True),
        Binding("r", "open_rag", "RAG", show=True),
        Binding("f", "open_fast_agent", "Fast Agent", show=True),
        Binding("a", "open_agent", "Advanced Agent", show=True),
        Binding("m", "open_models", "Models", show=True),
        Binding("t", "open_react", "ReAct", show=True),
        Binding("d", "open_coding", "Coding", show=True),
        Binding("h", "show_help", "Help", show=True),
        Binding("ctrl+l", "focus_input", "Focus Input", show=False),
    ]

    DEFAULT_CSS = """
    MainTUIScreen {
        layout: vertical;
    }

    MainTUIScreen #main-container {
        height: 1fr;
        padding: 1 2;
    }

    MainTUIScreen #content {
        height: 1fr;
    }
    """

    # __init__, action_quit, action_back are inherited from BaseAgentXScreen.

    def compose(self) -> ComposeResult:
        """Compose the complete main screen layout."""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            with Vertical(id="content"):
                yield WelcomePanel()
                yield Label("\nQuick Actions:", classes="section-title")
                yield MenuGrid()
                yield CommandInput()

        yield SessionStatusBar()
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # DO NOT auto-focus input - it prevents keyboard bindings from working
        # User can focus input with Ctrl+L or by clicking on it
        # self.set_interval(0.1, self._focus_input_delayed)

        # Show welcome notification
        self.notify("Welcome to AgentX! Press 'h' for help.", severity="information", timeout=5)

    def on_button_pressed(self, event) -> None:  # type: ignore[override]
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "btn-chat":
            self.action_open_chat()
        elif button_id == "btn-rag":
            self.action_open_rag()
        elif button_id == "btn-fast-agent":
            self.action_open_fast_agent()
        elif button_id == "btn-agent":
            self.action_open_agent()
        elif button_id == "btn-models":
            self.action_open_models()
        elif button_id == "btn-react":
            self.action_open_react()
        elif button_id == "btn-coding":
            self.action_open_coding()
        elif button_id == "btn-help":
            self.action_show_help()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        """Handle command input submission."""
        command = event.value.strip()

        if not command:
            return

        # Clear input
        event.input.value = ""

        # Process command
        if self._controller:
            try:
                # Delegate to controller
                self._controller.run_command(command)  # type: ignore
                self.safe_notify(f"Command executed: {command}", timeout=2)
            except Exception as e:
                self.safe_error(f"Error: {str(e)}")
        else:
            # No controller, just show notification
            self.safe_notify(f"Command: {command}", timeout=2)

    # ----------------------------------------------------------- navigation actions

    def action_open_chat(self) -> None:
        """Open the Chat screen via the controller, then push the TUI screen."""
        from agentx.ui.tui.screens.chat_screen import ChatTUIScreen

        self.navigate_to_child(
            ChatTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_chat(),
            getter=lambda c: (
                c.get_chat_controller()
                if hasattr(c, "get_chat_controller")
                else (None, None)
            ),
        )

    def action_open_rag(self) -> None:
        """Open the RAG screen via the controller, then push the TUI screen."""
        from agentx.ui.tui.screens.rag_screen import RagTUIScreen

        self.navigate_to_child(
            RagTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_rag(),
            getter=lambda c: (
                c.get_rag_controller()
                if hasattr(c, "get_rag_controller")
                else (None, None)
            ),
        )

    def action_open_agent(self) -> None:
        """Open the Agent screen via the controller, then push the TUI screen."""
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        self.navigate_to_child(
            AgentTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_agent() if hasattr(c, "show_agent") else None,
            getter=lambda c: (
                c.get_agent_controller()
                if hasattr(c, "get_agent_controller")
                else None
            ),
        )

    def action_open_fast_agent(self) -> None:
        """Open the Fast Agent screen via the controller, then push the TUI screen."""
        from agentx.agent.view.tui.fast_agent_screen import FastAgentTUIScreen

        self.navigate_to_child(
            FastAgentTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_fast_agent() if hasattr(c, "show_fast_agent") else None,
            getter=lambda c: (
                c.get_fast_agent_controller()
                if hasattr(c, "get_fast_agent_controller")
                else None
            ),
        )

    def action_open_models(self) -> None:
        """Open the Models screen (select the current AI model provider)."""
        from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

        self.navigate_to_child(
            ModelsTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_models() if hasattr(c, "show_models") else None,
            getter=lambda c: (
                c.get_models_controller()
                if hasattr(c, "get_models_controller")
                else None
            ),
        )

    def action_open_react(self) -> None:
        """Open the ReAct screen (reasoning + acting chat)."""
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        self.navigate_to_child(
            ReactTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_react() if hasattr(c, "show_react") else None,
            getter=lambda c: (
                c.get_react_controller()
                if hasattr(c, "get_react_controller")
                else None
            ),
        )

    def action_open_coding(self) -> None:
        """Open the Coding screen (file operations chat)."""
        from agentx.ui.tui.screens.coding.coding_screen import CodingTUIScreen

        self.navigate_to_child(
            CodingTUIScreen,
            controller=self._controller,
            setup=lambda c: c.show_coding() if hasattr(c, "show_coding") else None,
            getter=lambda c: (
                c.get_coding_controller()
                if hasattr(c, "get_coding_controller")
                else None
            ),
        )

    # ----------------------------------------------------------- other actions

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
# AgentX Help

## Keyboard Shortcuts
- `q` - Quit application
- `c` - Open Chat
- `r` - Open RAG
- `f` - Open Fast Agent (simple modal UX)
- `a` - Open Advanced Agent (full workspace)
- `m` - Open Models (select AI model provider)
- `t` - Open ReAct (reasoning + acting chat)
- `d` - Open Coding (file operations chat)
- `h` - Show this help
- `Ctrl+L` - Focus command input

## Commands
Type commands in the input field below.
Use '/' for command list.

## Navigation
- Click buttons with mouse
- Use keyboard shortcuts
- Tab to navigate widgets
        """
        try:
            self.notify(help_text, severity="information", timeout=10)
        except Exception:
            pass  # Skip notification if no app context

    def action_focus_input(self) -> None:
        """Focus the command input."""
        try:
            input_widget = self.query_one("#command-input", Input)
            input_widget.focus()
        except Exception:
            pass
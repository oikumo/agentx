"""Main TUI Screen - Full implementation with menu, input, and status bar.

This is the complete main screen for AgentX with modern Textual UI.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    Label,
    Static,
)
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.binding import Binding

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner


class SessionStatusBar(Static):
    """Status bar showing session context."""

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
    """Grid layout for menu buttons."""

    DEFAULT_CSS = """
    MenuGrid {
        grid-size: 4 1;
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
        yield Button("🤖 Agent", id="btn-agent", variant="success")
        yield Button("⚙️ Help", id="btn-help", variant="default")


class CommandInput(Vertical):
    """Command input section."""

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


class MainTUIScreen(Screen):
    """Main screen with full UI layout.
    
    Features:
    - Header with clock
    - Welcome panel
    - Menu buttons (Chat, RAG, Help)
    - Command input field
    - Session status bar
    - Footer with key bindings
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("c", "open_chat", "Chat", show=True),
        Binding("r", "open_rag", "RAG", show=True),
        Binding("a", "open_agent", "Agent", show=True),
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

    def __init__(self, controller: IMainViewPartner | None = None) -> None:
        """Initialize main screen.
        
        Args:
            controller: MainController for command handling
        """
        super().__init__()
        self._controller = controller

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-chat":
            self.action_open_chat()
        elif button_id == "btn-rag":
            self.action_open_rag()
        elif button_id == "btn-agent":
            self.action_open_agent()
        elif button_id == "btn-help":
            self.action_show_help()

    def on_input_submitted(self, event: Input.Submitted) -> None:
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
                # Only notify if app context is available
                try:
                    self.notify(f"Command executed: {command}", severity="information", timeout=2)
                except Exception:
                    pass  # Skip notification if no app context
            except Exception as e:
                try:
                    self.notify(f"Error: {str(e)}", severity="error", timeout=None)
                except Exception:
                    pass  # Skip notification if no app context
        else:
            # No controller, just show notification if possible
            try:
                self.notify(f"Command: {command}", severity="information", timeout=2)
            except Exception:
                pass  # Skip notification if no app context

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_open_chat(self) -> None:
        """Open chat screen via controller and direct navigation.
        
        Calls controller.show_chat() to set up controller/view,
        then pushes the TUI screen with the controller for proper navigation.
        """
        # Call controller to set up chat controller and view
        if self._controller:
            try:
                self._controller.show_chat()
            except Exception as e:
                try:
                    self.notify(f"Controller error: {str(e)}", severity="error", timeout=None)
                except Exception:
                    pass
        
        # Get the chat controller and view from main controller
        chat_controller = None
        chat_view = None
        if self._controller and hasattr(self._controller, 'get_chat_controller'):
            chat_controller, chat_view = self._controller.get_chat_controller()
        
        # Push the TUI screen with controller for proper navigation
        try:
            from agentx.ui.tui.screens.chat_screen import ChatTUIScreen
            from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
            if hasattr(self, 'app') and self.app is not None:
                chat_screen = ChatTUIScreen(chat_controller)
                # Connect the adapter to the screen if we have a view
                if chat_view and isinstance(chat_view, TUIChatAdapter):
                    chat_view.set_screen(chat_screen)
                self.app.push_screen(chat_screen)
        except Exception as e:
            try:
                self.notify(f"Error opening Chat: {str(e)}", severity="error", timeout=None)
            except Exception:
                pass

    def action_open_rag(self) -> None:
        """Open RAG screen via controller and direct navigation.
        
        Calls controller.show_rag() to set up controller/view,
        then pushes the TUI screen with the controller for proper navigation.
        """
        # Call controller to set up RAG controller and view
        if self._controller:
            try:
                self._controller.show_rag()
            except Exception as e:
                try:
                    self.notify(f"Controller error: {str(e)}", severity="error", timeout=None)
                except Exception:
                    pass
        
        # Get the RAG controller and view from main controller
        rag_controller = None
        rag_view = None
        if self._controller and hasattr(self._controller, 'get_rag_controller'):
            rag_controller, rag_view = self._controller.get_rag_controller()
        
        # Push the TUI screen with controller for proper navigation
        try:
            from agentx.ui.tui.screens.rag_screen import RagTUIScreen
            from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter
            if hasattr(self, 'app') and self.app is not None:
                rag_screen = RagTUIScreen(rag_controller)
                # Connect the adapter to the screen if we have a view
                if rag_view and isinstance(rag_view, TUIRagAdapter):
                    rag_view.set_screen(rag_screen)
                self.app.push_screen(rag_screen)
        except Exception as e:
            try:
                self.notify(f"Error opening RAG: {str(e)}", severity="error", timeout=None)
            except Exception:
                pass

    def action_open_agent(self) -> None:
        """Open the Agent screen via controller and direct navigation.

        Calls controller.show_agent() to create and wire the Agent + AgentController,
        then pushes the AgentTUIScreen with the controller for proper navigation.
        """
        # Call controller to create agent + controller
        if self._controller and hasattr(self._controller, 'show_agent'):
            try:
                self._controller.show_agent()
            except Exception as e:
                try:
                    self.notify(f"Controller error: {str(e)}", severity="error", timeout=None)
                except Exception:
                    pass

        # Get the agent controller from main controller
        agent_controller = None
        if self._controller and hasattr(self._controller, 'get_agent_controller'):
            agent_controller = self._controller.get_agent_controller()

        # Push the Agent TUI screen with controller
        try:
            from agentx.agent.view.tui.agent_screen import AgentTUIScreen
            if hasattr(self, 'app') and self.app is not None:
                agent_screen = AgentTUIScreen(agent_controller)
                self.app.push_screen(agent_screen)
        except Exception as e:
            try:
                self.notify(f"Error opening Agent: {str(e)}", severity="error", timeout=None)
            except Exception:
                pass

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
# AgentX Help

## Keyboard Shortcuts
- `q` - Quit application
- `c` - Open Chat
- `r` - Open RAG
- `a` - Open Agent
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
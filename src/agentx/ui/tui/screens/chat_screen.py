"""Chat TUI Screen - Simple chat interface with LLM.

This screen provides a basic chat interface for interacting with the LLM.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Input,
    Label,
    Static,
)
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding
from textual.message import Message

if TYPE_CHECKING:
    from agentx.ui.interfaces import IChatViewPartner


class ChatMessage(Static):
    """A single chat message widget."""

    DEFAULT_CSS = """
    ChatMessage {
        width: 100%;
        padding: 1;
        margin: 0 0 1 0;
    }
    
    ChatMessage.user {
        background: $primary-darken-2;
        color: white;
        text-align: right;
        border: solid $primary;
    }
    
    ChatMessage.assistant {
        background: $surface;
        color: $text;
        text-align: left;
        border: solid $secondary;
    }
    """

    def __init__(self, message: str, role: str = "user") -> None:
        """Initialize chat message.
        
        Args:
            message: Message content
            role: 'user' or 'assistant'
        """
        super().__init__(message)
        self.role = role
        self.add_class(role)


class ChatTUIScreen(Screen):
    """Chat screen with message history and input.
    
    Features:
    - Message history display
    - Input field for user messages
    - Streaming response from LLM
    - Keyboard shortcuts
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+enter", "send", "Send", show=True),
    ]

    DEFAULT_CSS = """
    ChatTUIScreen {
        layout: vertical;
    }
    
    ChatTUIScreen #chat-container {
        height: 1fr;
        padding: 1;
    }
    
    ChatTUIScreen #messages {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    
    ChatTUIScreen #input-section {
        height: auto;
        dock: bottom;
    }
    
    ChatTUIScreen #input-section Input {
        width: 100%;
    }
    """

    def __init__(self, controller: "IChatViewPartner | None" = None) -> None:
        """Initialize chat screen.
        
        Args:
            controller: Optional IChatViewPartner for message processing
        """
        super().__init__()
        self._controller = controller
        self.history: list = []
        self._streaming_message: str = ""
        self._is_streaming: bool = False
        self._streaming_widget: ChatMessage | None = None

    def compose(self) -> ComposeResult:
        """Compose chat screen layout."""
        yield Header(show_clock=True)
        
        with Container(id="chat-container"):
            with Vertical():
                yield ScrollableContainer(id="messages")
                
                with Horizontal(id="input-section"):
                    yield Input(
                        placeholder="Type your message... (Ctrl+Enter to send, 'quit' to exit)",
                        id="chat-input",
                    )
        
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Initialize controller if provided
        if self._controller:
            self._controller.start_interactive_streaming(system_prompt="You are a helpful assistant.")
        
        # Show welcome message
        self._add_message("Welcome to AgentX Chat! Ask me anything.", "assistant")
        
        # Focus input
        try:
            self.query_one("#chat-input", Input).focus()
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission."""
        if event.input.id != "chat-input":
            return
            
        message = event.value.strip()
        
        if not message:
            return
        
        # Clear input
        event.input.value = ""
        
        # Check for quit command
        if message.lower() in ("quit", "exit"):
            self.action_quit()
            return
        
        # Add user message to UI
        self._add_message(message, "user")
        
        # Process through controller if available
        if self._controller:
            try:
                # Process user message via controller
                self._controller.process_user_message(message)
            except Exception as e:
                self._add_message(f"Error: {str(e)}", "assistant")
        else:
            # Fallback: show placeholder
            self._add_message("(No controller connected)", "assistant")

    def _add_message(self, message: str, role: str = "user") -> None:
        """Add a message to the chat display.
        
        Args:
            message: Message content
            role: 'user' or 'assistant'
        """
        try:
            messages_container = self.query_one("#messages", ScrollableContainer)
            chat_message = ChatMessage(message, role)
            messages_container.mount(chat_message)
            
            # Scroll to bottom
            self.call_later(messages_container.scroll_end, animate=False)
        except Exception:
            pass

    # View methods for IChatView interface (used by controller)
    def show_initial_message(self) -> None:
        """Show welcome message."""
        self._add_message("Welcome to AgentX Chat! Ask me anything.", "assistant")

    def show_message(self, message: str) -> None:
        """Show a complete message."""
        self._add_message(message, "assistant")

    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message."""
        try:
            messages_container = self.query_one("#messages", ScrollableContainer)
            
            if not self._is_streaming:
                # Start new streaming message
                self._is_streaming = True
                self._streaming_message = message
                chat_message = ChatMessage(message, "assistant")
                messages_container.mount(chat_message)
                self._streaming_widget = chat_message
            else:
                # Append to existing streaming message
                self._streaming_message += message
                if self._streaming_widget:
                    self._streaming_widget.update(self._streaming_message)
            
            # Scroll to bottom
            self.call_later(messages_container.scroll_end, animate=False)
        except Exception:
            pass

    def show_stream_message(self, message: str) -> None:
        """Stream message with typing effect (alias for show_partial_message)."""
        self.show_partial_message(message)

    def show_message_chat_error(self) -> None:
        """Show chat error."""
        self._add_message("Error: Failed to get response from assistant.", "assistant")

    def _on_streaming_complete(self) -> None:
        """Called when streaming is complete."""
        self._is_streaming = False
        self._streaming_message = ""
        self._streaming_widget = None

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_back(self) -> None:
        """Go back to main screen."""
        self.app.pop_screen()

    def action_send(self) -> None:
        """Send current message."""
        try:
            input_widget = self.query_one("#chat-input", Input)
            if input_widget.value.strip():
                # Call handler directly
                event = type('InputSubmitted', (), {'value': input_widget.value, 'input': input_widget})()
                self.on_input_submitted(event)
        except Exception:
            pass
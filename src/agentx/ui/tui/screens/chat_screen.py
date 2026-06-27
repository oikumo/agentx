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

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

if TYPE_CHECKING:
    from agentx.model.ai.service import AIService


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

    def __init__(self) -> None:
        """Initialize chat screen."""
        super().__init__()
        self.history: list = []
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize LLM from AI service."""
        try:
            from agentx.model.ai.service import AIService
            self.llm = AIService().openrouter_llm_provider().create_llm()
        except Exception as e:
            self.llm = None
            print(f"Warning: Could not initialize LLM: {e}")

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
        # Add system message to history
        self.history.append(SystemMessage(content="You are a helpful assistant."))
        
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
        
        # Add user message to UI and history
        self._add_message(message, "user")
        self.history.append(HumanMessage(content=message))
        
        # Get response
        self._get_response()

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

    def _get_response(self) -> None:
        """Get response from LLM."""
        if not self.llm:
            self._add_message("Error: LLM not available. Please check your API key.", "assistant")
            return
        
        try:
            full_response = ""
            
            # Stream response
            for chunk in self.llm.stream(self.history):
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    # Update display incrementally (could be improved with streaming widget)
            
            # Add assistant response to history and display
            if full_response:
                self.history.append(AIMessage(content=full_response))
                self._add_message(full_response, "assistant")
            else:
                self._add_message("No response received.", "assistant")
                
        except Exception as e:
            self._add_message(f"Error: {str(e)}", "assistant")

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
                # Simulate submission
                from textual.events import Submit
                input_widget.post_message(Input.Submitted(input_widget.value))
        except Exception:
            pass
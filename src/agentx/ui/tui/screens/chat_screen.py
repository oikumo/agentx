"""Chat TUI Screen — Chat interface with conversation history and persistence.

Refactored (feature_012.tui_framework) to inherit from
:class:`BaseAgentXScreen` and import :class:`ChatMessage`
from ``agentx.ui.tui.framework.widgets``.

Enhanced (feature_017):
- Conversation sidebar with history list (toggleable via Ctrl+L)
- Message timestamps
- New conversation (Ctrl+N), Export (Ctrl+E), Delete (Ctrl+D)
- Conversation persistence via ChatHistoryRepository
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Input, ListItem, ListView, Static

from agentx.model.chat import Conversation
from agentx.ui.tui.framework import BaseAgentXScreen, ChatMessage

if TYPE_CHECKING:
    from agentx.ui.interfaces import IChatViewPartner


__all__ = ["ChatTUIScreen", "ChatMessage"]


class ConversationSidebar(Static):
    """Sidebar widget showing conversation history."""
    
    def __init__(self, conversations: list[Conversation] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.conversations = conversations or []
        self.selected_index = 0
    
    def compose(self) -> ComposeResult:
        yield ListView(id="conversation-list")
    
    def on_mount(self) -> None:
        self.refresh_conversations()
    
    def refresh_conversations(self) -> None:
        """Update the conversation list."""
        try:
            list_view = self.query_one("#conversation-list", ListView)
            list_view.clear()
            
            for conv in self.conversations:
                # Format: "Title - X msgs - HH:MM"
                time_str = conv.updated_at.strftime("%H:%M") if conv.updated_at else ""
                item_text = f"{conv.title} ({conv.message_count} msgs) {time_str}"
                list_view.append(ListItem(Static(item_text), id=f"conv-{conv.id}"))
            
            # Add "New Conversation" item at top
            if self.conversations:
                list_view.insert(0, ListItem(Static("➕ New Conversation"), id="conv-new"))
            
            if list_view.children:
                list_view.index = self.selected_index
        except Exception:
            pass
    
    def set_conversations(self, conversations: list[Conversation]) -> None:
        """Set conversations and refresh."""
        self.conversations = conversations
        self.refresh_conversations()
    
    def get_selected_conversation(self) -> Conversation | None:
        """Get the currently selected conversation."""
        try:
            list_view = self.query_one("#conversation-list", ListView)
            if list_view.index is not None and list_view.index < len(self.conversations):
                return self.conversations[list_view.index]
        except Exception:
            pass
        return None


class ChatTUIScreen(BaseAgentXScreen):
    """Chat screen with message history, input, and conversation sidebar.
    
    Features:
    - Message history display with timestamps
    - Input field for user messages
    - Streaming response from LLM
    - Conversation sidebar (Ctrl+L to toggle)
    - New conversation (Ctrl+N)
    - Export conversation (Ctrl+E)
    - Delete conversation (Ctrl+D)
    - Keyboard shortcuts
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+enter", "send", "Send", show=True),
        Binding("ctrl+l", "toggle_sidebar", "Sidebar", show=True),
        Binding("ctrl+n", "new_conversation", "New", show=True),
        Binding("ctrl+e", "export_conversation", "Export", show=True),
        Binding("ctrl+d", "delete_conversation", "Delete", show=True),
    ]

    DEFAULT_CSS = """
    ChatTUIScreen {
        layout: vertical;
    }

    ChatTUIScreen #chat-container {
        height: 1fr;
        padding: 1;
        layout: horizontal;
    }

    ChatTUIScreen #sidebar {
        width: 30;
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-right: 1;
        display: none;  /* Hidden by default */
    }

    ChatTUIScreen #sidebar.visible {
        display: block;
    }

    ChatTUIScreen #main-chat-area {
        width: 1fr;
        height: 1fr;
        layout: vertical;
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

    ChatTUIScreen #conversation-list {
        height: 1fr;
    }

    ChatTUIScreen #sidebar-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    """

    def __init__(self, controller: "IChatViewPartner | None" = None) -> None:
        """Initialize chat screen.

        Args:
            controller: Optional IChatViewPartner for message processing
        """
        super().__init__(controller)
        self.history: list = []
        self._streaming_message: str = ""
        self._is_streaming: bool = False
        self._streaming_widget: ChatMessage | None = None
        self._sidebar_visible: bool = False
        self._conversations: list[Conversation] = []
        # LLM attribute — initialized to None; actual LLM creation is deferred
        # to on_mount() to avoid blocking screen construction (provider
        # factories may validate API keys / network).  The controller also
        # holds its own LLM; this attribute is for fallback / inspection.
        self.llm = None

    # action_quit / action_back are inherited from BaseAgentXScreen.

    def compose(self) -> ComposeResult:
        """Compose chat screen layout with optional sidebar."""
        yield Header(show_clock=True)

        with Container(id="chat-container"):
            # Sidebar (hidden by default)
            with Vertical(id="sidebar"):
                yield Static("💬 Conversations", id="sidebar-title")
                yield ConversationSidebar(id="conversation-sidebar")

            # Main chat area
            with Vertical(id="main-chat-area"):
                yield ScrollableContainer(id="messages")

                with Horizontal(id="input-section"):
                    yield Input(
                        placeholder="Type your message... (Ctrl+Enter to send, Ctrl+L sidebar, Ctrl+N new)",
                        id="chat-input",
                    )

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Initialize controller if provided
        if self._controller:
            self._controller.start_interactive_streaming(system_prompt="You are a helpful assistant.")
            
            # Load conversations for sidebar
            self._load_conversations()

        # Focus input
        try:
            self.query_one("#chat-input", Input).focus()
        except Exception:
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle conversation selection from sidebar."""
        if event.list_view.id == "conversation-list":
            item = event.item
            if item.id == "conv-new":
                self.action_new_conversation()
            else:
                # Extract conversation ID from item ID (format: "conv-{id}")
                try:
                    conv_id = int(item.id.split("-")[1])
                    self._load_conversation(conv_id)
                except (IndexError, ValueError):
                    pass

    def _load_conversations(self) -> None:
        """Load conversations from controller for sidebar."""
        if self._controller and hasattr(self._controller, 'list_conversations'):
            self._conversations = self._controller.list_conversations(limit=50)
            self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        """Refresh the sidebar with current conversations."""
        try:
            sidebar = self.query_one("#conversation-sidebar", ConversationSidebar)
            sidebar.set_conversations(self._conversations)
        except Exception:
            pass

    def _load_conversation(self, conversation_id: int) -> None:
        """Load a conversation from the database."""
        if self._controller and hasattr(self._controller, 'load_conversation'):
            success = self._controller.load_conversation(conversation_id)
            if success:
                self._refresh_sidebar()
                # Hide sidebar after selection
                self._toggle_sidebar(visible=False)

    def _add_message(self, message: str, role: str = "user", timestamp: datetime | None = None) -> None:
        """Add a message to the chat display with timestamp.

        Args:
            message: Message content
            role: 'user' or 'assistant'
            timestamp: Optional timestamp (defaults to now)
        """
        try:
            messages_container = self.query_one("#messages", ScrollableContainer)
            if timestamp is None:
                timestamp = datetime.now()
            chat_message = ChatMessage(message, role, timestamp)
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
        """Show a complete message with timestamp."""
        self._add_message(message, "assistant")

    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message."""
        try:
            messages_container = self.query_one("#messages", ScrollableContainer)

            if not self._is_streaming:
                # Start new streaming message
                self._is_streaming = True
                self._streaming_message = message
                chat_message = ChatMessage(message, "assistant", datetime.now())
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

    def action_send(self) -> None:
        """Send current message."""
        try:
            input_widget = self.query_one("#chat-input", Input)
            if input_widget.value.strip():
                # Call handler directly
                event = type('InputSubmitted', (), {'value': input_widget.value, 'input': input_widget})()
                self.on_input_submitted(event)  # type: ignore[arg-type]
        except Exception:
            pass

    def action_toggle_sidebar(self) -> None:
        """Toggle conversation sidebar visibility."""
        self._sidebar_visible = not self._sidebar_visible
        try:
            sidebar = self.query_one("#sidebar", Vertical)
            if self._sidebar_visible:
                sidebar.add_class("visible")
                self._load_conversations()
            else:
                sidebar.remove_class("visible")
        except Exception:
            pass

    def _toggle_sidebar(self, visible: bool) -> None:
        """Set sidebar visibility."""
        self._sidebar_visible = visible
        try:
            sidebar = self.query_one("#sidebar", Vertical)
            if visible:
                sidebar.add_class("visible")
            else:
                sidebar.remove_class("visible")
        except Exception:
            pass

    def action_new_conversation(self) -> None:
        """Start a new conversation."""
        if self._controller and hasattr(self._controller, 'start_new_conversation'):
            conv_id = self._controller.start_new_conversation()
            if conv_id:
                # Clear UI messages
                try:
                    messages_container = self.query_one("#messages", ScrollableContainer)
                    messages_container.clear()
                except Exception:
                    pass
                
                # Show welcome message
                self._add_message("Welcome to AgentX Chat! Ask me anything.", "assistant")
                
                # Refresh sidebar
                self._load_conversations()

    def action_export_conversation(self) -> None:
        """Export current conversation."""
        if self._controller and hasattr(self._controller, 'export_current_conversation_markdown'):
            markdown = self._controller.export_current_conversation_markdown()
            if markdown:
                # Save to file
                from pathlib import Path
                filename = Path.home() / ".agentx" / f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                filename.parent.mkdir(parents=True, exist_ok=True)
                filename.write_text(markdown, encoding="utf-8")
                self.notify(f"Exported to {filename}", severity="information", timeout=3)
            else:
                self.notify("No active conversation to export", severity="warning", timeout=2)
        else:
            self.notify("Export not available", severity="warning", timeout=2)

    def action_delete_conversation(self) -> None:
        """Delete current conversation (with confirmation)."""
        if self._controller and hasattr(self._controller, 'delete_current_conversation'):
            # Simple confirmation - in real app would use a modal
            success = self._controller.delete_current_conversation()
            if success:
                # Clear UI messages
                try:
                    messages_container = self.query_one("#messages", ScrollableContainer)
                    messages_container.clear()
                except Exception:
                    pass
                
                # Show welcome message
                self._add_message("Welcome to AgentX Chat! Ask me anything.", "assistant")
                
                # Refresh sidebar
                self._load_conversations()
                self.notify("Conversation deleted", severity="information", timeout=2)
            else:
                self.notify("No conversation to delete", severity="warning", timeout=2)

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
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

        # Add user message to UI with timestamp
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
"""Coding Agent TUI Screen — chat-like conversation with file operations.

This screen provides a chat-like interface where the AI agent uses file system
tools (search, read, edit, list, create) to help with coding tasks. It shows:

- 💭 **Thinking** — the agent's reasoning chain
- 🔧 **Tool calls** — when the agent uses a file tool
- 📊 **Tool results** — the output of executed tools (with diff highlighting)
- **Answer** — the final streamed response

The agent runs on a background thread (via the controller) and streaming events
are marshalled to the UI thread via ``app.call_from_thread()``.

Design: ``design_001_coding_agent_screen.md`` §3.3.
Operation spec: ``operation_spec_001_coding_operations.md`` OP-3/9-14.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Input, Static

from agentx.ui.tui.framework import BaseAgentXScreen, ChatMessage, register_partner
from agentx.ui.interfaces import ICodingViewPartner

__all__ = ["CodingTUIScreen"]


class CodingTUIScreen(BaseAgentXScreen):
    """Coding Agent conversation screen with visible reasoning and tool calls.

    Features:
    - Chat-like input/output with Ctrl+Enter to send
    - 💭 Thinking blocks showing the agent's reasoning
    - 🔧 Tool call blocks showing which tools the agent uses
    - 📊 Tool result blocks showing tool outputs (with diff highlighting)
    - Streaming final answer (token-by-token)
    - Non-blocking (agent runs on background thread via controller)
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+enter", "send", "Send", show=True),
        Binding("ctrl+n", "new_conversation", "New", show=True),
    ]

    DEFAULT_CSS = """
    CodingTUIScreen {
        layout: vertical;
    }

    CodingTUIScreen #coding-container {
        height: 1fr;
        padding: 1;
    }

    CodingTUIScreen #coding-main-area {
        width: 1fr;
        height: 1fr;
        layout: vertical;
    }

    CodingTUIScreen #coding-messages {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
        overflow-y: auto;
    }

    CodingTUIScreen #coding-input-section {
        height: auto;
        dock: bottom;
    }

    CodingTUIScreen #coding-input-section Input {
        width: 100%;
    }

    /* Thinking blocks — dimmed/italic */
    CodingTUIScreen .coding-thinking {
        color: $text-muted;
        text-style: italic;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }

    /* Tool call blocks — distinct background */
    CodingTUIScreen .coding-tool-call {
        background: $surface;
        color: $accent;
        padding: 0 2;
        margin: 0 0 0 0;
        width: 100%;
    }

    /* Tool result blocks — slightly different shade */
    CodingTUIScreen .coding-tool-result {
        background: $surface-darken-1;
        color: $success;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }

/* Diff highlighting in tool results */
    CodingTUIScreen .coding-diff {
    }
    CodingTUIScreen .coding-diff-add {
        color: $success;
        background: $success-darken-3;
    }
    CodingTUIScreen .coding-diff-remove {
        color: $error;
        background: $error-darken-3;
    }

    /* Error blocks */
    CodingTUIScreen .coding-error {
        color: $error;
        text-style: bold;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }
    """

    def __init__(self, controller: ICodingViewPartner | None = None) -> None:
        """Initialize the Coding Agent screen.

        Args:
            controller: Optional ICodingViewPartner for agent interaction.
        """
        super().__init__(controller)
        self._is_streaming: bool = False
        self._streaming_text: str = ""
        self._streaming_widget: ChatMessage | None = None
        self._is_mounted: bool = False

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Compose the Coding Agent screen layout."""
        yield Header(show_clock=True)

        with Container(id="coding-container"):
            with Vertical(id="coding-main-area"):
                yield ScrollableContainer(id="coding-messages")
                with Horizontal(id="coding-input-section"):
                    yield Input(
                        placeholder="Ask the coding agent... (Ctrl+Enter to send, Esc to go back, Ctrl+N for new)",
                        id="coding-input",
                    )

        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self._is_mounted = True

        # Wire the controller with app + view references for call_from_thread
        if self._controller:
            if hasattr(self._controller, "set_app"):
                self._controller.set_app(self.app)
            if hasattr(self._controller, "set_view"):
                self._controller.set_view(self)

            # Start a fresh conversation
            try:
                self._controller.start_new_conversation()
            except Exception:
                pass

        # Show welcome message
        self._add_message(
            "💻 Coding Agent ready. Ask me to explore, edit, or create files!",
            "assistant",
        )

        # Focus input
        try:
            self.query_one("#coding-input", Input).focus()
        except Exception:
            pass

    # ── Display methods ───────────────────────────────────────────────────────

    def _add_message(self, message: str, role: str = "user") -> None:
        """Add a message to the chat display.

        Args:
            message: Message content.
            role: 'user' or 'assistant'.
        """
        try:
            container = self.query_one("#coding-messages", ScrollableContainer)
            chat_message = ChatMessage(message, role)
            container.mount(chat_message)
            self.call_later(container.scroll_end, animate=False)
        except Exception:
            pass

    def show_user_message(self, text: str) -> None:
        """Display a user message in the chat area.

        Args:
            text: The user's message text.
        """
        self._add_message(text, "user")

    def show_thinking(self, text: str) -> None:
        """Display a thinking/reasoning block.

        Args:
            text: The reasoning text from the agent.
        """
        def _do_mount() -> None:
            try:
                container = self.query_one("#coding-messages", ScrollableContainer)
                widget = Static(f"💭 {text}", classes="coding-thinking")
                container.mount(widget)
                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        self.call_later(_do_mount)

    def show_tool_call(self, name: str, args: str) -> None:
        """Display a tool call block.

        Args:
            name: The tool name.
            args: The tool arguments (as a string).
        """
        def _do_mount() -> None:
            try:
                container = self.query_one("#coding-messages", ScrollableContainer)
                text = f"🔧 {name}({args})"
                widget = Static(text, classes="coding-tool-call")
                container.mount(widget)
                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        self.call_later(_do_mount)

    def show_tool_result(self, name: str, result: str) -> None:
        """Display a tool result block.

        Args:
            name: The tool name.
            result: The tool output.
        """
        def _do_mount() -> None:
            try:
                container = self.query_one("#coding-messages", ScrollableContainer)
                # Check if result looks like a unified diff
                if result.startswith("--- ") and "+++ " in result:
                    widget = Static(result, classes="coding-tool-result coding-diff")
                else:
                    text = f"📊 {result}"
                    widget = Static(text, classes="coding-tool-result")
                container.mount(widget)
                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        self.call_later(_do_mount)

    def show_answer_chunk(self, text: str) -> None:
        """Display a streaming answer chunk.

        The first chunk creates a ChatMessage widget; subsequent chunks
        append to the accumulated text and update the widget.

        Args:
            text: A text delta from the agent's final answer.
        """
        def _do_update() -> None:
            try:
                container = self.query_one("#coding-messages", ScrollableContainer)

                if not self._streaming_widget:
                    # First chunk — create the widget
                    widget = ChatMessage(text, "assistant")
                    container.mount(widget)
                    self._streaming_widget = widget
                else:
                    # Update existing widget
                    if self._streaming_widget:
                        self._streaming_widget.update(
                            f"Assistant: {self._streaming_text}"
                        )

                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        # Set streaming state synchronously so tests can assert immediately
        if not self._is_streaming:
            self._is_streaming = True
            self._streaming_text = text
        else:
            self._streaming_text += text

        self.call_later(_do_update)

    def show_answer_final(self) -> None:
        """Finalize the streaming answer — reset streaming state."""
        self._is_streaming = False
        self._streaming_text = ""
        self._streaming_widget = None

    def show_error(self, text: str) -> None:
        """Display an error message.

        Args:
            text: The error message.
        """
        def _do_mount() -> None:
            try:
                container = self.query_one("#coding-messages", ScrollableContainer)
                widget = Static(f"⚠️ {text}", classes="coding-error")
                container.mount(widget)
                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        self.call_later(_do_mount)
        self.safe_error(text)

    # ── Actions ──────────────────────────────────────────────────────────────

    def action_send(self) -> None:
        """Send the current input to the Coding agent."""
        try:
            input_widget = self.query_one("#coding-input", Input)
            text = input_widget.value.strip()

            if not text:
                return

            # Clear input
            input_widget.value = ""

            # Check for quit command
            if text.lower() in ("q", "quit", "exit"):
                self.action_quit()
                return

            # Show user message
            self.show_user_message(text)

            # Send to controller
            if self._controller:
                self._controller.send_message(text)

        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        """Handle input submission."""
        if event.input.id != "coding-input":
            return
        self.action_send()

    def action_new_conversation(self) -> None:
        """Start a new conversation (clear history)."""
        try:
            container = self.query_one("#coding-messages", ScrollableContainer)
            # Remove all child widgets
            for child in container.children:
                child.remove()
        except Exception:
            pass

        if self._controller:
            self._controller.start_new_conversation()

        # Show welcome message
        self._add_message(
            "💻 New conversation started. Ask me anything!",
            "assistant",
        )

        # Focus input
        try:
            self.query_one("#coding-input", Input).focus()
        except Exception:
            pass

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_unmount(self) -> None:
        """Clean up on screen exit — cancel any running agent."""
        super().on_unmount()
        if self._controller and getattr(self._controller, "is_running", False):
            self._controller.cancel()


# Register the screen as a virtual subclass of ICodingViewPartner
# (avoids the Textual/abc metaclass conflict — see partner.py).
register_partner(ICodingViewPartner, CodingTUIScreen)
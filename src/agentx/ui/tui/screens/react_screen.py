"""ReAct TUI Screen — chat-like conversation with reasoning + tool calls.

This screen provides a chat-like interface where the AI agent uses LangChain's
ReAct pattern (Reasoning + Acting). Unlike the plain Chat screen, the ReAct
screen shows:

- 💭 **Thinking** — the agent's reasoning chain (chain-of-thought)
- 🔧 **Tool calls** — when the agent decides to use a tool
- 📊 **Tool results** — the output of executed tools
- **Answer** — the final streamed response

The agent runs on a background thread (via the controller) and streaming events
are marshalled to the UI thread via ``app.call_from_thread()``.

Design: ``design_001_react_screen.md`` §3.3.
Operation spec: ``operation_spec_001_react_operations.md`` OP-3/9-14.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Input, Static

from agentx.ui.tui.framework import BaseAgentXScreen, ChatMessage, register_partner
from agentx.ui.interfaces import IReactViewPartner

__all__ = ["ReactTUIScreen"]


class ReactTUIScreen(BaseAgentXScreen):
    """ReAct conversation screen with visible reasoning and tool calls.

    Features:
    - Chat-like input/output with Ctrl+Enter to send
    - 💭 Thinking blocks showing the agent's reasoning
    - 🔧 Tool call blocks showing which tools the agent uses
    - 📊 Tool result blocks showing tool outputs
    - Streaming final answer (token-by-token)
    - Non-blocking (agent runs on background thread via controller)
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+enter", "send", "Send", show=True),
    ]

    DEFAULT_CSS = """
    ReactTUIScreen {
        layout: vertical;
    }

    ReactTUIScreen #react-container {
        height: 1fr;
        padding: 1;
    }

    ReactTUIScreen #react-main-area {
        width: 1fr;
        height: 1fr;
        layout: vertical;
    }

    ReactTUIScreen #react-messages {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
        overflow-y: auto;
    }

    ReactTUIScreen #react-input-section {
        height: auto;
        dock: bottom;
    }

    ReactTUIScreen #react-input-section Input {
        width: 100%;
    }

    /* Thinking blocks — dimmed/italic */
    ReactTUIScreen .react-thinking {
        color: $text-muted;
        text-style: italic;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }

    /* Tool call blocks — distinct background */
    ReactTUIScreen .react-tool-call {
        background: $surface;
        color: $accent;
        padding: 0 2;
        margin: 0 0 0 0;
        width: 100%;
    }

    /* Tool result blocks — slightly different shade */
    ReactTUIScreen .react-tool-result {
        background: $surface-darken-1;
        color: $success;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }

    /* Error blocks */
    ReactTUIScreen .react-error {
        color: $error;
        text-style: bold;
        padding: 0 2;
        margin: 0 0 1 0;
        width: 100%;
    }
    """

    def __init__(self, controller: IReactViewPartner | None = None) -> None:
        """Initialize the ReAct screen.

        Args:
            controller: Optional IReactViewPartner for agent interaction.
        """
        super().__init__(controller)
        self._is_streaming: bool = False
        self._streaming_text: str = ""
        self._streaming_widget: ChatMessage | None = None
        self._is_mounted: bool = False
        # Worker thread reference (for cleanup)
        self._worker_thread: Any = None

    # ── Compose ─────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Compose the ReAct screen layout."""
        yield Header(show_clock=True)

        with Container(id="react-container"):
            with Vertical(id="react-main-area"):
                yield ScrollableContainer(id="react-messages")
                with Horizontal(id="react-input-section"):
                    yield Input(
                        placeholder="Ask the ReAct agent... (Ctrl+Enter to send, Esc to go back)",
                        id="react-input",
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
            "🤖 ReAct Agent ready. Ask me anything — I'll show my reasoning!",
            "assistant",
        )

        # Focus input
        try:
            self.query_one("#react-input", Input).focus()
        except Exception:
            pass

    # ── Display methods ─────────────────────────────────────────────────────

    def _add_message(self, message: str, role: str = "user") -> None:
        """Add a message to the chat display.

        Args:
            message: Message content.
            role: 'user' or 'assistant'.
        """
        try:
            container = self.query_one("#react-messages", ScrollableContainer)
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
                container = self.query_one("#react-messages", ScrollableContainer)
                widget = Static(f"💭 {text}", classes="react-thinking")
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
                container = self.query_one("#react-messages", ScrollableContainer)
                text = f"🔧 {name}({args})"
                widget = Static(text, classes="react-tool-call")
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
                container = self.query_one("#react-messages", ScrollableContainer)
                text = f"📊 {result}"
                widget = Static(text, classes="react-tool-result")
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
                container = self.query_one("#react-messages", ScrollableContainer)

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
                container = self.query_one("#react-messages", ScrollableContainer)
                widget = Static(f"⚠️ {text}", classes="react-error")
                container.mount(widget)
                self.call_later(container.scroll_end, animate=False)
            except Exception:
                pass

        self.call_later(_do_mount)
        self.safe_error(text)

    # ── Actions ──────────────────────────────────────────────────────────────

    def action_send(self) -> None:
        """Send the current input to the ReAct agent."""
        try:
            input_widget = self.query_one("#react-input", Input)
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
        if event.input.id != "react-input":
            return
        self.action_send()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_unmount(self) -> None:
        """Clean up on screen exit — cancel any running agent."""
        super().on_unmount()
        if self._controller and getattr(self._controller, "is_running", False):
            self._controller.cancel()


# Register the screen as a virtual subclass of IReactViewPartner
# (avoids the Textual/abc metaclass conflict — see partner.py).
register_partner(IReactViewPartner, ReactTUIScreen)

"""ReAct screen controller — orchestrates View and Model.

The controller sits between the TUI View (``ReactTUIScreen``) and the Model
(``ReactAgentService``).  When the user sends a message, the controller
spawns a background worker thread that calls ``service.stream_agent()``.
The streaming callbacks are marshalled back to the UI thread via
``app.call_from_thread()``.

Design: ``design_001_react_screen.md`` §3.2.
Operation spec: ``operation_spec_001_react_operations.md`` OP-4/5.
"""

from __future__ import annotations

import threading
from typing import Any

from agentx.model.react.react_agent_service import ReactAgentService
from agentx.ui.interfaces import IReactViewPartner


class ReactController(IReactViewPartner):
    """Controller for the ReAct screen.

    Attributes:
        _service: The ReactAgentService (Model layer).
        _worker_thread: The background thread running the agent.
        _app: Reference to the Textual App for call_from_thread marshalling.
    """

    def __init__(self, service: ReactAgentService | None = None) -> None:
        """Initialize the controller.

        Args:
            service: An optional injected ReactAgentService. If None, a new
                one is created (which uses AIService().get_current_llm()).
        """
        self._service: ReactAgentService = service or ReactAgentService()
        self._worker_thread: threading.Thread | None = None
        self._app: Any = None  # Set by the View via set_app()
        self._view: Any = None  # Set by the View via set_view()

    # ── IReactViewPartner implementation ────────────────────────────────────

    def send_message(self, user_message: str) -> bool:
        """Send a user message to the ReAct agent.

        If the agent is already running, the message is rejected.

        Args:
            user_message: The user's input text.

        Returns:
            True if accepted, False if agent is busy.
        """
        if self._service.is_running:
            return False

        # Clear any previous cancel state for a fresh run
        self._service._cancel_event.clear()

        thread = threading.Thread(
            target=self._run_agent,
            args=(user_message, None),  # view will be set via _app
            daemon=True,
            name="AgentX-ReAct-Worker",
        )
        self._worker_thread = thread
        thread.start()
        return True

    def cancel(self) -> None:
        """Cancel an in-progress agent run."""
        self._service.cancel()

    @property
    def is_running(self) -> bool:
        """Whether the agent is currently running."""
        return self._service.is_running

    def get_history(self) -> list:
        """Get the conversation message history."""
        return self._service.get_history()

    def close(self) -> None:
        """Close the controller and cancel any running agent."""
        self._service.cancel()

    def start_new_conversation(self) -> None:
        """Start a new conversation (reset thread)."""
        self._service.reset_conversation()

    # ── Streaming ───────────────────────────────────────────────────────────

    def set_app(self, app: Any) -> None:
        """Set the Textual App reference for call_from_thread marshalling.

        The View calls this on mount so the controller can marshal callbacks
        back to the UI thread.
        """
        self._app = app

    def set_view(self, view: Any) -> None:
        """Set the View reference for streaming callbacks.

        The View calls this on mount so the controller can route streaming
        events to the View's show_* methods.
        """
        self._view = view

    def _run_agent(self, user_message: str, view: Any | None = None) -> None:
        """Run the agent and route streaming events to the View.

        **Runs on the worker thread.** All View calls are marshalled to the
        UI thread via ``app.call_from_thread()``.

        Args:
            user_message: The user's input text.
            view: The View object (duck-typed, has show_* methods). If None,
                  the controller will use its stored reference.
        """
        if view is None:
            view = self._view  # May be None if not set

        app = self._app

        def marshal(fn: Any, *args: Any) -> None:
            """Marshal a View call to the UI thread."""
            if app is not None:
                app.call_from_thread(fn, *args)
            elif view is not None:
                # Fallback: call directly (used in tests without an App)
                fn(*args)

        try:
            self._service.stream_agent(
                user_message=user_message,
                on_reasoning=lambda t: marshal(
                    getattr(view, "show_thinking", lambda _: None), t
                ),
                on_tool_call=lambda n, a: marshal(
                    getattr(view, "show_tool_call", lambda n, a: None), n, a
                ),
                on_tool_result=lambda n, r: marshal(
                    getattr(view, "show_tool_result", lambda n, r: None), n, r
                ),
                on_answer=lambda t: marshal(
                    getattr(view, "show_answer_chunk", lambda _: None), t
                ),
                on_done=lambda: marshal(
                    getattr(view, "show_answer_final", lambda: None)
                ),
                on_error=lambda e: marshal(
                    getattr(view, "show_error", lambda _: None), e
                ),
            )
        except Exception as exc:
            if view is not None:
                marshal(getattr(view, "show_error", lambda _: None), str(exc))

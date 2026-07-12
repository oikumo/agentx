"""Freeze regression tests for ReAct screen.

These tests verify that the ReAct screen doesn't freeze the UI thread
during agent execution, similar to the fixes in feature_011 and feature_014.
"""

from __future__ import annotations

import asyncio
import threading
import time
from unittest.mock import MagicMock, patch

import pytest


class TestReactFreezeRegression:
    """Regression tests for UI freezing during ReAct agent execution."""

    def test_react_agent_runs_off_ui_thread(self) -> None:
        """The agent should run on a background thread, not the UI thread."""
        from agentx.ui.screens.react.react_controller import ReactController
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_service = MagicMock(spec=ReactAgentService)
        mock_service.is_running = False
        mock_service._cancel_event = MagicMock()
        mock_service._cancel_event.is_set.return_value = False

        controller = ReactController(service=mock_service)
        mock_app = MagicMock()
        controller.set_app(mock_app)
        mock_view = MagicMock()
        controller.set_view(mock_view)

        # Track which thread the stream_agent is called on
        thread_id = None

        def capture_thread(*args, **kwargs):
            nonlocal thread_id
            thread_id = threading.current_thread().ident

        mock_service.stream_agent.side_effect = capture_thread

        controller.send_message("test message")
        time.sleep(0.2)  # Wait for thread to start

        # The stream_agent should be called on a different thread than main
        assert thread_id is not None
        assert thread_id != threading.main_thread().ident

    def test_react_escape_during_agent_run(self) -> None:
        """Escape should call on_unmount which cancels the agent."""
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        mock_controller = MagicMock()
        mock_controller.is_running = True
        screen = ReactTUIScreen(mock_controller)

        # Mock the app
        mock_app = MagicMock()
        screen._app = mock_app
        screen._is_mounted = True

        # Call on_unmount directly (which is what happens on Escape/Back)
        with patch("agentx.ui.tui.framework.base_screen.BaseAgentXScreen.on_unmount"):
            screen.on_unmount()

        # Should cancel the running agent
        mock_controller.cancel.assert_called_once()

    def test_react_q_quits_during_agent_run(self) -> None:
        """'q' key should quit even during agent execution."""
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        mock_controller = MagicMock()
        mock_controller.is_running = True
        screen = ReactTUIScreen(mock_controller)

        mock_app = MagicMock()
        screen._app = mock_app
        screen._is_mounted = True

        with patch.object(screen, "action_quit") as mock_quit:
            with patch.object(screen, "query_one") as mock_query:
                mock_input = MagicMock()
                mock_input.value = "q"
                mock_query.return_value = mock_input
                screen.action_send()
                mock_quit.assert_called_once()

    def test_react_cancel_stops_streaming(self) -> None:
        """Cancel should immediately stop the streaming loop."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        # Mock stream_events to simulate a stream with many chunks
        mock_stream = MagicMock()
        mock_message = MagicMock()
        mock_message.reasoning = iter([])

        # Create a slow iterator that we can interrupt
        def slow_text_iter():
            for i in range(100):
                time.sleep(0.001)  # Small delay to allow cancel to be checked
                yield "chunk"

        mock_message.text = slow_text_iter()
        mock_message.tool_calls = MagicMock()
        mock_message.tool_calls.get.return_value = []
        mock_stream.messages = [mock_message]
        mock_stream.tool_calls = iter([])
        mock_stream.output = {"messages": []}

        service._agent.stream_events = MagicMock(return_value=mock_stream)

        on_done = MagicMock()
        on_answer = MagicMock()

        # Start streaming in background thread
        def run_stream():
            service.stream_agent(
                user_message="test",
                on_reasoning=MagicMock(),
                on_tool_call=MagicMock(),
                on_tool_result=MagicMock(),
                on_answer=on_answer,
                on_done=on_done,
                on_error=MagicMock(),
            )

        thread = threading.Thread(target=run_stream, daemon=True)
        thread.start()

        # Give it time to start streaming
        time.sleep(0.05)

        # Cancel it from another thread
        service.cancel()

        # Wait for thread to finish
        thread.join(timeout=1.0)

        # on_done should NOT be called because we cancelled
        on_done.assert_not_called()

    def test_react_concurrent_send_rejected(self) -> None:
        """Second send_message should be rejected while first is running."""
        from agentx.ui.screens.react.react_controller import ReactController
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_service = MagicMock(spec=ReactAgentService)
        mock_service.is_running = True  # Already running
        controller = ReactController(service=mock_service)

        result = controller.send_message("second message")
        assert result is False

    def test_react_on_unmount_cancels(self) -> None:
        """Screen on_unmount should cancel running agent."""
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        mock_controller = MagicMock()
        mock_controller.is_running = True
        screen = ReactTUIScreen(mock_controller)

        with patch("agentx.ui.tui.framework.base_screen.BaseAgentXScreen.on_unmount"):
            screen.on_unmount()

        mock_controller.cancel.assert_called_once()


class TestReactBackgroundThreadCleanup:
    """Verify background threads are properly cleaned up."""

    def test_react_controller_worker_daemon(self) -> None:
        """Worker thread should be daemon so it dies with the app."""
        from agentx.ui.screens.react.react_controller import ReactController
        from agentx.model.react.react_agent_service import ReactAgentService

        # Use a real ReactAgentService but with mocked LLM and stream_agent
        mock_llm = MagicMock()
        mock_service = ReactAgentService(llm=mock_llm)
        mock_service.stream_agent = MagicMock()

        controller = ReactController(service=mock_service)

        mock_app = MagicMock()
        controller.set_app(mock_app)
        mock_view = MagicMock()
        controller.set_view(mock_view)

        controller.send_message("test")
        time.sleep(0.1)

        assert controller._worker_thread is not None
        assert controller._worker_thread.daemon is True

    def test_react_screen_on_unmount_cancels_and_calls_super(self) -> None:
        """Screen on_unmount should call super().on_unmount() and cancel."""
        from agentx.ui.tui.screens.react_screen import ReactTUIScreen

        mock_controller = MagicMock()
        mock_controller.is_running = True
        screen = ReactTUIScreen(mock_controller)

        with patch("agentx.ui.tui.framework.base_screen.BaseAgentXScreen.on_unmount") as mock_super:
            screen.on_unmount()
            mock_super.assert_called_once()
            mock_controller.cancel.assert_called_once()

    def test_react_service_cancel_event_cleared_after_stream(self) -> None:
        """Cancel event should be cleared after stream completes (normal or error)."""
        from agentx.model.react.react_agent_service import ReactAgentService

        mock_llm = MagicMock()
        service = ReactAgentService(llm=mock_llm)

        mock_stream = MagicMock()
        mock_message = MagicMock()
        mock_message.reasoning = iter([])
        mock_message.text = iter(["done"])
        mock_message.tool_calls = MagicMock()
        mock_message.tool_calls.get.return_value = []
        mock_stream.messages = [mock_message]
        mock_stream.tool_calls = iter([])
        mock_stream.output = {"messages": []}

        service._agent.stream_events = MagicMock(return_value=mock_stream)

        on_done = MagicMock()
        service.stream_agent(
            user_message="test",
            on_reasoning=MagicMock(),
            on_tool_call=MagicMock(),
            on_tool_result=MagicMock(),
            on_answer=MagicMock(),
            on_done=on_done,
            on_error=MagicMock(),
        )

        # After completion, cancel event should be cleared
        assert service._cancel_event.is_set() is False
        assert service.is_running is False
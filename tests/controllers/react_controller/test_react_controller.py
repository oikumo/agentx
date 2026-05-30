"""
Unit + Integration tests for ReActController.

Follows OMT++ §11:
  - Stage 1: Unit test Controller with mocked View + mocked Agent
  - Stage 2: Integration test Controller + View with mocked Agent

Tests use the Abstract Partner interface (IReActViewPartner) to verify wiring.
"""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import MagicMock, patch

from agentx.ui.screens.react.react_controller import ReActController
from agentx.ui.screens.react.react_view import IReActViewPartner


class TestReActControllerUnit(TestCase):
    """Unit tests — Controller with mock View and mock Agent."""

    def setUp(self) -> None:
        self.controller = ReActController()
        # Replace real view with mock
        self.mock_view = MagicMock()
        self.controller._view = self.mock_view
        # Replace real agent with mock
        self.mock_agent = MagicMock()
        self.controller._agent = self.mock_agent

    def test_controller_implements_partner_interface(self) -> None:
        """ReActController should be an instance of IReActViewPartner."""
        assert isinstance(self.controller, IReActViewPartner)

    def test_controller_has_process_task_method(self) -> None:
        """Should implement process_task as defined in Abstract Partner."""
        result = self.controller.process_task("test task")
        assert result is True

    def test_controller_has_close_method(self) -> None:
        """Should implement close() as defined in Abstract Partner."""
        # Should not raise
        self.controller.close()

    def test_process_task_streams_agent_events_to_view(self) -> None:
        """Agent events should be dispatched to the correct view method."""
        # Mock agent.stream() to yield events
        self.mock_agent.stream.return_value = [
            {"event_type": "thought", "content": "I need to calculate", "metadata": {}},
            {"event_type": "tool_call", "content": "calculator(2+2)", "metadata": {"name": "calculator", "args": {"expression": "2+2"}}},
            {"event_type": "observation", "content": "4", "metadata": {"tool": "calculator"}},
            {"event_type": "answer", "content": "The answer is 4", "metadata": {}},
        ]

        self.controller.process_task("what is 2+2?")

        self.mock_view.display_thought.assert_called_once_with("I need to calculate")
        self.mock_view.display_tool_call.assert_called_once_with("calculator(2+2)")
        self.mock_view.display_observation.assert_called_once_with("4")
        self.mock_view.display_answer.assert_called_once_with("The answer is 4")

    def test_process_task_handles_unknown_event_type(self) -> None:
        """Unknown event types should fall through to display_thought."""
        self.mock_agent.stream.return_value = [
            {"event_type": "unknown_type", "content": "something", "metadata": {}},
        ]

        self.controller.process_task("test")

        self.mock_view.display_thought.assert_called_once_with("something")

    def test_process_task_handles_exception_gracefully(self) -> None:
        """If agent.stream() raises, an error should be displayed and loop continues."""
        self.mock_agent.stream.side_effect = RuntimeError("LLM unavailable")

        result = self.controller.process_task("test")

        assert result is True  # Loop continues
        self.mock_view.display_error.assert_called_once()

    def test_show_delegates_to_view_show(self) -> None:
        """show() should call view.show()."""
        self.controller.show()
        self.mock_view.show.assert_called_once()

    def test_close_does_not_raise(self) -> None:
        """close() should be a no-op, not raise."""
        self.controller.close()  # Should pass

    def test_controller_creates_view_in_init(self) -> None:
        """The real controller should create a ReActView on init."""
        controller = ReActController()
        assert controller._view is not None
        assert hasattr(controller._view, "show")

    def test_controller_creates_agent_in_init(self) -> None:
        """The real controller should create a ReActAgent on init."""
        controller = ReActController()
        assert controller._agent is not None
        assert hasattr(controller._agent, "stream")


class TestReActControllerIntegration(TestCase):
    """Integration tests — Controller + real View with mock Agent."""

    def setUp(self) -> None:
        self.controller = ReActController()
        # Keep real view, mock only the agent
        self.mock_agent = MagicMock()
        self.controller._agent = self.mock_agent

    def test_controller_wires_to_view_correctly(self) -> None:
        """Controller._view should have a reference to controller as partner."""
        assert self.controller._view._partner is self.controller

    def test_process_task_from_view_perspective(self) -> None:
        """Simulating what the view calls should flow through to view output methods."""
        self.mock_agent.stream.return_value = [
            {"event_type": "answer", "content": "42", "metadata": {}},
        ]

        with patch.object(self.controller._view.console, "header") as mock_header:
            with patch.object(self.controller._view.console, "success") as mock_success:
                self.controller.process_task("what is the meaning of life?")

                mock_header.assert_called_once_with("ANSWER")
                mock_success.assert_called_once_with("42")

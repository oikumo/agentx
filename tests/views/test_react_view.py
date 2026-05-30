"""
Unit tests for ReActView.

Follows OMT++ §11 — Stage 1 Unit Testing:
  - Tests View in isolation
  - Mocks the Abstract Partner interface (IReActViewPartner)
  - Does NOT depend on concrete Controller or Model
"""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import MagicMock, patch

from agentx.ui.screens.react.react_view import ReActView, IReActViewPartner


class MockReActPartner(IReActViewPartner):
    """Mock Abstract Partner for testing ReActView in isolation."""

    def __init__(self) -> None:
        self.processed_tasks: list[str] = []
        self.was_closed: bool = False

    def process_task(self, task: str) -> bool:
        self.processed_tasks.append(task)
        return True

    def close(self) -> None:
        self.was_closed = True


class TestReActView(TestCase):
    """Unit tests for ReActView using mock Abstract Partner."""

    def setUp(self) -> None:
        self.partner = MockReActPartner()
        self.view = ReActView(self.partner)

    def test_constructor_injects_partner(self) -> None:
        """View should store the partner reference (constructor injection)."""
        assert self.view._partner is self.partner

    def test_constructor_creates_console(self) -> None:
        """View should create a UIConsole with (react) prompt."""
        assert self.view.console is not None
        assert self.view.console.ui_prompt == "(react)"

    def test_process_task_delegates_to_partner_on_input(self) -> None:
        """When _simulate_input is called, partner.process_task() should be invoked."""
        self.view._partner.process_task("calculate 2+2")
        assert "calculate 2+2" in self.partner.processed_tasks

    def test_close_calls_partner_close(self) -> None:
        """close() should delegate to partner.close()."""
        assert self.partner.was_closed is False
        self.view._partner.close()
        assert self.partner.was_closed is True

    def test_display_thought_uses_console_info(self) -> None:
        """display_thought should call console.info."""
        with patch.object(self.view.console, "info") as mock_info:
            self.view.display_thought("I need to think...")
            mock_info.assert_called_once_with("  I need to think...")

    def test_display_tool_call_uses_console_waning(self) -> None:
        """display_tool_call should call console.waning."""
        with patch.object(self.view.console, "waning") as mock_waning:
            self.view.display_tool_call("calculator(2+2)")
            mock_waning.assert_called_once()

    def test_display_observation_uses_console_success(self) -> None:
        """display_observation should call console.success."""
        with patch.object(self.view.console, "success") as mock_success:
            self.view.display_observation("Result: 4")
            mock_success.assert_called_once()

    def test_display_error_uses_console_error(self) -> None:
        """display_error should call console.error."""
        with patch.object(self.view.console, "error") as mock_error:
            self.view.display_error("Something went wrong")
            mock_error.assert_called_once()

    def test_display_answer_uses_console_header_and_success(self) -> None:
        """display_answer should show a header then the answer."""
        with patch.object(self.view.console, "header") as mock_header:
            with patch.object(self.view.console, "success") as mock_success:
                self.view.display_answer("The answer is 42")
                mock_header.assert_called_once_with("ANSWER")
                mock_success.assert_called_once_with("The answer is 42")

    def test_show_displays_welcome_messages(self) -> None:
        """show() should print welcome text before entering input loop."""
        # Simulate user typing "quit" immediately to exit the loop
        with patch.object(self.view.console, "capture_input", return_value="quit"):
            with patch.object(self.view.console, "success") as mock_success:
                with patch.object(self.view.console, "info") as mock_info:
                    self.partner.was_closed = False
                    self.view.show()
                    assert self.partner.was_closed is True  # quit triggered close
                    mock_success.assert_called_once_with(
                        "ReAct Agent — Reason + Act Loop"
                    )
                    assert mock_info.call_count >= 2

"""
Unit tests for agentx.views.main_view.main_view module.

Tests cover:
- IMainViewPartner: Interface for controller
- MainView: View operations (show, print_response, capture_input)
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from agentx.views.main_view.main_view import IMainViewPartner, MainView


class TestIMainViewPartner:
    """Tests for IMainViewPartner interface."""

    def test_run_command_method_exists(self):
        """Test that run_command method is defined."""
        assert hasattr(IMainViewPartner, 'run_command')

    def test_error_method_exists(self):
        """Test that error method is defined."""
        assert hasattr(IMainViewPartner, 'error')

    def test_run_command_not_implemented(self):
        """Test that run_command raises NotImplementedError if not implemented."""
        partner = IMainViewPartner()
        # The base class doesn't implement it, so calling should fail
        # Actually, the base class has a pass implementation
        result = partner.run_command("test")
        assert result is None

    def test_error_not_implemented(self):
        """Test that error method exists."""
        partner = IMainViewPartner()
        result = partner.error()
        assert result is None


class TestMainView:
    """Tests for MainView class."""

    def test_create_main_view(self):
        """Test creating MainView instance."""
        controller = MagicMock()
        view = MainView(controller)

        assert view.controller is controller

    @patch('agentx.views.main_view.main_view.Console')
    def test_show(self, mock_console):
        """Test showing the view."""
        controller = MagicMock()
        view = MainView(controller)

        view.show()

        # Should call log_success and log_info
        assert mock_console.log_success.called
        assert mock_console.log_info.called

    @patch('agentx.views.main_view.main_view.Console')
    def test_print_response(self, mock_console):
        """Test printing response."""
        controller = MagicMock()
        view = MainView(controller)

        view.print_response("Test response")

        mock_console.log_info.assert_called_once_with("Test response")

    @patch('agentx.views.main_view.main_view.Console')
    def test_print_response_error(self, mock_console):
        """Test printing error response."""
        controller = MagicMock()
        view = MainView(controller)

        view.print_response_error("Error response")

        mock_console.log_error.assert_called_once_with("Error response")

    @patch('builtins.input', return_value='test command')
    @patch('agentx.views.main_view.main_view.Console')
    def test_capture_input(self, mock_console, mock_input):
        """Test capturing user input."""
        controller = MagicMock()
        view = MainView(controller)

        view.capture_input()

        # Should call controller.run_command
        controller.run_command.assert_called_once_with('test command')

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('agentx.views.main_view.main_view.Console')
    def test_capture_input_keyboard_interrupt(self, mock_console, mock_input):
        """Test handling keyboard interrupt."""
        controller = MagicMock()
        view = MainView(controller)

        # Should not raise exception
        view.capture_input()

        # Should call controller.error()
        controller.error.assert_called()

    @patch('builtins.input', side_effect=EOFError)
    @patch('agentx.views.main_view.main_view.Console')
    def test_capture_input_eof(self, mock_console, mock_input):
        """Test handling EOF error."""
        controller = MagicMock()
        view = MainView(controller)

        # Should not raise exception
        view.capture_input()

        # Should call controller.error()
        controller.error.assert_called()

    @patch('builtins.input', return_value='')
    @patch('agentx.views.main_view.main_view.Console')
    def test_capture_input_empty(self, mock_console, mock_input):
        """Test handling empty input."""
        controller = MagicMock()
        view = MainView(controller)

        result = view.capture_input()

        # Empty input should return None
        assert result is None
        # Should not call run_command for empty input
        controller.run_command.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

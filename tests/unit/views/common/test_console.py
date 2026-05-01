"""
Unit tests for agentx.views.common.console module.

Tests cover:
- Colors: ANSI color codes
- Console: Logging methods (info, success, error, warning, header)
"""

import pytest
from io import StringIO
import sys
from unittest.mock import patch

from agentx.views.common.console import Colors, Console


class TestColors:
    """Tests for Colors class."""

    def test_color_codes_exist(self):
        """Test that all color codes are defined."""
        assert hasattr(Colors, 'PURPLE')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'DARKCYAN')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'UNDERLINE')
        assert hasattr(Colors, 'END')

    def test_color_codes_are_strings(self):
        """Test that color codes are strings."""
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.RED, str)

    def test_color_codes_not_empty(self):
        """Test that color codes are not empty."""
        assert len(Colors.CYAN) > 0
        assert len(Colors.END) > 0


class TestConsole:
    """Tests for Console class."""

    @patch('builtins.print')
    def test_log_info(self, mock_print):
        """Test logging info message."""
        Console.log_info("Test message")
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        assert "Test message" in call_args
        assert "ℹ️" in call_args

    @patch('builtins.print')
    def test_log_info_with_custom_color(self, mock_print):
        """Test logging info with custom color."""
        Console.log_info("Test message", Colors.BLUE)
        mock_print.assert_called()

    @patch('builtins.print')
    def test_log_success(self, mock_print):
        """Test logging success message."""
        Console.log_success("Success!")
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        assert "Success!" in call_args
        assert "✅" in call_args

    @patch('builtins.print')
    def test_log_error(self, mock_print):
        """Test logging error message."""
        Console.log_error("Error occurred")
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        assert "Error occurred" in call_args
        assert "❌" in call_args

    @patch('builtins.print')
    def test_log_warning(self, mock_print):
        """Test logging warning message."""
        Console.log_warning("Warning message")
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        assert "Warning message" in call_args
        assert "⚠️" in call_args

    @patch('builtins.print')
    def test_log_header(self, mock_print):
        """Test logging header."""
        Console.log_header("Test Header")
        # Header should print multiple times (separator, content, separator)
        assert mock_print.call_count >= 3
        
        # Check all calls contain the header text
        all_calls_text = str(mock_print.call_args_list)
        assert "Test Header" in all_calls_text
        assert "🚀" in all_calls_text

    def test_console_output_format(self):
        """Test that console output includes ANSI codes."""
        # Capture stdout
        captured = StringIO()
        sys.stdout = captured

        try:
            Console.log_info("Test")
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        # Should contain ANSI color codes
        assert "\033[" in output
        assert "Test" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

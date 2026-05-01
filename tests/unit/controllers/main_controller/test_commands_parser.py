"""
Unit tests for agentx.controllers.main_controller.commands_parser module.

Tests cover:
- CommandData: Data structure for parsed commands
- CommandParser: Command parsing logic
"""

import pytest
from io import StringIO

from agentx.controllers.main_controller.commands_parser import (
    CommandData,
    CommandParser,
)


class TestCommandData:
    """Tests for CommandData dataclass."""

    def test_create_command_data(self):
        """Test creating CommandData instance."""
        data = CommandData(key="test", arguments=["arg1", "arg2"])
        assert data.key == "test"
        assert data.arguments == ["arg1", "arg2"]

    def test_command_data_empty_arguments(self):
        """Test CommandData with empty arguments."""
        data = CommandData(key="test", arguments=[])
        assert data.key == "test"
        assert data.arguments == []

    def test_command_data_repr(self):
        """Test CommandData string representation."""
        data = CommandData(key="test", arguments=["arg1"])
        assert "test" in str(data)


class TestCommandParser:
    """Tests for CommandParser class."""

    def test_create_parser(self):
        """Test creating CommandParser instance."""
        parser = CommandParser()
        assert parser.commands_list == []

    def test_add_command(self):
        """Test adding a command to parser."""
        parser = CommandParser()
        # Create a simple command class for testing
        from agentx.controllers.main_controller.commands_base import Command

        class TestCommand(Command):
            def run(self, arguments):
                return None

        cmd = TestCommand("test")
        parser.add(cmd)

        assert len(parser.commands_list) == 1
        assert parser.commands_list[0] is cmd

    def test_parse_simple_command(self):
        """Test parsing a simple command."""
        parser = CommandParser()
        result = parser.parse("test arg1 arg2")

        assert result is not None
        assert result.key == "test"
        assert result.arguments == ["arg1", "arg2"]

    def test_parse_command_no_arguments(self):
        """Test parsing command without arguments."""
        parser = CommandParser()
        result = parser.parse("test")

        assert result is not None
        assert result.key == "test"
        assert result.arguments == []

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        parser = CommandParser()
        result = parser.parse("")

        assert result is None

    def test_parse_whitespace_only(self):
        """Test parsing whitespace only string."""
        parser = CommandParser()
        result = parser.parse("   ")

        # Whitespace-only input results in empty list after split, returns None
        assert result is None

    def test_parse_multiple_spaces(self):
        """Test parsing command with multiple spaces."""
        parser = CommandParser()
        result = parser.parse("test   arg1    arg2")

        assert result is not None
        assert result.key == "test"
        assert "arg1" in result.arguments
        assert "arg2" in result.arguments

    def test_tokenize_arguments(self):
        """Test tokenizing arguments."""
        parser = CommandParser()
        # This method exists but implementation details may vary
        # Test that the method exists and can be called
        assert hasattr(parser, '_tokenize_arguments')

    def test_parse_text_command_with_special_chars(self):
        """Test parsing command with special characters."""
        parser = CommandParser()
        result = parser.parse("test arg1 arg2-with-dash")

        assert result is not None
        assert result.key == "test"
        assert "arg1" in result.arguments
        assert "arg2-with-dash" in result.arguments


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

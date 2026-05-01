"""
Unit tests for agentx.controllers.main_controller.commands_base module.

Tests cover:
- CommandResult: Abstract base class
- Command: Abstract base class with key and description
"""

import pytest
from abc import ABC

from agentx.controllers.main_controller.commands_base import (
    CommandResult,
    Command,
)


class TestCommandResult:
    """Tests for CommandResult abstract class."""

    def test_command_result_is_abstract(self):
        """Test that CommandResult is an abstract class."""
        assert issubclass(CommandResult, ABC)

    def test_command_result_cannot_be_instantiated(self):
        """Test that abstract CommandResult cannot be instantiated."""
        with pytest.raises(TypeError):
            CommandResult()

    def test_command_result_subclass_must_implement_apply(self):
        """Test that subclasses must implement apply method."""

        class IncompleteResult(CommandResult):
            pass

        with pytest.raises(TypeError):
            IncompleteResult()

    def test_command_result_subclass_implementation(self):
        """Test that concrete implementation works."""

        class ConcreteResult(CommandResult):
            def apply(self):
                return "applied"

        result = ConcreteResult()
        assert result.apply() == "applied"


class TestCommand:
    """Tests for Command abstract class."""

    def test_command_is_abstract(self):
        """Test that Command is an abstract class."""
        assert issubclass(Command, ABC)

    def test_command_cannot_be_instantiated(self):
        """Test that abstract Command cannot be instantiated."""
        with pytest.raises(TypeError):
            Command("test")

    def test_command_subclass_must_implement_run(self):
        """Test that subclasses must implement run method."""

        class IncompleteCommand(Command):
            pass

        with pytest.raises(TypeError):
            IncompleteCommand("test")

    def test_command_initialization(self):
        """Test that concrete implementation works."""

        class ConcreteCommand(Command):
            def run(self, arguments):
                return None

        cmd = ConcreteCommand("test_key", "Test description")
        assert cmd.key == "test_key"
        assert cmd.description == "Test description"

    def test_command_default_description(self):
        """Test command with default description."""

        class ConcreteCommand(Command):
            def run(self, arguments):
                return None

        cmd = ConcreteCommand("test_key")
        assert cmd.description == ""

    def test_command_run_returns_result(self):
        """Test command run method returns result."""

        class ConcreteCommand(Command):
            def run(self, arguments):
                return f"Executed with {arguments}"

        cmd = ConcreteCommand("test")
        result = cmd.run(["arg1", "arg2"])
        assert result == "Executed with ['arg1', 'arg2']"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

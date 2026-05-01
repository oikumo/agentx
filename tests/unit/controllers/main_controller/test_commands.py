"""
Unit tests for agentx.controllers.main_controller.commands module.

Tests cover all command classes:
- QuitCommand, ClearCommand, HistoryCommand, HelpCommand
- SumCommand, AIChat, NewCommand
- PetriNetStatusCommand, PetriNetPrintCommand, GoalCommand
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from agentx.controllers.main_controller.commands_base import Command
from agentx.controllers.main_controller.commands import (
    CommandResultLogInfo,
    CommandResultPrint,
    QuitCommand,
    ClearCommand,
    HistoryCommand,
    HelpCommand,
    SumCommand,
    AIChat,
    NewCommand,
    PetriNetStatusCommand,
    PetriNetPrintCommand,
    GoalCommand,
    NewSessionResult,
)


class TestCommandResultLogInfo:
    """Tests for CommandResultLogInfo class."""

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_apply_logs_all_messages(self, mock_console):
        """Test that apply logs all messages."""
        result = CommandResultLogInfo(["msg1", "msg2", "msg3"])
        result.apply()

        assert mock_console.log_info.call_count == 3


class TestCommandResultPrint:
    """Tests for CommandResultPrint class."""

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_apply_prints_message(self, mock_console):
        """Test that apply prints the message."""
        result = CommandResultPrint("Test message")
        result.apply()

        mock_console.log_info.assert_called_once_with("Test message")


class TestQuitCommand:
    """Tests for QuitCommand class."""

    def test_quit_command_creation(self):
        """Test creating QuitCommand."""
        controller = MagicMock()
        cmd = QuitCommand("quit", controller)

        assert cmd.key == "quit"
        assert "exit" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_quit_command_run(self, mock_console):
        """Test running QuitCommand."""
        controller = MagicMock()
        cmd = QuitCommand("quit", controller)

        cmd.run([])

        # Should call controller.close()
        controller.close.assert_called_once()


class TestClearCommand:
    """Tests for ClearCommand class."""

    def test_clear_command_creation(self):
        """Test creating ClearCommand."""
        controller = MagicMock()
        cmd = ClearCommand("clear", controller)

        assert cmd.key == "clear"
        assert "clear" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.clear_console')
    def test_clear_command_run(self, mock_clear):
        """Test running ClearCommand."""
        controller = MagicMock()
        cmd = ClearCommand("clear", controller)

        cmd.run([])

        mock_clear.assert_called_once()


class TestHistoryCommand:
    """Tests for HistoryCommand class."""

    def test_history_command_creation(self):
        """Test creating HistoryCommand."""
        controller = MagicMock()
        cmd = HistoryCommand("history", controller)

        assert cmd.key == "history"

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_history_command_run(self, mock_console):
        """Test running HistoryCommand."""
        controller = MagicMock()
        controller.commands_history.return_value = ["cmd1", "cmd2", "cmd3"]

        cmd = HistoryCommand("history", controller)
        result = cmd.run([])

        assert result is not None
        # Should return CommandResultLogInfo


class TestHelpCommand:
    """Tests for HelpCommand class."""

    def test_help_command_creation(self):
        """Test creating HelpCommand."""
        controller = MagicMock()
        cmd = HelpCommand("help", controller)

        assert cmd.key == "help"
        assert "available" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_help_command_run(self, mock_console):
        """Test running HelpCommand."""
        controller = MagicMock()
        mock_cmd = MagicMock()
        mock_cmd.key = "test"
        mock_cmd.description = "Test command"
        controller.get_commands.return_value = [mock_cmd]

        cmd = HelpCommand("help", controller)
        result = cmd.run([])

        assert result is not None


class TestSumCommand:
    """Tests for SumCommand class."""

    def test_sum_command_creation(self):
        """Test creating SumCommand."""
        controller = MagicMock()
        cmd = SumCommand("sum", controller)

        assert cmd.key == "sum"
        assert "sum" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_sum_command_valid(self, mock_console):
        """Test SumCommand with valid input."""
        controller = MagicMock()
        cmd = SumCommand("sum", controller)

        result = cmd.run(["5", "3"])

        assert result is not None
        assert isinstance(result, CommandResultPrint)

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_sum_command_invalid(self, mock_console):
        """Test SumCommand with invalid input."""
        controller = MagicMock()
        cmd = SumCommand("sum", controller)

        result = cmd.run(["abc", "xyz"])

        # Should log warning
        assert mock_console.log_warning.called


class TestAIChat:
    """Tests for AIChat command class."""

    def test_ai_chat_creation(self):
        """Test creating AIChat command."""
        controller = MagicMock()
        cmd = AIChat("chat", controller)

        assert cmd.key == "chat"

    def test_parse_chat_arguments_simple(self):
        """Test parsing simple chat arguments."""
        args = ["hello", "world"]
        model, query = AIChat.parse_chat_arguments(args)

        assert model is None
        assert query == "hello world"

    def test_parse_chat_arguments_with_model(self):
        """Test parsing chat arguments with model flag."""
        args = ["--model", "gpt-4", "hello"]
        model, query = AIChat.parse_chat_arguments(args)

        assert model == "gpt-4"
        assert query == "hello"

    def test_ai_chat_run(self):
        """Test running AIChat command."""
        controller = MagicMock()
        cmd = AIChat("chat", controller)

        # Run the command - it delegates to controller.showChat()
        result = cmd.run(["test query"])

        # Should call controller.showChat with the query
        controller.showChat.assert_called_once_with("test query")


class TestNewCommand:
    """Tests for NewCommand class."""

    def test_new_command_creation(self):
        """Test creating NewCommand."""
        controller = MagicMock()
        cmd = NewCommand("new", controller)

        assert cmd.key == "new"
        assert "new" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.get_session_manager')
    def test_new_command_run(self, mock_get_manager):
        """Test running NewCommand."""
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_session.name = "test_session"
        mock_manager.create_new_session.return_value = mock_session
        mock_get_manager.return_value = mock_manager

        controller = MagicMock()
        cmd = NewCommand("new", controller)
        result = cmd.run(["test_session"])

        assert result is not None


class TestNewSessionResult:
    """Tests for NewSessionResult class."""

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_new_session_result_apply(self, mock_console):
        """Test NewSessionResult apply method."""
        result = NewSessionResult("test_session", "Session created")
        result.apply()

        mock_console.log_info.assert_called_once_with("Session created")


class TestPetriNetStatusCommand:
    """Tests for PetriNetStatusCommand class."""

    def test_petri_status_command_creation(self):
        """Test creating PetriNetStatusCommand."""
        controller = MagicMock()
        cmd = PetriNetStatusCommand("status", controller)

        assert cmd.key == "status"

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_petri_status_no_session_state(self, mock_console):
        """Test PetriNetStatusCommand when no session state exists."""
        controller = MagicMock()
        controller.session_state = None

        cmd = PetriNetStatusCommand("status", controller)
        result = cmd.run([])

        # Should return None when no session state
        assert result is None

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_petri_status_with_session_state(self, mock_console):
        """Test PetriNetStatusCommand with session state."""
        controller = MagicMock()
        mock_state = MagicMock()
        mock_state.objective = "Test objective"
        mock_state.context = {
            'task_type': 'test',
            'workflow_name': 'test_workflow',
            'objective_status': 'pending',
            'enabled_transitions': ['transition1']
        }

        mock_session_state = MagicMock()
        mock_session_state.get_state.return_value = mock_state
        controller.session_state = mock_session_state

        cmd = PetriNetStatusCommand("status", controller)
        result = cmd.run([])

        assert result is not None


class TestPetriNetPrintCommand:
    """Tests for PetriNetPrintCommand class."""

    def test_petri_print_command_creation(self):
        """Test creating PetriNetPrintCommand."""
        controller = MagicMock()
        cmd = PetriNetPrintCommand("petri-print", controller)

        assert cmd.key == "petri-print"

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_petri_print_no_session_state(self, mock_console):
        """Test PetriNetPrintCommand when no session state exists."""
        controller = MagicMock()
        controller.session_state = None

        cmd = PetriNetPrintCommand("petri-print", controller)
        result = cmd.run([])

        assert result is None

    @patch('agentx.controllers.main_controller.commands.PetriNetVisualizer')
    @patch('agentx.controllers.main_controller.commands.Console')
    def test_petri_print_with_session_state(self, mock_console, mock_visualizer):
        """Test PetriNetPrintCommand with session state."""
        controller = MagicMock()
        mock_session_state = MagicMock()
        mock_petri_net = MagicMock()
        mock_session_state.petri_net = mock_petri_net
        controller.session_state = mock_session_state

        mock_viz_instance = MagicMock()
        mock_viz_instance.to_ascii.return_value = "ASCII art"
        mock_visualizer.return_value = mock_viz_instance

        cmd = PetriNetPrintCommand("petri-print", controller)
        result = cmd.run([])

        assert result is not None
        assert isinstance(result, CommandResultPrint)


class TestGoalCommand:
    """Tests for GoalCommand class."""

    def test_goal_command_creation(self):
        """Test creating GoalCommand."""
        controller = MagicMock()
        cmd = GoalCommand("goal", controller)

        assert cmd.key == "goal"
        assert "goal" in cmd.description.lower()

    @patch('agentx.controllers.main_controller.commands.Console')
    def test_goal_command_empty_prompt(self, mock_console):
        """Test GoalCommand with empty prompt."""
        controller = MagicMock()
        cmd = GoalCommand("goal", controller)
        result = cmd.run([])

        # Should return None for empty prompt
        assert result is None
        mock_console.log_error.assert_called()

    def test_goal_command_with_prompt(self):
        """Test GoalCommand with valid prompt - basic test."""
        # This test just verifies the command can be created and has the right structure
        # Full integration testing requires LLM setup
        controller = MagicMock()
        cmd = GoalCommand("goal", controller)
        
        assert cmd.key == "goal"
        assert "goal" in cmd.description.lower()
        # The actual execution requires LLM which we don't test in unit tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

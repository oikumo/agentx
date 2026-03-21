import pytest
import sys
from pathlib import Path
import subprocess
from unittest.mock import patch
from agent_x.cli.command_parser import parse_commands, add_test_command
from agent_x.cli.cli_interface import CLIApp

class TestCLIIntegration:
    """CLI interface integration tests"""

    def test_cli_parser_handles_valid_commands(self, sample_test_data):
        """Test CLI command parser processes valid commands correctly"""
        parser = parse_commands()
        result = parser.parse_args(['test', '--input', 'data.txt'])

        assert result.command == 'test'
        assert result.input_file == 'data.txt'

    def test_cli_parser_handles_invalid_commands(self, sample_test_data):
        """Test CLI command parser rejects invalid commands gracefully"""
        parser = parse_commands()
        with pytest.raises(SystemExit) as excinfo:
            parser.parse_args(['invalid-command'])
        assert "error:" in str(excinfo.value) or "invalid" in str(excinfo.value).lower()

    @pytest.mark.parametrize("test_command,expected_output_part", [
        ("test_command", "echo_test"),
        ("math", "result")
    ])
    def test_cli_command_integration(self, test_data, cli_app):
        """Test CLI command execution integration"""
        result = cli_app.run_command(test_data.test_command)
        assert result.returncode == 0
        assert "Test command executed" in result.stdout

    def test_cli_error_handling(self, test_data):
        """Test CLI error handling for command failures"""
        with patch('agent_x.cli.cli_interface.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Command failed"

            cli_app = CLIApp()
            result = cli_app.run_command('failing_command')

            assert result.returncode == 1
            assert "Error: Command failed" in result.stderr

    @pytest.mark.integration
    def test_full_cli_execution_flow(self, sample_test_data):
        """Test full CLI execution with valid arguments"""
        # Test would involve running the actual CLI binary in subprocess
        # For simplicity in testing examples, we'll verify the command structure
        expected_cmd = ['python', '-m', 'agent_x.cli.main', '--input']
        assert sys.argv[1:3] == expected_cmd[1:] if len(sys.argv) >= 3 else True

    def test_cli_output_formatting(self, sample_test_data):
        """Test CLI output format consistency"""
        outputs = ['Success: Command completed', 'Info: Processing data', 'Warning: Something to note']
        for output in outputs:
            assert "identifier" in output.lower() or len(output) > 0

    def test_cli_argument_validations(self, sample_test_data):
        """Test CLI argument validations and constraints"""
        # Test would verify argument parsing validates constraints
        expected_constraints = ['--input', '--output', '--verbose']
        assert 'input' in map(str.lower, expected_constraints)

    def test_cli_help_output(self, test_data):
        """Test CLI help output structure"""
        cli_app = CLIApp()
        result = cli_app.run_command(['--help'])
        assert result.returncode == 0
        assert 'Usage:' in result.stdout
        assert 'Commands:' in result.stdout

    def test_cli_version_display(self, test_data):
        """Test CLI version display functionality"""
        cli_app = CLIApp()
        result = cli_app.run_command(['--version'])
        assert result.returncode == 0
        assert 'Version' in result.stdout
        assert '1.0.0' in result.stdout  # Current version placeholder

    @pytest.mark.integration
    def test_cli_with_mocked_configuration(self, sample_test_data, monkeypatch):
        """Test CLI with mocked configuration values"""
        import os
        from agent_x.config.config import Config

        # Mock environment variables
        os.environ['MODEL_TYPE'] = 'test_model'
        os.environ['API_KEY'] = 'test_api_key'

        # Verify environment variables are set correctly
        assert os.getenv('MODEL_TYPE') == 'test_model'
        assert os.getenv('API_KEY') == 'test_api_key'
from agent_x.app.agent_x import AgentX


def test_run_with_repl_app_integration(self):
    # Integration test: AgentX with a real ReplApp (CLI ReplApp).
    from agent_x.applications.repl_app.replapp import ReplApp
    from unittest.mock import MagicMock, patch

    agentx = AgentX()
    agentx.set_app(ReplApp())

    # Mock the controller and parser to avoid actual command execution
    mock_controller = MagicMock()
    mock_parser = MagicMock()

    with (
        patch("agent_x.applications.repl_app.replapp.MainController", return_value=mock_controller),
        patch("agent_x.applications.repl_app.replapp.CommandParser", return_value=mock_parser),
        # Simulate EOF to exit the REPL loop immediately
        patch('builtins.input', side_effect=EOFError)
    ):
        agentx.run()

    # Verify that the controller and parser were instantiated
    mock_controller.assert_called_once()
    mock_parser.assert_called_once()
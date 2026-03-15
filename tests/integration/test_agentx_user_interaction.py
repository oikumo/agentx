import unittest
from unittest.mock import patch
from agent_x.app.agent_x import AgentX


class TestAgentXUserInteraction(unittest.TestCase):
    """Integration tests for AgentX user interaction."""

    def test_run_with_repl_app_integration(self):
        """Integration test: AgentX with a real ReplApp (CLI ReplApp)."""
        from agent_x.applications.repl_app.replapp import ReplApp

        agentx = AgentX()
        app = ReplApp()
        # Verify that the ReplApp has been initialized with a controller and parser
        self.assertIsNotNone(app.controller)
        self.assertIsNotNone(app.parser)
        agentx.set_app(app)

        # Simulate EOF to exit the REPL loop immediately
        with patch("builtins.input", side_effect=EOFError):
            agentx.run()

        # If we get here without exception, the test passes.

    def test_run_without_app_raises_error(self):
        """Test that running AgentX without setting an app raises ValueError."""
        agentx = AgentX()

        with self.assertRaises(ValueError) as context:
            agentx.run()

        self.assertIn("No app set", str(context.exception))

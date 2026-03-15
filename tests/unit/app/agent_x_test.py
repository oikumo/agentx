from unittest import TestCase
from unittest.mock import patch
from agent_x.app.agent_x import AgentX


class AgentXTest(TestCase):
    def test_run_with_repl_app_integration(self):
        # Integration test: AgentX with a real ReplApp (CLI ReplApp).
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

import unittest
from unittest.mock import patch, MagicMock

from agent_x.app.agent_x import AgentX
from agent_x.app.configuration.configuration import AgentXConfiguration
from agent_x.common.logger import log_info


class AgentXTest(unittest.TestCase):
    # ── Legacy smoke test (kept for historical continuity) ────────────────────

    def test_configure_appends_sequential_strings(self):
        # configure() appends str(len(llms)) before appending, so successive
        # calls produce ["0", "1", "2", …].  This was the original smoke test,
        # now expressed as a proper assertion.
        agentx = AgentX()
        log_info(",".join(agentx.llms))

        agentx.configure()
        self.assertEqual(agentx.llms, ["0"])

        agentx.configure()
        self.assertEqual(agentx.llms, ["0", "1"])

    # ── __init__ defaults ─────────────────────────────────────────────────────

    def test_init_llms_is_empty_list(self):
        # A brand-new AgentX must start with no LLMs registered.
        agentx = AgentX()
        self.assertEqual(agentx.llms, [])

    def test_init_creates_default_configuration(self):
        # AgentX must hold an AgentXConfiguration instance out of the box so
        # callers can immediately call configure_agentx() without extra setup.
        agentx = AgentX()
        self.assertIsInstance(agentx.configuration, AgentXConfiguration)

    # ── configure() ───────────────────────────────────────────────────────────

    def test_configure_is_idempotent_in_terms_of_count(self):
        # Each call to configure() must grow llms by exactly 1 entry.
        agentx = AgentX()
        for expected_len in range(1, 6):
            agentx.configure()
            self.assertEqual(len(agentx.llms), expected_len)

    # ── run() ─────────────────────────────────────────────────────────────────

    def test_run_delegates_to_repl_app(self):
        # AgentX.run() must create a ReplApp and call its run() method.
        # We mock ReplApp so the infinite loop never starts.
        agentx = AgentX()

        with patch("agent_x.app.agent_x.ReplApp") as mock_repl_cls:
            mock_repl_instance = MagicMock()
            mock_repl_cls.return_value = mock_repl_instance
            agentx.run()

        mock_repl_cls.assert_called_once()
        mock_repl_instance.run.assert_called_once()

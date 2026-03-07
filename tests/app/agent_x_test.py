import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from agent_x.app.agent_x import AgentX, IApp
from agent_x.app.configuration.configuration import AgentXConfiguration, AppType
from agent_x.common.logger import log_info


class FakeReplApp:
    """Fake ReplApp for integration testing — avoids the infinite while loop."""

    def __init__(self):
        self.run_called = False

    def run(self):
        self.run_called = True


class FakeChatApp:
    """Fake ChatApp for integration testing."""

    def __init__(self):
        self.run_called = False

    def run(self):
        self.run_called = True


class FakeWebIngestionApp:
    """Fake WebIngestionApp for integration testing."""

    def __init__(self, vectorstore=None, tav=None, site_url="", result_path=""):
        self.vectorstore = vectorstore
        self.tav = tav
        self.site_url = site_url
        self.result_path = result_path
        self.run_called = False

    def run(self):
        self.run_called = True


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

    def test_init_accepts_custom_configuration(self):
        # AgentX must accept a custom configuration via constructor.
        config = AgentXConfiguration(app=AppType.CHAT, debug=True)
        agentx = AgentX(configuration=config)
        self.assertEqual(agentx.configuration.app, AppType.CHAT)
        self.assertTrue(agentx.configuration.debug)

    def test_init_accepts_app_via_constructor(self):
        # AgentX must accept an app via constructor injection.
        fake_app = FakeReplApp()
        agentx = AgentX(app=fake_app)
        agentx.run()
        self.assertTrue(fake_app.run_called)

    # ── configure() ───────────────────────────────────────────────────────────

    def test_configure_is_idempotent_in_terms_of_count(self):
        # Each call to configure() must grow llms by exactly 1 entry.
        agentx = AgentX()
        for expected_len in range(1, 6):
            agentx.configure()
            self.assertEqual(len(agentx.llms), expected_len)

    # ── set_app() ─────────────────────────────────────────────────────────────

    def test_set_app_returns_self_for_fluent_interface(self):
        # set_app() must return self to support chaining.
        agentx = AgentX()
        fake_app = FakeReplApp()
        result = agentx.set_app(fake_app)
        self.assertIs(result, agentx)

    def test_set_app_overrides_previous_app(self):
        # Multiple set_app() calls must override the previous app.
        agentx = AgentX()
        app1 = FakeReplApp()
        app2 = FakeChatApp()

        agentx.set_app(app1)
        agentx.run()
        self.assertTrue(app1.run_called)
        self.assertFalse(app2.run_called)

        app1.run_called = False
        agentx.set_app(app2)
        agentx.run()
        self.assertFalse(app1.run_called)
        self.assertTrue(app2.run_called)

    # ── run() ─────────────────────────────────────────────────────────────────

    def test_run_delegates_to_injected_app(self):
        # AgentX.run() must call run() on the injected app.
        agentx = AgentX()

        mock_app = MagicMock()
        agentx.set_app(mock_app)
        agentx.run()

        mock_app.run.assert_called_once()

    def test_run_raises_when_no_app_set(self):
        # AgentX.run() must raise ValueError when no app is set.
        agentx = AgentX()

        with self.assertRaises(ValueError) as ctx:
            agentx.run()

        self.assertIn("No app set", str(ctx.exception))

    # ── Integration tests with real app classes ───────────────────────────────

    def test_run_with_repl_app_integration(self):
        # Integration test: AgentX with a real ReplApp (mocked inner loop).
        from agent_x.applications.repl_app.replapp import ReplApp

        agentx = AgentX()
        agentx.set_app(ReplApp())

        with patch("agent_x.applications.repl_app.replapp.MainController"):
            with patch("agent_x.applications.repl_app.replapp.CommandLine") as mock_cli:
                mock_cli_instance = MagicMock()
                mock_cli.return_value = mock_cli_instance
                mock_cli_instance.run.side_effect = StopIteration

                try:
                    agentx.run()
                except StopIteration:
                    pass

                mock_cli.assert_called_once()
                mock_cli_instance.run.assert_called()

    def test_run_with_chat_app_integration(self):
        # Integration test: AgentX with ChatApp.
        from agent_x.applications.chat_app.chat_app import ChatApp

        agentx = AgentX()
        agentx.set_app(ChatApp())

        with patch.object(ChatApp, "run"):
            agentx.run()

    def test_run_with_web_ingestion_app_integration(self):
        # Integration test: AgentX with WebIngestionApp.
        # Uses mocks to avoid calling real TavilySearch.
        from agent_x.applications.web_ingestion_app.web_ingestion_app import (
            WebIngestionApp,
        )
        from agent_x.applications.web_ingestion_app.tavily import WebExtract

        agentx = AgentX()
        mock_vs = MagicMock()
        mock_tav = MagicMock(spec=WebExtract)
        web_app = WebIngestionApp(vectorstore=mock_vs, tav=mock_tav)
        agentx.set_app(web_app)

        # Mock the run method to avoid actual Tavily calls
        with patch.object(web_app, "run", new=AsyncMock()) as mock_run:
            agentx.run()
            mock_run.assert_called_once()

    # ── IApp Protocol compliance ─────────────────────────────────────────────

    def test_repl_app_implements_iapp_protocol(self):
        # ReplApp must implement IApp protocol (duck typing verification).
        from agent_x.applications.repl_app.replapp import ReplApp

        app = ReplApp()
        self.assertTrue(hasattr(app, "run"))
        self.assertTrue(callable(app.run))

    def test_chat_app_implements_iapp_protocol(self):
        # ChatApp must implement IApp protocol.
        from agent_x.applications.chat_app.chat_app import ChatApp

        app = ChatApp()
        self.assertTrue(hasattr(app, "run"))
        self.assertTrue(callable(app.run))

    def test_web_ingestion_app_implements_iapp_protocol(self):
        # WebIngestionApp must implement IApp protocol.
        from agent_x.applications.web_ingestion_app.web_ingestion_app import (
            WebIngestionApp,
        )
        from agent_x.applications.web_ingestion_app.tavily import WebExtract

        mock_vs = MagicMock()
        mock_tav = MagicMock(spec=WebExtract)
        app = WebIngestionApp(vectorstore=mock_vs, tav=mock_tav)
        self.assertTrue(hasattr(app, "run"))
        self.assertTrue(callable(app.run))

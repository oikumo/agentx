from unittest import TestCase
from unittest.mock import Mock, patch
from agent_x.app.agent_x import AgentX, IApp
from agent_x.app.configuration.configuration import AgentXConfiguration


class AgentXTest(TestCase):
    """Unit tests for the AgentX class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.configuration = Mock(spec=AgentXConfiguration)
        self.mock_app = Mock(spec=IApp)

    def test_init_with_default_parameters(self):
        """Test AgentX initialization with default parameters."""
        agentx = AgentX()

        self.assertIsInstance(agentx.configuration, AgentXConfiguration)
        self.assertIsNone(agentx._app)
        self.assertEqual(agentx.llms, [])

    def test_init_with_custom_configuration(self):
        """Test AgentX initialization with custom configuration."""
        agentx = AgentX(configuration=self.configuration)

        self.assertEqual(agentx.configuration, self.configuration)
        self.assertIsNone(agentx._app)
        self.assertEqual(agentx.llms, [])

    def test_init_with_custom_app(self):
        """Test AgentX initialization with custom app."""
        agentx = AgentX(app=self.mock_app)

        self.assertIsInstance(agentx.configuration, AgentXConfiguration)
        self.assertEqual(agentx._app, self.mock_app)
        self.assertEqual(agentx.llms, [])

    def test_init_with_both_configuration_and_app(self):
        """Test AgentX initialization with both configuration and app."""
        agentx = AgentX(configuration=self.configuration, app=self.mock_app)

        self.assertEqual(agentx.configuration, self.configuration)
        self.assertEqual(agentx._app, self.mock_app)
        self.assertEqual(agentx.llms, [])

    def test_configure_method(self):
        """Test the configure method behavior."""
        agentx = AgentX()

        # Initial state
        self.assertEqual(agentx.llms, [])

        # After first configure call
        agentx.configure()
        self.assertEqual(agentx.llms, ["0"])

        # After second configure call
        agentx.configure()
        self.assertEqual(agentx.llms, ["0", "1"])

    def test_set_app_method(self):
        """Test the set_app method."""
        agentx = AgentX()

        # Initially no app
        self.assertIsNone(agentx._app)

        # Set app and verify return value
        result = agentx.set_app(self.mock_app)

        # Should return self for chaining
        self.assertIs(result, agentx)
        # Should have set the app
        self.assertEqual(agentx._app, self.mock_app)

    def test_run_without_app_raises_value_error(self):
        """Test that run() raises ValueError when no app is set."""
        agentx = AgentX()

        with self.assertRaises(ValueError) as context:
            agentx.run()

        self.assertIn("No app set", str(context.exception))
        self.assertIn("agentx.set_app(YourApp())", str(context.exception))

    def test_run_with_app_calls_app_run(self):
        """Test that run() calls the app's run method when app is set."""
        agentx = AgentX(app=self.mock_app)

        agentx.run()

        # Verify the app's run method was called
        self.mock_app.run.assert_called_once()

    def test_run_with_app_after_configure(self):
        """Test that run() works correctly after configure() calls."""
        agentx = AgentX(app=self.mock_app)

        # Call configure a few times
        agentx.configure()
        agentx.configure()
        agentx.configure()

        # Run should still work
        agentx.run()

        # Verify app run was called and llms were updated
        self.mock_app.run.assert_called_once()
        self.assertEqual(agentx.llms, ["0", "1", "2"])

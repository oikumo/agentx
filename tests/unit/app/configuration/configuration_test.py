import unittest

from agent_x.app.configuration.configuration import AgentXConfiguration, LLMModel, LLMProvider


class AgentXConfigurationTest(unittest.TestCase):
    def test_empty_config(self):
        config = AgentXConfiguration()

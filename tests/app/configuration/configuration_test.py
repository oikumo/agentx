import unittest

from agent_x.app.configuration.configuration import AgentXConfiguration, LLMModel

class AgentXConfigurationTest(unittest.TestCase):
    def test_parse(self):
        json = '{"name": "uno"}'
        config = AgentXConfiguration()
        llm = LLMModel.model_validate_json(json)
        config.llm_models.append(llm)

        self.assertTrue(len(config.llm_models) == 1)
        self.assertEqual(config.llm_models[0].name, "uno")

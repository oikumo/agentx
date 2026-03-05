import unittest

from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    LLMModel,
    configure_agentx,
)
from agent_x.app.agent_x import AgentX


class AgentXConfigurationTest(unittest.TestCase):
    def test_empty_config(self):
        config = AgentXConfiguration()
        self.assertEqual(len(config.llm_models), 0)

    def test_add_single_model(self):
        json = '{"name": "uno"}'
        config = AgentXConfiguration()
        llm = LLMModel.model_validate_json(json)
        config.llm_models.append(llm)

        self.assertTrue(len(config.llm_models) == 1)
        self.assertEqual(config.llm_models[0].name, "uno")

    def test_add_multiple_models(self):
        config = AgentXConfiguration()
        model1 = LLMModel(name="gpt-4")
        model2 = LLMModel(name="claude-3")
        model3 = LLMModel(name="ollama")

        config.llm_models.extend([model1, model2, model3])

        self.assertEqual(len(config.llm_models), 3)
        self.assertEqual(config.llm_models[0].name, "gpt-4")
        self.assertEqual(config.llm_models[1].name, "claude-3")
        self.assertEqual(config.llm_models[2].name, "ollama")

    def test_llm_model_creation(self):
        model = LLMModel(name="test-model")
        self.assertEqual(model.name, "test-model")

    def test_configure_agentx(self):
        config = AgentXConfiguration()
        agentx = AgentX()
        result = configure_agentx(config, agentx)
        self.assertTrue(result)

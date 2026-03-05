import unittest

from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    AppType,
    LLMModel,
    LLMProvider,
    configure_agentx,
)
from agent_x.app.agent_x import AgentX


class AgentXConfigurationTest(unittest.TestCase):
    def test_empty_config(self):
        config = AgentXConfiguration()
        self.assertEqual(len(config.llm_models), 0)
        self.assertEqual(config.default_model, "gpt-4")
        self.assertEqual(config.app, AppType.REPL)
        self.assertFalse(config.debug)

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
        self.assertEqual(agentx.configuration, config)

    def test_add_model_helper(self):
        config = AgentXConfiguration()
        config.add_model("gpt-4", LLMProvider.OPENAI, temperature=0.7)
        config.add_model("llama-3", LLMProvider.OLLAMA, temperature=0.5)

        self.assertEqual(len(config.llm_models), 2)
        self.assertEqual(config.llm_models[0].provider, LLMProvider.OPENAI)
        self.assertEqual(config.llm_models[1].provider, LLMProvider.OLLAMA)

    def test_get_model(self):
        config = AgentXConfiguration()
        config.add_model("gpt-4", LLMProvider.OPENAI)
        config.add_model("claude-3", LLMProvider.ANTHROPIC)

        model = config.get_model("gpt-4")
        self.assertIsNotNone(model)
        self.assertEqual(model.name, "gpt-4")

        missing = config.get_model("nonexistent")
        self.assertIsNone(missing)

    def test_get_default_model(self):
        config = AgentXConfiguration(default_model="claude-3")
        config.add_model("gpt-4", LLMProvider.OPENAI)
        config.add_model("claude-3", LLMProvider.ANTHROPIC)

        default = config.get_default_model()
        self.assertIsNotNone(default)
        self.assertEqual(default.name, "claude-3")

    def test_app_type_enum(self):
        config = AgentXConfiguration(app=AppType.CHAT)
        self.assertEqual(config.app, AppType.CHAT)

    def test_llm_provider_enum(self):
        model = LLMModel(name="test", provider=LLMProvider.OLLAMA)
        self.assertEqual(model.provider, LLMProvider.OLLAMA)

    def test_model_temperature_bounds(self):
        with self.assertRaises(Exception):
            LLMModel(name="test", temperature=3.0)

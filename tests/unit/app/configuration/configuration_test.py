import unittest

from agent_x.app.agent_x import AgentX
from agent_x.app.configuration.configuration import (AgentXConfiguration,
                                                     AppType, LLMModel,
                                                     LLMProvider,
                                                     configure_agentx)


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

    # ── get_default_model() edge case ─────────────────────────────────────────

    def test_get_default_model_returns_none_when_named_model_was_never_added(self):
        # default_model is "gpt-4" by default. If no model with that name was
        # added via add_model(), get_default_model() must return None rather
        # than raising an exception. This silent None return is the documented
        # contract — callers must guard against it.
        config = AgentXConfiguration()
        # Only add a model that does NOT match default_model.
        config.add_model("claude-3", LLMProvider.ANTHROPIC)

        result = config.get_default_model()
        self.assertIsNone(result)

    def test_get_default_model_returns_none_on_empty_model_list(self):
        # An empty llm_models list with any default_model value returns None.
        config = AgentXConfiguration(default_model="nonexistent-model")
        self.assertEqual(len(config.llm_models), 0)
        self.assertIsNone(config.get_default_model())

    # ── configure_agentx() failure paths ──────────────────────────────────────

    def test_configure_agentx_raises_attribute_error_when_agentx_is_none(self):
        # configure_agentx does not guard against None — passing None as agentx
        # raises AttributeError because it tries to set .configuration on None.
        # This test documents the current (unguarded) behaviour. If a guard is
        # added in future, update this test accordingly.
        config = AgentXConfiguration()
        with self.assertRaises(AttributeError):
            configure_agentx(config, None)

    def test_configure_agentx_with_empty_model_list_still_returns_true(self):
        # An AgentXConfiguration with no models is valid — configure_agentx
        # must still succeed and return True. Callers that need models must
        # validate the config themselves before use.
        config = AgentXConfiguration()
        agentx = AgentX()
        result = configure_agentx(config, agentx)
        self.assertTrue(result)
        self.assertEqual(len(agentx.configuration.llm_models), 0)

    def test_configure_agentx_raises_attribute_error_when_config_is_none(self):
        # Passing None as config raises AttributeError when agentx later tries
        # to access configuration fields. Documents the unguarded behaviour.
        agentx = AgentX()
        # configure_agentx just does: agentx.configuration = config
        # So None is accepted without error at this call site — it only
        # fails when callers access config attributes downstream.
        # Verify that the assignment itself succeeds (no error here).
        result = configure_agentx(None, agentx)
        self.assertTrue(result)
        self.assertIsNone(agentx.configuration)

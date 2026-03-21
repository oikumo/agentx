import unittest

from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)


class AgentXConfigurationTest(unittest.TestCase):
    def test_empty_config(self):
        config = AgentXConfiguration()
        self.assertEqual(len(config.llm_configs), 0)
        self.assertEqual(config.default_chat_model, "qwen3:1.7b")
        self.assertEqual(config.default_embedding_model, "nomic-embed-text")

    def test_add_llm_config(self):
        config = AgentXConfiguration()
        llm_config = LLMConfig(
            name="test-model",
            provider=LLMProvider.OLLAMA,
            model_name="llama2:7b",
            temperature=0.5,
            max_tokens=1024,
        )
        config.add_llm_config(llm_config)
        self.assertEqual(len(config.llm_configs), 1)

    def test_get_llm_config(self):
        config = AgentXConfiguration()
        llm_config = LLMConfig(
            name="test-model", provider=LLMProvider.OLLAMA, model_name="llama2:7b"
        )
        config.add_llm_config(llm_config)
        retrieved = config.get_llm_config("test-model")
        self.assertIsNotNone(retrieved)
        if retrieved is not None:
            self.assertEqual(retrieved.name, "test-model")
            self.assertEqual(retrieved.model_name, "llama2:7b")

    def test_get_llm_config_not_found(self):
        config = AgentXConfiguration()
        retrieved = config.get_llm_config("non-existent")
        self.assertIsNone(retrieved)

    def test_get_default_chat_config(self):
        config = AgentXConfiguration()
        # Should be None initially since no configs added
        self.assertIsNone(config.get_default_chat_config())

        # Add default chat model config
        llm_config = LLMConfig(
            name="qwen3:1.7b", provider=LLMProvider.OLLAMA, model_name="qwen3:1.7b"
        )
        config.add_llm_config(llm_config)
        retrieved = config.get_default_chat_config()
        self.assertIsNotNone(retrieved)
        if retrieved is not None:
            self.assertEqual(retrieved.name, "qwen3:1.7b")

    def test_get_default_embedding_config(self):
        config = AgentXConfiguration()
        # Should be None initially since no configs added
        self.assertIsNone(config.get_default_embedding_config())

        # Add default embedding model config
        llm_config = LLMConfig(
            name="nomic-embed-text",
            provider=LLMProvider.OLLAMA,
            model_name="nomic-embed-text",
        )
        config.add_llm_config(llm_config)
        retrieved = config.get_default_embedding_config()
        self.assertIsNotNone(retrieved)
        if retrieved is not None:
            self.assertEqual(retrieved.name, "nomic-embed-text")

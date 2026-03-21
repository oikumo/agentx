import unittest
from unittest.mock import Mock, patch

from app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)
from llm_models.llm_factory import LLMFactory


class LLMFactoryTest(unittest.TestCase):
    def setUp(self):
        self.config = AgentXConfiguration()
        # Add test configurations
        self.config.add_llm_config(
            LLMConfig(
                name="test-ollama",
                provider=LLMProvider.OLLAMA,
                model_name="llama2:7b",
                temperature=0.5,
                max_tokens=1024,
            )
        )
        self.config.add_llm_config(
            LLMConfig(
                name="test-openai",
                provider=LLMProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=2048,
                api_key="test-key",
            )
        )
        self.factory = LLMFactory(self.config)

    @patch("agent_x.llm_factory.ChatOllama")
    def test_get_chat_model_ollama(self, mock_chat_ollama):
        # Setup mock
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance

        # Execute
        result = self.factory.get_chat_model("test-ollama")

        # Verify
        mock_chat_ollama.assert_called_once()
        self.assertEqual(result, mock_instance)

    @patch("agent_x.llm_factory.ChatOpenAI")
    def test_get_chat_model_openai(self, mock_chat_openai):
        # Setup mock
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        # Execute
        result = self.factory.get_chat_model("test-openai")

        # Verify
        mock_chat_openai.assert_called_once()
        self.assertEqual(result, mock_instance)

    def test_get_chat_model_not_found(self):
        # Execute and verify
        with self.assertRaises(ValueError) as context:
            self.factory.get_chat_model("non-existent")
        self.assertIn(
            "LLM configuration 'non-existent' not found", str(context.exception)
        )

    @patch("agent_x.llm_factory.ChatOllama")
    def test_get_chat_model_caching(self, mock_chat_ollama):
        # Setup mock
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance

        # Execute twice
        result1 = self.factory.get_chat_model("test-ollama")
        result2 = self.factory.get_chat_model("test-ollama")

        # Verify - should only call constructor once due to caching
        mock_chat_ollama.assert_called_once()
        self.assertEqual(result1, mock_instance)
        self.assertEqual(result2, mock_instance)
        self.assertIs(result1, result2)  # Same object due to caching

    @patch("agent_x.llm_factory.ChatOllama")
    def test_get_chat_model_default(self, mock_chat_ollama):
        # Setup mock
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance

        # Update default model in config
        self.config.default_chat_model = "test-ollama"

        # Execute without specifying model name
        result = self.factory.get_chat_model()

        # Verify
        mock_chat_ollama.assert_called_once()
        self.assertEqual(result, mock_instance)

    # Similar tests for embedding models would go here
    # For brevity, we'll focus on chat models in this initial implementation

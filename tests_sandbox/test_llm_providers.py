import unittest
from unittest.mock import patch, MagicMock

from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers import local_llm_provider, cloud_llm_provider


class TestLLMProviderInterface(unittest.TestCase):
    def test_llm_provider_is_abstract(self):
        """Cannot instantiate LLMProvider directly."""
        with self.assertRaises(TypeError):
            LLMProvider()


class TestOpenAIProvider(unittest.TestCase):
    @patch("llm_managers.providers.openai_provider.get_remote_llm_openai_gpt3_5_turbo")
    def test_create_llm_returns_chat_model(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        provider = OpenAIProvider()
        result = provider.create_llm()

        mock_get_llm.assert_called_once()
        self.assertIs(result, mock_llm)


class TestLlamaCppProvider(unittest.TestCase):
    @patch("llm_managers.providers.llamacpp_provider.model_factory_llamacpp")
    def test_create_llm_returns_chat_model(self, mock_factory):
        mock_llm = MagicMock()
        mock_factory.create_model_instance.return_value = mock_llm

        provider = LlamaCppProvider()
        result = provider.create_llm()

        mock_factory.create_model_instance.assert_called_once()
        self.assertIs(result, mock_llm)

    @patch("llm_managers.providers.llamacpp_provider.model_factory_llamacpp")
    def test_create_llm_uses_custom_config(self, mock_factory):
        mock_llm = MagicMock()
        mock_factory.create_model_instance.return_value = mock_llm

        provider = LlamaCppProvider(model_filename="custom.gguf", context_size=16384)
        provider.create_llm()

        config_arg = mock_factory.create_model_instance.call_args[0][0]
        self.assertEqual(config_arg.model_filename, "custom.gguf")
        self.assertEqual(config_arg.context_size, 16384)


class TestProviderHelpers(unittest.TestCase):
    def test_local_llm_provider_returns_llamacpp(self):
        provider = local_llm_provider()
        self.assertIsInstance(provider, LlamaCppProvider)

    def test_cloud_llm_provider_returns_openai(self):
        provider = cloud_llm_provider()
        self.assertIsInstance(provider, OpenAIProvider)


if __name__ == "__main__":
    unittest.main()

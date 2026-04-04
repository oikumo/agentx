import unittest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel


class TestAgentFactoryCreateChat(unittest.TestCase):
    @patch("llm_managers.factory.OpenAIProvider")
    @patch("llm_managers.factory.SimpleChat")
    def test_create_chat_default_provider(self, mock_simple_chat, mock_provider_cls):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_provider_cls.return_value = mock_provider
        mock_agent = MagicMock()
        mock_simple_chat.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_chat()

        mock_provider_cls.assert_called_once()
        mock_provider.create_llm.assert_called_once()
        mock_simple_chat.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_agent)

    @patch("llm_managers.factory.SimpleChat")
    def test_create_chat_custom_provider(self, mock_simple_chat):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_simple_chat.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_chat(provider=mock_provider)

        mock_provider.create_llm.assert_called_once()
        mock_simple_chat.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_agent)


class TestAgentFactoryCreateChatLoop(unittest.TestCase):
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_managers.factory.ChatLoop")
    def test_create_chat_loop_default_provider(self, mock_chat_loop, mock_local):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_local.return_value = mock_provider
        mock_loop = MagicMock()
        mock_chat_loop.return_value = mock_loop

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_chat_loop()

        mock_local.assert_called_once()
        mock_provider.create_llm.assert_called_once()
        mock_chat_loop.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_loop)

    @patch("llm_managers.factory.ChatLoop")
    def test_create_chat_loop_custom_provider(self, mock_chat_loop):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_loop = MagicMock()
        mock_chat_loop.return_value = mock_loop

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_chat_loop(provider=mock_provider)

        mock_provider.create_llm.assert_called_once()
        mock_chat_loop.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_loop)


class TestAgentFactoryCreateFunctionRouter(unittest.TestCase):
    @patch("llm_managers.factory.QueryRouter")
    def test_create_function_router_default_routes(self, mock_query_router):
        mock_router = MagicMock()
        mock_query_router.return_value = mock_router

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_function_router()

        mock_query_router.assert_called_once()
        routes_arg = mock_query_router.call_args[0][0]
        self.assertIsInstance(routes_arg, list)
        self.assertEqual(len(routes_arg), 2)
        route_names = [r.name for r in routes_arg]
        self.assertIn("get_weather", route_names)
        self.assertIn("get_best_game", route_names)
        self.assertIs(result, mock_router)

    @patch("llm_managers.factory.QueryRouter")
    def test_create_function_router_custom_routes(self, mock_query_router):
        mock_router = MagicMock()
        mock_query_router.return_value = mock_router
        custom_route = MagicMock()
        custom_route.name = "custom"

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_function_router(routes=[custom_route])

        mock_query_router.assert_called_once_with([custom_route])
        self.assertIs(result, mock_router)


class TestAgentFactoryCreateRag(unittest.TestCase):
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_managers.factory.create_directory_with_timestamp")
    @patch("llm_managers.factory.AgentRagPdf")
    def test_create_rag_default_config(
        self, mock_agent_rag, mock_create_dir, mock_local
    ):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_embeddings = MagicMock(spec=Embeddings)
        mock_agent = MagicMock()
        mock_create_dir.return_value = "/tmp/vs_path"
        mock_local.return_value = mock_provider
        mock_agent_rag.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        with patch(
            "llm_models.local.ollama.ollama_embeddings.create_embeddings_model",
            return_value=mock_embeddings,
        ):
            result = AgentFactory.create_rag()

        mock_create_dir.assert_called_once()
        mock_provider.create_llm.assert_called_once()
        mock_agent_rag.assert_called_once()
        self.assertIs(result, mock_agent)

    @patch("llm_managers.factory.AgentRagPdf")
    def test_create_rag_custom_config(self, mock_agent_rag):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_embeddings = MagicMock(spec=Embeddings)
        mock_agent = MagicMock()
        mock_agent_rag.return_value = mock_agent

        from llm_managers.factory import RagConfig, AgentFactory

        config = RagConfig(
            pdf_path="/docs/test.pdf",
            vectorstore_path="/tmp/vs",
            llm_provider=mock_provider,
            embeddings=mock_embeddings,
        )

        result = AgentFactory.create_rag(config=config)

        mock_provider.create_llm.assert_called_once()
        mock_agent_rag.assert_called_once_with(
            pdf_path="/docs/test.pdf",
            vectorstore_path="/tmp/vs",
            llm=mock_llm,
            embeddings=mock_embeddings,
        )
        self.assertIs(result, mock_agent)


class TestAgentFactoryCreateReactWebSearch(unittest.TestCase):
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_managers.factory.AgentReactWebSearch")
    def test_create_react_web_search_default(self, mock_agent_cls, mock_local):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_local.return_value = mock_provider
        mock_agent = MagicMock()
        mock_agent_cls.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_react_web_search()

        mock_local.assert_called_once()
        mock_provider.create_llm.assert_called_once()
        mock_agent_cls.assert_called_once_with(mock_llm)
        self.assertIs(result, mock_agent)

    @patch("llm_managers.factory.AgentReactWebSearch")
    def test_create_react_web_search_custom_provider(self, mock_agent_cls):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_cls.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_react_web_search(provider=mock_provider)

        mock_provider.create_llm.assert_called_once()
        mock_agent_cls.assert_called_once_with(mock_llm)
        self.assertIs(result, mock_agent)


class TestAgentFactoryCreateGraphReactWebSearch(unittest.TestCase):
    @patch("llm_managers.factory.local_llm_provider")
    @patch("llm_managers.factory.GraphReactWebSearch")
    def test_create_graph_react_default(self, mock_agent_cls, mock_local):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_local.return_value = mock_provider
        mock_agent = MagicMock()
        mock_agent_cls.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_graph_react_web_search()

        mock_local.assert_called_once()
        mock_provider.create_llm.assert_called_once()
        mock_agent_cls.assert_called_once_with(llm=mock_llm, max_search_results=1)
        self.assertIs(result, mock_agent)

    @patch("llm_managers.factory.GraphReactWebSearch")
    def test_create_graph_react_custom_provider_and_max(self, mock_agent_cls):
        mock_llm = MagicMock(spec=BaseChatModel)
        mock_provider = MagicMock()
        mock_provider.create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_cls.return_value = mock_agent

        from llm_managers.factory import AgentFactory

        result = AgentFactory.create_graph_react_web_search(
            provider=mock_provider, max_search_results=5
        )

        mock_provider.create_llm.assert_called_once()
        mock_agent_cls.assert_called_once_with(llm=mock_llm, max_search_results=5)
        self.assertIs(result, mock_agent)


class TestRagConfig(unittest.TestCase):
    def test_rag_config_defaults(self):
        from llm_managers.factory import RagConfig

        config = RagConfig()
        self.assertEqual(config.pdf_path, "_resources/react.pdf")
        self.assertIsNone(config.vectorstore_path)
        self.assertIsNone(config.embeddings)

    def test_rag_config_custom_values(self):
        from llm_managers.factory import RagConfig

        mock_provider = MagicMock()
        mock_embeddings = MagicMock()
        config = RagConfig(
            pdf_path="/custom.pdf",
            vectorstore_path="/vs",
            llm_provider=mock_provider,
            embeddings=mock_embeddings,
        )
        self.assertEqual(config.pdf_path, "/custom.pdf")
        self.assertEqual(config.vectorstore_path, "/vs")
        self.assertIs(config.llm_provider, mock_provider)
        self.assertIs(config.embeddings, mock_embeddings)


if __name__ == "__main__":
    unittest.main()

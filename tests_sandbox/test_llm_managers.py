import unittest
from unittest.mock import patch, MagicMock

from llm_managers.agent_chat_factory import create_agent_chat
from llm_managers.agent_function_router_factory import create_agent_function_router
from llm_managers.agent_react_web_search_factory import create_agent_react_web_search
from llm_managers.graph_react_web_search_factory import (
    create_graph_react_web_search,
    create_graph_react_web_search_local,
    create_graph_react_web_search_cloud,
)
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider


class TestAgentChatFactory(unittest.TestCase):
    @patch.object(OpenAIProvider, "create_llm")
    @patch("llm_managers.agent_chat_factory.SimpleChat")
    def test_create_agent_chat_default_provider(
        self, mock_simple_chat, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_simple_chat.return_value = mock_agent

        result = create_agent_chat()

        mock_create_llm.assert_called_once()
        mock_simple_chat.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_agent)

    @patch.object(LlamaCppProvider, "create_llm")
    @patch("llm_managers.agent_chat_factory.SimpleChat")
    def test_create_agent_chat_with_custom_provider(
        self, mock_simple_chat, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_simple_chat.return_value = mock_agent

        result = create_agent_chat(
            provider=LlamaCppProvider(
                model_filename="test.gguf",
                context_size=32768,
            )
        )

        mock_create_llm.assert_called_once()
        mock_simple_chat.assert_called_once_with(llm=mock_llm)
        self.assertIs(result, mock_agent)


class TestAgentFunctionRouterFactory(unittest.TestCase):
    @patch("llm_managers.agent_function_router_factory.QueryRouter")
    def test_create_agent_function_router_default_routes(self, mock_query_router):
        mock_router = MagicMock()
        mock_query_router.return_value = mock_router

        result = create_agent_function_router()

        mock_query_router.assert_called_once()
        routes_arg = mock_query_router.call_args[0][0]
        self.assertIsInstance(routes_arg, list)
        self.assertEqual(len(routes_arg), 2)
        route_names = [r.name for r in routes_arg]
        self.assertIn("get_weather", route_names)
        self.assertIn("get_best_game", route_names)
        self.assertIs(result, mock_router)

    @patch("llm_managers.agent_function_router_factory.QueryRouter")
    def test_create_agent_function_router_custom_routes(self, mock_query_router):
        mock_router = MagicMock()
        mock_query_router.return_value = mock_router
        custom_route = MagicMock()

        result = create_agent_function_router(routes=[custom_route])

        mock_query_router.assert_called_once_with([custom_route])
        self.assertIs(result, mock_router)


class TestAgentReactWebSearchFactory(unittest.TestCase):
    @patch.object(LlamaCppProvider, "create_llm")
    @patch("llm_managers.agent_react_web_search_factory.AgentReactWebSearch")
    def test_create_agent_react_web_search_default_provider(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_agent_react_web_search()

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(mock_llm)
        self.assertIs(result, mock_agent)

    @patch.object(OpenAIProvider, "create_llm")
    @patch("llm_managers.agent_react_web_search_factory.AgentReactWebSearch")
    def test_create_agent_react_web_search_custom_provider(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_agent_react_web_search(provider=OpenAIProvider())

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(mock_llm)
        self.assertIs(result, mock_agent)


class TestGraphReactWebSearchFactory(unittest.TestCase):
    @patch.object(LlamaCppProvider, "create_llm")
    @patch("llm_managers.graph_react_web_search_factory.GraphReactWebSearch")
    def test_create_graph_react_web_search_default(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_graph_react_web_search()

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(llm=mock_llm, max_search_results=1)
        self.assertIs(result, mock_agent)

    @patch.object(OpenAIProvider, "create_llm")
    @patch("llm_managers.graph_react_web_search_factory.GraphReactWebSearch")
    def test_create_graph_react_web_search_cloud(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_graph_react_web_search_cloud()

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(llm=mock_llm, max_search_results=1)
        self.assertIs(result, mock_agent)

    @patch.object(LlamaCppProvider, "create_llm")
    @patch("llm_managers.graph_react_web_search_factory.GraphReactWebSearch")
    def test_create_graph_react_web_search_local(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_graph_react_web_search_local()

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(llm=mock_llm, max_search_results=1)
        self.assertIs(result, mock_agent)

    @patch.object(OpenAIProvider, "create_llm")
    @patch("llm_managers.graph_react_web_search_factory.GraphReactWebSearch")
    def test_create_graph_react_web_search_custom_max_results(
        self, mock_agent_class, mock_create_llm
    ):
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        result = create_graph_react_web_search(
            provider=OpenAIProvider(), max_search_results=5
        )

        mock_create_llm.assert_called_once()
        mock_agent_class.assert_called_once_with(llm=mock_llm, max_search_results=5)
        self.assertIs(result, mock_agent)


if __name__ == "__main__":
    unittest.main()

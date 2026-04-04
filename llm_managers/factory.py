from dataclasses import dataclass, field
from typing import Optional

from langchain_core.embeddings import Embeddings

from agents.chat.simple_chat import SimpleChat
from agents.chat.chat_loop import ChatLoop
from agents.function_tool_router.function_call import QueryRouter
from agents.function_tool_router.functions import get_weather, get_best_game
from agents.function_tool_router.route import Route
from agents.rag_pdf.agent_rag_pdf import AgentRagPdf
from agents.react_web_search.agent_react_web_search import AgentReactWebSearch
from agents.graph_react_web_search.graph_react_web_search import GraphReactWebSearch
from app.common.utils.file_utils import create_directory_with_timestamp
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers import local_llm_provider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_NEMOTRON_3_NANO


@dataclass
class RagConfig:
    """Configuration for RAG agent creation.

    Attributes:
        pdf_path: Path to the PDF document.
        vectorstore_path: Optional path for vectorstore persistence.
        llm_provider: LLMProvider strategy for the language model.
        embeddings: Embeddings model for vectorization.
    """

    pdf_path: str = "_resources/react.pdf"
    vectorstore_path: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None
    embeddings: Optional[Embeddings] = None


class AgentFactory:
    """Unified factory for creating all agent types.

    Provides a single entry point with consistent API for agent creation.
    """

    @staticmethod
    def create_chat(provider: LLMProvider | None = None) -> SimpleChat:
        """Create a SimpleChat agent.

        Args:
            provider: LLMProvider strategy. Defaults to OpenAIProvider.

        Returns:
            Configured SimpleChat instance.
        """
        if provider is None:
            provider = OpenAIProvider()
        llm = provider.create_llm()
        return SimpleChat(llm=llm)

    @staticmethod
    def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
        """Create a ChatLoop agent.

        Args:
            provider: LLMProvider strategy. Defaults to local LlamaCpp.

        Returns:
            Configured ChatLoop instance.
        """
        if provider is None:
            provider = local_llm_provider(
                model_filename=LLAMA_CPP_MODEL_NEMOTRON_3_NANO,
                context_size=32768)

        llm = provider.create_llm()
        return ChatLoop(llm=llm)

    @staticmethod
    def create_function_router(routes: list[Route] | None = None) -> QueryRouter:
        """Create a QueryRouter agent.

        Args:
            routes: List of Route objects. Defaults to weather and game routes.

        Returns:
            Configured QueryRouter instance.
        """
        if routes is None:
            routes = [
                Route("get_weather", get_weather),
                Route("get_best_game", get_best_game),
            ]
        return QueryRouter(routes)

    @staticmethod
    def create_rag(config: RagConfig | None = None) -> AgentRagPdf:
        """Create an AgentRagPdf instance.

        Args:
            config: RagConfig object. Defaults to local LlamaCpp setup.

        Returns:
            Configured AgentRagPdf instance.
        """
        if config is None:
            config = RagConfig()

        if config.vectorstore_path is None:
            config.vectorstore_path = create_directory_with_timestamp(
                "faiss_index_react", "local_vector_databases"
            )

        if config.embeddings is None:
            from llm_models.local.ollama.ollama_embeddings import (
                create_embeddings_model,
            )

            config.embeddings = create_embeddings_model()

        if config.llm_provider is None:
            config.llm_provider = local_llm_provider()

        llm = config.llm_provider.create_llm()

        return AgentRagPdf(
            pdf_path=config.pdf_path,
            vectorstore_path=config.vectorstore_path,
            llm=llm,
            embeddings=config.embeddings,
        )

    @staticmethod
    def create_react_web_search(
        provider: LLMProvider | None = None,
    ) -> AgentReactWebSearch:
        """Create an AgentReactWebSearch instance.

        Args:
            provider: LLMProvider strategy. Defaults to local LlamaCpp.

        Returns:
            Configured AgentReactWebSearch instance.
        """
        if provider is None:
            provider = local_llm_provider()
        llm = provider.create_llm()
        return AgentReactWebSearch(llm)

    @staticmethod
    def create_graph_react_web_search(
        provider: LLMProvider | None = None,
        max_search_results: int = 1,
    ) -> GraphReactWebSearch:
        """Create a GraphReactWebSearch instance.

        Args:
            provider: LLMProvider strategy. Defaults to local LlamaCpp.
            max_search_results: Maximum number of search results to process.

        Returns:
            Configured GraphReactWebSearch instance.
        """
        if provider is None:
            provider = local_llm_provider()
        llm = provider.create_llm()
        return GraphReactWebSearch(llm=llm, max_search_results=max_search_results)

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from views.main_view import ChatLoop
from agents.function_tool_router.function_call import QueryRouter
from agents.function_tool_router.functions import get_weather, get_best_game
from agents.function_tool_router.route import Route
from agents.rag_pdf.agent_rag_pdf import AgentRagPdf
from agents.react_web_search.agent_react_web_search import AgentReactWebSearch
from agents.graph_react_web_search.graph_react_web_search import GraphReactWebSearch
from app.utils import create_directory_with_timestamp
from app_modules.document_loaders.pdf_loader import pdf_loader
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers import local_llm_provider, openrouter_llm_provider


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
    def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
        """Create a ChatLoop agent.

        Args:
            provider: LLMProvider strategy. Defaults to local LlamaCpp.

        Returns:
            Configured ChatLoop instance.
        """
        if provider is None:
            provider = openrouter_llm_provider()

        llm = provider.create_llm()
        return ChatLoop(llm=llm)

    @staticmethod
    def create_chat_loop_rag(
        pdf_path: str = "_resources/react.pdf",
        vectorstore_path: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None,
        embeddings: Optional[Embeddings] = None,
    ) -> ChatLoop:
        """Create a ChatLoop agent with RAG capabilities.

        Args:
            pdf_path: Path to the PDF document.
            vectorstore_path: Optional path for vectorstore persistence.
            llm_provider: LLMProvider strategy. Defaults to local LlamaCpp.
            embeddings: Embeddings model for vectorization.

        Returns:
            Configured ChatLoop instance with RAG retriever.
        """

        base_vector_databases_directory = "local_vector_databases"
        faiss_directory = "faiss_index_chat_rag"
        if vectorstore_path is None:
            directory = f"{base_vector_databases_directory}/{faiss_directory}"
            vectorstore_path = str(Path(directory).resolve())

        if embeddings is None:
            from llm_models.local.ollama.ollama_embeddings import (
                create_embeddings_model,
            )

            embeddings = create_embeddings_model()

        if not Path(vectorstore_path).is_dir():
            docs = pdf_loader(pdf_path)
            print(f"docs from pdf: {len(docs)}")
            print(f"load docs int vector store, path: {vectorstore_path}")
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(vectorstore_path)

        loaded_vectorstore = FAISS.load_local(
            vectorstore_path, embeddings, allow_dangerous_deserialization=True
        )

        if llm_provider is None:
            llm_provider = openrouter_llm_provider()

        llm = llm_provider.create_llm()

        print(f"docs loaded in vector store")

        retriever = loaded_vectorstore.as_retriever()

        return ChatLoop(llm=llm, retriever=retriever)

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

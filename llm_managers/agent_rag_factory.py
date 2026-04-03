from dataclasses import dataclass, field
from typing import Optional

from langchain_core.embeddings import Embeddings

from agents.rag_pdf.agent_rag_pdf import AgentRagPdf
from app.common.utils.file_utils import create_directory_with_timestamp
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider


def _default_llm_provider() -> LLMProvider:
    return LlamaCppProvider()


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
    llm_provider: LLMProvider = field(default_factory=_default_llm_provider)
    embeddings: Optional[Embeddings] = None


def create_agent_rag(config: RagConfig | None = None) -> AgentRagPdf:
    """Create an AgentRagPdf instance with the specified configuration.

    Args:
        config: RagConfig object with PDF path, vectorstore path, LLM provider,
            and embeddings. Defaults to local LlamaCpp setup.

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
        from llm_models.local.ollama.ollama_embeddings import create_embeddings_model

        config.embeddings = create_embeddings_model()

    llm = config.llm_provider.create_llm()

    return AgentRagPdf(
        pdf_path=config.pdf_path,
        vectorstore_path=config.vectorstore_path,
        llm=llm,
        embeddings=config.embeddings,
    )


create_agent_rag_local = create_agent_rag

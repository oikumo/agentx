from dataclasses import dataclass
from typing import Optional

from langchain_core.embeddings import Embeddings

from views.main_view import ChatLoop
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers import openrouter_llm_provider


@dataclass
class RagConfig:
    pdf_path: str = "_resources/react.pdf"
    vectorstore_path: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None
    embeddings: Optional[Embeddings] = None


class AgentFactory:

    @staticmethod
    def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
        if provider is None:
            provider = openrouter_llm_provider()

        llm = provider.create_llm()
        return ChatLoop(llm=llm)

import pprint
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set

from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import BaseChatModel
from agentx.model.rag.query.rag_prompts import RagChatPrompts


@dataclass
class RagChatHistory:
    """Conversation history for RAG chat sessions.
    
    Each instance maintains independent history lists to prevent
    cross-session contamination (bug fix for class attributes).
    """
    chat_answers_history: list[str] = field(default_factory=list)
    user_prompt_history: list[str] = field(default_factory=list)
    chat_history: list[tuple[str, str]] = field(default_factory=list)

class RagQuery:
    def __init__(self, llm: BaseChatModel, vector_store: Chroma):
        self.llm = llm
        self.vector_store = vector_store

    def ask(self, user_prompt: str, history: RagChatHistory) -> RagChatHistory:
        generated_response = self._run_llm(
            query=user_prompt,
            chat_history=history.chat_history
        )

        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )

        for doc in generated_response["source_documents"]:
            pprint.pprint(doc)

        formatted_response = (
            f"{generated_response['result']} \n\n {self._create_sources_string(sources)}"
        )

        history.user_prompt_history.append(user_prompt)
        history.chat_answers_history.append(formatted_response)
        history.chat_history.append(("human", user_prompt))
        history.chat_history.append(("ai", generated_response["result"]))

        return history

    def _run_llm(self, query: str, chat_history: list[tuple[str, str]] = []):
        rag_prompt = RagChatPrompts.create_rag_template()
        rephrase_prompt = RagChatPrompts.create_rephase_template()

        stuff_documents_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=rag_prompt
        )

        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            prompt=rephrase_prompt
        )

        qa = create_retrieval_chain(
            retriever=history_aware_retriever,
            combine_docs_chain=stuff_documents_chain
        )

        result = qa.invoke(input={"input": query, "chat_history": chat_history})

        new_result = {
            "query": result["input"],
            "result": result["answer"],
            "source_documents": result["context"]
        }

        return new_result

    @classmethod
    def _create_sources_string(cls, source_urls: Set[str]) -> str:
        if not source_urls:
            return ""
        sources_list = list(source_urls)
        sources_list.sort()
        sources_string = "sources:\n"
        for i, source in enumerate(sources_list):
            sources_string += f"{i+1}. {source}\n"
        return sources_string

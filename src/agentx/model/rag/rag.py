import asyncio
import time
from typing import List, Dict, Any, Set

from langchain_classic import hub
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import BaseChatModel
from rich import pretty

from agentx.common import utils
from agentx.common.input_utils import InputUtils
from agentx.model.ai.service import AIService
from agentx.model.rag.rag_db import RagDatabase
from agentx.model.rag.web_ingestion.web_extract import WebExtract
from agentx.model.rag.web_ingestion.web_ingestion_app import WebIngestionApp

RAG_PROMPT="""
Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {question}
"""

class RagChatHistory:
    chat_answers_history = []
    user_prompt_history = []
    chat_history = []


class Rag:
    working_directory: str
    site_url = str | None


    def __init__(self, working_directory: str):
        self.working_directory = working_directory
        self.site_url = None
        self.vector_db_path = f"{self.working_directory}/chroma_db"
        self.documents_path = f"{self.working_directory}/documents.jsonl"
        self.rag_db_path = f"{self.working_directory}/rag.db"
        self.rag_db = RagDatabase(self.rag_db_path)

    def ask(self, user_prompt: str, history: RagChatHistory) -> RagChatHistory:

        generated_response = self.run_llm(
            chat = AIService().openrouter_llm_provider().create_llm(),
            query=user_prompt, chat_history=history.chat_history
        )

        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )

        formatted_response = (
            f"{generated_response['result']} \n\n {self.create_sources_string(sources)}"
        )

        history.user_prompt_history.append(user_prompt)
        history.chat_answers_history.append(formatted_response)
        history.chat_history.append(("human", user_prompt))
        history.chat_history.append(("ai", generated_response["result"]))

        return history

    def is_data(self) -> bool:
        return (
                utils.directory_exists(self.vector_db_path) and
                utils.file_exists(self.documents_path) and
                utils.file_exists(self.rag_db_path)
        )

    def web_ingestion(self) -> bool:
        if not InputUtils.is_valid_url(self.site_url):
            return False

        self.rag_db.insert_ingestion_entry(self.vector_db_path)
        ai_service = AIService()
        vectorstore = ai_service.rag_chromadb(self.vector_db_path)

        web_extractor = WebExtract(1, 2, 100)
        app = WebIngestionApp(vectorstore, web_extractor)

        asyncio.run(app.run(
            site_url= self.site_url,
            result_json_file_path= self.documents_path
        ))



        return True

    def run_llm(self, chat: BaseChatModel, query: str, chat_history: List[Dict[str, Any]] = []):
        self.rag_db.insert_ingestion_entry(self.vector_db_path)
        ai_service = AIService()
        vectorstore = ai_service.rag_chromadb(self.vector_db_path)

        rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        print("CORE: create_stuff_documents_chain")
        stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

        print("CORE: create_history_aware_retriever")

        history_aware_retriever = create_history_aware_retriever(
            llm=chat, retriever=vectorstore.as_retriever(), prompt=rephrase_prompt
        )

        print("CORE: create_retrieval_chain")

        qa = create_retrieval_chain(
            retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
        )

        print("CORE: qa.invoke start")
        start_time = time.perf_counter()

        result = qa.invoke(input={"input": query, "chat_history": chat_history})

        print(f"CORE: qa.invoke end, elapsed: {time.perf_counter() - start_time} seconds")
        print("CORE: result")

        new_result = {
            "query": result["input"],
            "result": result["answer"],
            "source_documents": result["context"]
        }

        return new_result

    def create_sources_string(self, source_urls: Set[str]) -> str:
        if not source_urls:
            return ""
        sources_list = list(source_urls)
        sources_list.sort()
        sources_string = "sources:\n"
        for i, source in enumerate(sources_list):
            sources_string += f"{i+1}. {source}\n"
        return sources_string

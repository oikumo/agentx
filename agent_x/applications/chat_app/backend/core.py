import multiprocessing
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic import hub
from langchain_classic.chains.combine_documents import \
    create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import \
    create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import BaseChatModel
from langchain_ollama import OllamaEmbeddings

load_dotenv()


def run_llm(
    chat: BaseChatModel,
    query: str,
    chat_history: List[Dict[str, Any]] | None = None,
):
    if chat_history is None:
        chat_history = []

    embeddings = OllamaEmbeddings(model="nomic-embed-text", keep_alive=-1)

    vectorstore_chroma_path = "chroma_db_vf_device_management"
    docsearch = Chroma(
        persist_directory=vectorstore_chroma_path, embedding_function=embeddings
    )

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docsearch.as_retriever(), prompt=rephrase_prompt
    )

    qa = create_retrieval_chain(
        retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
    )

    start_time = time.perf_counter()
    result = qa.invoke(input={"input": query, "chat_history": chat_history})
    elapsed = time.perf_counter() - start_time

    if "answer" not in result:
        raise ValueError("Response does not contain expected answer key.")

    new_result = {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"],
    }

    return new_result

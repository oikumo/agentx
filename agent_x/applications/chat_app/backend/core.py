import multiprocessing
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

load_dotenv()
from typing import Any, Dict, List

from langchain_classic.chains.history_aware_retriever import \
    create_history_aware_retriever
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from langchain_classic.chains.retrieval import create_retrieval_chain
import time

load_dotenv()

from langchain_classic import hub
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


def run_llm(chat: BaseChatModel, query: str, chat_history: List[Dict[str, Any]] = []):
    #embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    #docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)

    """
    #model_path = "/home/oikumo/.cache/llama.cpp/unsloth_Qwen3-1.7B-GGUF_Qwen3-1.7B-Q4_K_M.gguf"
    model_path = "/home/oikumo/.cache/llama.cpp/Qwen_Qwen3-0.6B-GGUF_Qwen3-0.6B-Q8_0.gguf"
    chat = ChatLlamaCpp(
            temperature=0.5,
            model_path=model_path,
            n_ctx=10000,
            n_batch=64,
            max_tokens=1000,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=0.5,
            verbose=False)
    """

    embeddings = OllamaEmbeddings(model="nomic-embed-text", keep_alive=-1)

    vectorstore_chroma_path = "chroma_db_vf_device_management"
    docsearch = Chroma(persist_directory=vectorstore_chroma_path, embedding_function=embeddings)


    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    print("CORE: create_stuff_documents_chain")
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    print("CORE: create_history_aware_retriever")

    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docsearch.as_retriever(), prompt=rephrase_prompt
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

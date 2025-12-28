import os
import pathlib

from langchain_classic import hub
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, OpenAI

from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

from agent_x.app.llm.llms import get_llama_cpp_llm, get_local_llm_qwen3
from agent_x.modules.document_loaders.pdf.pdf_loader import pdf_loader
from agent_x.modules.vector_store.faiss.vector_store_faiss import create_faiss

load_dotenv()

def rag_pdf(pdf_path, vectorstore_path, retrieval_qa_chat_prompt, llm, embeddings):
    docs = pdf_loader(pdf_path)
    new_vectorstore = create_faiss(vectorstore_path, docs, embeddings)
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    retrieval_chain = create_retrieval_chain(new_vectorstore.as_retriever(), combine_docs_chain)

    res = retrieval_chain.invoke({"input": "Give me the gist of ReAct in 3 sentences, the output MUST BE in bullet points"})
    return res["answer"]

if __name__ == "__main__":
    print("rag_pdf")
    answer = rag_pdf(
        pdf_path="/home/oikumo/Proyectos/llm-projects/agent-x/resources/react.pdf",
        vectorstore_path = "/home/oikumo/Proyectos/llm-projects/agent-x/local/faiss_index_react",
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat"),
        # llm = get_llama_cpp_llm()
        llm = get_local_llm_qwen3(),
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # llm = OpenAI()
        # embeddings = OpenAIEmbeddings()
    )

    print(answer)

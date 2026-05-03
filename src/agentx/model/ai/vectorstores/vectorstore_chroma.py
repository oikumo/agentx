from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings


def vectorstore_chroma_openai(persist_directory: str):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        show_progress_bar=False,
        chunk_size=50,
        retry_min_seconds=10,
    )
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)


def vectorstore_chroma_ollama(persist_directory: str):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

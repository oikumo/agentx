from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


def create_vectorstore_chroma(persist_directory: str):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        show_progress_bar=False,
        chunk_size=50,
        retry_min_seconds=10,
    )
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

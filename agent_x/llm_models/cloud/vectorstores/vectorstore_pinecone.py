from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


def create_vectorstore_pinecone(index_name: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", show_progress_bar=False, chunk_size=50,
                                  retry_min_seconds=10, )
    return PineconeVectorStore(index_name=index_name, embedding=embeddings)

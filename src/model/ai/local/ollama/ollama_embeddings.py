from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

def create_embeddings_model() -> Embeddings:
    return OllamaEmbeddings(model="nomic-embed-text")
from langchain_ollama import OllamaEmbeddings


def create_embeddings_model():
    return OllamaEmbeddings(model="nomic-embed-text")
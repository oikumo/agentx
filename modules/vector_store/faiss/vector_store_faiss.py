from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def create_faiss(vectorstore_path: str, docs: List[Document], embeddings: Embeddings):
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(vectorstore_path)

    new_vectorstore = FAISS.load_local(
        vectorstore_path, embeddings, allow_dangerous_deserialization=True
    )

    return new_vectorstore

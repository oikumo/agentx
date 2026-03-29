from langchain_classic import hub
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from app_modules.document_loaders.pdf_loader import pdf_loader
from app_modules.data_stores.vector_store_faiss import create_faiss

class AgentRagPdf:
    def __init__(self, pdf_path: str, vectorstore_path: str, llm: BaseChatModel, embeddings: Embeddings):
        self.pdf_path = pdf_path
        self.vectorstore_path = vectorstore_path
        self.llm = llm
        self.embeddings = embeddings

    def run(self, query: str):

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        print(retrieval_qa_chat_prompt)

        self.rag_pdf(
            query=query,
            pdf_path=self.pdf_path,
            vectorstore_path=self.vectorstore_path,
            retrieval_qa_chat_prompt=retrieval_qa_chat_prompt,
            llm=self.llm,
            embeddings=self.embeddings
        )

    def rag_pdf(self, query: str, pdf_path, vectorstore_path, retrieval_qa_chat_prompt, llm, embeddings):
        print(f"rag_pdf query: {query}")
        print(f"rag_pdf loading pdf")
        input_data = {"input": query}
        docs = pdf_loader(pdf_path)

        print(f"rag_pdf creating vector store")
        new_vectorstore = create_faiss(vectorstore_path, docs, embeddings)
        combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
        retrieval_chain = create_retrieval_chain(
            new_vectorstore.as_retriever(), combine_docs_chain
        )

        print(f"rag_pdf processing response")

        res = retrieval_chain.invoke(input_data)
        print(res["answer"])

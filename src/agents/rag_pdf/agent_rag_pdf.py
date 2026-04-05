from pathlib import Path

from pathlib import Path

from langchain_classic import hub
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from app_modules.document_loaders.pdf_loader import pdf_loader
from app_modules.data_stores.vector_store_faiss import create_faiss


class AgentRagPdf:
    def __init__(
        self,
        pdf_path: str,
        vectorstore_path: str,
        llm: BaseChatModel,
        embeddings: Embeddings,
    ):
        self.pdf_path = pdf_path
        self.vectorstore_path = vectorstore_path
        self.llm = llm
        self.embeddings = embeddings
        self._vectorstore = None

    def _get_or_create_vectorstore(self):
        if self._vectorstore is not None:
            return self._vectorstore

        if Path(self.vectorstore_path).exists():
            from langchain_community.vectorstores import FAISS

            self._vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            docs = pdf_loader(self.pdf_path)
            self._vectorstore = create_faiss(
                self.vectorstore_path, docs, self.embeddings
            )
        return self._vectorstore

    def run(self, query: str) -> str:
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        return self.rag_pdf(
            query=query,
            pdf_path=self.pdf_path,
            vectorstore_path=self.vectorstore_path,
            retrieval_qa_chat_prompt=retrieval_qa_chat_prompt,
            llm=self.llm,
            embeddings=self.embeddings,
        )

    def rag_pdf(
        self,
        query: str,
        pdf_path,
        vectorstore_path,
        retrieval_qa_chat_prompt,
        llm,
        embeddings,
    ) -> str:
        input_data = {"input": query}
        vectorstore = self._get_or_create_vectorstore()
        combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
        retrieval_chain = create_retrieval_chain(
            vectorstore.as_retriever(), combine_docs_chain
        )

        res = retrieval_chain.invoke(input_data)
        return res["answer"]

    def run_streaming(self, query: str) -> str:
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        return self.rag_pdf_streaming(
            query=query,
            pdf_path=self.pdf_path,
            vectorstore_path=self.vectorstore_path,
            retrieval_qa_chat_prompt=retrieval_qa_chat_prompt,
            llm=self.llm,
            embeddings=self.embeddings,
        )

    def rag_pdf_streaming(
        self,
        query,
        pdf_path,
        vectorstore_path,
        retrieval_qa_chat_prompt,
        llm,
        embeddings,
    ) -> str:
        input_data = {"input": query}
        vectorstore = self._get_or_create_vectorstore()
        combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
        retrieval_chain = create_retrieval_chain(
            vectorstore.as_retriever(), combine_docs_chain
        )

        full_response = ""
        for chunk in retrieval_chain.stream(input_data):
            if "answer" in chunk and chunk["answer"]:
                full_response += chunk["answer"]
        return full_response

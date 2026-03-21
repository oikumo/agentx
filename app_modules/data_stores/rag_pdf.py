from langchain_classic.chains.combine_documents import \
    create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain

from app_modules.document_loaders.pdf.pdf_loader import pdf_loader
from app_modules.vector_store.faiss.vector_store_faiss import create_faiss


def rag_pdf(
    query: str, pdf_path, vectorstore_path, retrieval_qa_chat_prompt, llm, embeddings
):
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

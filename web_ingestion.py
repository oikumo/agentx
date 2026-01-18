import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp
from agent_x.core.common.logger import log_info

if __name__ == "__main__":
    #site_url= "https://developer.android.com/"
    site_url = "https://www.verifone.cloud/docs/device-management/device-management-user-guide/"

    now = datetime.datetime.now()
    datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    directory = f"vf/{datetime_string}"
    session_directory = f"sessions/web_ingestion/{directory}"

    directory_path = Path(session_directory)
    directory_path.mkdir(parents=True, exist_ok=True)

    vectorstore_chroma_dir = f"{session_directory}/chroma_db"
    result_json_file_path = f"{session_directory}/documents.jsonl"

    #embeddings = OllamaEmbeddings(model="nomic-embed-text") # embeddings = OllamaEmbeddings(model="embeddinggemma")



    #vectorstore = Chroma(persist_directory=vectorstore_chroma_dir, embedding_function=embeddings)
    #log_info(f"Vector store Chroma: {vectorstore_chroma_dir}")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", show_progress_bar=False, chunk_size=50,
                                  retry_min_seconds=10, )
    vectorstore = PineconeVectorStore(index_name=os.environ["INDEX_NAME_DOCUMENT_HELPER"], embedding=embeddings)
    log_info(f"Vector store Pinecone")

    app = WebIngestionApp(vectorstore)
    app.run(
        site_url= site_url,
        result_json_file_path= result_json_file_path
    )
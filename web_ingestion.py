import asyncio

from agent_x.applications.web_ingestion_app.tavily import WebExtract
from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp
from agent_x.core.sessions.session import Session
from agent_x.llm_models.local.vectorstores.vectorstrore_chroma import create_vectorstore_chroma

if __name__ == "__main__":
    #site_url= "https://developer.android.com/"
    site_url = "https://www.verifone.cloud/docs/device-management/device-management-user-guide/"


    session = Session("x")
    session.create()
    session_directory = session.directory

    result_json_file_path = f"{session_directory}/documents.jsonl"
    vectorstore_chroma_dir = f"{session_directory}/chroma_db"
    vectorstore = create_vectorstore_chroma(vectorstore_chroma_dir)
    #vectorstore = create_vectorstore_pinecone(os.environ["INDEX_NAME_DOCUMENT_HELPER"])

    tav = WebExtract(1, 1, 1000)

    app = WebIngestionApp(vectorstore, tav)
    asyncio.run(app.run(
        site_url= site_url,
        result_json_file_path= result_json_file_path
    ))
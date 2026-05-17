import asyncio

from agentx.common import utils
from agentx.common.input_utils import InputUtils
from agentx.model.ai.service import AIService
from agentx.model.rag.rag_db import RagDatabase
from agentx.model.rag.web_ingestion.web_extract import WebExtract
from agentx.model.rag.web_ingestion.web_ingestion_app import WebIngestionApp
from src import rag_add_entry

RAG_PROMPT="""
Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {question}
"""

class Rag:
    working_directory: str
    site_url = str | None

    def __init__(self, working_directory: str):
        self.working_directory = working_directory
        self.site_url = None
        self.vector_db_path = f"{self.working_directory}/chroma_db"
        self.documents_path = f"{self.working_directory}/documents.jsonl"
        self.rag_db_path = f"{self.working_directory}/rag.db"
        self.rag_db = RagDatabase(self.rag_db_path)

    def is_data(self) -> bool:
        return (
                utils.directory_exists(self.vector_db_path) and
                utils.file_exists(self.documents_path) and
                utils.file_exists(self.rag_db_path)
        )

    def web_ingestion(self) -> bool:
        if not InputUtils.is_valid_url(self.site_url):
            return False

        self.rag_db.insert_ingestion_entry(self.vector_db_path)
        ai_service = AIService()
        vectorstore = ai_service.rag_chromadb(self.vector_db_path)

        web_extractor = WebExtract(1, 2, 100)
        app = WebIngestionApp(vectorstore, web_extractor)

        asyncio.run(app.run(
            site_url= self.site_url,
            result_json_file_path= self.documents_path
        ))



        return True

import asyncio
from dataclasses import dataclass

from agentx.model.ai.service import AIService
from agentx.model.rag.query.rag_query import RagQuery, RagChatHistory
from agentx.model.rag.rag_db import RagDatabase
from agentx.model.rag.web_ingestion.web_extract import WebExtract
from agentx.model.rag.web_ingestion.web_ingestion_app import WebIngestionApp
from agentx.utils.utils_directories import is_directory_exists, is_file_exists
from agentx.utils.utils_input import is_valid_url


@dataclass
class RagWebExtractLevel:
    label: str
    max_depth: int
    max_breadth: int
    max_pages: int


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
        self.rag_query = RagQuery(
            llm=AIService().openrouter_llm_provider().create_llm(),
            vector_store=AIService().rag_chromadb(self.vector_db_path)
        )

    def query(self, user_prompt: str, history: RagChatHistory) -> RagChatHistory:
        return self.rag_query.ask(user_prompt, history)

    def is_data(self) -> bool:
        return (
                is_directory_exists(self.vector_db_path) and
                is_file_exists(self.documents_path) and
                is_file_exists(self.rag_db_path)
        )

    def web_ingestion(self, extract_level: RagWebExtractLevel) -> bool:
        if not is_valid_url(self.site_url):
            return False

        self.rag_db.insert_ingestion_entry(self.vector_db_path)
        ai_service = AIService()
        vectorstore = ai_service.rag_chromadb(self.vector_db_path)

        web_extractor = WebExtract(
            extract_level.max_depth,
            extract_level.max_breadth,
            extract_level.max_pages)

        app = WebIngestionApp(vectorstore, web_extractor)

        asyncio.run(app.run(
            site_url= self.site_url,
            result_json_file_path= self.documents_path
        ))

        return True
    
    def database_exists(self) -> bool:
        """Check if SQLite database exists."""
        return is_file_exists(self.rag_db_path)
    
    def documents_exist(self) -> bool:
        """Check if documents file exists."""
        return is_file_exists(self.documents_path)
    
    def get_ingested_url(self) -> str | None:
        """
        Get the most recently ingested URL.
        Returns None if no ingestion history.
        """
        if not self.database_exists():
            return None
        
        try:
            ingestions = self.rag_db.select_ingestion_entries()
            if ingestions:
                # Return the most recent URL (last entry)
                return ingestions[-1].vector_db_path
            return None
        except Exception:
            return None


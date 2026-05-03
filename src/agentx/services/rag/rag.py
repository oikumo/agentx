import asyncio
from urllib.parse import urlparse
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.services.ai.service import AIService
from agentx.services.rag.web_ingestion.web_extract import WebExtract
from agentx.services.rag.web_ingestion.web_ingestion_app import WebIngestionApp
from agentx.views.common.console import Console


class Rag:
    def __init__(self, session_manager: SessionController, ai_service: AIService):
        self.session_manager = session_manager
        self.ai_service = ai_service

    def web_ingestion(self, site_url):
        def is_valid_url(url):
            try:
                result = urlparse(url)
                # Check if both scheme (http/https) and netloc (domain) are present
                return all([result.scheme, result.netloc])
            except ValueError:
                return False

        if not is_valid_url(site_url):
            Console.log_info("Invalid URL")
            return False

        prompt = """
        Answer the following question based only on the provided context:

        <context>
        {context}
        </context>

        Question: {question}
        """
        Console.log_info(prompt)

        rag_directory = self.session_manager.get_directory_rag()

        result_json_file_path = f"{rag_directory}/documents.jsonl"
        chroma_dir = f"{rag_directory}/chroma_db"

        Console.log_info(f"Results folder: {result_json_file_path}")
        Console.log_info(f"Chroma folder: {chroma_dir}")

        vectorstore = self.ai_service.rag_chromadb(chroma_dir)


        web_extractor = WebExtract(1, 2, 100)
        app = WebIngestionApp(vectorstore, web_extractor)

        asyncio.run(app.run(
            site_url=site_url,
            result_json_file_path=result_json_file_path
        ))
        return None

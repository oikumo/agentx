import asyncio
from urllib.parse import urlparse
from agentx.model.ai.service import AIService
from agentx.model.rag.web_ingestion.web_extract import WebExtract
from agentx.model.rag.web_ingestion.web_ingestion_app import WebIngestionApp

class Rag:
    working_directory: str
    site_url = str | None

    def __init__(self, working_directory: str):
        self.working_directory = working_directory
        self.site_url = None

    def web_ingestion(self) -> bool:
        if not self.is_valid_url():
            return False

        prompt = """
        Answer the following question based only on the provided context:

        <context>
        {context}
        </context>

        Question: {question}
        """
        print(prompt)

        result_json_file_path = f"{self.working_directory}/documents.jsonl"
        chroma_dir = f"{self.working_directory}/chroma_db"

        print(f"Results folder: {result_json_file_path}")
        print(f"Chroma folder: {chroma_dir}")

        ai_service = AIService()
        vectorstore = ai_service.rag_chromadb(chroma_dir)

        web_extractor = WebExtract(1, 2, 100)
        app = WebIngestionApp(vectorstore, web_extractor)

        asyncio.run(app.run(
            site_url= self.site_url,
            result_json_file_path= result_json_file_path
        ))
        return False

    def is_valid_url(self):
        if not self.site_url:
            return False
        try:
            result = urlparse(self.site_url)
            # Check if both scheme (http/https) and netloc (domain) are present
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

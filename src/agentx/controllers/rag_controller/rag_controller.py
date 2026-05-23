from __future__ import annotations

from dataclasses import dataclass

from agentx.controllers.common.input_controllers.input_url_controller import InputUrlController
from agentx.controllers.rag_controller.rag_chat_controller import RagChatController
from agentx.controllers.rag_controller.rag_web_ingestion_controller import RagWebIngestionController
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.model.rag.rag import Rag, RagWebExtractLevel
from agentx.views.rag_view.rag_view import RagView

@dataclass
class RagState:
    url: str | None
    data_base_location: str | None
    documents_location: str | None

class RagController:
    view: RagView

    def __init__(self) -> None:
        self.view = RagView(self)
        self.session_controller = SessionController()
        rag_working_directory = self.session_controller.get_directory_rag()
        self.rag = Rag(rag_working_directory)

    def show(self):
        if self.view: self.view.show()

    def show_chat(self):
        chat = RagChatController()
        chat.show()

    def show_web_ingestion(self):
        ingestion = RagWebIngestionController()
        ingestion.show()

    def close(self) -> None:
        if self.view: self.view.print_message("close")

    def get_rag_state(self):
        data_base_path = None
        documents_path = None
        if self.rag.is_data():
            data_base_path = self.rag.vector_db_path
            documents_path = self.rag.documents_path

        return RagState(
            url=self.rag.site_url,
            data_base_location=data_base_path,
            documents_location=documents_path
        )


from __future__ import annotations

from dataclasses import dataclass

from agentx.screens.rag_controller.rag_chat_controller import RagChatController
from agentx.screens.rag_controller.rag_repository_selection_controller import RagRepositorySelectionController
from agentx.screens.rag_controller.rag_web_ingestion_controller import RagWebIngestionController
from agentx.model.session.session_manager import SessionController
from agentx.model.rag.rag_repository import RagRepository
from agentx.screens.rag_controller.rag_view import RagView

@dataclass
class RagState:
    url: str | None
    data_base_location: str | None
    documents_location: str | None

class RagController:
    view: RagView
    current_rag_repository: RagRepository | None

    def __init__(self) -> None:
        self.view = RagView(self)
        self.session_controller = SessionController()
        self.rag_working_directory = self.session_controller.get_directory_rag()
        self.current_rag_repository = None

    def show(self):
        if self.view: self.view.show()

    def select_repository(self):
        repository_selection = RagRepositorySelectionController(self.rag_working_directory)
        repository_selection.show()
        self.current_rag_repository = repository_selection.get_selected_repository()

    def show_chat(self):
        if not self.current_rag_repository: return
        chat = RagChatController(self.current_rag_repository)
        chat.show()

    def show_web_ingestion(self):
        if not self.current_rag_repository: return
        ingestion = RagWebIngestionController(self.current_rag_repository)
        ingestion.show()

    def close(self) -> None:
        if self.view: self.view.print_message("close")

    def get_rag_state(self) -> RagState | None:
        if not self.current_rag_repository:
            return None

        return None
        """
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
        """


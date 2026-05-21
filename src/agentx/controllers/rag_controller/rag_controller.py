from __future__ import annotations

from dataclasses import dataclass

from agentx.controllers.common.input_controllers.input_url_controller import InputUrlController
from agentx.controllers.rag_controller.rag_chat_controller import RagChatController
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.model.rag.rag import Rag
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

    def close(self) -> None:
        if self.view: self.view.print_message("close")

    def show_chat(self):
        chat = RagChatController()
        chat.show()

    def ask_user_site_url(self):
        input_controller = InputUrlController()
        input_controller.show()
        self.rag.site_url = input_controller.url
        if not self.rag.site_url:
            self.view.print_message_error("INVALID URL")

    def set_site_url(self, site_url: str):
        self.rag.site_url = site_url

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

    def do_web_ingestion(self):
        if not self.rag.site_url:
            self.view.print_message("missing site url")
            return

        self.view.print_message(f"{self.rag.site_url}")
        self.view.print_message(f"{self.rag.working_directory}")
        self.rag.web_ingestion()


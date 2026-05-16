from __future__ import annotations

from agentx.controllers.session_controller.session_controller import SessionController
from agentx.model.rag.rag import Rag
from agentx.views.rag_view.rag_view import RagView

class RagController:
    view: RagView

    def __init__(self) -> None:
        self.view = RagView(self)
        self.session_controller = SessionController()
        self.site_url = ""

    def show(self):
        if self.view: self.view.show()

    def close(self) -> None:
        if self.view: self.view.print_message("close")

    def set_site_url(self, site_url: str):
        self.site_url = site_url

    def do_web_ingestion(self):
        if not self.site_url:
            self.view.print_message("missing site url")
            return

        rag_directory = self.session_controller.get_directory_rag()
        self.view.print_message(f"{self.site_url}")
        self.view.print_message(f"{rag_directory}")

        rag = Rag()
        rag.web_ingestion(self.site_url, rag_directory)


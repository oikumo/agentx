from __future__ import annotations
from agentx.views.ui.ui_console import UIConsole
from agentx.views.rag_view.rag_view import RagView

class RagController:
    view: RagView

    def __init__(self) -> None:
        self.view = RagView(self, UIConsole())

    def show(self):
        if self.view: self.view.show()

    def close(self) -> None:
        if self.view: self.view.print_message("close")

        """
        site_url = arguments[0]

        rag = Rag()
        rag.web_ingestion(site_url, self.controller.session_controller.get_directory_rag())
        """


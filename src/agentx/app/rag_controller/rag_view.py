from __future__ import annotations
from typing import TYPE_CHECKING
from agentx.ui.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.app.rag_controller.rag_controller import RagController

RAG_MENU= """
OPTIONS
    (1) Select RAG repository
    (2) Web Ingestion
    (3) RAG Chat
    (4) Quit

"""

class RagView:
    controller: RagController

    def __init__(self, controller: RagController):
        self.controller = controller
        self.console = UIConsole("(rag)")

    def show(self):
        while True:
            self._show_rag_main_menu()
            user_input = self.console.capture_input()
            match user_input:
                case "1":
                    self.controller.select_repository()
                case "2":
                    self.controller.show_web_ingestion()
                case "3":
                    self.controller.show_chat()
                case "4":
                    self.controller.close()
                    return
                case "quit":
                    self.controller.close()
                    return
                case _  : self.print_message("Invalid option")


    def _show_rag_main_menu(self):
        self.console.header("RAG")
        self._show_rag_state()
        self.console.info(RAG_MENU)

    def _show_rag_state(self) -> None:
        state = self.controller.get_rag_state()
        if not state:
            self.console.waning(f"NO SELECTED REPOSITORY")
            return
        if not state.url:
            self.console.waning(f"url: MISSING")
        else:
            self.console.success(f"url: {state.url}")

        if not state.data_base_location:
            self.console.waning(f"database: MISSING")
        else:
            self.console.success(f"database: {state.data_base_location}\n")

    def print_message(self, message: str):
        self.console.info(message)

    def print_message_error(self, message: str):
        self.console.error(message)


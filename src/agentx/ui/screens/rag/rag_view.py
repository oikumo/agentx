from __future__ import annotations
from typing import TYPE_CHECKING
from agentx.ui.common.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.ui.screens.rag.rag_controller import RagController

RAG_MENU= """
OPTIONS
    (1) Select RAG repository
    (2) Create RAG repository
    (3) Web Ingestion
    (4) RAG Chat
    (5) Quit

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
            
            if user_input is None:
                continue
            
            match user_input:
                case "1":
                    self.controller.select_repository()
                case "2":
                    self.controller.create_repository()
                case "3":
                    self.controller.show_web_ingestion()
                case "4":
                    self.controller.show_chat()
                case "5":
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
            self.console.waning("⚠️  NO SELECTED REPOSITORY")
            self.console.info("   Please select or create a repository to continue")
            return
        
        # Show repository info
        if self.controller.current_rag_repository and self.controller.current_rag_repository.id:
            self.console.success(f"📁 Repository: {self.controller.current_rag_repository.id}")
        
        if not state.url:
            self.console.waning("   Status: Empty (no data ingested yet)")
        else:
            self.console.success(f"   Ingested URL: {state.url}")

        if not state.data_base_location:
            self.console.waning("   Database: Not initialized")
        else:
            self.console.success(f"   Database: {state.data_base_location}")

        if not state.documents_location:
            self.console.waning("   Documents: No documents ingested")
        else:
            self.console.success(f"   Documents: {state.documents_location}")

    def print_message(self, message: str):
        self.console.info(message)

    def print_message_error(self, message: str):
        self.console.error(message)


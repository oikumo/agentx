from __future__ import annotations
from typing import TYPE_CHECKING
from agentx.ui_common.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.ui.rag_controller.rag_web_ingestion_controller import RagWebIngestionController

RAG_WEB_INGESTION_MENU= """
OPTIONS
    (1) Set ingestion URL
    (2) Set ingestion level
    (3) Ingest
    (4) Quit

"""

class RagWebIngestionView:
    def __init__(self, controller: RagWebIngestionController):
        self.controller = controller
        self.console = UIConsole("(rag/web-ingestion)")

    def show(self):
        while True:
            self.console.info(RAG_WEB_INGESTION_MENU)
            user_input = self.console.capture_input()
            match user_input:
                case "1":
                    self.controller.ask_user_site_url()
                case "2":
                    self.controller.ask_user_web_extraction_level()
                case "3":
                    self.controller.do_web_ingestion()
                case "4":
                    self.controller.close()
                    return
                case "quit":
                    self.controller.close()
                    return
                case _  : self.print_message(f"Invalid option: {user_input}")

    def show_web_extraction_level(self):
        self.console.info(f"Web extraction level: {self.controller.get_web_extract_level().label}")

    def show_error_missing_url(self):
        self.console.error("Missing site url")

    def show_web_ingestion_begin(self):
        self.console.header("WEB INGESTION BEGIN")
        self.console.info(f"Url to ingest: {self.controller.get_site_url()}")
        self.console.info(f"Working directory: {self.controller.get_working_directory()}")

    def show_web_ingestion_end(self):
        self.console.header("WEB INGESTION END")

    def show_input_error_invalid_url(self):
        self.console.error("Invalid URL")

from __future__ import annotations

from agentx.controllers.common.input_controllers.input_options_controller import InputOptionsController
from agentx.controllers.common.input_controllers.input_url_controller import InputUrlController
from agentx.controllers.rag_controller.constants import WEB_EXTRACT_LEVEL_LOW, WEB_EXTRACT_LEVEL_MID, WEB_EXTRACT_LEVEL_HIGH
from agentx.views.rag_view.rag_web_ingestion_view import RagWebIngestionView
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from agentx.controllers.session_controller.session_controller import SessionController
from agentx.model.ai.service import AIService
from agentx.model.rag.rag import Rag, RagChatHistory, RagWebExtractLevel
from agentx.views.rag_view.rag_chat_view import RagChatView

class RagWebIngestionController:
    web_extract_level: RagWebExtractLevel = WEB_EXTRACT_LEVEL_LOW

    def __init__(self) -> None:
        self.view = RagWebIngestionView(self)
        self.session_controller = SessionController()
        rag_working_directory = self.session_controller.get_directory_rag()
        self.rag = Rag(rag_working_directory)

    def show(self):
        self.view.show()

    def close(self) -> None:
        pass

    def ask_user_site_url(self):
        input_controller = InputUrlController()
        input_controller.show()
        self.rag.site_url = input_controller.url
        if not self.rag.site_url:
            self.view.show_input_error_invalid_url()

    def ask_user_web_extraction_level(self):
        options: dict[int, str] = {
            1: "Low",
            2: "Mid",
            3: "High"
        }
        option_selection = InputOptionsController(options)
        option_selection.show()
        selected_option = option_selection.get_option()

        match selected_option:
            case 1: self.web_extract_level = WEB_EXTRACT_LEVEL_LOW
            case 2: self.web_extract_level = WEB_EXTRACT_LEVEL_MID
            case 3: self.web_extract_level = WEB_EXTRACT_LEVEL_HIGH
            case _ : self.web_extract_level = WEB_EXTRACT_LEVEL_LOW

        self.view.show_web_extraction_level()

    def get_web_extract_level(self) -> RagWebExtractLevel:
        return self.web_extract_level

    def set_site_url(self, site_url: str) -> None:
        self.rag.site_url = site_url

    def get_site_url(self) -> str:
        return self.rag.site_url

    def get_working_directory(self) -> str:
        return self.rag.working_directory

    def do_web_ingestion(self):
        if not self.rag.site_url:
            self.view.show_error_missing_url()
            return

        self.view.show_web_ingestion_begin()
        self.rag.web_ingestion(self.web_extract_level)
        self.view.show_web_ingestion_end()
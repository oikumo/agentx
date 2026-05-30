from __future__ import annotations
from langchain_core.messages import BaseMessage
from agentx.model.ai.service import AIService
from agentx.model.rag.rag import Rag, RagChatHistory
from agentx.model.rag.rag_repository import RagRepository
from agentx.ui.rag_controller.rag_chat_view import RagChatView


class RagChatController:
    def __init__(self, rag_repository: RagRepository) -> None:
        self.view = RagChatView(self)
        self.history: list[BaseMessage] = []
        self.llm = AIService().openrouter_llm_provider().create_llm()
        self.rag = Rag(rag_repository.path)
        self.rag_chat_history = RagChatHistory()

    def show(self):
        self.view.show()

    def close(self) -> None:
        pass

    def process_user_message(self, user_input: str) -> bool:
        if user_input.strip().lower() in ("quit", "exit"):
            return False
        self.rag_chat_history = self.rag.query(user_input, self.rag_chat_history)

        for text in self.rag_chat_history.chat_answers_history:
            self.view.show_message(text)

        for text in self.rag_chat_history.chat_history:
            self.view.show_message(text)

        return True

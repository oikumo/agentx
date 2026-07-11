from __future__ import annotations
from langchain_core.messages import BaseMessage
from agentx.model.ai.service import AIService
from agentx.model.chat import ChatHistoryRepository, Conversation
from agentx.model.rag.rag import Rag, RagChatHistory
from agentx.model.rag.rag_repository import RagRepository
from agentx.ui.screens.rag.rag_chat_view import RagChatView


class RagChatController:
    def __init__(
        self, 
        rag_repository: RagRepository,
        history_repo: ChatHistoryRepository | None = None
    ) -> None:
        self.view = RagChatView(self)
        self.history: list[BaseMessage] = []
        self.llm = AIService().get_current_llm()
        self.rag = Rag(rag_repository.path)
        self.rag_chat_history = RagChatHistory()
        self.history_repo = history_repo or ChatHistoryRepository()
        self.current_conversation_id: int | None = None

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

        # Persist to database if conversation is active
        if self.current_conversation_id:
            self._save_messages(user_input)

        return True

    # === Persistence Methods ===

    def start_new_conversation(self, title: str | None = None, model_provider: str | None = None) -> int:
        """Create a new conversation and set as current."""
        if title is None:
            from datetime import datetime
            title = f"RAG Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        if model_provider is None:
            model_provider = AIService().get_current_provider_name() or "Unknown"
        
        self.current_conversation_id = self.history_repo.create_conversation(title, model_provider)
        self.rag_chat_history = RagChatHistory()  # Reset RAG history
        return self.current_conversation_id

    def load_conversation(self, conversation_id: int) -> bool:
        """Load a conversation from the database."""
        result = self.history_repo.get_conversation_with_messages(conversation_id)
        if not result:
            return False
        
        conv, messages = result
        self.current_conversation_id = conversation_id
        self.rag_chat_history = RagChatHistory()  # Reset RAG history
        
        # Notify view to refresh
        if self.view:
            self.view.show_initial_message()
            for msg in messages:
                if msg.role != "system":
                    self.view.show_message(f"[{msg.timestamp.strftime('%H:%M')}] {msg.role.capitalize()}: {msg.content}")
        
        return True

    def save_conversation(self) -> bool:
        """Save current in-memory history to the database."""
        if self.current_conversation_id is None:
            return False
        return True

    def list_conversations(self, limit: int = 20) -> list[Conversation]:
        """Get recent conversations for the sidebar."""
        return self.history_repo.get_recent_conversations(limit)

    def _save_messages(self, user_message: str) -> None:
        """Save user message and latest RAG answer to the database."""
        if self.current_conversation_id is None:
            return
        
        # Get the latest answer
        latest_answer = ""
        if self.rag_chat_history.chat_answers_history:
            latest_answer = self.rag_chat_history.chat_answers_history[-1]
        
        self.history_repo.add_message(
            self.current_conversation_id, 
            "user", 
            user_message
        )
        if latest_answer:
            self.history_repo.add_message(
                self.current_conversation_id, 
                "assistant", 
                latest_answer
            )
    
    def get_current_conversation_id(self) -> int | None:
        """Get the current conversation ID."""
        return self.current_conversation_id
    
    def set_current_conversation_id(self, conversation_id: int) -> None:
        """Set the current conversation ID (for loading existing)."""
        self.current_conversation_id = conversation_id
    
    def delete_current_conversation(self) -> bool:
        """Delete the current conversation."""
        if self.current_conversation_id is None:
            return False
        result = self.history_repo.delete_conversation(self.current_conversation_id)
        if result:
            self.current_conversation_id = None
            self.rag_chat_history = RagChatHistory()
        return result
    
    def update_conversation_title(self, title: str) -> bool:
        """Update the current conversation title."""
        if self.current_conversation_id is None:
            return False
        return self.history_repo.update_conversation_title(self.current_conversation_id, title)
    
    def export_current_conversation_json(self) -> dict | None:
        """Export current conversation as JSON."""
        if self.current_conversation_id is None:
            return None
        return self.history_repo.export_conversation_json(self.current_conversation_id)
    
    def export_current_conversation_markdown(self) -> str | None:
        """Export current conversation as Markdown."""
        if self.current_conversation_id is None:
            return None
        return self.history_repo.export_conversation_markdown(self.current_conversation_id)
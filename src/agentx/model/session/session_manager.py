from __future__ import annotations

from agentx.model.session.session import Session

SESSION_DIRECTORIES_RAG = "rag"


class SessionManager:
    def __init__(self):
        self._current_session: Session | None = Session()

    def get_directory_rag(self) -> str:
        if not self._current_session:
            return ""
        return f"{self._current_session.directory}/{SESSION_DIRECTORIES_RAG}"

    def get_current_session(self) -> Session | None:
        return self._current_session

    def create_new_session(self) -> Session:
        if self._current_session:
            self._current_session = self._current_session.create_new_session()
            return self._current_session

        self._current_session = Session()
        if not self._current_session.create():
            raise Exception("Failed to create new session")

        return self._current_session

    def insert_history_entry(self, entry: str):
        if self._current_session:
            self._current_session.insert_history_entry(entry)

    def select_history_entry(self):
        if self._current_session:
            return self._current_session.select_history_entry()
        return None

    def get_session_name(self) -> str:
        if not self._current_session or not self._current_session.name:
            return "none"
        return self._current_session.name


from app.model.db.data_base import SessionDatabase
from app.model.user_sessions.session import Session

from app.model.model_entities import HistoryEntry


class Model:
    def __init__(self, session_name: str) -> None:
        self.session = Session(session_name)
        if not self.session.create() or not self.session.is_created():
            raise Exception()

        self.database = SessionDatabase(self.session)

    def log_command(self, entry: HistoryEntry) -> bool:
        return self.database.insert_history_entry(entry.command)

    def get_command_history(self) -> list[HistoryEntry]:
        entries = self.database.select_history_entry()
        if not entries:
            return []

        return [
            HistoryEntry(
                command=entry.command, id=entry.id, created_at=entry.created_at
            )
            for entry in entries
        ]

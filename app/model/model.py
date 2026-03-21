from dataclasses import dataclass

from app.model.db.data_base import SessionDatabase
from app.model.user_sessions.session import Session


@dataclass
class HistoryEntry:
    command_name: str


class Model:
    def __init__(self, session_name: str):
        self.session = Session(session_name)
        if not self.session.create() or not self.session.is_created():
            raise Exception()

        self.database = SessionDatabase(self.session)

    def log_command(self, entry: HistoryEntry):
        self.database.insert_history_entry(entry.command_name)


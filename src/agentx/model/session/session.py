from __future__ import annotations

from agentx.common.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from agentx.common.utils import create_directory_with_timestamp, create_directory_without_timestamp, directory_exists
from agentx.model.session.session_db import SessionDatabase, TableHistory


class Session:
    session_name: str | None
    directory: str | None
    database: SessionDatabase | None = None

    __use_timestamp: bool

    @classmethod
    def create_session_name(cls, name: str) -> str:
        if not (name and name.strip()):
            return SESSION_DEFAULT_NAME
        elif " " in name:
            return name.replace(" ", "_").lower()
        else:
            return name

    @classmethod
    def create_session_directory(cls, session_name: str, use_timestamp: bool = False) -> str | None:
        if use_timestamp:
            return create_directory_with_timestamp(
                session_name, SESSION_DEFAULT_BASE_DIRECTORY)
        else:
            return create_directory_without_timestamp(
                session_name, SESSION_DEFAULT_BASE_DIRECTORY)

    def __init__(self):
        self.session_name = self.create_session_name(SESSION_DEFAULT_NAME)
        self.create()

    def create(self, time_stamp: bool = False) -> bool:
        if not self.session_name:
            return False

        directory = self.create_session_directory(self.session_name, time_stamp)
        if not directory:
            return False

        self.directory = directory
        self.database = SessionDatabase(self)

        return True

    def insert_history_entry(self, entry: str):
        self.database.insert_history_entry(entry)

    def select_history_entry(self) -> list[TableHistory.History] | None:
        return self.database.select_history_entry()

    def is_created(self):
        if not self.directory:
            return False
        return directory_exists(self.directory)


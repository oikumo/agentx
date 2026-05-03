from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.model.session.session_db import SessionDatabase, TableHistory

from agentx.common.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from agentx.common.utils import create_directory_with_timestamp, create_directory_without_timestamp, directory_exists
from agentx.model.session.session_db import SessionDatabase


class Session:
    database: SessionDatabase
    __directory: str | None
    __session_name: str
    __use_timestamp: bool

    @property
    def name(self) -> str:
        return self.__session_name

    @property
    def directory(self) -> str | None:
        return self.__directory

    def __init__(self, name: str, use_timestamp: bool = True):
        self.__directory = None
        self.__session_name = SESSION_DEFAULT_NAME
        self.__use_timestamp = use_timestamp
        if not (name and name.strip()):
            self.__session_name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.__session_name = name.replace(" ", "_").lower()
        else:
            self.__session_name = name

    def create(self):
        self.__directory = None
        if self.__use_timestamp:
            new_directory = create_directory_with_timestamp(
                self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY
            )
        else:
            new_directory = create_directory_without_timestamp(
                self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY
            )
        if not new_directory:
            return False
        self.__directory = new_directory
        self.database = SessionDatabase(self)

        return True

    def insert_history_entry(self, entry: str):
        self.database.insert_history_entry(entry)

    def select_history_entry(self) -> list[TableHistory.History] | None:
        return self.database.select_history_entry()

    def is_created(self):
        if not self.__directory:
            return False
        return directory_exists(self.__directory)

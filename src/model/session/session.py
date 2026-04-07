from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Any

from app.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from app.utils import (
    create_directory_with_timestamp,
    directory_exists,
    dangerous_delete_directory,
)
from model.session.session_db import TableHistory, TableUser


class Session:
    __directory: str | None
    __session_name: str

    @property
    def name(self) -> str:
        return self.__session_name

    @property
    def directory(self) -> str | None:
        return self.__directory

    def __init__(self, name: str):
        self.__directory = None
        self.__session_name = SESSION_DEFAULT_NAME
        if not (name and name.strip()):
            self.__session_name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.__session_name = name.replace(" ", "_").lower()
        else:
            self.__session_name = name

    def create(self):
        self.__directory = None
        new_directory = create_directory_with_timestamp(
            self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY
        )
        if not new_directory:
            return False
        self.__directory = new_directory
        return True

    def is_created(self):
        if not self.__directory:
            return False
        return directory_exists(self.__directory)

    def destroy(self) -> bool:
        if not self.is_created():
            return False
        dangerous_delete_directory(self.__directory)
        return True


class SessionDatabase:
    def __init__(self, session: Session):
        self._session = session
        self._create()

    def _create(self):
        db_path = self._get_session_path()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(TableUser.TABLE_USER)
            cursor.execute(TableHistory.TABLE_HISTORY)
            conn.commit()

    def _get_session_path(self):
        db_directory = Path(self._session.directory)
        db_filename = Path(f"{self._session.name}.db")
        db_path = db_directory / db_filename
        return db_path

    def insert_history_entry(self, info: str) -> bool:
        now = datetime.now(timezone.utc)
        return self._insert(TableHistory.INSERT_HISTORY, [info, now])

    def select_history_entry(self) -> list[TableHistory.History] | None:
        rows = self._select_all(TableHistory.TABLE_NAME)
        if not rows:
            return None
        return [TableHistory.History(*row) for row in rows]

    def _insert(self, query: str, parameters: list[Any]) -> bool:
        db_path = self._get_session_path()
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
            return True
        except Exception:
            return False

    def _select_all(self, table) -> list[Any] | None:
        allowed_tables = {TableHistory.TABLE_NAME, TableUser.TABLE_NAME}
        if table not in allowed_tables:
            raise ValueError("Invalid table name")
        db_path = self._get_session_path()
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            return None

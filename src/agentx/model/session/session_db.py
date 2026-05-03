from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.model.session.session import Session

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class HistoryEntry:
    command: str
    id: int = 0
    created_at: str = ""


class TableHistory:
    TABLE_NAME = "history"
    TABLE_HISTORY = """
    CREATE TABLE IF NOT EXISTS history (
     id INTEGER PRIMARY KEY, 
     command TEXT, 
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """
    INSERT_HISTORY = "INSERT INTO history (command, created_at) VALUES (?, ?)"

    @dataclass
    class History:
        id: int
        command: str
        created_at: str

class TableUser:
    TABLE_NAME = "users"
    TABLE_USER = "CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    INSERT_USER = "INSERT INTO users (name, age) VALUES (?, ?)"

SESSION_DATABASE_FILENAME = "session.db"

class SessionDatabase:
    exists = False
    session: Session | None = None

    def __init__(self, session: Session):
        self.session = session

    def get_db_path(self) -> str | None:
        if not self.session or not self.session.directory: return None
        db_path = Path(self.session.directory) / Path(SESSION_DATABASE_FILENAME)

        if not db_path.exists() and not self.create_if_not_exists(self.session.directory):
            return None

        return str(db_path.absolute().resolve())


    def create_if_not_exists(self, session_directory: str) -> bool:
        if not session_directory: return False
        db_path = Path(session_directory) / Path(SESSION_DATABASE_FILENAME)
        if db_path.exists():
            return True

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(TableUser.TABLE_USER)
                cursor.execute(TableHistory.TABLE_HISTORY)
                conn.commit()
        except Exception:
            return False

        self.exists = True

        return True

    def insert_history_entry(self, info: str) -> bool:
        now = datetime.now(timezone.utc)
        return self._insert(TableHistory.INSERT_HISTORY, [info, now])

    def select_history_entry(self) -> list[TableHistory.History] | None:
        rows = self._select_all(TableHistory.TABLE_NAME)
        if not rows:
            return None
        return [TableHistory.History(*row) for row in rows]

    def _insert(self, query: str, parameters: list[Any]) -> bool:
        db_path = self.get_db_path()
        if not db_path: return False

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                return True
        except Exception:
            return False

    def _select_all(self, table) -> list[Any] | None:
        db_path = self.get_db_path()
        if not db_path: return None

        allowed_tables = {TableHistory.TABLE_NAME, TableUser.TABLE_NAME}
        if table not in allowed_tables:
            raise ValueError("Invalid table name")

        if not db_path: return None
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            return None

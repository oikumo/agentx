from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Any
from app.model.db.database_definition import TableHistory, TableUser
from app.model.user_sessions.session import Session


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

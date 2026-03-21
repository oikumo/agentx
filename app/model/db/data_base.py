from datetime import datetime, timezone
import sqlite3
from pathlib import Path

from app.model.user_sessions.session import Session

class TableUser:
    TABLE_USER = "CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    INSERT_USER = "INSERT INTO users (name, age) VALUES (?, ?)"

class TableHistory:
    TABLE_HISTORY = """
    CREATE TABLE IF NOT EXISTS history (
     id INTEGER PRIMARY KEY, 
     command TEXT, 
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """
    INSERT_HISTORY = "INSERT INTO history (command, created_at) VALUES (?, ?)"


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

    def _get_session_path(self):
        db_directory = Path(self._session.directory)
        db_filename = Path(f"{self._session.name}.db")
        db_path = db_directory / db_filename
        return db_path

    def insert_history_entry(self, info: str) -> bool:
        now = datetime.now(timezone.utc)
        return self._insert(TableHistory.INSERT_HISTORY, [info, now])

    def _insert(self, query: str, parameters: list[str]) -> bool:
        db_path = self._get_session_path()
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
            return False
        except Exception as e:
            return True


import sqlite3
from pathlib import Path

from app.model.user_sessions.session import Session

SCHEMA = "CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
INSERT_USER = "INSERT INTO users (name, age) VALUES (?, ?)"

class SessionDatabase:
    def get_sesstion_path(self, session: Session):
        db_directory = Path(session.directory)
        db_filename = Path(f"{session.name}.db")
        db_path = db_directory / db_filename
        return db_path

    def run_query(self, session: Session):
        db_path = self.get_sesstion_path(session)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SCHEMA)
            cursor.execute(INSERT_USER, ("Test", 33))
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            print(rows)
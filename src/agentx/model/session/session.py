from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY
from agentx.common.utils import create_directory_with_timestamp, create_directory_without_timestamp, directory_exists
from agentx.model.session.session_db import SessionDatabase, TableHistory

SESSION_CURRENT_NAME = "current"

class Session:
    name: str | None
    directory: str | None
    database: SessionDatabase | None = None

    def __init__(self):
        self.name = self.create_session_name(SESSION_CURRENT_NAME)
        self.create()

    def create(self, time_stamp: bool = False) -> bool:
        if not self.name:
            return False

        directory = self.create_session_directory(self.name, time_stamp)
        if not directory:
            return False

        self.directory = directory
        self.database = SessionDatabase(self)

        return True

    def insert_history_entry(self, entry: str) -> bool:
        if not self.database: return False
        return self.database.insert_history_entry(entry)


    def select_history_entry(self) -> list[TableHistory.History] | None:
        if not self.database: return None
        return self.database.select_history_entry()

    def is_created(self):
        if not self.directory:
            return False
        return directory_exists(self.directory)

    def create_new_session(self) -> Session:
        backup_path = self.backup_current_session()
        if backup_path:
            print(f"Previous session backed up to: {backup_path}")
        else:
            print("Warning: Could not backup current session")

        new_session = Session()
        if not new_session.create(time_stamp=True):
            raise Exception("Failed to create new session")

        return new_session


    def backup_current_session(self) -> str | None:
        if not self.is_created():
            return None

        current_dir = self.directory
        if not current_dir:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        backup_name = f"current_backup_{timestamp}"
        base_path = Path(SESSION_DEFAULT_BASE_DIRECTORY)
        backup_dir = base_path / backup_name

        try:
            shutil.move(str(current_dir), str(backup_dir))
            return str(backup_dir)
        except Exception as e:
            print(f"Error backing up session: {e}")
            return None

    @classmethod
    def create_session_name(cls, name: str) -> str:
        if not (name and name.strip()):
            return SESSION_CURRENT_NAME
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



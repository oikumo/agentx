from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from agentx.utils import utils_directories
from agentx.utils.constants import SESSION_DEFAULT_BASE_DIRECTORY
from agentx.utils.utils import create_directory_with_timestamp, create_directory_without_timestamp
from agentx.utils.utils_directories import is_directory_exists
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
        return is_directory_exists(self.directory)

    def create_new_session(self) -> Session:
        """AXR-04: one coherent session transition.

        Back up the current session, then create the replacement at the
        startup contract's ``current`` name (a fresh ``Session()`` opens
        ``current`` — a timestamped replacement was never read back).
        Stop on backup failure instead of continuing with an ambiguous active
        session; if replacement creation fails, roll the backup back into
        place so the previous usable session stays active.
        """
        backup_path = self.backup_current_session()
        if backup_path is None:
            # A usable current session existed but could not be moved:
            # refuse the transition rather than risk a split/ambiguous state.
            if self.is_created():
                raise RuntimeError(
                    "failed to back up current session; new session not created"
                )
            # No current session on disk: safe to proceed with a plain one.

        new_session = Session()
        if not new_session.is_created():
            # Rollback: restore the backed-up session before failing.
            if backup_path is not None and self.directory:
                try:
                    shutil.move(str(backup_path), str(self.directory))
                    print("Rolled back previous session after failed creation")
                except Exception as rollback_err:  # noqa: BLE001
                    print(f"Error rolling back session: {rollback_err}")
            raise RuntimeError("Failed to create new session")

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


# TA: AXR-04: is_created imports helper explicitly; create_new_session backs up then replaces AT current (startup contract), raises on backup failure of a live session, rolls back backup if replacement creation fails (pkg4 agentx_1_0_0).

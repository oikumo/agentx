from pathlib import Path
import shutil
from datetime import datetime

from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY
from agentx.model.session.session import Session

SESSION_DIRECTORIES_RAG = "rag"
SESSION_CURRENT_NAME = "current"

class SessionController:
    _current_session = Session | None

    def __init__(self):
        self._current_session = Session()

    def get_directory_rag(self):
        return f"{self._current_session.directory}/{SESSION_DIRECTORIES_RAG}"

    def get_current_session(self) -> Session | None:
        return self._current_session

    def _backup_current_session(self) -> str | None:
        if self._current_session is None or not self._current_session.is_created():
            return None
        
        current_dir = self._current_session.directory
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

    def create_new_session(self, name: str = "session") -> Session:
        if self._current_session is not None and self._current_session.is_created():
            backup_path = self._backup_current_session()
            if backup_path:
                print(f"Previous session backed up to: {backup_path}")
            else:
                print("Warning: Could not backup current session")

        self._current_session = None
        self._current_session = Session()
        if not self._current_session.create(time_stamp=True):
            raise Exception("Failed to create new session")


        return self._current_session

    def insert_history_entry(self, entry: str):
        self._current_session.insert_history_entry(entry)

    def select_history_entry(self):
        return self._current_session.select_history_entry()

    def get_session_name(self) -> str:
        if not self._current_session or not self._current_session.session_name :
            return "none"
        return self._current_session.session_name


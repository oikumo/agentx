from pathlib import Path
from typing import Optional
import shutil
from datetime import datetime
from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY
from agentx.model.session.session import Session
from agentx.model.session.session_db import SessionDatabase

SESSION_DIRECTORIES_RAG = "rag"
SESSION_CURRENT_NAME = "current"

class SessionController:
    _current_session: Session = None
    _database: Optional[SessionDatabase] = None

    def __init__(self):
        self._ensure_current_session_exists()
        self._ensure_folder_exists(SESSION_DIRECTORIES_RAG)

    def get_directory_rag(self):
        return f"{self._current_session.directory}/{SESSION_DIRECTORIES_RAG}"

    def _ensure_current_session_exists(self) -> Session:
        self._current_session = Session(SESSION_CURRENT_NAME, use_timestamp=False)
        if not self._current_session.create():
            raise Exception("Failed to create 'current' session")
        self._database = SessionDatabase(self._current_session)
        return self._current_session

    def _ensure_folder_exists(self, session_folder_path: str):
        """Ensure the 'rag' folder always exists in the session directory."""
        rag_path = Path(self._current_session.directory) / session_folder_path
        rag_path.mkdir(exist_ok=True)

    def get_current_session(self) -> Session:
        """Get the current session. Creates one if it doesn't exist."""
        if self._current_session is None:
            self._ensure_current_session_exists()
        return self._current_session

    def _backup_current_session(self) -> str:
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
            # Rename current directory to backup (add timestamp)
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
        self._database = None
        
        self._current_session = Session(SESSION_CURRENT_NAME, use_timestamp=False)
        if not self._current_session.create():
            raise Exception("Failed to create new session")

        self._database = SessionDatabase(self._current_session)
        
        return self._current_session
    
    def get_database(self) -> Optional[SessionDatabase]:
        return self._database
    
    def get_session_name(self) -> str:
        if self._current_session:
            return self._current_session.name
        return "none"
    
    def has_session(self) -> bool:
        return self._current_session is not None and self._current_session.is_created()

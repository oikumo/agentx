from pathlib import Path
from typing import Optional
import shutil
from datetime import datetime
from agentx.model.session.session import Session, SessionDatabase
from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY


class SessionController:

    SESSION_DIRECTORIES_RAG = "rag"

    _current_session: Session = None
    _database: Optional[SessionDatabase] = None
    _current_session_name: str = "current"  # Always use "current" as the active session name

    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._ensure_current_session_exists()

        self._ensure_folder_exists(self.SESSION_DIRECTORIES_RAG)

    def get_directory_rag(self):
        return f"{self._current_session.directory}/{self.SESSION_DIRECTORIES_RAG}"

    def _ensure_current_session_exists(self) -> Session:
        """
        Ensure the 'current' session always exists.
        If no current session exists, create one named 'current' without timestamp.
        """
        # Create session without timestamp (just "current", not "current_2026-...")
        self._current_session = Session(self._current_session_name, use_timestamp=False)
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
        """
        Backup the current session with a timestamp before creating a new one.
        
        Returns:
            The backup directory path if successful, None otherwise
        """
        if self._current_session is None or not self._current_session.is_created():
            return None
        
        current_dir = self._current_session.directory
        if not current_dir:
            return None
        
        # Generate timestamp for backup with microseconds for uniqueness
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
        """
        Create a new session. The previous 'current' session is backed up with a timestamp.
        
        When the user creates a new session with 'new':
        1. The current session directory is renamed with a timestamp backup
        2. A fresh 'current' session is created
        3. The new session becomes the active session

        Args:
            name: Name for the new session (used for backup naming)

        Returns:
            The newly created Session
        """
        # Backup the current session with timestamp before replacing
        if self._current_session is not None and self._current_session.is_created():
            backup_path = self._backup_current_session()
            if backup_path:
                print(f"Previous session backed up to: {backup_path}")
            else:
                print("Warning: Could not backup current session")
        
        # Clear the current session reference
        self._current_session = None
        self._database = None
        
        # Create new 'current' session (always named 'current', no timestamp)
        self._current_session = Session(self._current_session_name, use_timestamp=False)
        if not self._current_session.create():
            raise Exception("Failed to create new session")
        
        # Create new database for the session
        self._database = SessionDatabase(self._current_session)
        
        return self._current_session
    
    def get_database(self) -> Optional[SessionDatabase]:
        """Get the database for the current session."""
        return self._database
    
    def get_session_name(self) -> str:
        """Get the name of the current session."""
        if self._current_session:
            return self._current_session.name
        return "none"
    
    def has_session(self) -> bool:
        """Check if a session exists."""
        return self._current_session is not None and self._current_session.is_created()


# Global instance accessor
def get_session_manager() -> SessionController:
    """Get the global session manager instance."""
    if SessionController._instance is None:
        SessionController()  # Create instance if it doesn't exist
    return SessionController._instance

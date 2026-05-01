from pathlib import Path
from typing import Optional
from agentx.model.session.session import Session, SessionDatabase
from agentx.common.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from agentx.common.utils import create_directory_with_timestamp, directory_exists


class SessionManager:
    """
    Manages sessions ensuring a current session always exists.
    
    - If no current session exists, one is automatically created
    - Users can create a new session with the 'new' command
    - Only one current session exists at a time
    """
    
    _instance: Optional['SessionManager'] = None
    _current_session: Optional[Session] = None
    _database: Optional[SessionDatabase] = None
    
    def __new__(cls) -> 'SessionManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._current_session is None:
            self._create_default_session()
    
    def _create_default_session(self, name: str = "default") -> Session:
        """Create the default session if none exists."""
        self._current_session = Session(name)
        if not self._current_session.create():
            raise Exception("Failed to create default session")
        self._database = SessionDatabase(self._current_session)
        return self._current_session
    
    def get_current_session(self) -> Session:
        """Get the current session. Creates one if it doesn't exist."""
        if self._current_session is None:
            self._create_default_session()
        return self._current_session
    
    def create_new_session(self, name: str = "session") -> Session:
        """
        Create a new session, destroying the current one.
        
        Args:
            name: Name for the new session
            
        Returns:
            The newly created Session
        """
        # Create new session
        self._current_session = Session(name)
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
def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return SessionManager()

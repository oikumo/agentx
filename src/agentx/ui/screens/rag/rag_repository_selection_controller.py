from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from agentx.ui.screens.rag.rag_create_repository_controller import RagCreateRepositoryController
from agentx.model.rag.rag_provider import RagRepository, RagProvider
from agentx.ui.screens.rag.rag_repostitory_selection_view import RagRepositorySelectionView

if TYPE_CHECKING:
    pass


class RagRepositorySelectionController:
    def __init__(self, rag_working_directory: str):
        self.view = RagRepositorySelectionView(self)
        self.rag_provider = RagProvider(rag_working_directory)
        self._cached_repositories: list[RagRepository] | None = None

    def show(self) -> None:
        self.view.show()

    def get_repositories(self) -> list[str] | None:
        """Get list of valid repository IDs for display."""
        repositories = self.rag_provider.get_repositories()
        if not repositories:
            self._cached_repositories = None
            return None
        
        # Filter valid repositories and cache for later retrieval
        self._cached_repositories = [
            repo for repo in repositories 
            if self._validate_repository(repo)
        ]
        
        if not self._cached_repositories:
            return None
        
        return [repo.id for repo in self._cached_repositories if repo.id]

    def createRepository(self) -> None:
        """Create a new repository."""
        from agentx.model.session.session_manager import SessionManager
        from agentx.ui.common.ui_console import UIConsole
        
        session_controller = SessionManager()
        working_directory = session_controller.get_directory_rag()
        
        creator = RagCreateRepositoryController(working_directory)
        new_repo = creator.show()
        
        if new_repo:
            console = UIConsole("(rag)")
            console.info(f"Repository '{new_repo.id}' created. Please select it.")

    def get_selected_repository(self) -> RagRepository | None:
        """
        Return the repository selected by user.
        Returns None if no selection or cancelled.
        """
        selected_index = self.view.get_selected_index()
        
        if selected_index is None:
            return None
        
        # Map 1-based index to 0-based list index
        list_index = selected_index - 1
        
        if not self._cached_repositories:
            return None
        
        if list_index < 0 or list_index >= len(self._cached_repositories):
            return None
        
        return self._cached_repositories[list_index]
    
    def _validate_repository(self, repository: RagRepository) -> bool:
        """
        Validate repository integrity.
        Returns True if repository is valid.
        """
        # Check repository has ID and path
        if not repository.id or not repository.path:
            return False
        
        repo_path = Path(repository.path)
        
        # Check directory exists
        if not repo_path.exists():
            return False
        
        # Check rag.db exists
        db_path = repo_path / "rag.db"
        if not db_path.exists():
            return False
        
        # Check database is readable
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
        except Exception:
            return False
        
        return True

    def close(self):
        self._cached_repositories = None
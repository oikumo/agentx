from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from agentx.model.rag.rag_repository import RagRepository
from agentx.model.rag.rag_db import RagDatabase
from agentx.ui.screens.rag.rag_create_repository_view import RagCreateRepositoryView, IRagCreateRepositoryViewPartner

if TYPE_CHECKING:
    pass


class RagCreateRepositoryController(IRagCreateRepositoryViewPartner):
    def __init__(self, working_directory: str):
        self._view = RagCreateRepositoryView(self)
        self._working_directory = working_directory
        self._created_repository: RagRepository | None = None
    
    def show(self) -> RagRepository | None:
        """
        Show repository creation screen.
        Returns created RagRepository or None if cancelled.
        """
        self._view.show()
        return self._created_repository
    
    def on_name_entered(self, name: str) -> bool:
        """
        Process entered repository name.
        Returns True if name is valid and creation succeeded.
        """
        # Strip and validate
        name = name.strip()
        if not name:
            self._view.show_error("Repository name cannot be empty")
            return False
        
        # Validate name
        is_valid, error_message = self._validate_repository_name(name)
        if not is_valid:
            self._view.show_error(error_message)
            return False
        
        # Create repository
        repository = self._create_repository(name)
        if not repository:
            self._view.show_error("Failed to create repository")
            return False
        
        self._created_repository = repository
        # These are guaranteed to be set since we just created them
        repo_id: str = repository.id if repository.id else ""
        repo_path_str: str = repository.path if repository.path else ""
        self._view.show_success(repo_id, repo_path_str)
        return True
    
    def get_prompt(self) -> str:
        return "(create-repository)"
    
    def _validate_repository_name(self, name: str) -> tuple[bool, str]:
        """
        Validate repository name format and availability.
        Returns (True, "") if valid, (False, error_message) if invalid.
        """
        # Check empty
        if not name or not name.strip():
            return False, "Repository name cannot be empty"
        
        name = name.strip()
        
        # Check length
        if len(name) > 50:
            return False, "Repository name too long (max 50 characters)"
        
        # Check format (alphanumeric + underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            return False, "Repository name contains invalid characters (use letters, numbers, underscore only)"
        
        # Check for prefix
        if name.startswith('rag_'):
            return False, "Repository name must not include 'rag_' prefix (added automatically)"
        
        # Check for path traversal
        if '..' in name or '/' in name or '\\' in name:
            return False, "Repository name contains invalid characters"
        
        # Check existence
        repo_path = Path(self._working_directory) / f"rag_{name}"
        if repo_path.exists():
            return False, f"Repository '{name}' already exists"
        
        return True, ""
    
    def _create_repository(self, name: str) -> RagRepository | None:
        """
        Create repository directory and initialize database.
        Returns RagRepository on success, None on failure.
        """
        repo_path: Path | None = None
        try:
            # Create directory
            repo_path = Path(self._working_directory) / f"rag_{name}"
            repo_path.mkdir(parents=True, exist_ok=False)
            
            # Initialize database
            db_path = repo_path / "rag.db"
            db = RagDatabase(str(db_path))
            if not db.create_if_not_exists():
                # Clean up directory
                import shutil
                shutil.rmtree(repo_path, ignore_errors=True)
                return None
            
            # Create repository object
            repository = RagRepository(
                id=f"rag_{name}",
                path=str(repo_path)
            )
            
            # These are guaranteed to be set, but type checker needs assertion
            repo_id: str = repository.id if repository.id else ""
            repo_path_str: str = repository.path if repository.path else ""
            
            return repository
            
        except FileExistsError:
            return None
        except PermissionError:
            return None
        except Exception as e:
            # Clean up partial creation
            if repo_path and repo_path.exists():
                import shutil
                shutil.rmtree(repo_path, ignore_errors=True)
            return None
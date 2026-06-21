from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from agentx.ui.common.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.ui.screens.rag.rag_create_repository_controller import RagCreateRepositoryController

class IRagCreateRepositoryViewPartner(ABC):
    """Abstract Partner Interface for Repository Creation View."""
    
    @abstractmethod
    def on_name_entered(self, name: str) -> bool:
        """Process entered name. Returns True if accepted."""
        pass
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt prefix for this screen."""
        pass

class RagCreateRepositoryView:
    def __init__(self, partner: IRagCreateRepositoryViewPartner):
        self._partner = partner
        self._console = UIConsole(self._partner.get_prompt())
    
    def show(self) -> None:
        """Display repository creation screen and capture user input."""
        while True:
            self._console.info("")
            self._console.info("Create New RAG Repository")
            self._console.info("─" * 40)
            self._console.info("")
            self._console.info("Enter repository name (without 'rag_' prefix):")
            self._console.info("  - Use letters, numbers, and underscores only")
            self._console.info("  - Maximum 50 characters")
            self._console.info("  - Type 'cancel' to abort")
            self._console.info("")
            
            name = self._console.capture_input()
            if not name:
                continue
            name = name.strip()
            
            # Check cancellation
            if name and name.lower() in ['cancel', 'back', 'q', 'quit']:
                self._console.info("Repository creation cancelled.")
                return
            
            if not name:
                self._console.error("Repository name cannot be empty")
                continue
            
            # Send to controller for validation and creation
            if self._partner.on_name_entered(name):
                # Success - repository created
                return
            # If we get here, validation failed - loop continues
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        self._console.error(message)
    
    def show_success(self, repository_name: str, path: str) -> None:
        """Display success message."""
        self._console.success(f"✅ Repository '{repository_name}' created successfully!")
        self._console.info(f"   Path: {path}")
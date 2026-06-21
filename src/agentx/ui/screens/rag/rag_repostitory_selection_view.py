from __future__ import annotations

from typing import TYPE_CHECKING
from agentx.ui.common.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.ui.screens.rag.rag_repository_selection_controller import RagRepositorySelectionController

class RagRepositorySelectionView:
    def __init__(self, controller: RagRepositorySelectionController):
        self.controller = controller
        self.console = UIConsole("(rag/repositories)")
        self._selected_index: int | None = None

    def show(self):
        self._selected_index = None  # Reset selection
        while True:
            self._show_options_menu()
            user_input = self.console.capture_input()
            
            if user_input is None:
                continue
            
            # Check for cancellation
            if user_input.lower() in ['cancel', 'back', 'q', 'quit']:
                self.console.info("Repository selection cancelled.")
                self._selected_index = None
                return
            
            # Check for create new repository
            if user_input == "0":
                self._create_new_repository()
                continue
            
            # Try to parse as index
            try:
                index = int(user_input)
                repositories = self.controller.get_repositories()
                if repositories and 1 <= index <= len(repositories):
                    self._selected_index = index  # Store selection (1-based)
                    return
                else:
                    self.console.error("Invalid option")
            except ValueError:
                self.console.error("Invalid option. Please enter a number.")

    def _show_options_menu(self) -> None:
        repositories = self.controller.get_repositories()
        if not repositories:
            self.console.info("NO REPOSITORIES")
            self.console.info("")
            self.console.info("(0) **Create new repository**")
            self.console.info("(q) Cancel")
        else:
            self.console.info("REPOSITORIES")
            self.console.info("")
            for index, r in enumerate(repositories):
                self.console.info(f"    ({index + 1}) {r}")
            self.console.info("")
            self.console.info("(0) **Create new repository**")
            self.console.info("(q) Cancel")
            self.console.info("")


    def _create_new_repository(self) -> None:
        self.controller.createRepository()
    
    def get_selected_index(self) -> int | None:
        """Return the selected index (1-based) or None if cancelled."""
        return self._selected_index
from __future__ import annotations

from typing import TYPE_CHECKING
from agentx.ui.common.ui_console import UIConsole

if TYPE_CHECKING:
    from agentx.ui.screens.rag_controller.rag_repository_selection_controller import RagRepositorySelectionController

class RagRepositorySelectionView:
    def __init__(self, controller: RagRepositorySelectionController):
        self.controller = controller
        self.console = UIConsole("(rag/repositories)")

    def show(self):
        while True:
            self._show_options_menu()
            user_input = self.console.capture_input()
            match user_input:
                case "0":
                    self._create_new_repository()
                case "quit":
                    self.controller.close()
                    return
                case _  : self.console.error("Invalid option")

    def _show_options_menu(self) -> None:
        repositories = self.controller.get_repositories()
        if not repositories:
            self.console.info("NO REPOSITORIES CREATED")
        else:
            self.console.info("REPOSITORIES")
            for index, r in enumerate(repositories):
                self.console.info(f"    ({index + 1}) {r}")

        self.console.info("(0) **Create new repository**")


    def _create_new_repository(self) -> None:
        self.controller.createRepository()
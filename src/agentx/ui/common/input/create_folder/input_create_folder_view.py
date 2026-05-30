from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.utils.constants import SESSION_DEFAULT_BASE_DIRECTORY

if TYPE_CHECKING:
    from agentx.ui.common.input.create_folder.input_create_folder_controller import InputCreateFolderController
from agentx.ui.common.ui_console import UIConsole


class InputCreateFolderView:

    def __init__(self, controller: InputCreateFolderController):
        self.controller = controller
        self.console = UIConsole("(new)")

    def show(self) -> str | None:
        """Prompt the user for a folder name.

        Returns the raw input string, or None if cancelled.
        """
        return self.console.capture_input()

    def show_error_folder_exists(self, folder_name: str) -> None:
        """Display an error that *folder_name* is already taken."""
        self.console.error(
            f"A directory named '{folder_name}' already exists "
            f"in '{SESSION_DEFAULT_BASE_DIRECTORY}/'"
        )

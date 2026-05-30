from __future__ import annotations

from pathlib import Path

from agentx.utils.constants import SESSION_DEFAULT_BASE_DIRECTORY
from agentx.utils.utils_directories import is_directory_exists
from agentx.ui.common.input.create_folder.input_create_folder_view import InputCreateFolderView


class InputCreateFolderController:
    folder_name: str | None

    def __init__(self):
        self.view = InputCreateFolderView(self)
        self.folder_name = None

    def show(self) -> None:
        self.folder_name = None

        user_input = self.view.show()
        if not user_input:
            return

        if not self._is_folder_name_available(user_input):
            self.view.show_error_folder_exists(user_input)
            return

        self.folder_name = user_input

    def _is_folder_name_available(self, name: str) -> bool:
        """Check that no directory with *name* exists in the session base."""
        candidate = Path(SESSION_DEFAULT_BASE_DIRECTORY) / name
        return not is_directory_exists(str(candidate))


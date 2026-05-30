from __future__ import annotations

from agentx.ui.common.input.input_create_folder_view import InputCreateFolderView


class InputCreateFolderController:

    def __init__(self):
        self.view = InputCreateFolderView(self)

    def show(self) -> None:
        self.view.show()


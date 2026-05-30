from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.ui.common.input.create_folder.input_create_folder_controller import InputCreateFolderController
from agentx.ui.common.ui_console import UIConsole

class InputCreateFolderView:

    def __init__(self, controller: InputCreateFolderController):
        self.controller = controller
        self.console = UIConsole("(new)")

    def show(self):
        pass

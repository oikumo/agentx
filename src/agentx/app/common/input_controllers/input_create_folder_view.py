from typing import TYPE_CHECKING

from agentx.common.input_utils import InputUtils

if TYPE_CHECKING:
    from agentx.app.common.input_controllers.input_create_folder_controller import InputCreateFolderController
from agentx.ui.ui_console import UIConsole

class InputCreateFolderView:

    def __init__(self, controller: InputCreateFolderController):
        self.controller = controller
        self.console = UIConsole("(new)")

    def show(self):
        pass

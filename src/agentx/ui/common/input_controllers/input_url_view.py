from typing import TYPE_CHECKING

from agentx.common.input_utils import InputUtils

if TYPE_CHECKING:
    from agentx.ui.common.input_controllers.input_url_controller import InputUrlController
from agentx.ui_common.ui_console import UIConsole


class InputUrlView:
    def __init__(self, controller: InputUrlController):
        self.controller = controller
        self.console = UIConsole("(url)")

    def show(self):
        user_input = self.console.capture_input()
        if not user_input:
            self.controller.url = None
            return

        if not InputUtils.is_valid_url(user_input):
            self.controller.url = None
            return

        self.controller.url = user_input


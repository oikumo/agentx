from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.utils import utils_input

if TYPE_CHECKING:
    from agentx.ui.common.input.url_entry.input_url_controller import InputUrlController
from agentx.ui.common.ui_console import UIConsole


class InputUrlView:
    def __init__(self, controller: InputUrlController):
        self.controller = controller
        self.console = UIConsole("(url)")

    def show(self):
        user_input = self.console.capture_input()
        if not user_input:
            self.controller.url = None
            return

        if not utils_input.is_valid_url(user_input):
            self.controller.url = None
            return

        self.controller.url = user_input


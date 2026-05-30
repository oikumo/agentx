from typing import TYPE_CHECKING

from agentx.utils.utils import safe_int

if TYPE_CHECKING:
    from agentx.ui.common.input.options.input_options_controller import InputOptionsController
from agentx.ui.common.ui_console import UIConsole

class InputOptionsView:
    options: dict[int, str]

    def __init__(self, controller: InputOptionsController, options: dict[int, str]):
        self.controller = controller
        self.options = options
        self.console = UIConsole("(option)")

    def show(self):
        self.controller.set_option(None)

        self.console.info("OPTIONS")

        for key, value in self.options.items():
            self.console.info(f" ({key}): {value}")

        self.console.info("")

        user_input = self.console.capture_input()
        option = safe_int(user_input);

        if not option or option not in self.options:
            self.console.error(f"Invalid option: {option}")
            return

        self.controller.set_option(option)


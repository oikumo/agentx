from agentx.ui.common.ui_console import UIConsole
from agentx.ui.interfaces import IMainViewPartner


class MainView:
    def __init__(self, controller: IMainViewPartner):
        self.controller = controller
        self.console = UIConsole("(agentx)")

    def show(self):
        self.console.success("Agent-X")
        self.console.info("Type 'help' for commands, Ctrl+C to exit")

        while True:
            user_input = self.console.capture_input()
            if not user_input:
                return

            self.controller.run_command(user_input)


    def print_message(self, message: str):
        self.console.info(message)

    def print_warring_message(self, message: str):
        self.console.waning(message)

    def print_error_message(self, message: str):
        self.console.error(message)

    def print_response(self, response: str):
        self.console.info(response)

    def print_response_error(self, response: str):
        self.console.error(response)

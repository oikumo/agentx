from agentx.views.ui.ui import UIConsoleBase


class IMainViewPartner:
    def run_command(self, user_input: str):
        pass
    def error(self):
        pass
    def print(self):
        pass

class MainView:
    def __init__(self, controller: IMainViewPartner, console: UIConsoleBase):
        self.controller = controller
        self.console = console

    def show(self):
        self.console.success("Agent-X")
        self.console.info("Type 'help' for commands, Ctrl+C to exit").flush()

        while True:
            user_input = self.console.capture_input("(agent-x) > ")
            if not user_input:
                return

            self.controller.run_command(user_input)


    def print_message(self, message: str):
        self.console.info(message).flush()

    def print_warring_message(self, message: str):
        self.console.waning(message).flush()

    def print_error_message(self, message: str):
        self.console.error(message).flush()

    def print_response(self, response: str):
        self.console.info(response).flush()

    def print_response_error(self, response: str):
        self.console.error(response).flush()

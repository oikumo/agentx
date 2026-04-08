from controllers.main_controller.repl import IMainViewPartner
from views.common.console import Console


class MainView:
    def __init__(self, controller: IMainViewPartner):
        self.controller = controller

    def show(self):
        Console.log_success("Agent-X")
        Console.log_info("Type 'help' for commands, Ctrl+C to exit")

    def print_response(self, response: str):
        Console.log_info(response)

    def print_response_error(self, response: str):
        Console.log_error(response)

    def capture_input(self):
        try:
            user_input = input("(agent-x) > ").strip()
            if not user_input:
                return None

            self.controller.run_command(user_input)

        except KeyboardInterrupt:
            Console.log_info("\nReceived interrupt, exiting...")
            self.controller.error()
        except EOFError:
            Console.log_info("\nEOF received, exiting...")
            self.controller.error()


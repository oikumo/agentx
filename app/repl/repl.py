from app.repl.command_line_controller.command_parser import CommandParser
from app.repl.controllers.main_controller.main_controller import MainController
from app.repl.logger import Console


class ReplApp:
    def __init__(self, controller: MainController):
        self.controller = controller
        self.parser = CommandParser()

    def run(self):
        Console.log_success("Agent-X")
        Console.log_info("Type 'help' for commands, Ctrl+C to exit")

        while True:
            try:
                user_input = input("(agent-x) > ").strip()
                if not user_input:
                    continue

                command_data = self.parser.parse(user_input)
                if not command_data:
                    continue

                command = self.controller.find_command(command_data.key)
                if not command:
                    Console.log_error(f"Unknown command: {command_data.key}")
                    continue

                try:
                    result = command.run(command_data.arguments)
                    if result:
                        result.apply()

                except Exception as e:
                    Console.log_error(f"Command execution failed: {e}")

            except KeyboardInterrupt:
                Console.log_info("\nReceived interrupt, exiting...")
                break
            except EOFError:
                Console.log_info("\nEOF received, exiting...")
                break

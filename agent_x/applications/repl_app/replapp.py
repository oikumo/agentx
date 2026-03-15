from agent_x.applications.repl_app.controllers.main_controller.main_controller import (
    MainController,
)
from agent_x.applications.repl_app.command_line_controller.command_parser import (
    CommandParser,
)
from agent_x.common.logger import log_info, log_warning, log_error


class ReplApp:
    def __init__(self):
        self.controller = MainController()
        self.parser = CommandParser()

    def run(self):
        log_info("Agent-X CLI REPL started")
        log_info("Type 'help' for commands, Ctrl+C to exit")

        while True:
            try:
                # Get user input
                user_input = input("(agent-x) > ").strip()

                if not user_input:
                    continue

                # Parse command
                command_data = self.parser.parse(user_input)
                if not command_data:
                    continue

                # Find and execute command
                command = self.controller.find_command(command_data.key)
                if not command:
                    log_warning(f"Unknown command: {command_data.key}")
                    continue

                # Execute command
                try:
                    command.run(command_data.arguments)
                except Exception as e:
                    log_error(f"Command execution failed: {e}")

            except KeyboardInterrupt:
                log_info("\nReceived interrupt, exiting...")
                break
            except EOFError:
                log_info("\nEOF received, exiting...")
                break

from agent_x.app.command_line_controller.command_parser import CommandParser
from agent_x.app.command_line_controller.commands_controller import CommandsController
from agent_x.common.logger import log_info, log_warning, log_error


class ReplApp:
    def __init__(self, controller: CommandsController):
        self.controller = controller
        self.parser = CommandParser()

    def run(self):
        log_info("Agent-X")
        log_info("Type 'help' for commands, Ctrl+C to exit")

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
                    log_warning(f"Unknown command: {command_data.key}")
                    continue

                try:
                    result = command.run(command_data.arguments)
                    if result:
                        result.apply()

                except Exception as e:
                    log_error(f"Command execution failed: {e}")

            except KeyboardInterrupt:
                log_info("\nReceived interrupt, exiting...")
                break
            except EOFError:
                log_info("\nEOF received, exiting...")
                break

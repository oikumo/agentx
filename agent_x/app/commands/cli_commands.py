from agent_x.app.command_line_controller.command import Command
from agent_x.app.commands.repl_commands import ReplCommand

from agent_x.common.logger import log_info
from agent_x.utils.utils import clear_console


class QuitCommand(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Exit Agent-X")

    def run(self, arguments: list[str]):
        log_info("QUIT COMMAND")
        self.actions.close()


class ClearCommand(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Clear the output screen")

    def run(self, arguments: list[str]):
        clear_console()


class HelpCommand(ReplCommand):
    def __init__(self, key: str, controller):
        super().__init__(key, controller, description="Show available commands")

    def run(self, arguments: list[str]):
        for command in self.controller.get_commands():
            log_info(command.key)


class ReadFile(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Read and display a file: read <filename>")

    def run(self, arguments: list[str]):
        if not arguments:
            log_info("Usage: read <filename>")
            return
        filename = arguments[0]
        try:
            with open(filename, "r") as file:
                content = file.read()
            log_info(content)
        except FileNotFoundError:
            log_info(f"File not found: {filename}")
        except OSError as e:
            log_info(f"Error reading file: {e}")

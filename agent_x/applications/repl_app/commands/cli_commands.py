from agent_x.applications.repl_app.commands.repl_commands import ReplCommand
from agent_x.applications.repl_app.controllers.main_controller.imain_controller import (
    IMainController,
)
from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.common.logger import log_info

from agent_x.utils.utils import clear_console


class QuitCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key)
        self.controller = controller

    def run(self, arguments: list[str]):
        log_info("QUIT COMMAND")
        self.controller.close()
        exit(0)


class ClearCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(self, arguments: list[str]):
        clear_console()


class HelpCommand(ReplCommand):
    def run(self, arguments: list[str]):
        for command in self.controller.get_commands():
            log_info(command.key)


class ReadFile(Command):
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

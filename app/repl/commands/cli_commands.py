from __future__ import annotations

from app.repl.base import IMainController
from app.repl.command import Command
from app.repl.commands.math_commands import CommandResultLogInfo

from app.repl.logger import Console
from app.common.utils.utils import clear_console


class QuitCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Exit Agent-X")

    def run(self, arguments: list[str]):
        Console.log_info("QUIT COMMAND")
        self.controller.close()


class ClearCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Clear the output screen")

    def run(self, arguments: list[str]):
        clear_console()


class HelpCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Show available commands")

    def run(self, arguments: list[str]):
        commands: list[str] = []
        for command in self.controller.get_commands():
            commands.append(f"{command.key} - {command.description}")
        return CommandResultLogInfo(commands)


class ReadFile(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Read and display a file: read <filename>")

    def run(self, arguments: list[str]):
        if not arguments:
            Console.log_info("Usage: read <filename>")
            return
        filename = arguments[0]
        try:
            with open(filename, "r") as file:
                content = file.read()
            Console.log_info(content)
        except FileNotFoundError:
            Console.log_info(f"File not found: {filename}")
        except OSError as e:
            Console.log_info(f"Error reading file: {e}")

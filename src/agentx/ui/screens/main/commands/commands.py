from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.ui.screens.main.main_controller import MainController

import os

from agentx.ui.screens.main.commands.commands_base import Command

from agentx.utils.utils import clear_console, safe_int


class QuitCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Exit Agent-X")
        self.controller = controller

    def run(self, arguments: list[str]):
        self.controller.print_message("QUIT COMMAND")
        self.controller.close()


class ClearCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Clear the output screen")
        self.controller = controller

    def run(self, arguments: list[str]):
        clear_console()

class HistoryCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show commands history")
        self.controller = controller

    def run(self, arguments: list[str]):
        for command in self.controller.commands_history()[:-1]:
            self.controller.print_message(f"    {command}")

class HelpCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show available commands")
        self.controller = controller

    def run(self, arguments: list[str]):
        for command in self.controller.get_commands():
            self.controller.print_message(f"{command.key} - {command.description}")


class RagShowCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Open RAG")
        self.controller = controller

    def run(self, arguments: list[str]):
        if len(arguments) != 0:
            self.controller.print_warring_message("invalid command")
            return

        self.controller.show_rag()

class SumCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Add two integers: sum <a> <b>")
        self.controller = controller

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) is not None and safe_int(y) is not None:
                    self.controller.print_message(str(int(x) + int(y)))
                else:
                    self.controller.print_warring_message("invalid params for sum command")
            case _:
                self.controller.print_warring_message("invalid command")

        return None


class AIChat(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        if len(arguments) != 0:
            self.controller.print_warring_message("invalid command")

        self.controller.show_chat()

class NewSessionCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Create a new session: new [name]")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        try:
            session_controller = self.controller.get_session_manager()
            new_session = session_controller.create_new_session()
            self.controller.print_message(f"New session created: {new_session.name}")

        except Exception as e:
            self.controller.print_error_message(f"Failed to create new session: {str(e)}")


class LSCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="List files in directory: ls [path]")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        if arguments:
            path = arguments[0]
        else:
            path = os.getcwd()

        try:
            if os.path.exists(path) and os.path.isdir(path):
                files = sorted(os.listdir(path))
                self.print(files, path)
            else:
                self.controller.print_error_message(f"Path does not exist or is not a directory: {path}")
                return
        except PermissionError:
            self.controller.print_error_message(f"Permission denied: {path}")
            return
        except Exception as e:
            self.controller.print_error_message(f"Error listing directory: {str(e)}")

    def print(self, files: list[str], path: str):
        if files:
            self.controller.print_message(f"Directory: {path}")
            for file in files:
                self.controller.print_message(f"  {file}")
        else:
            self.controller.print_message(f"Directory {path} is empty")
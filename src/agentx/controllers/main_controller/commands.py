from __future__ import annotations

from agentx.controllers.main_controller.commands_base import Command, CommandResult
from agentx.controllers.main_controller.main_controller import MainController
from agentx.common.utils import clear_console, safe_int
from agentx.views.common.console import Console


class CommandResultLogInfo(CommandResult):
    def __init__(self, messages: list[str]):
        self._messages = messages

    def apply(self):
        for message in self._messages:
            Console.log_info(message)


class CommandResultPrint(CommandResult):
    def __init__(self, message: str):
        self._message = message

    def apply(self):
        Console.log_info(self._message)


class QuitCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Exit Agent-X")
        self.controller = controller

    def run(self, arguments: list[str]):
        Console.log_info("QUIT COMMAND")
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
        commands: list[str] = []
        for command in self.controller.commands_history()[:-1]:
            commands.append(f"{command}")
        return CommandResultLogInfo(commands)

class HelpCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show available commands")
        self.controller = controller

    def run(self, arguments: list[str]):
        commands: list[str] = []
        for command in self.controller.get_commands():
            commands.append(f"{command.key} - {command.description}")
        return CommandResultLogInfo(commands)


class SumCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Add two integers: sum <a> <b>")
        self.controller = controller

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) is not None and safe_int(y) is not None:
                    result = str(int(x) + int(y))
                    return CommandResultPrint(result)
                else:
                    Console.log_warning("invalid params for sum command")
            case _:
                Console.log_warning("invalid command")
        return None


class AIChat(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        model_name, query = self.parse_chat_arguments(arguments)
        self.controller.showChat(query)

    @staticmethod
    def parse_chat_arguments(arguments: list[str]) -> tuple[str | None, str]:
        model: str | None = None
        query_parts: list[str] = []
        i = 0
        while i < len(arguments):
            if arguments[i] == "--model":
                if i + 1 < len(arguments):
                    model = arguments[i + 1]
                    i += 2
                else:
                    i += 1
            else:
                query_parts.append(arguments[i])
                i += 1
        query = " ".join(query_parts)
        return model, query

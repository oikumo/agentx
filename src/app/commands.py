from __future__ import annotations

from app.repl import Command, CommandResult, MainController
from views.common.console import Console
from utils.utils import clear_console, safe_int
from model.ai.providers import OpenRouterProvider


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


class AIChat(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from model.ai.providers import AgentFactory

        model_name, query = parse_chat_arguments(arguments)

        if model_name:
            provider = OpenRouterProvider(model_name=model_name)
            chat_loop = AgentFactory.create_chat_loop(provider=provider)
        else:
            chat_loop = AgentFactory.create_chat_loop()

        if not query:
            Console.log_info(
                "Starting interactive chat (type 'quit' or 'exit' to end):"
            )
            chat_loop.start_interactive_streaming()
        else:
            try:
                response, metrics = chat_loop.run_streaming_with_metrics(query)
                if response is not None:
                    print()
                    Console.log_info(metrics.format())
            except Exception as e:
                Console.log_error(f"Chat error: {e}")


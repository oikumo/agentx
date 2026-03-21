from app.repl.base import IMainController
from app.repl.command import Command, CommandResult
from app.repl.console import Console
from app.common.utils.utils import safe_int

class SumCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Add two integers: sum <a> <b>")

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


class CommandResultPrint(CommandResult):
    def __init__(self, message: str):
        self._message = message

    def apply(self):
        Console.log_info(self._message)

class CommandResultLogInfo(CommandResult):
    def __init__(self, messages: list[str]):
        self._messages = messages

    def apply(self):
        for message in self._messages:
            Console.log_info(message)

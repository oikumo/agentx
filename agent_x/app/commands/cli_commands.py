from agent_x.core.repl.command import Command
from agent_x.core.utils.utils import clear_console


class QuitCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)
    def run(cls, arguments: list[str]):
        print(f"QUIT COMMAND")

class ClearCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(cls, arguments: list[str]):
        clear_console()


class HelpCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(cls, arguments: list[str]):
        print(f"HELP COMMAND")
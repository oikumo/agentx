from agent_x.base.commands.repl_commands import ReplCommand
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

class HelpCommand(ReplCommand):
    def run(self, arguments: list[str]):
        for command in self.controller.get_commands():
            print(f"{command.key}")

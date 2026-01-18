from agent_x.app.controlllers.main_controller.imain_controller import IMainController
from agent_x.app.controlllers.main_controller.commands.repl_commands import ReplCommand
from agent_x.core.controllers.command_line_controller.command import Command

from agent_x.core.utils.utils import clear_console

class QuitCommand(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key)
        self.controller = controller

    def run(self, arguments: list[str]):
        print(f"QUIT COMMAND")
        self.controller.close()
        exit(0)


class ClearCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

    def run(cls, arguments: list[str]):
        clear_console()

class HelpCommand(ReplCommand):
    def run(self, arguments: list[str]):
        for command in self.controller.get_commands():
            print(f"{command.key}")

class ReadFile(Command):
    def run(self, arguments: list[str]):
        with open("uno.txt", "w") as file:
            file.write("hola")
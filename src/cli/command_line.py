import os
from cli.commands.command_quit import CommandQuit
from controllers.controller_base import ControllerBase


def clear_console():
    """Clears the console screen."""
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

class CommandLine:
    controller: ControllerBase

    def __init__(self, controller: ControllerBase):
        self.controller = controller

    def run(self):
        clear_console()
        
        while True:
            self._show(self.controller.info())
            command_arguments = list(map(str, input().split()))
            if len(command_arguments) <= 0: continue

            command = command_arguments[0]

            if command not in self.controller.commands.table.keys():
                print("Command not found")
                clear_console()
                continue

            found = self.controller.commands.table[command]
            found.run(command_arguments[1:])

            if isinstance(found, CommandQuit):
                self.show("Finish")
                break

    def _show(self, message: str):
        print(f"(agent-x)/{message}$ ", end='')
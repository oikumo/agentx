from src.utils.utils import clear_console

class CommandLine:
    def __init__(self, commands: dict):
        self.info = ""
        self.commands = commands

    def run(self):
        clear_console()
        self._show("")
        command_arguments = list(map(str, input().split()))
        if len(command_arguments) <= 0: return

        command = command_arguments[0]

        if command not in self.commands:
            print("Command not found")
            return

        result = self.commands[command](command_arguments[1:])
        if result is not None:
            print(result)

    def _show(self, message: str):
        print(f"(agent-x)/{message}$ ", end='')
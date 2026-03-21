from app.repl.base import IMainController
from app.repl.command import Command

class MainController(IMainController):
    def __init__(self):
        super().__init__()
        self.commands: dict[str, Command] = {}

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        if key in self.commands:
            return self.commands[key]
        return None

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def close(self) -> None:
        exit(0)




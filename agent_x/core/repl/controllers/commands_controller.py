from agent_x.core.repl.command import Command
from agent_x.core.repl.interface.interfaces import ICommandsController


class CommandsController(ICommandsController) :
    commands: dict[str, Command] = {}

    def __init__(self):
        pass

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        if key in self.commands:
            return self.commands[key]
        return None

    def add_command(self, command: Command):
        self.commands[command.key] = command

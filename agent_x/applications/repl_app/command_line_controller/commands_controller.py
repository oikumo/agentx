from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.applications.repl_app.controller import Controller


class CommandsController(Controller):
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

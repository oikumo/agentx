from __future__ import annotations
import typing

from agent_x.app.controller import Controller

if typing.TYPE_CHECKING:
    from agent_x.app.command_line_controller.command import Command



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

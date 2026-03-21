from abc import ABC

from app.command_line_controller.command import \
    Command
from app.command_line_controller.commands_controller import \
    CommandsController


class ReplCommand(Command, ABC):
    def __init__(self, key: str, controller: CommandsController, description: str = ""):
        super().__init__(key, description=description)
        self.controller = controller

from abc import ABC

from agent_x.core.controllers.command_line_controller.command import Command
from agent_x.core.controllers.command_line_controller.commands_controller import CommandsController


class ReplCommand(Command, ABC):
    def __init__(self, key: str, controller: CommandsController):
        super().__init__(key)
        self.controller = controller

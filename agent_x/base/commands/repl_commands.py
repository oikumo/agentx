from abc import ABC
from agent_x.core.repl.command import Command
from agent_x.core.repl.interface.interfaces import ICommandsController


class ReplCommand(Command, ABC):
    def __init__(self, key: str, controller: ICommandsController):
        super().__init__(key)
        self.controller = controller

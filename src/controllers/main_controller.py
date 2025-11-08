from cli.commands.command_help import CommandHelp
from cli.commands.command_math import CommandMath
from cli.commands.command_quit import CommandQuit
from controllers.controller_base import ControllerBase


class MainController(ControllerBase):
    def __init__(self):
        super().__init__()
        self.commands.add(CommandQuit())
        self.commands.add(CommandMath())
        self.commands.add(CommandHelp())

    def info(self) -> str:
        return "main"
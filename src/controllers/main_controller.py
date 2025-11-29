from src.cli.commands.command_clean import CommandClean
from src.cli.commands.command_help import CommandHelp
from src.cli.commands.command_math import CommandMath
from src.cli.commands.command_quit import CommandQuit
from src.controllers.controller_base import ControllerBase


class MainController(ControllerBase):
    def __init__(self):
        super().__init__()
        self.commands.add(CommandQuit())
        self.commands.add(CommandMath())
        self.commands.add(CommandHelp())
        self.commands.add(CommandClean())

    def info(self) -> str:
        return "main"
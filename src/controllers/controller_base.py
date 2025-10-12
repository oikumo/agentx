from src.cli.command_lookup import CommandsLookUp
from src.cli.commands.command_base import CommandBase

class ControllerBase:
    def __init__(self):
        self.commands = CommandsLookUp()

    def info(self) -> str:
        return "no controller"

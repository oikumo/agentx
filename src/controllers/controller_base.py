from cli.command_lookup import CommandsLookUp
from cli.commands.command_base import CommandBase

class ControllerBase:
    def __init__(self):
        self.commands = CommandsLookUp()

    def info(self) -> str:
        return "no controller"

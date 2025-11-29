from src.cli.command_lookup import CommandsLookUp


class ControllerBase:
    def __init__(self):
        self.commands = CommandsLookUp()

    def info(self) -> str:
        return "no controller"

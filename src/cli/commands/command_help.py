from abc import ABC

from cli.commands.command_base import CommandBase

class CommandHelp(CommandBase):
    def __init__(self):
        super().__init__()
        self.key = "help"

    def run(self, arguments):
        print(f"HELP COMMAND {arguments}")

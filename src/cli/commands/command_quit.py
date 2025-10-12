from abc import ABC

from src.cli.commands.command_base import CommandBase

class CommandQuit(CommandBase):
    def __init__(self):
        super().__init__()
        self.key = "quit"

    def run(self, arguments):
        print(f"QUIT COMMAND {arguments}")

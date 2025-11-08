from abc import ABC

from cli.commands.command_base import CommandBase
from utils.utils import clear_console

class CommandClean(CommandBase):
    def __init__(self):
        super().__init__()
        self.key = "clean"

    def run(self, _):
        clear_console()
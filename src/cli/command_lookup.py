from src.cli.commands.command_base import CommandBase

class CommandsLookUp:
    def __init__(self):
        self.table = {}
    def add(self, command: CommandBase):
        if command.key not in self.table:
            self.table[command.key] = command

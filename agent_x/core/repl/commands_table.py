from agent_x.core.repl.command import Command


class CommandsTable :
    commands: dict[str, Command] = {}

    def __init__(self):
        pass

    def find_command(self, key) -> Command | None:
        if key in self.commands:
            return self.commands[key]
        return None

    def add_command(self, command: Command):
        self.commands[command.key] = command

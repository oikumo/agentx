from controllers.main_controller.repl import Command


class MainController:
    def __init__(self):
        self.commands: dict[str, Command] = {}

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        return self.commands.get(key)

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def close(self):
        exit(0)


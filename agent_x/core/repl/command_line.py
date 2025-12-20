from agent_x.core.repl.command_parser import CommandParser, CommandData
from agent_x.core.repl.controllers.commands_controller import CommandsController
from agent_x.core.utils.utils import clear_console

class CommandLine:
    def __init__(self, commands_table: CommandsController):
        self.info = ""
        self.commands_table = commands_table
        self.command_parser = CommandParser()

    def run(self):
        clear_console()
        self._show("")
        try:
            command_entry = input()

        except (EOFError, KeyboardInterrupt):
            exit(0)
        except Exception as e:
            exit(1)

        command_data : CommandData = self.command_parser.parse(command_entry)
        if not command_data: return

        command = self.commands_table.find_command(command_data.key)
        if not command: return

        command.run(command_data.arguments)

    def _show(self, message: str):
        print(f"(agent-x)/{message}$ ", end='')
from agent_x.applications.repl_app.command_line_controller.command_parser import (
    CommandData, CommandParser)
from agent_x.applications.repl_app.command_line_controller.commands_controller import \
    CommandsController


class CommandLine:
    def __init__(self, commands_table: CommandsController):
        self.info = ""
        self.commands_table = commands_table
        self.command_parser = CommandParser()

    def run(self):
        self._show("")
        try:
            command_entry = input()
        except (EOFError, KeyboardInterrupt):
            exit(0)
            return
        except Exception as e:
            exit(1)
            return

        command_data: CommandData | None = self.command_parser.parse(command_entry)
        if not command_data:
            return

        command = self.commands_table.find_command(command_data.key)
        if not command:
            self.notify_unknown_command(command_data.key)
            return

        command.run(command_data.arguments)

    def notify_unknown_command(self, key: str) -> None:
        """Called when the user types a key that is not registered.

        The default implementation is a no-op so the legacy behaviour
        (silent skip) is preserved. The Textual TUI overrides this to
        display a styled error message in the output pane.
        """
        pass

    def _show(self, message: str):
        print(f"(agent-x)/{message}$ ", end="")

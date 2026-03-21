from app.repl.command_line_controller.commands_controller import \
    CommandsController
from app.repl.commands.llm_chat_commands import AIChat


class ChatController(CommandsController):
    def __init__(self):
        super().__init__()
        self.add_command(AIChat("chat"))

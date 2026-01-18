from agent_x.app_repl.commands.llm_chat_commands import AIChat
from agent_x.core.controllers.command_line_controller.commands_controller import CommandsController

class ChatController(CommandsController):
    def __init__(self):
        super().__init__()
        self.add_command(AIChat("chat"))
from abc import ABC, abstractmethod

from agentx.views.ui.ui import UIConsoleBase

class ChatViewPartner(ABC):

    @abstractmethod
    def process_user_message(self, user_message: str) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

class ChatView:
    def __init__(self, partner: ChatViewPartner, console: UIConsoleBase):
        self.partner = partner
        self.console = console

    def show(self):
        while True:
            user_input = input("> ")
            if not self.partner.process_user_message(user_input):
                return

    def show_initial_message(self):
        self.console.info(
            "starting interactive chat (type 'quit' or 'exit' to end):"
        ).flush()

    def show_message(self, message):
        self.console.info(message)

    def show_message_chat_error(self):
        self.console.error("chat error")

    def show_stream_message(self, message: str):
        self.console.info(message)
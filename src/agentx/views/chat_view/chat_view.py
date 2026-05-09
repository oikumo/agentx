from abc import ABC, abstractmethod

from agentx.views.ui.ui import UIConsoleBase

class ChatViewPartner(ABC):
    @abstractmethod
    def close(self) -> None: ...

class ChatView:
    def __init__(self, partner: ChatViewPartner, console: UIConsoleBase):
        self.partner = partner
        self.console = console

    def show_initial_message(self):
        self.console.info(
            "starting interactive chat (type 'quit' or 'exit' to end):"
        ).flush()

    def show_message(self, message):
        self.console.info(message)

    def show_message_chat_error(self):
        self.console.error("chat error")
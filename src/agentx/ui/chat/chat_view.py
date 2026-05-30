from abc import ABC, abstractmethod

from agentx.ui_common.ui_console import UIConsole


class ChatViewPartner(ABC):

    @abstractmethod
    def process_user_message(self, user_message: str) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

class ChatView:
    def __init__(self, controller: ChatViewPartner):
        self.controller = controller
        self.console = UIConsole("(chat)")

    def show(self):
        self.show_initial_message()

        while True:
            user_input = self.console.capture_input()
            if not user_input: return
            if not self.controller.process_user_message(user_input): return

    def show_partial_message(self, message: str):
        self.console.partial_info(message)

    def show_initial_message(self):
        self.console.info("""Starting interactive chat (type 'quit' or 'exit' to end):""")

    def show_message(self, message):
        self.console.info(message)

    def show_message_chat_error(self):
        self.console.error("chat error")

    def show_stream_message(self, message: str):
        self.console.info(message)
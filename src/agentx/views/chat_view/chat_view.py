from agentx.views.ui.ui import UIConsoleBase


class ChatViewController:
    def __init__(self, console: UIConsoleBase):
        self.console = console

    def showInitialMessage(self):
        self.console.info(
            "starting interactive chat (type 'quit' or 'exit' to end):"
        ).flush()

    def showMessage(self, message):
        self.console.info(message)

    def showMessageChatError(self):
        self.console.error("chat error")
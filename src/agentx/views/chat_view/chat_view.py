from agentx.views.common.console import Console


class ChatViewController:
    def __init__(self):
        pass

    def showInitialMessage(self):
        Console.log_info(
            "Starting interactive chat (type 'quit' or 'exit' to end):"
        )

    def showMessage(self, message):
        Console.log_info(message)

    def showMessageChatError(self):
        Console.log_error("Chat error")
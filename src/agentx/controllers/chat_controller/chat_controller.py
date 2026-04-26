from agentx.services.ai.services import cloud_llm_provider
from agentx.views.chat_view.chat_loop import ChatLoop
from agentx.views.chat_view.chat_view import ChatViewController


class ChatController:
    def __init__(self):
        self.view = ChatViewController()
        pass

    def show(self, query: str | None):
        provider = cloud_llm_provider()
        llm = provider.create_llm()
        chat_loop = ChatLoop(llm=llm)

        if not query:
            self.view.showInitialMessage()
            chat_loop.start_interactive_streaming()
        else:
            try:
                response, metrics = chat_loop.run_streaming_with_metrics(query)
                if response is not None:
                    self.view.showMessage(metrics.format())
            except Exception as e:
                self.view.showMessageChatError()
from agentx.model.ai.service import AIService
from agentx.views.chat_view.chat_loop import ChatLoop
from agentx.views.chat_view.chat_view import ChatView, ChatViewPartner
from agentx.views.ui.ui_console import UIConsole


class ChatController(ChatViewPartner):
    def __init__(self):
        self.view = ChatView(self, UIConsole())

    def show(self, query: str | None):
        llm = AIService().openrouter_llm_provider().create_llm()
        chat_loop = ChatLoop(llm=llm)

        if not query:
            self.view.show_initial_message()
            chat_loop.start_interactive_streaming()
        else:
            try:
                response, metrics = chat_loop.run_streaming_with_metrics(query)
                if response is not None:
                    self.view.show_message(metrics.format())
            except Exception as e:
                self.view.show_message_chat_error()

    def close(self) -> None:
        pass

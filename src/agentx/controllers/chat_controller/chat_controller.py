from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from agentx.model.ai.service import AIService
from agentx.views.chat_view.chat_view import ChatView, ChatViewPartner
from agentx.views.ui.ui_console import UIConsole


class ChatController(ChatViewPartner):
    def __init__(self):
        self.view = ChatView(self, UIConsole())
        self.history: list[BaseMessage] = []
        self.llm = AIService().openrouter_llm_provider().create_llm()

    def show(self):
        self.start_interactive_streaming(system_prompt="You are a helpful assistant.")
        self.view.show()

    def close(self) -> None:
        pass

    def start_interactive_streaming(self, system_prompt: str) -> None:
        self.history.clear()
        self.history.append(SystemMessage(content=system_prompt))

    def process_user_message(self, user_input: str) -> bool:
        if user_input.strip().lower() in ("quit", "exit"):
            return False

        stripped = user_input.strip()
        if not stripped:
            return False

        self.history.append(HumanMessage(content=stripped))

        try:
            full_response: list[str] = []

            for chunk_content in self.get_streaming_response(self.llm, self.history):
                self.view.show_partial_text(chunk_content)
                full_response.append(chunk_content)

            self.view.show_partial_text("\n")
            self.history.append(AIMessage(content="".join(full_response)))

            return True

        except Exception as e:
            self.history.pop()
            print(f"Error: {e}")

            return True

    def get_streaming_response(self, llm: BaseChatModel, history: list):
        for chunk in llm.stream(history):
            content = self._extract_chunk_content(chunk)
            if content:
                yield content

    def _extract_chunk_content(self, chunk) -> str:
        if hasattr(chunk, "text"):
            return str(chunk.text)
        if chunk.content is None:
            return ""
        if isinstance(chunk.content, list):
            return " ".join(str(item) for item in chunk.content if item is not None)
        return str(chunk.content)


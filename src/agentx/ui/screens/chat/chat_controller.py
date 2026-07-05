from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from agentx.model.ai.service import AIService
from agentx.ui.interfaces import IChatView, IChatViewPartner


class ChatController(IChatViewPartner):
    def __init__(self, view: IChatView | None = None) -> None:
        self.view = view if view else None  # Will be set by provider if None
        self.history: list[BaseMessage] = []
        self.llm = AIService().get_current_llm()

    def show(self):
        self.start_interactive_streaming(system_prompt="You are a helpful assistant.")
        if self.view:
            self.view.show()

    def close(self) -> None:
        pass

    def start_interactive_streaming(self, system_prompt: str) -> None:
        self.history.clear()
        self.history.append(SystemMessage(content=system_prompt))

    def process_user_message(self, user_message: str) -> bool:
        if user_message.strip().lower() in ("quit", "exit"):
            return False

        stripped = user_message.strip()
        if not stripped:
            return False

        self.history.append(HumanMessage(content=stripped))

        try:
            full_response: list[str] = []

            for chunk_content in self.get_streaming_response(self.llm, self.history):
                if self.view:
                    self.view.show_partial_message(chunk_content)
                full_response.append(chunk_content)

            if self.view:
                self.view.show_partial_message("\n")
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


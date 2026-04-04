from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.common.utils.streaming_metrics import StreamingMetrics


class ChatLoop:
    def __init__(
        self, llm: BaseChatModel, system_prompt: str = "You are a helpful assistant."
    ):
        self.llm = llm
        self.history: list = [SystemMessage(content=system_prompt)]
        self.is_running = False

    def add_user_message(self, content: str) -> None:
        self.history.append(HumanMessage(content=content))

    def add_assistant_message(self, content: str) -> None:
        self.history.append(AIMessage(content=content))

    def _extract_content(self, response) -> str:
        if response.content is None:
            return ""
        if isinstance(response.content, list):
            return " ".join(str(item) for item in response.content if item is not None)
        return str(response.content)

    def _extract_chunk_content(self, chunk) -> str:
        if hasattr(chunk, "text"):
            return str(chunk.text)
        if chunk.content is None:
            return ""
        if isinstance(chunk.content, list):
            return " ".join(str(item) for item in chunk.content if item is not None)
        return str(chunk.content)

    def get_streaming_response(self, user_input: str):
        for chunk in self.llm.stream(self.history):
            content = self._extract_chunk_content(chunk)
            if content:
                yield content

    def run_streaming(
        self, user_input: str, model_override: str | None = None
    ) -> str | None:
        stripped = user_input.strip()
        if not stripped:
            return None
        if self.should_exit(stripped):
            self.exit()
            return None
        self.is_running = True
        self.add_user_message(stripped)
        try:
            full_response = ""
            for chunk_content in self.get_streaming_response(stripped):
                full_response += chunk_content
            self.add_assistant_message(full_response)
        except Exception as e:
            self.history.pop()
            self.is_running = False
            raise e
        self.is_running = False
        return full_response

    def run_streaming_with_metrics(
        self, user_input: str
    ) -> tuple[str | None, StreamingMetrics]:
        metrics = StreamingMetrics()
        stripped = user_input.strip()
        if not stripped:
            return None, metrics
        if self.should_exit(stripped):
            self.exit()
            return None, metrics
        self.is_running = True
        self.add_user_message(stripped)
        try:
            full_response = ""
            with metrics:
                for chunk_content in self.get_streaming_response(stripped):
                    metrics.add_text(chunk_content)
                    full_response += chunk_content
            self.add_assistant_message(full_response)
        except Exception as e:
            self.history.pop()
            self.is_running = False
            raise e
        self.is_running = False
        return full_response, metrics

    def start_interactive_streaming(self) -> None:
        self.is_running = True
        while self.is_running:
            user_input = self._read_input()
            if self.should_exit(user_input):
                self.exit()
                break
            stripped = user_input.strip()
            if not stripped:
                continue
            self.add_user_message(stripped)
            try:
                full_response = ""
                metrics = StreamingMetrics()
                with metrics:
                    for chunk_content in self.get_streaming_response(stripped):
                        print(chunk_content, end="", flush=True)
                        metrics.add_text(chunk_content)
                        full_response += chunk_content
                print()
                print(metrics.format())
                self.add_assistant_message(full_response)
            except Exception as e:
                self.history.pop()
                print(f"Error: {e}")

    def get_response(self) -> str:
        response = self.llm.invoke(self.history)
        content = self._extract_content(response)
        self.add_assistant_message(content)
        return content

    def exit(self) -> None:
        self.is_running = False

    def should_exit(self, user_input: str) -> bool:
        return user_input.strip().lower() in ("quit", "exit")

    def run(self, user_input: str) -> str | None:
        stripped = user_input.strip()
        if not stripped:
            return None
        if self.should_exit(stripped):
            self.exit()
            return None
        self.is_running = True
        self.add_user_message(stripped)
        try:
            response = self.get_response()
        except Exception as e:
            self.history.pop()
            self.is_running = False
            raise e
        self.is_running = False
        return response

    def start_interactive(self) -> None:
        self.is_running = True
        while self.is_running:
            user_input = self._read_input()
            if self.should_exit(user_input):
                self.exit()
                break
            stripped = user_input.strip()
            if not stripped:
                continue
            self.add_user_message(stripped)
            try:
                response = self.get_response()
                print(response)
            except Exception as e:
                self.history.pop()
                print(f"Error: {e}")

    def _read_input(self) -> str:
        return input("> ")

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama


class Ollama:
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None

    def get_model(self) -> BaseChatModel:
        if not self._model:
            self._model = ChatOllama(
            model=self._model_name,
            temperature=0,
            # other params...
            )
        return self._model

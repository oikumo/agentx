from __future__ import annotations
from agent_x.app.agent_x import AgentX
from enum import Enum
from pydantic import BaseModel, Field


class AppType(str, Enum):
    REPL = "repl"
    CHAT = "chat"
    WEB_INGESTION = "web_ingestion"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


class LLMModel(BaseModel):
    name: str = Field(description="Name of the model")
    provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1)


class AgentXConfiguration(BaseModel):
    def __init__(self):
        self.llm_models: list[LLMModel] = []
        self.app: AppType = Field(default=AppType.REPL)
        self.default_model: str = Field(default="gpt-4")
        self.session_directory: str = Field(default="sessions")
        self.debug: bool = Field(default=False)

    def add_model(
        self,
        name: str,
        provider: LLMProvider = LLMProvider.OPENAI,
        temperature: float = 0.7,
    ) -> None:
        model = LLMModel(name=name, provider=provider, temperature=temperature)
        self.llm_models.append(model)

    def get_model(self, name: str) -> LLMModel | None:
        for model in self.llm_models:
            if model.name == name:
                return model
        return None

    def get_default_model(self) -> LLMModel | None:
        return self.get_model(self.default_model)


def configure_agentx(config: "AgentXConfiguration", agentx: "AgentX") -> bool:
    agentx.configuration = config
    return True

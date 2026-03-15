from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

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
    llm_models: list[LLMModel] = Field(default_factory=list)
    default_model: str = Field(default="gpt-4")
    session_directory: str = Field(default="sessions")
    debug: bool = Field(default=False)

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


from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    name: str = Field(description="Name of the model configuration")
    provider: LLMProvider = Field(description="Provider of the model")
    model_name: str = Field(description="Actual model identifier (e.g., 'gpt-4-turbo')")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1)
    api_key: Optional[str] = Field(
        default=None, description="API key for cloud providers"
    )
    base_url: Optional[str] = Field(
        default=None, description="Base URL for custom endpoints"
    )
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific parameters"
    )


class AgentXConfiguration(BaseModel):
    llm_configs: List[LLMConfig] = Field(
        default_factory=list, description="List of LLM configurations"
    )
    default_chat_model: str = Field(
        default="qwen3:1.7b", description="Default chat model name"
    )
    default_embedding_model: str = Field(
        default="nomic-embed-text", description="Default embedding model name"
    )
    session_directory: str = Field(
        default="sessions", description="Directory for session storage"
    )
    debug: bool = Field(default=False, description="Debug mode flag")

    def add_llm_config(self, config: LLMConfig) -> None:
        """Add an LLM configuration to the collection."""
        self.llm_configs.append(config)

    def get_llm_config(self, name: str) -> Optional[LLMConfig]:
        """Get LLM configuration by name."""
        for config in self.llm_configs:
            if config.name == name:
                return config
        return None

    def get_default_chat_config(self) -> Optional[LLMConfig]:
        """Get default chat model configuration."""
        return self.get_llm_config(self.default_chat_model)

    def get_default_embedding_config(self) -> Optional[LLMConfig]:
        """Get default embedding model configuration."""
        return self.get_llm_config(self.default_embedding_model)

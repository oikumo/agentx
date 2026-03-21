"""
Centralized LLM Factory for Agent-X
Provides centralized model instantiation with caching and fallback mechanisms.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)


class LLMFactory:
    """
    Factory for creating and caching LLM instances based on configuration.
    """

    def __init__(self, config: AgentXConfiguration):
        """
        Initialize the LLM factory with configuration.

        Args:
            config: AgentXConfiguration instance containing LLM configurations
        """
        self.config = config
        self._cache: Dict[str, BaseLanguageModel] = {}
        self._embedding_cache: Dict[str, Embeddings] = {}

    def get_chat_model(self, name: Optional[str] = None) -> BaseLanguageModel:
        """
        Get a chat model by name, using default if not specified.

        Args:
            name: Name of the model configuration to use

        Returns:
            BaseLanguageModel instance
        """
        model_name = name or self.config.default_chat_model

        # Check cache first
        if model_name in self._cache:
            return self._cache[model_name]

        # Get configuration
        llm_config = self.config.get_llm_config(model_name)
        if llm_config is None:
            raise ValueError(f"LLM configuration '{model_name}' not found")

        # Create model based on provider
        model = self._create_chat_model(llm_config)

        # Cache and return
        self._cache[model_name] = model
        return model

    def get_embedding_model(self, name: Optional[str] = None) -> Embeddings:
        """
        Get an embedding model by name, using default if not specified.

        Args:
            name: Name of the model configuration to use

        Returns:
            Embeddings instance
        """
        model_name = name or self.config.default_embedding_model

        # Check cache first
        if model_name in self._embedding_cache:
            return self._embedding_cache[model_name]

        # Get configuration
        llm_config = self.config.get_llm_config(model_name)
        if llm_config is None:
            raise ValueError(f"LLM configuration '{model_name}' not found")

        # Create embedding model based on provider
        embedding_model = self._create_embedding_model(llm_config)

        # Cache and return
        self._embedding_cache[model_name] = embedding_model
        return embedding_model

    def _create_chat_model(self, config: LLMConfig) -> BaseLanguageModel:
        """
        Create a chat model based on the configuration.

        Args:
            config: LLMConfig instance

        Returns:
            BaseLanguageModel instance
        """
        if config.provider == LLMProvider.OLLAMA:
            return self._create_ollama_chat_model(config)
        elif config.provider == LLMProvider.OPENAI:
            return self._create_openai_chat_model(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            # Anthropic support would be added here
            raise NotImplementedError("Anthropic provider not yet implemented")
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    def _create_embedding_model(self, config: LLMConfig) -> Embeddings:
        """
        Create an embedding model based on the configuration.

        Args:
            config: LLMConfig instance

        Returns:
            Embeddings instance
        """
        if config.provider == LLMProvider.OLLAMA:
            return self._create_ollama_embedding_model(config)
        elif config.provider == LLMProvider.OPENAI:
            return self._create_openai_embedding_model(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            # Anthropic support would be added here
            raise NotImplementedError("Anthropic provider not yet implemented")
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    def _create_ollama_chat_model(self, config: LLMConfig) -> ChatOllama:
        """
        Create an Ollama chat model.

        Args:
            config: LLMConfig instance

        Returns:
            ChatOllama instance
        """
        return ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
            num_predict=config.max_tokens,
            **config.extra_params,
        )

    def _create_openai_chat_model(self, config: LLMConfig) -> ChatOpenAI:
        """
        Create an OpenAI chat model.

        Args:
            config: LLMConfig instance

        Returns:
            ChatOpenAI instance
        """
        return ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=config.api_key,
            base_url=config.base_url,
            **config.extra_params,
        )

    def _create_ollama_embedding_model(self, config: LLMConfig) -> OllamaEmbeddings:
        """
        Create an Ollama embedding model.

        Args:
            config: LLMConfig instance

        Returns:
            OllamaEmbeddings instance
        """
        return OllamaEmbeddings(model=config.model_name, **config.extra_params)

    def _create_openai_embedding_model(self, config: LLMConfig) -> OpenAIEmbeddings:
        """
        Create an OpenAI embedding model.

        Args:
            config: LLMConfig instance

        Returns:
            OpenAIEmbeddings instance
        """
        return OpenAIEmbeddings(
            model=config.model_name, api_key=config.api_key, **config.extra_params
        )

"""AIServiceAdapter — bridges the existing :class:`AIService` to :class:`IAIServicePartner`.

The agent subsystem depends on :class:`IAIServicePartner` (Abstract Partner),
not on the concrete LangChain/AIService stack.  This adapter is the integration
point: it wraps an :class:`AIService` provider and exposes a simple
``complete(prompt) -> str`` interface for the :class:`ReflectionEngine`.

If the AI service is not configured (missing API keys, model not found, etc.),
``complete()`` raises — the :class:`ReflectionEngine` catches this and degrades
gracefully to a no-reflection result.
"""

from __future__ import annotations

import logging
from typing import Any

from agentx.agent.interfaces import IAIServicePartner

_log = logging.getLogger(__name__)


class AIServiceAdapter(IAIServicePartner):
    """Adapts the existing :class:`AIService` to :class:`IAIServicePartner`.

    Lazily creates the LLM on first ``complete()`` call so the agent doesn't
    fail at construction time if the AI service isn't configured.
    """

    def __init__(self, ai_service: Any | None = None) -> None:
        self._ai_service = ai_service
        self._llm: Any | None = None
        self._init_attempted = False

    def _ensure_llm(self) -> Any:
        """Lazily create the LLM, trying providers in order."""
        if self._llm is not None:
            return self._llm
        if self._init_attempted:
            raise RuntimeError("AI service initialization already failed")
        self._init_attempted = True

        ai: Any = self._ai_service
        if ai is None:
            from agentx.model.ai.service import AIService

            ai = AIService()
            self._ai_service = ai

        # Try OpenRouter first (most likely to work with env config)
        for provider_factory in (
            lambda: ai.openrouter_llm_provider(),
            lambda: ai.cloud_llm_provider(),
        ):
            try:
                provider = provider_factory()
                self._llm = provider.create_llm()
                _log.info("AI service initialized: %s", type(provider).__name__)
                return self._llm
            except Exception as exc:
                _log.warning("AI provider failed to initialize: %s", exc)
                continue

        raise RuntimeError(
            "No AI service available — check API keys (OPENAI_API_KEY, "
            "OPENROUTER_API_KEY) or local model configuration"
        )

    def complete(self, prompt: str) -> str:
        """Send *prompt* to the LLM and return the response text.

        Raises:
            RuntimeError: if no AI provider is available.
        """
        from langchain_core.messages import HumanMessage

        llm = self._ensure_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        # LangChain response objects expose .content for the text
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

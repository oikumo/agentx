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

import concurrent.futures
import logging
from typing import Any

from agentx.agent.interfaces import IAIServicePartner

_log = logging.getLogger(__name__)

#: H6 (feature_015): timeout for a single LLM invocation.
_LLM_TIMEOUT: float = 60.0


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
        """Lazily create the LLM, trying providers in order.

        feature_013: the user-selected provider (via the :class:`ModelRegistry`)
        is tried first.  If it fails (missing key / model not found), the legacy
        fallback chain (OpenRouter → OpenAI) is attempted so the agent degrades
        gracefully — the same behaviour the reflection engine relied on before.

        M2 (feature_015): the ``_init_attempted`` latch is reset on each call
        so the user can add an API key later in the same session and retry.
        """
        if self._llm is not None:
            return self._llm
        # M2: reset the latch so retry is possible after a previous failure.
        self._init_attempted = True

        ai: Any = self._ai_service
        if ai is None:
            from agentx.model.ai.service import AIService

            ai = AIService()
            self._ai_service = ai

        # 1. Try the user-selected provider first (feature_013).
        try:
            self._llm = ai.get_current_llm()
            _log.info(
                "AI service initialized from selection: %s",
                ai.get_current_provider_info().name,
            )
            return self._llm
        except Exception as exc:
            _log.warning("selected AI provider failed to initialize: %s", exc)

        # 2. Legacy fallback chain (preserves pre-feature_013 robustness).
        for provider_factory in (
            lambda: ai.openrouter_llm_provider(),
            lambda: ai.cloud_llm_provider(),
        ):
            try:
                provider = provider_factory()
                self._llm = provider.create_llm()
                _log.info("AI service initialized (fallback): %s", type(provider).__name__)
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
            RuntimeError: if no AI provider is available or the invocation
                times out after ``_LLM_TIMEOUT`` seconds (H6).
        """
        from langchain_core.messages import HumanMessage

        llm = self._ensure_llm()
        # H6 (feature_015): wrap invoke in a thread-based timeout so a hung
        # HTTP call does not block the agent indefinitely.
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(llm.invoke, [HumanMessage(content=prompt)])
                response = future.result(timeout=_LLM_TIMEOUT)
        except concurrent.futures.TimeoutError:
            raise RuntimeError(f"LLM invocation timed out after {_LLM_TIMEOUT}s")
        # LangChain response objects expose .content for the text
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

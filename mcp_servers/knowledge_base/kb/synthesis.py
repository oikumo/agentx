"""Answer synthesis from retrieved knowledge-base entries.

Replaces the dead `advanced_rag._synthesize_answer` and the prompt-template
behaviour of `rag_tool.rag_ask` (Plan P4). Multi-hop and query rewriting are
deliberately dropped until proven needed.

Provides two synthesis modes:

- **Template** (``synthesize()``): Groups results by type, formats as
  markdown. Fast, deterministic, zero-dependency.

- **LLM** (``LLMSynthesizer``): Uses a pluggable LLM callable to generate
  a natural-language answer with source citation. Supports structured
  JSON output and optional faithfulness self-check.
"""

import dataclasses
import json
import re
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from .models import AskResult, AskSource


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TYPE_ORDER = ("pattern", "finding", "decision", "correction")
_MAX_PER_TYPE = 3

#: Default prompt template for LLM-based synthesis.
DEFAULT_SYNTHESIS_PROMPT = """You are a precise knowledge base assistant. Answer the question based ONLY on the provided context.

Question: {question}

Retrieved Context:
{context}

Instructions:
1. Answer concisely and accurately based only on the context.
2. Cite sources using [ID] notation (e.g., "[PAT-123]").
3. If the context cannot answer, state: "The knowledge base does not contain information about..."
4. Provide a confidence level (0.0-1.0) at the end of your answer.
5. Do NOT make up information not present in the context.

Answer:"""


# ---------------------------------------------------------------------------
# Template-based synthesis (v2-compatible)
# ---------------------------------------------------------------------------

def synthesize(question: str, results: List[Dict]) -> AskResult:
    """Build a markdown answer + sources list from raw search results.

    Args:
        question: the original user question (echoed for context, not required).
        results: list of result dicts as produced by ``kb.search.hybrid_search``
                 or ``kb.search.hybrid_search_v3``.

    Returns:
        An ``AskResult`` with a markdown answer, citation sources, and the
        average confidence across the cited entries.
    """
    if not results:
        return AskResult(
            success=True,
            answer="No relevant information found in the knowledge base.",
            sources=[],
            confidence=0.0,
        )

    by_type: Dict[str, List[Dict]] = defaultdict(list)
    for r in results:
        by_type[r.get("type", "unknown")].append(r)

    body_parts: List[str] = []
    sources: List[AskSource] = []
    total_confidence = 0.0

    for entry_type in _TYPE_ORDER:
        if entry_type not in by_type:
            continue
        type_results = by_type[entry_type]
        body_parts.append(f"\n## {entry_type.title()}s Found: {len(type_results)}")

        for i, r in enumerate(type_results[:_MAX_PER_TYPE], 1):
            conf = float(r.get("confidence", 0.5))
            sources.append(AskSource(
                id=r.get("id", "unknown"),
                title=r.get("title", "(untitled)"),
                type=r.get("type", entry_type),
                category=r.get("category", "unknown"),
                confidence=conf,
            ))
            total_confidence += conf

            body_parts.append(f"\n### {i}. {r.get('title', '(untitled)')} (`{r.get('id', '?')}`)")
            body_parts.append(
                f"**Type**: {r.get('type', entry_type)} | "
                f"**Category**: {r.get('category', 'unknown')} | "
                f"**Confidence**: {conf:.2f}"
            )
            if r.get("finding"):
                body_parts.append(f"**Finding**: {r['finding']}")
            if r.get("solution"):
                body_parts.append(f"**Solution**: {r['solution']}")
            if r.get("example"):
                body_parts.append(f"**Example**: {r['example']}")

    avg_confidence = total_confidence / len(sources) if sources else 0.0

    summary = (
        f"\n\n## Summary\n\n"
        f"Based on {len(sources)} relevant entries from the knowledge base, "
        f"with an average confidence of {avg_confidence:.2f}.\n"
    )
    if by_type.get("pattern"):
        first_pattern_solution = by_type["pattern"][0].get("solution", "")
        if first_pattern_solution:
            summary += f"\n**Key Pattern**: {first_pattern_solution[:200]}..."

    answer = summary + "\n" + "\n".join(body_parts)

    return AskResult(
        success=True,
        answer=answer,
        sources=sources,
        confidence=avg_confidence,
    )


# ---------------------------------------------------------------------------
# LLM-based synthesis
# ---------------------------------------------------------------------------

class LLMSynthesizer:
    """Generate answers using an LLM with RAG context.

    Uses a pluggable LLM callable so callers can supply any local or
    remote model (Ollama, llama.cpp, OpenAI-compatible, etc.).

    Args:
        llm: Callable ``fn(instruction: str, prompt: str) → str``.
             If ``None`` (default), the synthesizer cannot produce LLM
             answers and will fall back to template mode.
        prompt_template: Optional custom prompt template. Must contain
                         ``{question}`` and ``{context}`` placeholders.
        max_context_length: Maximum characters for the context block
                            (default: 8000). Longer contexts are truncated
                            from the end.

    Usage::

        from kb.synthesis import LLMSynthesizer

        def my_llm(instruction, prompt):
            # Call Ollama, OpenAI, etc.
            return "..."
        synth = LLMSynthesizer(llm=my_llm)
        result = synth.synthesize("What is RAG?", results)
    """

    def __init__(
        self,
        llm: Optional[Callable[[str, str], str]] = None,
        prompt_template: Optional[str] = None,
        max_context_length: int = 8000,
    ):
        self._llm = llm
        self._prompt_template = prompt_template or DEFAULT_SYNTHESIS_PROMPT
        self._max_context_length = max_context_length

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize(
        self,
        question: str,
        results: List[Dict],
        output_mode: str = "markdown",
    ) -> AskResult:
        """Generate an answer using the LLM.

        Args:
            question: The original user question.
            results: Retrieved KB entries (list of dicts).
            output_mode: ``"markdown"`` (default) or ``"json"`` for
                         structured output.

        Returns:
            An ``AskResult`` with the LLM-generated answer.
        """
        if not results:
            return AskResult(
                success=True,
                answer="No relevant information found in the knowledge base.",
                sources=[],
                confidence=0.0,
            )

        if self._llm is None:
            # No LLM configured — fall back to template
            return synthesize(question, results)

        # Build sources list
        sources = self._build_sources(results)
        context = self._format_context(results, sources)

        # Build and call LLM prompt
        if output_mode == "json":
            prompt = self._build_json_prompt(question, context)
        else:
            prompt = self._build_prompt(question, context)

        try:
            llm_response = self._llm(
                "You are a precise knowledge base assistant.",
                prompt,
            )
        except Exception as exc:
            # LLM call failed — fall back to template
            result = synthesize(question, results)
            result.answer += f"\n\n*(LLM synthesis failed: {exc}. Using template fallback.)*"
            return result

        if not llm_response or not llm_response.strip():
            return synthesize(question, results)

        # Parse response
        if output_mode == "json":
            return self._parse_json_response(llm_response, question, results, sources)
        else:
            return self._parse_markdown_response(llm_response, question, results, sources)

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_prompt(self, question: str, context: str) -> str:
        """Build the LLM prompt with question and context."""
        # Truncate context if too long
        if len(context) > self._max_context_length:
            context = context[: self._max_context_length] + "\n...[context truncated]"

        return self._prompt_template.format(
            question=question,
            context=context,
        )

    def _build_json_prompt(self, question: str, context: str) -> str:
        """Build a prompt that requests JSON structured output."""
        return f"""You are a precise knowledge base assistant. Answer the question based ONLY on the provided context.

Question: {question}

Retrieved Context:
{context}

Instructions:
1. Answer concisely and accurately based only on the context.
2. Cite sources using their ID.
3. If the context cannot answer, set "answer" to "The knowledge base does not contain information about..."
4. Return your response as a valid JSON object with these fields:
   - "answer": string (the main answer)
   - "confidence": float (0.0-1.0)
   - "sources": list of source IDs used
   - "summary": string (one-sentence summary)

Return ONLY the JSON object, no other text.

JSON Response:"""

    # ------------------------------------------------------------------
    # Context formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sources(results: List[Dict]) -> List[AskSource]:
        """Extract AskSource list from results."""
        sources: List[AskSource] = []
        seen_ids = set()
        for r in results:
            rid = r.get("id", "unknown")
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            sources.append(AskSource(
                id=rid,
                title=r.get("title", "(untitled)"),
                type=r.get("type", "unknown"),
                category=r.get("category", "unknown"),
                confidence=float(r.get("confidence", 0.5)),
            ))
        return sources

    @staticmethod
    def _format_context(results: List[Dict], sources: List[AskSource]) -> str:
        """Format results into a context block for the LLM."""
        parts: List[str] = []
        for i, r in enumerate(results):
            rid = r.get("id", "unknown")
            title = r.get("title", "(untitled)")
            finding = r.get("finding", "")
            solution = r.get("solution", "")
            example = r.get("example", "")

            entry_lines = [f"[{rid}] {title}"]
            if finding:
                entry_lines.append(f"  Finding: {finding}")
            if solution:
                entry_lines.append(f"  Solution: {solution}")
            if example:
                entry_lines.append(f"  Example: {example}")
            parts.append("\n".join(entry_lines))

        return "\n---\n".join(parts)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_markdown_response(
        llm_response: str,
        question: str,
        results: List[Dict],
        sources: List[AskSource],
    ) -> AskResult:
        """Parse an LLM markdown response into an AskResult."""
        # Extract confidence from response
        confidence = _extract_confidence_from_text(llm_response, sources)

        return AskResult(
            success=True,
            answer=llm_response.strip(),
            sources=sources,
            confidence=confidence,
        )

    @staticmethod
    def _parse_json_response(
        llm_response: str,
        question: str,
        results: List[Dict],
        sources: List[AskSource],
    ) -> AskResult:
        """Parse a JSON LLM response into an AskResult."""
        # Try to extract JSON from the response
        json_str = llm_response.strip()
        # Handle markdown code fences
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(json_str)
            answer = data.get("answer", llm_response.strip())
            confidence = float(data.get("confidence", 0.5))
            # Filter sources to just those cited in the JSON
            cited_ids = set(data.get("sources", []))
            cited_sources = [s for s in sources if s.id in cited_ids] or sources

            return AskResult(
                success=True,
                answer=answer,
                sources=cited_sources,
                confidence=min(max(confidence, 0.0), 1.0),
            )
        except (json.JSONDecodeError, ValueError, TypeError):
            # Fall back to markdown parsing
            return LLMSynthesizer._parse_markdown_response(
                llm_response, question, results, sources,
            )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def llm_synthesize(
    question: str,
    results: List[Dict],
    llm: Optional[Callable[[str, str], str]] = None,
    model: str = "",
    prompt_template: Optional[str] = None,
    output_mode: str = "markdown",
    max_context_length: int = 8000,
) -> AskResult:
    """Convenience function wrapping ``LLMSynthesizer``.

    Args:
        question: The original user question.
        results: Retrieved KB entries.
        llm: Optional LLM callable. If ``None``, falls back to template.
        model: Model name hint (passed to ``llm`` callable if provided).
        prompt_template: Optional custom prompt template.
        output_mode: ``"markdown"`` or ``"json"``.
        max_context_length: Max context characters.

    Returns:
        An ``AskResult``.
    """
    synthesizer = LLMSynthesizer(
        llm=llm,
        prompt_template=prompt_template,
        max_context_length=max_context_length,
    )
    return synthesizer.synthesize(question, results, output_mode=output_mode)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_confidence_from_text(text: str, sources: List[AskSource]) -> float:
    """Extract a confidence score from LLM response text.

    Looks for patterns like:
    - "Confidence: 0.85"
    - "confidence: high/medium/low"
    - Falls back to average source confidence.
    """
    # Look for explicit confidence score
    match = re.search(
        r"(?:confidence|conf)\s*[:\-=]\s*([01]\.\d+|1\.0|0\.\d+)",
        text,
        re.IGNORECASE,
    )
    if match:
        try:
            return min(max(float(match.group(1)), 0.0), 1.0)
        except ValueError:
            pass

    # Look for high/medium/low
    conf_match = re.search(
        r"(?:confidence|conf)\s*[:\-=]\s*(high|medium|low)",
        text,
        re.IGNORECASE,
    )
    if conf_match:
        mapping = {"high": 0.9, "medium": 0.6, "low": 0.3}
        return mapping.get(conf_match.group(1).lower(), 0.5)

    # Fall back to average source confidence
    if sources:
        return sum(s.confidence for s in sources) / len(sources)
    return 0.5

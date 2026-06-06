"""Query preprocessing for enhanced RAG retrieval.

Provides a ``QueryEngine`` that transforms raw user queries before they
enter the retrieval pipeline. Supports multiple modes:

- ``direct``: No transformation (passthrough).
- ``rewrite``: LLM-based query rewriting for clarity/expansion.
- ``hyde``: Hypothetical Document Embedding — generates a synthetic
  answer document and appends it as a second query.
- ``multi_query``: Generates N query variants for broader recall.
- ``decompose``: Breaks a complex question into sub-questions.

The LLM-based modes (rewrite, hyde, multi_query, decompose) use a
pluggable callable so callers can supply any local or remote LLM.
When no LLM is configured, those modes fall back to simple heuristics.
"""

import abc
import re
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

QueryTransformFn = Callable[[str], str]
"""Signature for a single-query transform: raw → rewritten."""


# ---------------------------------------------------------------------------
# QueryEngine
# ---------------------------------------------------------------------------

class QueryEngine:
    """Query preprocessing pipeline.

    Transforms a raw user query into one or more query variants to improve
    retrieval recall and precision.

    Args:
        mode: Processing mode (see class docstring). Default ``"direct"``.
        llm: Optional LLM callable ``fn(instruction, prompt) → str``.
              If ``None``, LLM-dependent modes fall back to heuristics.
        n_variants: Number of query variants for ``multi_query`` mode.
        hyde_instruction: Override instruction for HyDE generation.

    Usage::

        qe = QueryEngine(mode="multi_query", n_variants=3)
        queries = qe.process("How do I implement a retriever?")
        # → ["How do I implement a retriever?",
        #     "How to build a retriever class?",
        #     "Steps for creating a retriever component"]
    """

    def __init__(
        self,
        mode: str = "direct",
        llm: Optional[QueryTransformFn] = None,
        n_variants: int = 3,
        hyde_instruction: Optional[str] = None,
    ):
        self._mode = mode
        self._llm = llm
        self._n_variants = n_variants
        self._hyde_instruction = hyde_instruction

        # Validate mode
        valid_modes = {"direct", "rewrite", "hyde", "multi_query", "decompose"}
        if mode not in valid_modes:
            raise ValueError(
                f"Unknown query mode: {mode!r}. "
                f"Valid modes: {sorted(valid_modes)}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def mode(self) -> str:
        """Current processing mode."""
        return self._mode

    def process(self, query: str) -> List[str]:
        """Transform a raw query into one or more query variants.

        Args:
            query: The raw user query string.

        Returns:
            A list of query strings to use for retrieval. The first
            element is always the original query (or a rewritten version
            in ``rewrite`` mode).
        """
        if not query or not query.strip():
            return [""]

        dispatch = {
            "direct": self._process_direct,
            "rewrite": self._process_rewrite,
            "hyde": self._process_hyde,
            "multi_query": self._process_multi_query,
            "decompose": self._process_decompose,
        }
        return dispatch[self._mode](query.strip())

    # ------------------------------------------------------------------
    # Direct (no-op)
    # ------------------------------------------------------------------

    def _process_direct(self, query: str) -> List[str]:
        """Pass-through — single original query."""
        return [query]

    # ------------------------------------------------------------------
    # Rewrite
    # ------------------------------------------------------------------

    def _process_rewrite(self, query: str) -> List[str]:
        """LLM-based rewrite, with heuristic fallback."""
        if self._llm is not None:
            instruction = (
                "You are a query rewriting assistant. Rewrite the following "
                "search query to be clearer and more specific for a knowledge "
                "base search. Return ONLY the rewritten query, no explanation."
            )
            rewritten = self._llm(instruction, query)
            if rewritten and rewritten.strip():
                return [rewritten.strip()]
        # Fallback: heuristic expansion
        return self._heuristic_rewrite(query)

    @staticmethod
    def _heuristic_rewrite(query: str) -> List[str]:
        """Heuristic query rewrite when no LLM is available.

        Expands common abbreviations and returns the expanded form.
        """
        abbreviations = {
            r"\bkb\b": "knowledge base",
            r"\brag\b": "retrieval augmented generation",
            r"\bllm\b": "large language model",
            r"\bann\b": "approximate nearest neighbor",
            r"\brrf\b": "reciprocal rank fusion",
            r"\bmrr\b": "mean reciprocal rank",
            r"\bndcg\b": "normalized discounted cumulative gain",
            r"\bhyde\b": "hypothetical document embedding",
            r"\bmmr\b": "maximal marginal relevance",
            r"\bbm25\b": "BM25 ranking function",
        }
        expanded = query
        for pattern, replacement in abbreviations.items():
            expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
        return [expanded] if expanded != query else [query]

    # ------------------------------------------------------------------
    # HyDE (Hypothetical Document Embedding)
    # ------------------------------------------------------------------

    def _process_hyde(self, query: str) -> List[str]:
        """Generate a hypothetical document and use it as an additional query.

        Returns the original query plus the hypothetical document.
        """
        if self._llm is not None:
            instruction = self._hyde_instruction or (
                "You are a knowledge base assistant. Given a question, write "
                "a paragraph that answers the question as if you had retrieved "
                "the perfect document. Include specific technical details. "
                "Return ONLY the paragraph, no preamble."
            )
            hypo_doc = self._llm(instruction, query)
            if hypo_doc and hypo_doc.strip():
                return [query, hypo_doc.strip()]
        # No LLM: return query twice (dense retriever will embed both
        # identically, so HyDE has no effect — the fusion stage still
        # deduplicates on ID)
        return [query]

    # ------------------------------------------------------------------
    # Multi-Query
    # ------------------------------------------------------------------

    def _process_multi_query(self, query: str) -> List[str]:
        """Generate N query variants for broader recall."""
        if self._llm is not None and self._n_variants > 1:
            variants = self._llm(
                (
                    f"You are a query expansion assistant. Generate "
                    f"{self._n_variants - 1} alternative phrasings of the "
                    "given search query. Each on a new line. "
                    "Return ONLY the variants, numbered or bullet-free."
                ),
                query,
            )
            if variants:
                parsed = [
                    v.strip().lstrip("-*0123456789. ")
                    for v in variants.strip().split("\n")
                    if v.strip()
                ]
                valid = [v for v in parsed if v and len(v) > 5]
                if valid:
                    return [query] + valid[: self._n_variants - 1]

        # Heuristic fallback: generate simple variants
        return self._heuristic_multi_query(query)

    @staticmethod
    def _heuristic_multi_query(query: str) -> List[str]:
        """Generate simple query variants heuristically.

        Strategies:
        - Remove stopword-like filler phrases
        - Convert "how to X" → "X steps" / "X guide"
        """
        variants = [query]

        # "how to / how do I" → "steps for / guide to"
        how_match = re.match(
            r"how (to|do|does|can|would|should|will)\s+(.+)",
            query,
            re.IGNORECASE,
        )
        if how_match:
            action = how_match.group(2).strip()
            variants.append(f"steps for {action}")
            variants.append(f"guide to {action}")

        # "what is X" → "X explained" / "definition X"
        what_match = re.match(r"what (is|are|was|were)\s+(.+)", query, re.IGNORECASE)
        if what_match:
            subject = what_match.group(2).strip()
            variants.append(f"{subject} explained")
            variants.append(f"definition of {subject}")

        return variants[:3]

    # ------------------------------------------------------------------
    # Decompose
    # ------------------------------------------------------------------

    def _process_decompose(self, query: str) -> List[str]:
        """Decompose a complex question into sub-questions.

        Returns the original query plus sub-questions.
        """
        if self._llm is not None:
            sub_queries = self._llm(
                (
                    "You are a question decomposition assistant. Break the "
                    "following complex question into 2-3 simpler sub-questions "
                    "that each target a different aspect. Return each on a new "
                    "line. Return ONLY the sub-questions, no preamble."
                ),
                query,
            )
            if sub_queries:
                parsed = [
                    v.strip().lstrip("-*0123456789. ")
                    for v in sub_queries.strip().split("\n")
                    if v.strip()
                ]
                valid = [v for v in parsed if v and len(v) > 5]
                if valid:
                    return [query] + valid[:3]

        # Heuristic: split on "and" / "also" / comma + conjunction
        return self._heuristic_decompose(query)

    @staticmethod
    def _heuristic_decompose(query: str) -> List[str]:
        """Simple heuristic decomposition without LLM.

        Splits on " and ", " also ", and sentence-final punctuation.
        """
        parts = re.split(r"\s+(?:and|also|plus)\s+", query, flags=re.IGNORECASE)
        if len(parts) >= 2:
            return [query] + [p.strip().rstrip(".,;!?") + "?" for p in parts if p.strip()]
        return [query]

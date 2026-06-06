"""Tests for ``kb.query_engine.QueryEngine``."""

import pytest
from kb.query_engine import QueryEngine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_QUERIES = {
    "how_to": "how to implement a retriever",
    "what_is": "what is RRF fusion",
    "complex": "how to build a retriever and what is reranking",
    "short": "KB query",
}


# ---------------------------------------------------------------------------
# Direct mode
# ---------------------------------------------------------------------------

class TestDirectMode:
    def test_passes_query_through_unchanged(self):
        qe = QueryEngine(mode="direct")
        assert qe.process("hello world") == ["hello world"]

    def test_mode_property(self):
        qe = QueryEngine(mode="direct")
        assert qe.mode == "direct"

    def test_empty_query_returns_list_with_empty_string(self):
        qe = QueryEngine(mode="direct")
        assert qe.process("") == [""]

    def test_whitespace_query_returns_list_with_empty_string(self):
        qe = QueryEngine(mode="direct")
        assert qe.process("   ") == [""]


# ---------------------------------------------------------------------------
# Rewrite mode
# ---------------------------------------------------------------------------

class TestRewriteMode:
    def test_without_llm_falls_back_to_heuristic(self):
        qe = QueryEngine(mode="rewrite")
        result = qe.process("KB query")
        assert len(result) == 1
        # Heuristic should expand "KB" → "knowledge base"
        assert "knowledge base" in result[0].lower()

    def test_heuristic_expands_common_abbreviations(self):
        qe = QueryEngine(mode="rewrite")
        cases = {
            "KB": "knowledge base",
            "RAG": "retrieval augmented generation",
            "LLM": "large language model",
            "ANN": "approximate nearest neighbor",
            "RRF": "reciprocal rank fusion",
        }
        for abbrev, expansion in cases.items():
            result = qe.process(f"what is {abbrev}")
            assert expansion in result[0].lower(), f"{abbrev} → {expansion}"

    def test_with_llm_uses_llm_callable(self):
        def fake_llm(instruction, prompt):
            return "rewritten: " + prompt

        qe = QueryEngine(mode="rewrite", llm=fake_llm)
        result = qe.process("test query")
        assert result[0] == "rewritten: test query"

    def test_with_llm_strips_result(self):
        def fake_llm(instruction, prompt):
            return "  rewritten query  \n"

        qe = QueryEngine(mode="rewrite", llm=fake_llm)
        result = qe.process("test")
        assert result[0] == "rewritten query"

    def test_with_llm_returning_empty_falls_back(self):
        calls = []

        def fake_llm(instruction, prompt):
            calls.append(prompt)
            return ""

        qe = QueryEngine(mode="rewrite", llm=fake_llm)
        result = qe.process("KB test")
        assert len(result) == 1
        assert "knowledge base" in result[0]


# ---------------------------------------------------------------------------
# HyDE mode
# ---------------------------------------------------------------------------

class TestHydeMode:
    def test_without_llm_returns_single_query(self):
        qe = QueryEngine(mode="hyde")
        result = qe.process("test query")
        # Without LLM, HyDE mode returns [query] (no duplicate HyDE doc)
        assert result == ["test query"]

    def test_with_llm_returns_query_and_hypo_doc(self):
        def fake_llm(instruction, prompt):
            return "A hypothetical answer document."

        qe = QueryEngine(mode="hyde", llm=fake_llm)
        result = qe.process("test query")
        assert len(result) == 2
        assert result[0] == "test query"
        assert "hypothetical" in result[1]

    def test_custom_hyde_instruction(self):
        custom_inst = "Write a technical document about:"
        calls = []

        def fake_llm(instruction, prompt):
            calls.append(instruction)
            return "Custom answer."

        qe = QueryEngine(mode="hyde", llm=fake_llm, hyde_instruction=custom_inst)
        qe.process("test")
        assert calls[0] == custom_inst


# ---------------------------------------------------------------------------
# Multi-Query mode
# ---------------------------------------------------------------------------

class TestMultiQueryMode:
    def test_without_llm_uses_heuristic(self):
        qe = QueryEngine(mode="multi_query")
        result = qe.process("how to implement a retriever")
        assert len(result) >= 1
        assert result[0] == "how to implement a retriever"
        # Heuristic should produce at least one variant
        assert any("steps" in v or "guide" in v for v in result)

    def test_what_is_generates_explained_variants(self):
        qe = QueryEngine(mode="multi_query")
        result = qe.process("what is RRF fusion")
        assert any("explained" in v or "definition" in v for v in result[1:])

    def test_with_llm_generates_variants(self):
        def fake_llm(instruction, prompt):
            return "variant1\nvariant2"

        qe = QueryEngine(mode="multi_query", llm=fake_llm, n_variants=3)
        result = qe.process("test query")
        assert len(result) == 3
        assert result[0] == "test query"
        assert result[1] == "variant1"

    def test_respects_n_variants(self):
        qe = QueryEngine(mode="multi_query", n_variants=5)
        result = qe.process("how to code")
        assert len(result) <= 5

    def test_short_query_still_has_original(self):
        qe = QueryEngine(mode="multi_query")
        result = qe.process("short")
        assert result[0] == "short"


# ---------------------------------------------------------------------------
# Decompose mode
# ---------------------------------------------------------------------------

class TestDecomposeMode:
    def test_without_llm_splits_on_and(self):
        qe = QueryEngine(mode="decompose")
        result = qe.process("how to build a retriever and what is reranking")
        assert len(result) >= 2
        assert result[0] == "how to build a retriever and what is reranking"

    def test_with_llm_uses_llm_response(self):
        def fake_llm(instruction, prompt):
            return "sub question one\nsub question two"

        qe = QueryEngine(mode="decompose", llm=fake_llm)
        result = qe.process("complex question")
        assert len(result) == 3  # original + 2 subs
        assert "sub question one" in result

    def test_non_complex_returns_single(self):
        qe = QueryEngine(mode="decompose")
        result = qe.process("simple query")
        # No "and/also" to split on
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Mode validation
# ---------------------------------------------------------------------------

class TestModeValidation:
    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown query mode"):
            QueryEngine(mode="invalid_mode")

    def test_valid_modes_accepted(self):
        for mode in ("direct", "rewrite", "hyde", "multi_query", "decompose"):
            qe = QueryEngine(mode=mode)
            assert qe.mode == mode

    def test_empty_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown query mode"):
            QueryEngine(mode="")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_none_query(self):
        qe = QueryEngine(mode="direct")
        # None is falsy, so process returns [""] before reaching .strip()
        result = qe.process(None)  # type: ignore[arg-type]
        assert result == [""]

    def test_special_characters_preserved(self):
        qe = QueryEngine(mode="direct")
        result = qe.process("C++ vs Python: what's faster?")
        assert result[0] == "C++ vs Python: what's faster?"

    def test_unicode_text(self):
        qe = QueryEngine(mode="direct")
        result = qe.process("über cool")
        assert result[0] == "über cool"

    def test_heuristic_rewrite_non_abbreviation(self):
        qe = QueryEngine(mode="rewrite")
        result = qe.process("normal query without abbreviations")
        assert result[0] == "normal query without abbreviations"

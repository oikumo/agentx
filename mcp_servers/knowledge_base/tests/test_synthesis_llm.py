"""Tests for ``kb.synthesis.LLMSynthesizer`` and ``llm_synthesize``."""

import json
import pytest
from kb.synthesis import LLMSynthesizer, llm_synthesize, _extract_confidence_from_text
from kb.models import AskSource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_results():
    return [
        {
            "id": "PAT-001",
            "type": "pattern",
            "category": "code",
            "title": "Retriever Pattern",
            "finding": "The retriever pattern improves search accuracy.",
            "solution": "Use DenseRetriever with hybrid search.",
            "confidence": 0.9,
        },
        {
            "id": "PAT-002",
            "type": "pattern",
            "category": "architecture",
            "title": "RAG Pipeline",
            "finding": "RAG combines retrieval with generation.",
            "solution": "Use a retriever + synthesizer pipeline.",
            "confidence": 0.85,
        },
    ]


@pytest.fixture
def sample_sources():
    return [
        AskSource(id="PAT-001", title="Retriever Pattern", type="pattern",
                  category="code", confidence=0.9),
        AskSource(id="PAT-002", title="RAG Pipeline", type="pattern",
                  category="architecture", confidence=0.85),
    ]


# ---------------------------------------------------------------------------
# LLMSynthesizer basic construction
# ---------------------------------------------------------------------------

class TestLLMSynthesizerInit:
    def test_default_construction(self):
        synth = LLMSynthesizer()
        assert synth._llm is None
        assert synth._max_context_length == 8000

    def test_with_llm_callable(self):
        def fake_llm(inst, prompt):
            return "test"
        synth = LLMSynthesizer(llm=fake_llm)
        assert synth._llm is not None

    def test_custom_prompt_template(self):
        template = "Custom: {question} / {context}"
        synth = LLMSynthesizer(prompt_template=template)
        assert synth._prompt_template == template

    def test_custom_max_context(self):
        synth = LLMSynthesizer(max_context_length=500)
        assert synth._max_context_length == 500


# ---------------------------------------------------------------------------
# synthesize with no results
# ---------------------------------------------------------------------------

class TestSynthesizeNoResults:
    def test_returns_empty_result(self):
        synth = LLMSynthesizer()
        result = synth.synthesize("test", [])
        assert result.success is True
        assert "No relevant information" in result.answer
        assert result.sources == []
        assert result.confidence == 0.0

    def test_with_llm_also_returns_empty(self):
        def fake_llm(inst, prompt):
            return "should not be called"
        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", [])
        assert "No relevant information" in result.answer


# ---------------------------------------------------------------------------
# synthesize with no LLM (falls back to template)
# ---------------------------------------------------------------------------

class TestSynthesizeNoLLM:
    def test_falls_back_to_template(self, sample_results):
        synth = LLMSynthesizer()
        result = synth.synthesize("test", sample_results)
        # Template output should have "Patterns Found"
        assert "Patterns Found" in result.answer
        assert len(result.sources) == 2
        assert result.confidence > 0


# ---------------------------------------------------------------------------
# synthesize with LLM — markdown output
# ---------------------------------------------------------------------------

class TestSynthesizeWithLLM:
    def test_markdown_output(self, sample_results):
        def fake_llm(inst, prompt):
            assert "PAT-001" in prompt or "PAT-002" in prompt
            return "**Answer:** The retriever pattern improves accuracy. Confidence: 0.88"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results)
        assert result.success is True
        assert "**Answer:**" in result.answer
        assert len(result.sources) == 2
        assert result.confidence == 0.88

    def test_confidence_from_text(self, sample_results):
        def fake_llm(inst, prompt):
            return "Some answer. confidence: 0.75"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results)
        assert result.confidence == 0.75

    def test_llm_returning_empty_falls_to_template(self, sample_results):
        def fake_llm(inst, prompt):
            return ""

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results)
        # Should fall back to template
        assert "Patterns Found" in result.answer

    def test_llm_returning_whitespace_falls_to_template(self, sample_results):
        def fake_llm(inst, prompt):
            return "   \n  \n"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results)
        assert "Patterns Found" in result.answer


# ---------------------------------------------------------------------------
# JSON output mode
# ---------------------------------------------------------------------------

class TestJSONOutput:
    def test_json_output(self, sample_results):
        def fake_llm(inst, prompt):
            return json.dumps({
                "answer": "The retriever pattern improves accuracy.",
                "confidence": 0.88,
                "sources": ["PAT-001"],
                "summary": "Retrievers boost accuracy.",
            })

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results, output_mode="json")
        assert result.success is True
        assert "retriever pattern" in result.answer.lower()
        assert result.confidence == 0.88
        # Should only include cited sources
        assert len(result.sources) == 1
        assert result.sources[0].id == "PAT-001"

    def test_json_in_code_fence(self, sample_results):
        def fake_llm(inst, prompt):
            return f"```json\n{json.dumps({'answer': 'test', 'confidence': 0.9, 'sources': []})}\n```"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results, output_mode="json")
        assert result.success is True
        assert result.confidence == 0.9

    def test_invalid_json_falls_to_markdown(self, sample_results):
        def fake_llm(inst, prompt):
            return "This is not JSON. confidence: 0.7"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results, output_mode="json")
        # Should fall back to markdown parsing
        assert result.success is True
        assert result.confidence == 0.7

    def test_malformed_json_falls_to_markdown(self, sample_results):
        def fake_llm(inst, prompt):
            return "{invalid json}"

        synth = LLMSynthesizer(llm=fake_llm)
        result = synth.synthesize("test", sample_results, output_mode="json")
        assert result.success is True
        # Falls back - confidence from source average
        assert result.confidence > 0


# ---------------------------------------------------------------------------
# LLM call failure
# ---------------------------------------------------------------------------

class TestLLMFailure:
    def test_llm_exception_falls_back(self, sample_results):
        def failing_llm(inst, prompt):
            raise RuntimeError("Model not available")

        synth = LLMSynthesizer(llm=failing_llm)
        result = synth.synthesize("test", sample_results)
        assert result.success is True
        assert "Patterns Found" in result.answer
        assert "LLM synthesis failed" in result.answer


# ---------------------------------------------------------------------------
# Context formatting
# ---------------------------------------------------------------------------

class TestContextFormatting:
    def test_context_includes_entries(self, sample_results):
        synth = LLMSynthesizer(llm=lambda i, p: f"context received: {len(p)} chars")
        result = synth.synthesize("test", sample_results)
        assert result.success is True

    def test_context_truncation(self, sample_results):
        synth = LLMSynthesizer(llm=lambda i, p: p, max_context_length=100)
        result = synth.synthesize("test", sample_results)
        # Context should be truncated
        assert "[context truncated]" in result.answer


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

class TestPromptBuilding:
    def test_prompt_contains_question(self):
        synth = LLMSynthesizer()
        prompt = synth._build_prompt("What is RAG?", "context here")
        assert "What is RAG?" in prompt
        assert "context here" in prompt

    def test_json_prompt_contains_json_instruction(self):
        synth = LLMSynthesizer()
        prompt = synth._build_json_prompt("What is RAG?", "context here")
        assert "JSON" in prompt
        assert "answer" in prompt
        assert "confidence" in prompt


# ---------------------------------------------------------------------------
# _extract_confidence_from_text
# ---------------------------------------------------------------------------

class TestExtractConfidence:
    def test_explicit_confidence(self, sample_sources):
        assert _extract_confidence_from_text("Confidence: 0.85", sample_sources) == 0.85

    def test_confidence_colon_variants(self, sample_sources):
        assert _extract_confidence_from_text("conf: 0.75", sample_sources) == 0.75
        assert _extract_confidence_from_text("confidence = 0.9", sample_sources) == 0.9

    def test_high_medium_low(self, sample_sources):
        assert _extract_confidence_from_text("Confidence: high", sample_sources) == 0.9
        assert _extract_confidence_from_text("Confidence: medium", sample_sources) == 0.6
        assert _extract_confidence_from_text("Confidence: low", sample_sources) == 0.3

    def test_falls_back_to_source_average(self, sample_sources):
        conf = _extract_confidence_from_text("No confidence mentioned", sample_sources)
        assert conf == pytest.approx(0.875)  # (0.9 + 0.85) / 2

    def test_empty_sources_falls_to_05(self):
        assert _extract_confidence_from_text("no pattern", []) == 0.5

    def test_no_confidence_in_text(self, sample_sources):
        conf = _extract_confidence_from_text("Just a normal answer without score", sample_sources)
        assert conf == pytest.approx(0.875)


# ---------------------------------------------------------------------------
# llm_synthesize convenience function
# ---------------------------------------------------------------------------

class TestLLMSynthesizeFunction:
    def test_without_llm_falls_to_template(self, sample_results):
        result = llm_synthesize("test", sample_results)
        assert "Patterns Found" in result.answer

    def test_with_llm(self, sample_results):
        def fake_llm(inst, prompt):
            return "LLM answer. Confidence: 0.9"

        result = llm_synthesize("test", sample_results, llm=fake_llm)
        assert "LLM answer" in result.answer
        assert result.confidence == 0.9

    def test_json_mode(self, sample_results):
        def fake_llm(inst, prompt):
            return json.dumps({"answer": "json answer", "confidence": 0.85, "sources": []})

        result = llm_synthesize("test", sample_results, llm=fake_llm, output_mode="json")
        assert result.confidence == 0.85

    def test_custom_prompt(self, sample_results):
        def fake_llm(inst, prompt):
            assert "CUSTOM" in prompt
            return "Custom answer"

        result = llm_synthesize(
            "test", sample_results, llm=fake_llm,
            prompt_template="CUSTOM {question} / {context}",
        )
        assert "Custom answer" in result.answer

    def test_empty_results(self):
        result = llm_synthesize("test", [])
        assert "No relevant information" in result.answer

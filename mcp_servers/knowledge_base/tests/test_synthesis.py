"""Unit tests for `kb.synthesis.synthesize`."""

from kb.synthesis import synthesize


def _make(id_, type_, title, conf=0.8, category="class"):
    return {
        "id": id_, "type": type_, "category": category,
        "title": title, "finding": f"finding for {title}",
        "solution": f"solution for {title}", "confidence": conf,
    }


def test_empty_results_returns_no_info_message_with_zero_confidence():
    r = synthesize("anything", [])
    assert r.success is True
    assert r.confidence == 0.0
    assert r.sources == []
    assert "No relevant information" in r.answer


def test_single_pattern_result_is_summarised_with_its_confidence():
    r = synthesize("q", [_make("PAT-1", "pattern", "X", conf=0.9)])
    assert r.success is True
    assert r.confidence == 0.9
    assert len(r.sources) == 1
    assert r.sources[0].id == "PAT-1"
    assert "X" in r.answer
    assert "PAT-1" in r.answer


def test_average_confidence_is_correctly_computed():
    results = [
        _make("A", "pattern", "P", 0.8),
        _make("B", "finding", "F", 0.6),
    ]
    r = synthesize("q", results)
    # (0.8 + 0.6) / 2
    assert abs(r.confidence - 0.7) < 1e-9


def test_results_are_grouped_by_type_in_canonical_order():
    results = [
        _make("F1", "finding", "first finding"),
        _make("P1", "pattern", "first pattern"),
        _make("D1", "decision", "first decision"),
    ]
    r = synthesize("q", results)
    idx_pattern = r.answer.index("Patterns Found")
    idx_finding = r.answer.index("Findings Found")
    idx_decision = r.answer.index("Decisions Found")
    # canonical order is pattern -> finding -> decision -> correction
    assert idx_pattern < idx_finding < idx_decision


def test_output_is_not_a_prompt_template():
    """Regression for Plan §6: kb_ask must not return the old prompt skeleton."""
    r = synthesize("q", [_make("PAT-1", "pattern", "X")])
    assert "You are an AI agent" not in r.answer
    assert "### Your Answer:" not in r.answer

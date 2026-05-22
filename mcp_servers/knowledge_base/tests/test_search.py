"""Unit tests for the pure scoring functions in `kb.search`."""

from kb.search import keyword_score, semantic_boost, simple_tokenize


def test_simple_tokenize_lowercases_and_extracts_words():
    assert simple_tokenize("Hello, World! 123") == ["hello", "world", "123"]


def test_simple_tokenize_empty_returns_empty_list():
    assert simple_tokenize("") == []
    assert simple_tokenize(None) == []  # type: ignore[arg-type]


def test_keyword_score_returns_zero_for_no_overlap():
    assert keyword_score("apple banana", "carrot dragonfruit") == 0.0


def test_keyword_score_returns_zero_for_empty_inputs():
    assert keyword_score("", "anything") == 0.0
    assert keyword_score("anything", "") == 0.0


def test_keyword_score_is_in_unit_range():
    s = keyword_score("the quick brown fox jumps over the lazy dog",
                      "quick fox")
    assert 0.0 <= s <= 1.0
    assert s > 0


def test_keyword_score_rewards_exact_substring():
    s_substr = keyword_score("foo bar baz", "foo bar")
    s_disjoint = keyword_score("foo qux baz", "foo bar")
    # Substring presence should beat token-set equality with non-adjacent words.
    assert s_substr > s_disjoint


def test_semantic_boost_returns_value_in_expected_range():
    entry = {"title": "KBStore class", "finding": "store wraps Chroma",
             "solution": "use KBStore", "context": "kb module"}
    boost = semantic_boost(entry, "KBStore Chroma")
    # semantic_boost = 0.8 + score * 0.4, score in [0, 1]
    assert 0.8 <= boost <= 1.2


def test_semantic_boost_higher_when_title_matches():
    e_match = {"title": "KBStore wrapper", "finding": "x", "solution": "y", "context": "z"}
    e_no_match = {"title": "unrelated thing", "finding": "x", "solution": "y", "context": "z"}
    assert semantic_boost(e_match, "KBStore") > semantic_boost(e_no_match, "KBStore")
